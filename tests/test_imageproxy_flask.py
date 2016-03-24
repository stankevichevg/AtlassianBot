import pytest
import imageproxy.flask_app

GIFURL = '/image/aW1hZ2UvZ2lm/R0lGODlhAQABAIAAAP___wAAACwAAAAAAQABAAACAkQBADs='

PNGURL = '/image/aW1hZ2UvcG5n/iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4__8_w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=='

SVGURL = '/image/aW1hZ2Uvc3ZnK3htbDtjaGFyc2V0PVVURi04/PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8-Cjxzdmcgd2lkdGg9IjE2cHgiIGhlaWdodD0iMTZweCIgdmlld0JveD0iMCAwIDE2IDE2IiB2ZXJzaW9uPSIxLjEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiIHhtbG5zOnNrZXRjaD0iaHR0cDovL3d3dy5ib2hlbWlhbmNvZGluZy5jb20vc2tldGNoL25zIj4KICAgIDwhLS0gR2VuZXJhdG9yOiBTa2V0Y2ggMy4zICgxMTk3MCkgLSBodHRwOi8vd3d3LmJvaGVtaWFuY29kaW5nLmNvbS9za2V0Y2ggLS0-CiAgICA8dGl0bGU-YnVnPC90aXRsZT4KICAgIDxkZXNjPkNyZWF0ZWQgd2l0aCBTa2V0Y2guPC9kZXNjPgogICAgPGRlZnM-PC9kZWZzPgogICAgPGcgaWQ9IlBhZ2UtMSIgc3Ryb2tlPSJub25lIiBzdHJva2Utd2lkdGg9IjEiIGZpbGw9Im5vbmUiIGZpbGwtcnVsZT0iZXZlbm9kZCIgc2tldGNoOnR5cGU9Ik1TUGFnZSI-CiAgICAgICAgPGcgaWQ9ImJ1ZyIgc2tldGNoOnR5cGU9Ik1TQXJ0Ym9hcmRHcm91cCI-CiAgICAgICAgICAgIDxnIGlkPSJCdWciIHNrZXRjaDp0eXBlPSJNU0xheWVyR3JvdXAiIHRyYW5zZm9ybT0idHJhbnNsYXRlKDEuMDAwMDAwLCAxLjAwMDAwMCkiPgogICAgICAgICAgICAgICAgPHBhdGggZD0iTTEzLDE0IEwxLDE0IEMwLjQ0OCwxNCAwLDEzLjU1MiAwLDEzIEwwLDEgQzAsMC40NDggMC40NDgsMCAxLDAgTDEzLDAgQzEzLjU1MiwwIDE0LDAuNDQ4IDE0LDEgTDE0LDEzIEMxNCwxMy41NTIgMTMuNTUyLDE0IDEzLDE0IiBpZD0iRmlsbC0xIiBmaWxsPSIjRDA0NDM3IiBza2V0Y2g6dHlwZT0iTVNTaGFwZUdyb3VwIj48L3BhdGg-CiAgICAgICAgICAgICAgICA8cGF0aCBkPSJNMTAsNyBDMTAsOC42NTcgOC42NTcsMTAgNywxMCBDNS4zNDMsMTAgNCw4LjY1NyA0LDcgQzQsNS4zNDMgNS4zNDMsNCA3LDQgQzguNjU3LDQgMTAsNS4zNDMgMTAsNyIgaWQ9IkZpbGwtMiIgZmlsbD0iI0ZGRkZGRiIgc2tldGNoOnR5cGU9Ik1TU2hhcGVHcm91cCI-PC9wYXRoPgogICAgICAgICAgICA8L2c-CiAgICAgICAgPC9nPgogICAgPC9nPgo8L3N2Zz4='


@pytest.fixture
def app():
    return imageproxy.flask_app.app


@pytest.fixture
def cache():
    cache = imageproxy.flask_app.cache
    cache.clear()
    return cache


def test_is_debug(app):
    assert not app.debug


def test_no_default_page(client):
    assert client.get('/').status_code == 404


def test_validate_url(client):
    assert client.get('/image').status_code == 404
    assert client.get('/image/a').status_code == 404
    assert client.get('/image/a/b').status_code == 500
    assert client.get(GIFURL).status_code == 200


@pytest.mark.parametrize('url,content_type,result_header', [
    (GIFURL, 'image/gif', b'GIF89a'),
    (PNGURL, 'image/png', b'\x89PNG'),
    (SVGURL, 'image/png', b'\x89PNG')
])
def test_image_get(cache, client, url, content_type, result_header):
    expected_cache_retention = imageproxy.flask_app.CACHE_RETENTION
    assert cache.get(url) is None

    response = client.get(url)
    assert response.status_code == 200
    assert response.content_type == content_type
    assert response.cache_control.max_age == expected_cache_retention
    assert response.data.startswith(result_header)

    assert cache.get(url) is not None

    response = client.get(url)
    assert response.status_code == 200
    assert response.content_type == content_type
    assert response.cache_control.max_age == expected_cache_retention
    assert response.data.startswith(result_header)
