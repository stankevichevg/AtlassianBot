from flask import Flask, request, make_response
from werkzeug.contrib.cache import SimpleCache
import wand.image
from utils.imageproxy import decode

CACHE_RETENTION = 24 * 60 * 60
cache = SimpleCache()

app = Flask(__name__)
app.debug = False


@app.route('/image/<content_type>/<content>', methods=['GET'])
def convert(content_type, content):
    cachekey = request.path

    cachevalue = cache.get(cachekey)

    if cachevalue is None:
        content = decode(content)
        content_type = decode(content_type).decode()
        if content_type.startswith('image/svg+xml'):
            content = __svg2png(content)
            content_type = 'image/png'

        cache.set(cachekey, (content, content_type), timeout=CACHE_RETENTION)
    else:
        content = cachevalue[0]
        content_type = cachevalue[1]

    response = make_response(content)
    response.content_type = content_type
    response.cache_control.max_age = CACHE_RETENTION
    return response


def __svg2png(data):
    with wand.image.Image(blob=data, format="svg") as image:
        return image.make_blob("png")


if __name__ == '__main__':
    app.run()
