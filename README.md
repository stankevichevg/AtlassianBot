# Atlassian Bot
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
