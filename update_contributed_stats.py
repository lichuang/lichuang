import os
import re
import requests
from datetime import datetime

TARGET_REPOS = ["databendlabs/databend", "databendlabs/openraft"]# 你参与的目标项目
YOUR_USERNAME = "lichuang" # 你的 GitHub ID
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") # Action 会自动注入

def fetch_pr_stats():
  headers = {
      "Authorization": f"token {GITHUB_TOKEN}",
      "Accept": "application/vnd.github.v3+json"
  }
  
  ret = {}
  for TARGET_REPO in TARGET_REPOS:
    # 使用 Search API 查找你在该仓库的 PR (包括 open, closed, merged)
    query = f"repo:{TARGET_REPO} author:{YOUR_USERNAME} type:pr sort:created-desc"
    url = f"https://api.github.com/search/issues?q={query}"
    
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        raise Exception(f"API Error: {resp.text}")
    
    data = resp.json()
    total_count = data.get("total_count", 0)
    
    last_pr_date = "暂无"
    if data.get("items"):
        # 获取最近一个 PR 的创建时间 (UTC)
        raw_date = data["items"][0]["created_at"]
        # 简单格式化为 YYYY-MM-DD
        dt = datetime.strptime(raw_date, "%Y-%m-%dT%H:%M:%SZ")
        last_pr_date = dt.strftime("%Y-%m-%d")
        
    repo = TARGET_REPO.split("/")[1]
    ret[repo] = (str(total_count), last_pr_date)
  return ret

def update_readme(data):
  with open("README.md", "r", encoding="utf-8") as f:
      content = f.read()
  with open("README.template", "r", encoding="utf-8") as f:
      new_content = f.read()

  for key, value in data.items():
    (count, date) = value

    pattern = key + "_last"
    #print("pattern: {pattern}")
    new_content = re.sub(pattern, date, new_content, flags=re.DOTALL)

    pattern = key + "_count"
    new_content = re.sub(pattern, count, new_content, flags=re.DOTALL)
    
  if new_content != content:
      with open("README.md", "w", encoding="utf-8") as f:
          f.write(new_content)
      return True
  return False

if __name__ == "__main__":
  ret = fetch_pr_stats()
  print(f"Fetched: {ret}")
  if update_readme(ret):
      print("Readme updated.")
  else:
      print("No changes needed.")

