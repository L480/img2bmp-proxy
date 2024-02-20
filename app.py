import os
import waitress
import flask
import validators
import urllib.request
import tempfile
from PIL import Image

app = flask.Flask(__name__)


@app.route('/', methods=['GET'])
def main():
    url = flask.request.args.get('url')
    if not validators.url(url):
        return flask.jsonify({'status': 'error', 'message': 'Invalid value for url URL parameter'}), 400
    try:
        width = int(flask.request.args.get('width'))
        height = int(flask.request.args.get('height'))
        threshold = int(flask.request.args.get('threshold'))
    except (ValueError, TypeError):
        return flask.jsonify({'status': 'error', 'message': 'Invalid value for width, height, or threshold URL parameter'}), 400

    with tempfile.NamedTemporaryFile() as f:
        filename = f.name + url[len(url) - 4:]
        filename_bmp = f.name + '.bmp'
        urllib.request.urlretrieve(url, filename)
        img = Image.open(filename)
        try:
            img.verify()
        except Exception:
            return flask.jsonify({'status': 'error', 'message': 'Invalid image'}), 400
        img = Image.open(filename)
        def fn(x): return 255 if x > threshold else 0
        r = img.convert('L').point(fn, mode='1').resize((width, height))
        r.save(filename_bmp)
        return flask.send_file(filename_bmp, mimetype='image/bmp')


@app.route('/health', methods=['GET'])
def health():
    return flask.jsonify({'status': 'success', 'message': 'Healthy'}), 200


app.secret_key = os.urandom(24)
waitress.serve(app, host='0.0.0.0', port=8080)
