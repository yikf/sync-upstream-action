# Sync upstream repository docker action

This action syncs a fork of a repository to keep it up-to-date with the upstream repository.

## Inputs
| name  | required | description |
|:------|:---------| :-----|
| token | Y        | The GitHub token used to authenticate with the GitHub API |
| owner | Y        | The owner of the forked repository |
| repo  | Y        | The name of the forked repository |
| branch| N        | The name of the branch to sync with the upstream repository, default value is `master` |

## Example usage

```yaml
uses: docker-sync-upstream@v1
with:
  token: ${{ secrets.SYNC_UPSTREAM_TOKEN }}
  owner: 'owner'
  repo: 'repo'
  branch: 'master'
```
And you can also see the [current repo workflows](./.github/workflows/main.yml) for more details.

Note: The `SYNC_UPSTREAM_TOKEN` is a personal access token with the `repo` scope. You can create one.

TODO: Using other way to sync the forked repository, such as using the `git` command.