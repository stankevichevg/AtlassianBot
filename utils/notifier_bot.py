import abc
import inspect
import json
import logging
import threading

from concurrent.futures import ThreadPoolExecutor
from slackbot.bot import Bot

logger = logging.getLogger(__name__)

MAX_NOTIFIERS_WORKERS = 4

_executor = ThreadPoolExecutor(max_workers=MAX_NOTIFIERS_WORKERS)


class NotifierBot(object):
    def __init__(self, slackclient=None):
        logger.info('registered %s', self.__class__.__name__)

        if slackclient is None:
            slackclient = self.__get_slackclient()
        self.__slackclient = slackclient

        if self.__slackclient is None:
            logger.error('Unable to retrieve slackclient instance')
            return

    def submit(self, job):
        job._init_threaded(self.__slackclient)

    def __get_slackclient(self):
        stack = inspect.stack()
        for frame in [f[0] for f in stack]:
            if 'self' in frame.f_locals:
                instance = frame.f_locals['self']
                if isinstance(instance, Bot):
                    return instance._client


class NotifierJob(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, channel, polling_interval):
        self.channel = channel
        self.polling_interval = polling_interval

    def _init(self):
        try:
            self.init()
        except Exception as ex:
            logger.error('Unable to init notifier job: %s', ex, exc_info=True)

    def _run(self):
        try:
            self.run()
        except Exception as ex:
            logger.error('Unable to run notifier job: %s', ex, exc_info=True)

    def __run_async(self, fn):
        threading.Timer(self.polling_interval, self._run_in_executor).start()

    def _run_in_executor(self):
        _executor \
            .submit(self._run) \
            .add_done_callback(self.__run_async)

    def _init_threaded(self, slackclient):
        self.__slackclient = slackclient
        self.__channel_id = self.__get_channel(self.channel)
        if self.__channel_id is None:
            logger.error('Unable to find channel')
            return

        _executor \
            .submit(self._init) \
            .add_done_callback(self.__run_async)

    def __get_channel(self, channelname):
        for id, channel in list(self.__slackclient.channels.items()):
            if channel.get('name', None) == channelname:
                return id

    @abc.abstractmethod
    def init(self):
        """Method that should do something."""

    @abc.abstractmethod
    def run(self):
        """Method that should do something."""

    def send_message(self, attachments):
        self.__slackclient.send_message(
                self.__channel_id,
                '',
                attachments=json.dumps(attachments))
