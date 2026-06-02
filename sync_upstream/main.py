#!/usr/bin/env python3
import argparse
import sys
import os
from .config import ConfigLoader
from .github_api import GitHubAPI
from .scanner import RepositoryScanner
from .sync import Synchronizer
from .models import Repository


def main():
    parser = argparse.ArgumentParser(description="Sync upstream repositories")
    parser.add_argument("--config", "-c", help="Path to config file")
    parser.add_argument("--token", "-t", help="GitHub personal access token")
    parser.add_argument("--owner", "-o", help="Repository owner")
    parser.add_argument("--repo", "-r", help="Single repository name (legacy mode)")
    parser.add_argument("--branch", "-b", help="Single branch name (legacy mode)")
    
    args = parser.parse_args()

    # Check if running in legacy single repo mode
    if args.repo and args.owner and args.token:
        from .sync import Synchronizer
        from .github_api import GitHubAPI
        github_api = GitHubAPI(args.token)
        branch = args.branch if args.branch else "master"
        
        from .models import Repository
        repo_data = github_api.get_repository(args.owner, args.repo)
        if repo_data:
            repo = Repository(
                owner=repo_data["owner"]["login"],
                name=repo_data["name"],
                full_name=repo_data["full_name"],
                is_private=repo_data["private"],
                default_branch=repo_data["default_branch"]
            )
            if "parent" in repo_data:
                repo.has_upstream = True
                repo.upstream = repo_data["parent"]["full_name"]
            
            sync = Synchronizer(github_api)
            success = sync.sync_repository(repo, [branch])
            sys.exit(0 if success else 1)
        else:
            print(f"Repository {args.owner}/{args.repo} not found")
            sys.exit(1)

    # Load configuration
    try:
        if args.config:
            config = ConfigLoader.load_from_file(args.config)
        else:
            config = ConfigLoader.load_from_env()
        
        if args.token:
            config.github_token = args.token
        if args.owner:
            config.owner = args.owner
        
        if not config.github_token:
            print("Error: GitHub token is required. Set via --token, config file, or GITHUB_TOKEN environment variable.")
            parser.print_help()
            sys.exit(1)

    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)

    # Initialize components
    github_api = GitHubAPI(config.github_token)
    scanner = RepositoryScanner(config, github_api)
    synchronizer = Synchronizer(github_api)

    # Scan repositories
    try:
        repos = scanner.scan()
    except Exception as e:
        print(f"Error scanning repositories: {e}")
        sys.exit(1)

    if not repos:
        print("No repositories to sync")
        sys.exit(0)

    # Sync repositories
    repo_configs = config.repositories.get("included", [])
    results = synchronizer.sync_repositories(repos, repo_configs)

    # Print results
    print("\n" + "=" * 50)
    print(f"Sync complete: {results['success']} succeeded, {results['failed']} failed")
    print("=" * 50)

    for detail in results["details"]:
        status = "✓" if detail["success"] else "✗"
        print(f"{status} {detail['repo']}")

    sys.exit(0 if results["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
