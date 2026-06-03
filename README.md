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

#### Option 1: Install from PyPI (recommended)
```bash
# Install from PyPI
uv pip install sync-upstream

# Then you can run it from anywhere
uv run sync-upstream --owner "Yikf"
```

#### Option 2: Just install dependencies and run (simplest)
```bash
# Clone the repository
git clone https://github.com/yikf/sync-upstream-action.git
cd sync-upstream-action

# Install dependencies
uv sync

# Run the script
uv run python run_sync.py --owner "Yikf"
```

#### Option 3: Install directly from GitHub
```bash
# Install from GitHub
uv pip install git+https://github.com/yikf/sync-upstream-action.git

# Then you can run it from anywhere
uv run sync-upstream --owner "Yikf"
```

#### Option 4: Editable install (for development)
```bash
git clone https://github.com/yikf/sync-upstream-action.git
cd sync-upstream-action
uv pip install -e .
```

### Usage

```bash
# Set GitHub token
export GITHUB_TOKEN="your_personal_access_token"

# If you installed as a tool
uv run sync-upstream --owner "Yikf"
# Or with config file
uv run sync-upstream --config config.yaml

# If you just installed dependencies
uv run python run_sync.py --owner "Yikf"
# Or with config file
uv run python run_sync.py --config config.yaml
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

Create a GitHub Personal Access Token (PAT) at:
https://github.com/settings/tokens

#### Classic Token (旧版)
- Select `repo` scope (full control of private repositories)

#### Fine-grained Token (新版细粒度 - 推荐)
- Repository access: `All repositories` or select specific repositories you want to sync
- Permissions:
  - **Repository permissions**:
    - `Contents`: Read and write (required to sync branches)
    - `Workflows`: Read and write (required to sync workflow files)
    - `Metadata`: Read-only (automatically included)

**Note**: If you need to sync private repositories, make sure the token has access to them.

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
        run: uv pip install sync-upstream
      
      - name: Sync repositories
        run: uv run sync-upstream --token "${{ secrets.GITHUB_TOKEN }}" --owner "YOUR_GITHUB_USERNAME"
```

**Note**: Replace `YOUR_GITHUB_USERNAME` with your actual GitHub username, and you may need to create a personal access token with `repo` scope and store it as a secret in your repository.

## 🔒 Security Advice

### Using Secrets in GitHub Actions

Never commit tokens in plaintext to your repository. Use GitHub Secrets for secure storage:

1. Go to your repository → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `SYNC_UPSTREAM_TOKEN`
4. Value: Your GitHub Personal Access Token
5. Use in workflows: `${{ secrets.SYNC_UPSTREAM_TOKEN }}`

### Local Usage Security

1. **Use environment variables** (recommended):
   ```bash
   # Add to ~/.bashrc or ~/.zshrc
   export GITHUB_TOKEN="your_token_here"
   ```

2. **Use .gitignore**:
   ```
   # .gitignore
   config.yaml
   *.env
   ```

3. **Principle of least privilege**:
   - Use Fine-grained tokens instead of Classic tokens
   - Only grant necessary permissions (Contents + Workflows)
   - Set a reasonable expiration time

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

#### 选项 1：从 PyPI 安装（推荐）
```bash
# 从 PyPI 安装
uv pip install sync-upstream

# 然后可以在任何地方运行
uv run sync-upstream --owner "Yikf"
```

#### 选项 2：仅安装依赖并运行（最简单）
```bash
# 克隆仓库
git clone https://github.com/yikf/sync-upstream-action.git
cd sync-upstream-action

# 安装依赖
uv sync

# 运行脚本
uv run python run_sync.py --owner "Yikf"
```

#### 选项 3：直接从 GitHub 安装
```bash
# 从 GitHub 安装
uv pip install git+https://github.com/yikf/sync-upstream-action.git

# 然后可以在任何地方运行
uv run sync-upstream --owner "Yikf"
```

#### 选项 4：可编辑模式安装（用于开发）
```bash
git clone https://github.com/yikf/sync-upstream-action.git
cd sync-upstream-action
uv pip install -e .
```

### 使用方法

```bash
# 设置 GitHub 令牌
export GITHUB_TOKEN="your_personal_access_token"

# 如果作为工具安装
uv run sync-upstream --owner "Yikf"
# 或者使用配置文件
uv run sync-upstream --config config.yaml

# 如果仅安装了依赖
uv run python run_sync.py --owner "Yikf"
# 或者使用配置文件
uv run python run_sync.py --config config.yaml
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

在以下地址创建 GitHub 个人访问令牌（PAT）：
https://github.com/settings/tokens

#### Classic Token (旧版)
- 选择 `repo` 权限范围（完全控制私有仓库）

#### Fine-grained Token (新版细粒度 - 推荐)
- 仓库访问权限：`All repositories` 或选择您要同步的特定仓库
- 权限设置：
  - **仓库权限**：
    - `Contents`：读取和写入（同步分支必需）
    - `Workflows`：读取和写入（同步工作流文件必需）
    - `Metadata`：只读（自动包含）

**注意**：如果需要同步私有仓库，请确保令牌有权访问这些仓库。

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
        run: uv pip install sync-upstream
      
      - name: Sync repositories
        run: uv run sync-upstream --token "${{ secrets.GITHUB_TOKEN }}" --owner "YOUR_GITHUB_USERNAME"
```

**注意**：请将 `YOUR_GITHUB_USERNAME` 替换为您实际的 GitHub 用户名，您可能需要创建一个具有 `repo` 权限的个人访问令牌，并将其作为密钥存储在您的仓库中。

## 🔒 安全建议

### GitHub Actions 中使用 Secrets

永远不要将 token 明文提交到仓库中。使用 GitHub Secrets 安全存储：

1. 进入仓库 → **Settings** → **Secrets and variables** → **Actions**
2. 点击 **New repository secret**
3. 名称：`SYNC_UPSTREAM_TOKEN`
4. 值：您的 GitHub Personal Access Token
5. 在工作流中使用：`${{ secrets.SYNC_UPSTREAM_TOKEN }}`

### 本地使用安全配置

1. **使用环境变量**（推荐）：
   ```bash
   # 在 ~/.bashrc 或 ~/.zshrc 中添加
   export GITHUB_TOKEN="your_token_here"
   ```

2. **使用 .gitignore**：
   ```
   # .gitignore
   config.yaml
   *.env
   ```

3. **最小权限原则**：
   - 使用 Fine-grained tokens 代替 Classic tokens
   - 只授予必要的权限（Contents + Workflows）
   - 设置合理的过期时间

### 许可证

本项目采用 Apache License 2.0 许可证 - 有关详细信息，请参阅 [LICENSE](LICENSE) 文件。
