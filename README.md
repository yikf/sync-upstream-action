# Sync upstream repository docker action

This action syncs a fork of a repository to keep it up-to-date with the upstream repository.

## Inputs
| name  | required | description |
|:------|:---------| :-----|
| token | N        | The GitHub token used to authenticate with the GitHub API, default value is `${{ secrets.GITHUB_TOKEN }}` |
| owner | Y        | The owner of the forked repository |
| repo  | Y        | The name of the forked repository |
| branch| N        | The name of the branch to sync with the upstream repository, default value is `master` |

## Example usage

```yaml
uses: docker-sync-upstream@v1
with:
  token: ${{ secrets.GITHUB_TOKEN }}
  owner: 'owner'
  repo: 'repo'
  branch: 'master'
```