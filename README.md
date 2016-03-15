# Atlassian Bot
[![Build status](https://ci.appveyor.com/api/projects/status/iuqcblbxb9jyk2pb/branch/develop?svg=true)](https://ci.appveyor.com/project/gpailler/atlassianbot/branch/develop)
[![codecov.io](https://codecov.io/github/gpailler/AtlassianBot/coverage.svg?branch=develop)](https://codecov.io/github/gpailler/AtlassianBot?branch=develop)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/gpailler/AtlassianBot/blob/develop/LICENSE)

Atlassian Bot is a collection of plugins to integrate Atlassian tools into Slack.


## Installation
```bash
> git clone https://github.com/gpailler/AtlassianBot.git
> cd AtlassianBot

> pip install virtualenv
> virtualenv venv --python=python3.4
> source venv/bin/activate

> pip install -r requirements.txt
```

## Configuration
### Generate Slack bot API token
Go to https://api.slack.com/bot-users and create a new bot

Copy `local_settings-sample.py` to `local_settings.py` and fill the bot token

### Configure Atlassian bot
Copy `plugins/settings-sample.yml` to `plugins/settings.yml` and activate/configure each bot according your needs


## Launch
```
> python run.py
```

## Plugins
### JiraBot
This plugin reads messages on channels on which he's invited and gives details when he finds a Jira key in a discussion. Displayed details are the summary the issue type. The message is a link to access issue on Jira.

![jirabot](https://cloud.githubusercontent.com/assets/3621529/13786671/adcff88a-eb13-11e5-8de2-ec7814837382.jpg)

### CrucibleBot
This plugin reads messages on channels on which he's invited and gives details when he finds a Review key in a discussion. Displayed details are the summary and the uncompleted reviewers. The message is a link to access review on Crucible.
