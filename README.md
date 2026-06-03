# Sync Upstream

[English](#english) | [中文](#中文)

---

## English

Sync your forked GitHub repositories with their upstream repositories.

### Features

- **Auto Scan**: Automatically scan all your forked repositories
- **Configurable**: Include or exclude specific repositories via config file
- **Multi-branch Sync**: Sync all branches or specific branches of a repository

### Installation with uv

```bash
# Clone the repository
git clone https://github.com/yikf/sync-upstream-action.git
cd sync-upstream-action

# Install dependencies with uv
uv pip install -e .
```

### Usage

```bash
# Set GitHub token
export GITHUB_TOKEN="your_personal_access_token"

# Auto scan and sync all forked repositories
uv run sync-upstream --owner "Yikf"

# Or use a config file
uv run sync-upstream --config config.yaml
```

### Configuration File

Create a `config.yaml` file for advanced configuration:

```yaml
github_token: "your_personal_access_token_here"
owner: "Yikf"

auto_scan:
  enabled: true
  include_private: false

repositories:
  included:
    - name: "kyuubi"
      branches: ["master", "branch-1.8", "branch-1.9"]
    - name: "spark"
      branches: []
  excluded:
    - "old-fork-repo"
    - "test-repo"

sync:
  method: "api"
  timeout: 300
```

### Personal Access Token

Create a GitHub Personal Access Token (PAT) with the `repo` scope at:
https://github.com/settings/tokens

### GitHub Actions Schedule

You can use GitHub Actions to run the sync script periodically. Here's an example workflow:

```yaml
on:
  schedule:
    - cron: "0 0 * * *" # 每天 UTC 00:00 执行
  workflow_dispatch: # 允许手动触发

name: Sync upstream repositories

jobs:
  run:
    name: Run Sync
    runs-on: ubuntu-latest
    steps:
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      
      - name: Install sync-upstream
        run: uv pip install git+https://github.com/yikf/sync-upstream-action.git
      
      - name: Sync repositories
        run: uv run sync-upstream --token "${{ secrets.GITHUB_TOKEN }}" --owner "YOUR_GITHUB_USERNAME"
```

**Note**: Replace `YOUR_GITHUB_USERNAME` with your actual GitHub username, and you may need to create a personal access token with `repo` scope and store it as a secret in your repository.

### License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

---

## 中文

将您的 GitHub 复刻仓库与上游仓库同步。

### 功能

- **自动扫描**：自动扫描您所有的复刻仓库
- **可配置**：通过配置文件包含或排除特定仓库
- **多分支同步**：同步仓库的所有分支或特定分支

### 使用 uv 安装

```bash
# 克隆仓库
git clone https://github.com/yikf/sync-upstream-action.git
cd sync-upstream-action

# 使用 uv 安装依赖
uv pip install -e .
```

### 使用方法

```bash
# 设置 GitHub 令牌
export GITHUB_TOKEN="your_personal_access_token"

# 自动扫描并同步所有复刻仓库
uv run sync-upstream --owner "Yikf"

# 或者使用配置文件
uv run sync-upstream --config config.yaml
```

### 配置文件

创建 `config.yaml` 文件进行高级配置：

```yaml
github_token: "your_personal_access_token_here"
owner: "Yikf"

auto_scan:
  enabled: true
  include_private: false

repositories:
  included:
    - name: "kyuubi"
      branches: ["master", "branch-1.8", "branch-1.9"]
    - name: "spark"
      branches: []
  excluded:
    - "old-fork-repo"
    - "test-repo"

sync:
  method: "api"
  timeout: 300
```

### 个人访问令牌

在以下地址创建具有 `repo` 权限的 GitHub 个人访问令牌（PAT）：
https://github.com/settings/tokens

### GitHub Actions 定时任务

您可以使用 GitHub Actions 定期运行同步脚本。以下是一个示例工作流：

```yaml
on:
  schedule:
    - cron: "0 0 * * *" # 每天 UTC 00:00 执行
  workflow_dispatch: # 允许手动触发

name: Sync upstream repositories

jobs:
  run:
    name: Run Sync
    runs-on: ubuntu-latest
    steps:
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      
      - name: Install sync-upstream
        run: uv pip install git+https://github.com/yikf/sync-upstream-action.git
      
      - name: Sync repositories
        run: uv run sync-upstream --token "${{ secrets.GITHUB_TOKEN }}" --owner "YOUR_GITHUB_USERNAME"
```

**注意**：请将 `YOUR_GITHUB_USERNAME` 替换为您实际的 GitHub 用户名，您可能需要创建一个具有 `repo` 权限的个人访问令牌，并将其作为密钥存储在您的仓库中。

### 许可证

本项目采用 Apache License 2.0 许可证 - 有关详细信息，请参阅 [LICENSE](LICENSE) 文件。
