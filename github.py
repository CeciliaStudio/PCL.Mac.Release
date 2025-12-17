from dataclasses import dataclass
from typing import Optional, Any
import requests

@dataclass
class WorkflowRun:
    id: int
    name: str
    display_title: str
    created_at: str

@dataclass
class Artifact:
    id: int
    name: str
    download_url: str

API_ROOT = "https://api.github.com"

def get_last_workflow_run(repo: str, token: Optional[str]) -> WorkflowRun:
    url: str = API_ROOT + f"/repos/{repo}/actions/runs"
    headers: dict[str, str] = {}
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"
    response: requests.Response = requests.get(url, headers=headers, verify=False)
    workflow_run: dict[str, Any] = response.json()["workflow_runs"][0]
    return WorkflowRun(id=workflow_run["id"],
                       name=workflow_run["name"],
                       display_title=workflow_run["display_title"],
                       created_at=workflow_run["created_at"])

def get_workflow_artifacts(repo: str, id: int, token: Optional[str]) -> list[dict[str, Any]]:
    url: str = API_ROOT + f"/repos/{repo}/actions/runs/{id}/artifacts"
    headers: dict[str, str] = {}
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"
    response: requests.Response = requests.get(url, headers=headers, verify=False)
    return response.json()["artifacts"]
