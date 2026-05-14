from github import Github

g = Github("your-github-token")

org = g.get_organization("your-org")
for repo in org.get_repos():
    try:
        branch = repo.get_branch("main")
        branch.edit_protection(
            required_pull_request_reviews=True,
            enforce_admins=True,
            strict=True,
            required_status_checks=["default"]
        )
        print(f"✅ {repo.name} 保护规则已设置")
    except Exception as e:
        print(f"❌ {repo.name} 失败: {e}")