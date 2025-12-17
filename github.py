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

@dataclass
class Release:
    html_url: str
    upload_url: str
    id: int

API_ROOT = "https://api.github.com"

def get_last_workflow_run(repo: str, token: str) -> WorkflowRun:
    url: str = API_ROOT + f"/repos/{repo}/actions/runs"
    headers: dict[str, str] = {"Authorization": f"Bearer {token}"}
    response: requests.Response = requests.get(url, headers=headers, verify=False)
    workflow_run: dict[str, Any] = response.json()["workflow_runs"][0]
    return WorkflowRun(id=workflow_run["id"],
                       name=workflow_run["name"],
                       display_title=workflow_run["display_title"],
                       created_at=workflow_run["created_at"])

def get_workflow_artifacts(repo: str, id: int, token: str) -> list[dict[str, Any]]:
    url: str = API_ROOT + f"/repos/{repo}/actions/runs/{id}/artifacts"
    headers: dict[str, str] = {"Authorization": f"Bearer {token}"}
    response: requests.Response = requests.get(url, headers=headers, verify=False)
    return response.json()["artifacts"]

def generate_release_notes(repo: str, tag_name: str, token: str) -> str:
    url: str = API_ROOT + f"/repos/{repo}/releases/generate-notes"
    headers: dict[str, str] = {"Authorization": f"Bearer {token}"}
    body: dict[str, str] = {"tag_name": tag_name}
    return requests.post(url, headers=headers, json=body, verify=False).json()["body"]

def create_release(repo: str, tag_name: str, name: str, notes: str, token: str) -> Release:
    url: str = API_ROOT + f"/repos/{repo}/releases"
    headers: dict[str, str] = {"Authorization": f"Bearer {token}"}
    body: dict[str, str] = {
        "tag_name": tag_name,
        "name": name,
        "body": notes
    }
    response = requests.post(url, headers=headers, json=body, verify=False)
    response.raise_for_status()
    release: dict[str, Any] = response.json()
    return Release(html_url=release["html_url"],
                   upload_url=release["upload_url"],
                   id=release["id"])

def upload_release_asset(upload_url: str, filename: str, path: str, token: str) -> None:
    url: str = upload_url.replace("{?name,label}", f"?name={filename}")
    headers: dict[str, str] = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/octet-stream"
    }
    with open(path, "rb") as file:
        requests.post(url, headers=headers, data=file, verify=False).raise_for_status()