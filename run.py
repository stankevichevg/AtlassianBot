#!/usr/bin/env python

import sys
import logging
import logging.config

import slacker
from slackbot.bot import Bot
from slackbot.dispatcher import MessageDispatcher
from slackbot.manager import PluginsManager
from slackbot.slackclient import SlackClient

from slackbot import settings

import requests

requests.packages.urllib3.disable_warnings()

class ProxyBot(Bot):
    def __init__(self):
        self._client = SlackClient(
            settings.API_TOKEN,
            bot_icon=settings.BOT_ICON if hasattr(settings,
                                                  'BOT_ICON') else None,
            bot_emoji=settings.BOT_EMOJI if hasattr(settings,
                                                    'BOT_EMOJI') else None,
            connect=False
        )
        self._client.webapi = slacker.Slacker(
            settings.API_TOKEN,
            # add support for proxy settings
            http_proxy=settings.HTTP_PROXY if hasattr(settings, 'HTTP_PROXY') else None,
            https_proxy=settings.HTTPS_PROXY if hasattr(settings, 'HTTPS_PROXY') else None)
        self._client.rtm_connect()
        self._plugins = PluginsManager()
        self._dispatcher = MessageDispatcher(self._client, self._plugins,
                                             settings.ERRORS_TO)


def main():
    kw = {
        'format': '[%(asctime)s] | %(name)s | %(levelname)s | %(message)s',
        'datefmt': '%m/%d/%Y %H:%M:%S',
        'level': logging.DEBUG if settings.DEBUG else logging.INFO,
        'stream': sys.stdout,
    }
    logging.basicConfig(**kw)
    logging.getLogger('requests.packages.urllib3.connectionpool')\
        .setLevel(logging.WARNING)
    bot = ProxyBot()
    bot.run()

if __name__ == '__main__':
    main()
