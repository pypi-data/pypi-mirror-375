import json

from fastmcp import FastMCP

from .utils import get_jira, get_user, get_team, get_task_url, get_defense_text, get_search_filter

mcp = FastMCP("hh-jira-mcp-server")

@mcp.tool()
def search_team_active_portfolios(team: str) -> str:
    try:
        issues = get_jira().search_issues(jql_str=f'project = "PORTFOLIO" and "Delivery Team" = "{team}"' + get_search_filter(),
                                              maxResults=50,
                                              json_result=True,
                                              fields="summary,description,duedate,customfield_11212")
        return json.dumps(issues, indent=4)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def create_task(title: str) -> str:
    try:
        fields = {
            'project': "HH",
            'issuetype': {'id': '3'},
            'summary': title,
            'assignee': {'name': get_user()},
            'customfield_10961': {'value': get_team()}
        }

        task = get_jira().create_issue(prefetch=True, fields=fields)

        return get_task_url(task.key)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def set_defence_checked(portfolio: int) -> str:
    try:
        jira_api = get_jira()
        issue = jira_api.issue(f"PORTFOLIO-{portfolio}")
        issue.update(fields={'customfield_32210': [{'value': get_defense_text()}]})
        return "Defence checked for " + get_task_url(issue.key)
    except Exception as e:
        return f"Error: {str(e)}"

