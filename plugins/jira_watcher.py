# coding: utf-8

import logging

import re
import datetime as dt
from lazy import lazy
from slackbot.bot import listen_to

from plugins import settings
from plugins.jira_utils import get_Jira_instance
from utils.notifier_bot import NotifierBot, NotifierJob
logger = logging.getLogger(__name__)

MAX_NOTIFIERS_WORKERS = 2

class JiraUserWatcherBot(NotifierBot):
    def __init__(self, server, config, slackclient=None, suppression=None):
        super().__init__(slackclient)

        self.__server = server
        self._jobs = list(self.submit_jobs(config, suppression))

    def submit_jobs(self, config, suppression):
        for watcher_settings in config['watchers']:
            if watcher_settings['enabled']:
                if watcher_settings['type'] == "developer":
                    job = UsersWatcherJob(self.__jira, watcher_settings, suppression=suppression)
                    self.submit(job)
                    yield job

    @lazy
    def __jira(self):
        return get_Jira_instance(self.__server)


class WatcherRule():
    def __init__(self, jira, type, config):
        self.jira = jira
        self.type = type
        self.active_from = config['active_from']
        self.active_to = config['active_to']
        self.query = config['query']
        self.text = config['text']
        self.only_out_work_hours = config['only_out_work_hours'] == 'true'

    def apply(self, config_users, suppression):
        if self.__is_active():
            users = []
            for user in config_users:
                if user['slack_login'] not in suppression or dt.datetime.now() > suppression[user['slack_login']]:
                    users.append({
                        'jira_login': user['jira_login'],
                        'slack_login': user['slack_login'],
                        'tasks': []
                    })
            fields = 'summary,customfield_10012,updated,issuetype,assignee'
            results = self.jira.search_issues(self.query, fields=fields)
            if len(results) > 0:
                for issue in results[::-1]:
                    # ищем разработчика в списке
                    user = next((user for user in users if user['jira_login'] == issue.fields.assignee.name), None)
                    print(issue.fields.assignee.name)
                    if user is not None:
                        user['tasks'].append(issue)

            return self.do_action(users)
        else:
            return []

    def do_action(self, users):
        attachments = []
        for user in users:
            if self.is_triggered(user):
                for task in user['tasks']:
                    attachments.append({
                        'author_name': task.key,
                        'text': self.create_target_message(user) + self.text,
                        'color': '#B30C0C',
                        'mrkdwn_in': ['fields'],
                        'fields': [
                            {
                                'title': 'Задача на {}'.format(user['slack_login']),
                                'value': user['slack_login'],
                                'short': True
                            }
                        ]
                        })
        return attachments

    def is_triggered(self, user):
        return True

    def create_target_message(self, user):
        return '@' + user['slack_login'] + ', '

    def __is_active(self):
        return self.active_from <= dt.datetime.now().hour <= self.active_to


class NotifyWatcherRule(WatcherRule):
    def __init__(self, jira, config):
        super().__init__(jira, "notify", config)

    def is_triggered(self, user):
        return user['tasks'] is not None and len(user['tasks']) > 0

class TransitionWatcherRule(WatcherRule):
    def __init__(self, jira, config):
        super().__init__(jira, "transition", config)
        self.transition_name = config['transition_name']

    def do_action(self, users):
        attachments = []
        for user in users:
            if self.is_triggered(user):
                for task in user['tasks']:
                    target_transition_id = None
                    transitions = self.jira.transitions(task)
                    for transition in [(t['id'], t['name']) for t in transitions]:
                        if transition[1] == self.transition_name:
                            target_transition_id = transition[0]
                            break
                    if target_transition_id is not None:
                        # self.jira.transition_issue(task.key, 'Stop')
                        self.jira.transition_issue(task.key, 'Stop', assignee={'name': 'pm_user'}, resolution={'id': '3'})
                        attachments.append({
                            'author_name': task.key,
                            'text': self.create_target_message(user) + self.text,
                            'color': '#B30C0C',
                            'mrkdwn_in': ['fields'],
                            'fields': [
                                {
                                    'title': 'Задача на {}'.format(user['slack_login']),
                                    'value': user['slack_login'],
                                    'short': True
                                }
                            ]
                        })
        return attachments

    def is_triggered(self, user):
        return user['tasks'] is not None and len(user['tasks']) > 0 and \
               (not self.only_out_work_hours or not user['work_from'] <= dt.datetime.now().hour <= user['work_to'])


def create_rules(jira, rules_config):
    rules = []
    for config in rules_config:
        if config["type"] == "notify":
            rules.append(NotifyWatcherRule(jira, config))
        elif config["type"] == "transition":
            rules.append(TransitionWatcherRule(jira, config))
    return rules


class UsersWatcherJob(NotifierJob):
    def __init__(self, jira, config, suppression=None):
        super().__init__(config['channel'], config['polling_interval'])
        self.__jira = jira
        self.__config = config
        self.__rules = create_rules(jira, config['rules'])
        if suppression is None:
            suppression = dict()
        self.__suppression = suppression

    def run(self):
        logger.info('run')

        attachments = []

        for rule in self.__rules:
            for message in rule.apply(self.__config['users'], self.__suppression):
                attachments.append(message)

        if len(attachments) > 0:
            self.send_message(attachments)

notification_suppression = {}

if (settings.plugins.jirawatchbot.enabled):
    def get_pattern(text):
        jira_prefixes = '|'.join(settings.plugins.jirawatchbot.prefixes)
        return r'(?:^|\s|[\W]+)(?<!CLEAN\s)((?:{})-[\d]+)(?:$|\s|[\W]+) (?:{})'\
            .format(jira_prefixes, text)
    JiraUserWatcherBot(settings.servers.jira, settings.plugins.jirawatchbot, suppression=notification_suppression)

    @listen_to('отстань', re.IGNORECASE)
    def jirabot(message):
        user = message.channel._client.users[message.body['user']][u'name']
        notification_suppression.update({user : dt.datetime.now() + dt.timedelta(minutes=30)})
        message.reply('Прошу прощения за беспокойство, мой господин. Вернусь через 30 минут')

    @listen_to('отвянь', re.IGNORECASE)
    def jirabot(message):
        user = message.channel._client.users[message.body['user']][u'name']
        notification_suppression.update({user: dt.datetime.now() + dt.timedelta(minutes=60)})
        message.reply('Прошу прощения за беспокойство, мой господин. Вернусь через час')

    @listen_to('работаю', re.IGNORECASE)
    def jirabot(message):
        user = message.channel._client.users[message.body['user']][u'name']
        notification_suppression.update({user : dt.datetime.now() + dt.timedelta(minutes=30)})
        message.reply('Вернусь через 30 минут')

    @listen_to('работаю час', re.IGNORECASE)
    def jirabot(message):
        user = message.channel._client.users[message.body['user']][u'name']
        notification_suppression.update({user: dt.datetime.now() + dt.timedelta(minutes=60)})
        message.reply('Вернусь через час')

    @listen_to('работаю два часа', re.IGNORECASE)
    def jirabot(message):
        user = message.channel._client.users[message.body['user']][u'name']
        notification_suppression.update({user: dt.datetime.now() + dt.timedelta(minutes=120)})
        message.reply('Вернусь через два часа')
