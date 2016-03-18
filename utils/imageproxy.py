import requests
from base64 import b64encode


def convert_proxyurl(server, url):
    icon_request = requests.get(url)
    if icon_request.status_code == requests.codes.ok:
        content_type = icon_request.headers.get('Content-Type')
        content_type = b64encode(content_type.encode(), altchars=b'-_')
        content = b64encode(icon_request.content, altchars=b'-_')

        return '%s/converticon/%s/%s' % (
                                         server,
                                         content_type.decode(),
                                         content.decode())

    return url
