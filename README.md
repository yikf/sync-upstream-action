# Sync Upstream

Sync your forked GitHub repositories with their upstream repositories.

## Features

- **Auto Scan**: Automatically scan all your forked repositories
- **Configurable**: Include or exclude specific repositories via config file
- **Multi-branch Sync**: Sync all branches or specific branches of a repository
- **Backward Compatible**: Legacy single repository mode still works
- **Dual Mode**: Can be used as a GitHub Action or standalone script

## Installation with uv

```bash
# Clone the repository
git clone https://github.com/yikf/sync-upstream-action.git
cd sync-upstream-action

# Install dependencies with uv
uv pip install -e sync-upstream/
```

## Usage

### Standalone Script

```bash
# Set GitHub token
export GITHUB_TOKEN="your_personal_access_token"

# Auto scan and sync all forked repositories
uv run python sync-upstream/main.py --owner "Yikf"

# Or use a config file
uv run python sync-upstream/main.py --config config.yaml
```

### GitHub Action

#### Basic Usage - Auto Scan All Forks

```yaml
uses: yikf/sync-upstream-action@v2
with:
  token: ${{ secrets.SYNC_UPSTREAM_TOKEN }}
  owner: 'Yikf'
```

#### Legacy Mode - Single Repository

```yaml
uses: yikf/sync-upstream-action@v2
with:
  token: ${{ secrets.SYNC_UPSTREAM_TOKEN }}
  owner: 'Yikf'
  repo: 'repo-name'
  branch: 'master'
```

#### Advanced - With Config File

```yaml
uses: yikf/sync-upstream-action@v2
with:
  token: ${{ secrets.SYNC_UPSTREAM_TOKEN }}
  config: './config.yaml'
```

## Inputs

| name    | required | description                                                                 |
|---------|----------|-----------------------------------------------------------------------------|
| token   | Y        | GitHub personal access token with `repo` scope                             |
| owner   | N        | Owner of the forked repositories (defaults to current user)                 |
| repo    | N        | Single repository name (legacy mode)                                        |
| branch  | N        | Branch name for single repo mode (default: `master`)                        |
| config  | N        | Path to config file for advanced configuration                              |

## Configuration File

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

## Personal Access Token

Create a GitHub Personal Access Token (PAT) with the `repo` scope at:
https://github.com/settings/tokens

## Example Workflow

Check out the [workflow file](./.github/workflows/main.yml) in this repository.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
