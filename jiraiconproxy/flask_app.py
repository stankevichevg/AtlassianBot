from flask import Flask, abort, request, Response
from werkzeug.contrib.cache import SimpleCache
import wand.image


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024  # 50KB max for uploaded images
app.debug = False


CACHE_TIMEOUT = 24 * 60 * 60

cache = SimpleCache()


@app.route('/get', methods=['GET'])
def get():
    url = request.args.get('url', '')

    cacheitem = cache.get(url)
    if cacheitem is None:
        abort(404)

    return Response(cacheitem, mimetype='image/png')


@app.route('/set', methods=['POST'])
def set():
    url = request.form.get('url', '')
    content = request.files['file']

    if content.content_type.startswith('image/svg+xml'):
        content = svg2png(content.stream)

    cache.set(url, content, timeout=CACHE_TIMEOUT)
    return Response(content, mimetype='image/png')


def svg2png(stream):
    with wand.image.Image(blob=stream.read(), format="svg") as image:
        return image.make_blob("png")


if __name__ == '__main__':
    app.run()
