import os
from dotenv import load_dotenv
import urllib3

load_dotenv()
VERSION: str = os.environ.get("VERSION") or "v0.0.0"
GITHUB_TOKEN: str = os.environ["GITHUB_TOKEN"]
GITHUB_REPOSITORY: str = os.environ.get("GITHUB_REPOSITORY", "CeciliaStudio/PCL.Mac.Refactor")

urllib3.disable_warnings()

import github
import hash
import motrix
import time
from typing import Any

def download_artifact(url: str, name: str, digest: str) -> None:
    if os.path.exists(name):
        if hash.sha256_matches(file_path=name, target_hash=digest[7:]):
            print("文件存在且 SHA-256 匹配！")
            return
    print("正在尝试拉起 Motrix 进行下载...")
    motrix.download_file(url=url, dest=os.getcwd(), filename=name)
    for i in range(50):
        time.sleep(1)
        print(f"第 {i + 1}/50 次轮询...", end="\r")
        if os.path.exists("artifact.zip") and not os.path.exists("artifact.zip.aria2"):
            print("\n工件下载完成")
            return
    print("\n工件下载超时")
    exit(1)

def main() -> None:
    print(f"PCL.Mac Release CLI {VERSION}")

    print(f"正在拉取 workflow runs...")
    workflow_run: github.WorkflowRun = github.get_last_workflow_run(repo=GITHUB_REPOSITORY, token=GITHUB_TOKEN)
    id: int = workflow_run.id
    print(f"{workflow_run.name} {workflow_run.display_title} ({workflow_run.id}) {workflow_run.created_at}")
    if input("这是正确的 workflow run 吗？(Y/n): ").lower().strip() == "n":
        id = int(input("Workflow run id: "))

    print("正在拉取工件...")
    artifacts: list[dict[str, Any]] = github.get_workflow_artifacts(repo=GITHUB_REPOSITORY, id=id, token=GITHUB_TOKEN)
    i: int = 1
    for artifact in artifacts:
        print(f"{i}. {artifact["name"]:<32}\t{artifact["created_at"]}")
        i += 1
    i = int(input("选择一个工件："))
    artifact: dict[str, Any] = artifacts[i - 1]
    artifact_url: str = f"https://nightly.link/CeciliaStudio/PCL.Mac.Refactor/actions/runs/{id}/{artifact["name"]}.zip"
    print(f"下载 URL：{artifact_url}")
    download_artifact(url=artifact_url, name="artifact.zip", digest=artifact["digest"])

if __name__ == "__main__":
    main()