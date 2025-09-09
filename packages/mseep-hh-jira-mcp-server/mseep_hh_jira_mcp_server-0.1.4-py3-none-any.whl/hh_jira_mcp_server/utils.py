import os

import keyring
from jira import JIRA

def get_jira():
    return JIRA(server=get_host(),
                basic_auth=(get_user(), get_password()))

def get_env(key):
    value = os.getenv(key)
    if not value:
        raise ValueError(f"{key} environment variable required")
    return value

def get_search_filter():
    return " and " + get_env("HH_JIRA_MCP_SEARCH_FILTER")

def get_team():
    return get_env("HH_JIRA_MCP_TEAM")

def get_user():
    return get_env("HH_JIRA_MCP_USER")

def get_password():
     return keyring.get_password("hh-jira-mcp-server", get_user())

def get_host():
    return "https://jira.hh.ru"

def get_task_url(task_name):
    host = get_host()
    return f'{host}/browse/{task_name}'

def get_defense_text():
    return 'Я проверил портфель на безопасность по "Чеклисту", портфель не несет рисков или согласован с ' \
           'командой Defense.'
