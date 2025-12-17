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

def generate_release_notes(tag_name: str, description: str, workflow_run_id: int) -> str:
    raw_release_notes: str = github.generate_release_notes(repo=GITHUB_REPOSITORY, tag_name=tag_name, token=GITHUB_TOKEN)
    lines: list[str] = raw_release_notes.split("\n")
    pull_requests: list[str] = [line for line in lines[1:lines.index("")] if "[NOTE-IGN]" not in line]
    lines = [
        description,
        "",
        "## 更新日志",
        "",
        *pull_requests,
        "",
        f"完整日志：{lines[-1].split(": ")[-1]}",
        "",
        "---",
        "",
        f"本版本为 https://github.com/{GITHUB_REPOSITORY}/actions/runs/{workflow_run_id}"
    ]
    return "\n".join(lines)

def main() -> None:
    if not os.path.exists("run"):
        os.mkdir("run")
    os.chdir("run")
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
    artifact_url: str = f"https://nightly.link/{GITHUB_REPOSITORY}/actions/runs/{id}/{artifact["name"]}.zip"
    print(f"下载 URL：{artifact_url}")
    download_artifact(url=artifact_url, name="artifact.zip", digest=artifact["digest"])

    release_title: str = input("输入 Release 版本号：")
    tag_name: str = input("输入 Release tag：")
    description: str = input("输入 Release 描述：")
    print("正在生成更新日志...")
    release_notes = generate_release_notes(tag_name=tag_name, description=description, workflow_run_id=id)
    with open("release-notes.md", mode="w+", encoding="utf-8") as file:
        file.write(release_notes)
    print("将在 1s 后打开更新日志")
    time.sleep(1)
    os.system("open release-notes.md")
    print("请编辑更新日志，随后按下 Enter")
    input("> ")
    with open("release-notes.md", mode="r+", encoding="utf-8") as file:
        release_notes = file.read()
    
    print("正在创建 GitHub Release...")
    release = github.create_release(repo=GITHUB_REPOSITORY,
                                    tag_name=tag_name,
                                    name=release_title,
                                    notes=release_notes,
                                    token=GITHUB_TOKEN)
    print("正在上传工件...")
    github.upload_release_asset(upload_url=release.upload_url,
                                filename=f"PCL.Mac.Refactor-{tag_name}.zip",
                                path="artifact.zip",
                                token=GITHUB_TOKEN)
    print("工件上传成功")
    print(f"GitHub Release 已创建：{release.html_url}")

if __name__ == "__main__":
    main()