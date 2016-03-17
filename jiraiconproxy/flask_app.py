from flask import Flask, request, Response, redirect, url_for
from werkzeug.contrib.cache import SimpleCache
import wand.image
from requests import codes

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024  # 50KB max for uploaded images
app.debug = False


CACHE_TIMEOUT = 24 * 60 * 60

cache = SimpleCache()


@app.route('/', methods=['GET'])
def default():
    return Response(None)


@app.route('/has', methods=['GET'])
def has():
    url = request.values['url']
    cached = cache.has(url)
    return Response(None, status=codes.ok if cached else codes.not_found)


@app.route('/get', methods=['GET'])
def get():
    url = request.values['url']
    cacheitem = cache.get(url)
    if cacheitem is None:
        return redirect(url_for('has', url=url))

    return Response(cacheitem, mimetype='image/png')


@app.route('/add', methods=['POST'])
def set():
    url = request.values['url']
    image = request.files['image']

    if image.content_type.startswith('image/svg+xml'):
        image = svg2png(image.stream)

    cache.set(url, image, timeout=CACHE_TIMEOUT)
    return Response(None, status=codes.ok)


def svg2png(stream):
    with wand.image.Image(blob=stream.read(), format="svg") as image:
        return image.make_blob("png")


if __name__ == '__main__':
    app.run()
