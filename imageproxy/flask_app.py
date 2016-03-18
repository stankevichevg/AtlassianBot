from flask import Flask, request, Response
from werkzeug.contrib.cache import SimpleCache
import wand.image
from base64 import b64decode

app = Flask(__name__)
app.debug = False


CACHE_TIMEOUT = 24 * 60 * 60

cache = SimpleCache()


@app.route('/converticon/<content_type>/<content>', methods=['GET'])
def convert(content_type, content):
    cachekey = request.path

    cachevalue = cache.get(cachekey)

    if cachevalue is None:
        content = b64decode(content.encode(), altchars='-_')
        content_type = b64decode(content_type.encode(), altchars='-_').decode()

        if content_type.startswith('image/svg+xml'):
            content = svg2png(content)
            content_type = 'image/png'

        cache.set(cachekey, content, timeout=CACHE_TIMEOUT)
        cachevalue = content
    else:
        content_type = 'image/pmg'

    return Response(cachevalue, content_type=content_type)


@app.after_request
def add_header(response):
    response.cache_control.max_age = CACHE_TIMEOUT
    return response


def svg2png(data):
    with wand.image.Image(blob=data, format="svg") as image:
        return image.make_blob("png")


if __name__ == '__main__':
    app.run()
