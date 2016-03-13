import json
import logging
import requests
import plugins.settings as settings

headers = {'accept': 'application/json'}


def get(config, path, data=None):
    request = requests.get(
        url=__format_url(config, path),
        params=data,
        headers=headers,
        auth=(config['username'], config['password']),
        verify=settings.servers.verify_ssl)

    logging.debug('GET %s - Response %s - Data %s'
                  % (request.url, request.status_code, data))

    return request


def delete(config, path, data):
    request = requests.delete(
        url=__format_url(config, path),
        data=json.dumps(data),
        headers={
            'Content-type': 'application/json',
            'Accept': 'application/json'
        },
        auth=(config['username'], config['password']),
        verify=settings.servers.verify_ssl)

    logging.debug('DELETE %s - Response %s - Data %s'
                  % (request.url, request.status_code, data))

    return request


def post(config, path, data=None):
    request = requests.post(
        url=__format_url(config, path),
        data=data,
        headers=headers,
        auth=(config['username'], config['password']),
        verify=settings.servers.verify_ssl)

    logging.debug('POST %s - Response %s - Data %s'
                  % (request.url, request.status_code, data))

    return request


def __format_url(config, path):
    return '{server}{path}'.format(server=config['host'], path=path)
