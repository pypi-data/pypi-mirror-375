__all__ = ["CompressionMiddleware"]


from django import VERSION as DJANGO_VERSION
from django.http import HttpRequest, HttpResponse
from django.middleware.gzip import compress_sequence as gzip_compress_stream, compress_string as gzip_compress
from django.utils.cache import patch_vary_headers

from .br import brotli_compress, brotli_compress_stream
from .zstd import zstd_compress, zstd_compress_stream


try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:  # pragma: no cover
    MiddlewareMixin = object


# Minimum response length before we'll consider compression. Small responses
# won't necessarily be smaller after compression, and we want to save at least
# enough to make the time expended worthwhile. Since MTUs around 1500 are
# common, and HTTP headers are often more than 500 bytes (more so if there
# are cookies), we guess that responses smaller than 500 bytes is likely to fit
# in the MTU (or not) mostly due to other factors, not compression.
MIN_LEN = 500

# The compression has to reduce the length, otherwise we're just fooling
# around. Since we'll have to add the Content-Encoding header, we need to
# make that addition worthwhile, too. So the compressed response must be
# smaller by some margin. This value should be at least 24 which is
# len("Content-Encoding: gzip\r\n"), but a bigger value could reflect that a
# non-trivial improvement in transfer time is required to make up for the time
# required for decompression. An improvement of a few bytes is unlikely to
# actually reduce the network communication in terms of MTUs.
MIN_IMPROVEMENT = 100


# supported encodings in order of preference
# (encoding, bulk_compressor, stream_compressor)
compressors = (
    ("zstd", zstd_compress, zstd_compress_stream),
    ("br", brotli_compress, brotli_compress_stream),
    ("gzip", gzip_compress, gzip_compress_stream),
)


def encoding_name(s):
    """Obtain 'br' out of ' br;q=0.5' or similar."""
    # We won't break if the ordering is specified with q=, but we ignore it.
    # Only a quality level of 0 is honoured -- in such a case we handle it as
    # if the encoding wasn't specified at all.
    if ";" in s:
        s, q = s.split(";", 1)
        if "=" in q:
            _, q = q.split("=", 1)
            try:
                q = float(q)
                if q == 0.0:
                    return None
            except ValueError:
                pass
    return s.strip()


def compressor(accept_encoding):
    # We don't want to process extremely long headers. It might be an attack:
    accept_encoding = accept_encoding[:200]
    client_encodings = {encoding_name(e) for e in accept_encoding.split(",")}
    if "*" in client_encodings:
        # Our first choice:
        return compressors[0]
    for compressor in compressors:
        if compressor[0] in client_encodings:
            return compressor
    return (None, None, None)


class CompressionMiddleware(MiddlewareMixin):
    """Compress content if the browser allows gzip, brotli or zstd compression.

    Set the Vary header accordingly, so that caches will base their storage
    on the Accept-Encoding header.
    """

    max_random_bytes = 100

    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:  # noqa: D102
        # It's not worth attempting to compress really short responses.
        if not response.streaming and len(response.content) < MIN_LEN:
            return response

        # Avoid compression if we've already got a content-encoding.
        if response.has_header("Content-Encoding"):
            return response

        patch_vary_headers(response, ("Accept-Encoding",))

        ae = request.META.get("HTTP_ACCEPT_ENCODING", "")
        encoding, compress_string, compress_sequence = compressor(ae)
        if encoding is None:
            # No compression in common with client (the client probably didn't indicate support for anything).
            return response

        compress_kwargs = {}
        if encoding == "gzip" and DJANGO_VERSION >= (4, 2):
            compress_kwargs["max_random_bytes"] = self.max_random_bytes

        if response.streaming:
            if getattr(response, "is_async", False):
                # forward args explicitly to capture fixed references in case they are set again later.
                async def compress_wrapper(streaming_content, **compress_kwargs):
                    async for chunk in streaming_content:
                        yield compress_string(chunk, **compress_kwargs)

                response.streaming_content = compress_wrapper(response.streaming_content, **compress_kwargs)
            else:
                response.streaming_content = compress_sequence(response.streaming_content, **compress_kwargs)

            # Delete the `Content-Length` header for streaming content, because
            # we won't know the compressed size until we stream it.
            del response.headers["Content-Length"]
        else:
            # Return the compressed content only if it's actually shorter.
            compressed_content = compress_string(response.content, **compress_kwargs)
            if len(response.content) - len(compressed_content) < MIN_IMPROVEMENT:
                return response
            response.content = compressed_content
            response.headers["Content-Length"] = str(len(response.content))

        # If there is a strong ETag, make it weak to fulfill the requirements
        # of RFC 9110 Section 8.8.1 while also allowing conditional request
        # matches on ETags.
        etag = response.headers.get("ETag")
        if etag and etag.startswith('"'):
            response.headers["ETag"] = "W/" + etag
        response.headers["Content-Encoding"] = encoding

        return response
