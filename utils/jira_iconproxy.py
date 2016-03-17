import requests
import urllib.parse


def convert_proxyurl(server, url):
    payload = {'url': url}
    cache_request = requests.get(server + '/has', params=payload)

    if (cache_request.status_code == requests.codes.no_content):
        icon_request = requests.get(url)
        if icon_request.status_code == requests.codes.ok:
            files = {'image': (
                      'image',
                      icon_request.content,
                      icon_request.headers['Content-Type']
                      )}

            cache_request = requests.post(
                                          server + '/add',
                                          data=payload,
                                          files=files)

    if cache_request.status_code == requests.codes.ok:
        return server + '/get?' + urllib.parse.urlencode(payload)

    return url
