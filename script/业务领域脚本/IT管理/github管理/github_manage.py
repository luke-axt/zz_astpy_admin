import json
import os

import requests


class GithubManage:
    """
    此类用于设置github的分支管理权限。
    现在的github是用pro账号，允许高级分支设置。
    """
    def __init__(self):
        self.token_lukeaxt = os.getenv('GITHUB_TOKEN_LUKEAXT')
        if self.token_lukeaxt is None:
            print(f"无个人token的环境变量：GITHUB_TOKEN_LUKEAXT")

        self.owner = 'luke-axt'
        print(self.token_lukeaxt)

    def set_branch_no_push(self,repo_name,branch="main",repo_owner=None):
        """
        设置分支不允许直接推送。

        :param repo_name 仓库名。
        :param branch 分支，默认是main分支，可以改
        :param repo_owner 默认是空，使用类变量luke-axt，如有特殊可以指定。

        """
        # 没有指定就用类变量的owner
        if repo_owner is None:
            repo_owner = self.owner

        # GitHub API URL
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/branches/{branch}/protection"
        print(url)

        # 请求头
        headers = {
            "Authorization": f"token {self.token_lukeaxt}",
            "Accept": "application/vnd.github.v3+json",
        }

        # 分支保护规则配置
        # 关键点：设置 required_pull_request_reviews 以强制 PR，
        # 并且不设置 allow_force_pushes 或 users/teams 推送权限，即可禁止直接 push
        payload = {
            "required_pull_request_reviews": {
                "required_approving_review_count": 1,
                "dismiss_stale_reviews": False,
                "require_code_owner_reviews": False,
                "required_conversation_resolution": True
            },
            "required_status_checks": None,  # 如果你有 CI 检查可在这里配置
            "enforce_admins": True,  # 管理员也受限制
            "restrictions": None,  # 注意：设为 null 表示“不允许任何人直接 push”
            "allow_force_pushes": False,
            "allow_deletions": False,
            "required_linear_history": True
        }

        # 发送 PATCH 请求
        response = requests.put(url, json=payload, headers=headers)

        # 检查结果
        if response.status_code == 200:
            print("✅ 成功设置 main 分支保护：禁止直接 push！")
        else:
            print(f"❌ 设置失败，状态码: {response.status_code}")
            print(response.json())

    def set_shopify_repo_branch_rule(self):
        """
        shopify项目的代码统一在github管理。
        shopify项目有两种代码变更来源：
        1. 用户在shopify后台配置。
        2. 开发人员提交代码到github然后走合并请求
        """
        REPO_OWNER = "astshopify"
        REPO_NAME = "test"
        BRANCH_NAME = "main"  # 要保护的分支，通常是 main 或 master
        token_astshopify = 'xxxx'

        # GitHub API 头部
        headers = {
            "Authorization": f"token {token_astshopify}",
            "Accept": "application/vnd.github.v3+json"
        }

        # 构建分支保护规则
        # 核心是启用 'restrictions' 来限制推送权限，并设置 'required_pull_request_reviews'
        data = {
            "required_status_checks": None,  # 可以不设置状态检查
            "enforce_admins": True,  # 对管理员也启用这些限制
            "required_pull_request_reviews": {
                "required_approving_review_count": 1  # 需要至少1个批准
            },
            "restrictions": {
                "users": ['luke-axt'],  # 这里可以添加允许直接推送的用户列表，留空则所有用户都不能直接推送
            },
            "allow_force_pushes": False,  # 不允许强制推送
            "allow_deletions": False  # 不允许删除分支
        }

        # 发送请求更新分支保护规则
        url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/branches/{BRANCH_NAME}/protection"
        response = requests.put(url, json=data, headers=headers)

        # 检查响应
        if response.status_code == 200:
            print(f"✅ 已成功保护分支 {BRANCH_NAME}，所有用户（包括a账号）现在都需要通过Pull Request来合并更改。")
        else:
            print(f"❌ 设置失败，状态码：{response.status_code}")
            print(f"错误信息：{response.json()}")

    def verify_repo_exists(self, org_name, repo_name):
        """验证仓库是否存在且有访问权限"""
        token_astshopify = 'xxxx'
        headers = {
            "Authorization": f"token {token_astshopify}",
            "Accept": "application/vnd.github.v3+json"
        }

        url = f"https://api.github.com/repos/{org_name}/{repo_name}"
        print(url)
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            repo_data = response.json()
            print(f"✅ 仓库存在: {repo_data['full_name']}")
            print(f"   可见性: {repo_data['visibility']}")
            print(f"   权限: {repo_data['permissions']}")
            return True
        else:
            print(f"❌ 仓库不存在或无访问权限: {response.status_code}")
            print(f"错误信息: {response.json()}")
            return False

    def diagnose_token_issues(self):
        """诊断 Fine-grained Token 问题"""
        print("🔍 诊断 Fine-grained Token 权限...")
        token_astshopify = 'xxxx'
        headers = {
            "Authorization": f"token {token_astshopify}",
            "Accept": "application/vnd.github.v3+json"
        }

        # 1. 测试基础权限
        user_url = "https://api.github.com/user"
        user_response = requests.get(user_url, headers=headers)

        if user_response.status_code == 200:
            user_data = user_response.json()
            print(f"✅ Token 有效，用户: {user_data['login']}")
        else:
            print(f"❌ Token 基础权限问题: {user_response.status_code}")
            return

        # 2. 测试组织访问
        orgs_url = "https://api.github.com/user/orgs"
        orgs_response = requests.get(orgs_url, headers=headers)

        if orgs_response.status_code == 200:
            orgs = orgs_response.json()
            print("🏢 可访问的组织:")
            for org in orgs:
                print(f"   - {org['login']}")
        else:
            print("❌ 无法访问组织列表")

        # 3. 测试仓库访问（用你知道存在的仓库）
        test_repo_url = "https://api.github.com/repos/astshopify/test"  # 先用个人仓库测试
        repo_response = requests.get(test_repo_url, headers=headers)

        if repo_response.status_code == 200:
            print("✅ 有仓库访问权限")
        else:
            print(f"❌ 仓库访问权限问题: {repo_response.status_code}")

# GithubManage().verify_repo_exists(org_name='astshopify',repo_name='test')
# GithubManage().diagnose_token_issues()
GithubManage().set_branch_no_push('web-ext-data')



