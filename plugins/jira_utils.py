# encoding=utf8

from jira import JIRA

from plugins import settings


def get_Jira_instance(server):
    auth = None
    if 'username' in server and 'password' in server:
        auth = (server['username'], server['password'])

    jira = JIRA(
        options={
            'server': server['host'],
            'verify': settings.servers.verify_ssl},
        basic_auth=auth,
        get_server_info=False,
        max_retries=1
    )

    proxies = {}
    if 'http_proxy' in server:
        proxies.update({'http' : server['http_proxy']})
    if 'https_proxy' in server:
        proxies.update({'https' : server['https_proxy']})
    if len(proxies) > 0:
        jira._session.proxies = proxies
    return jira