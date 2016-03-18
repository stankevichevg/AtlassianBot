from flask import Flask, request, Response
from werkzeug.contrib.cache import SimpleCache
import wand.image
from base64 import b64decode

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024  # 50KB max for uploaded images
app.debug = False


CACHE_TIMEOUT = 24 * 60 * 60

cache = SimpleCache()


@app.route('/converticon/<content_type>/<content>', methods=['GET'])
def convert(content_type, content):
    cachekey = request.path
    print(cachekey)
    content_type = b64decode(content_type.encode(), altchars='-_').decode()
    content = b64decode(content.encode(), altchars='-_')

    cachevalue = cache.get(cachekey)
    if cachevalue is None:
        print('Add in cache')
        if content_type.startswith('image/svg+xml'):
            content = svg2png(content)
            content_type = 'image/png'

        cache.set(cachekey, content, timeout=CACHE_TIMEOUT)
        cachevalue = content

    return Response(content, mimetype=content_type)


def svg2png(data):
    with wand.image.Image(blob=data, format="svg") as image:
        return image.make_blob("png")


if __name__ == '__main__':
    app.run()
