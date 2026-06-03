#!/usr/bin/env python3
import argparse
import sys
import os
import logging
from .config import ConfigLoader
from .github_api import GitHubAPI
from .scanner import RepositoryScanner
from .sync import Synchronizer
from .models import Repository


class EmojiLogFormatter(logging.Formatter):
    """自定义日志格式化器，添加友好的图标"""
    LEVEL_EMOJIS = {
        logging.DEBUG: "🔍",
        logging.INFO: "ℹ️",
        logging.WARNING: "⚠️",
        logging.ERROR: "❌",
        logging.CRITICAL: "🔥"
    }

    def format(self, record):
        emoji = self.LEVEL_EMOJIS.get(record.levelno, "")
        record.emoji = emoji
        return super().format(record)


# Configure logging
handler = logging.StreamHandler()
formatter = EmojiLogFormatter(
    '%(asctime)s - %(name)s - %(emoji)s %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)

root_logger = logging.getLogger()
root_logger.addHandler(handler)
root_logger.setLevel(logging.INFO)

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Sync upstream repositories")
    parser.add_argument("--config", "-c", help="Path to config file")
    parser.add_argument("--token", "-t", help="GitHub personal access token")
    parser.add_argument("--owner", "-o", help="Repository owner")
    parser.add_argument("--repo", "-r", help="Single repository name (legacy mode)")
    parser.add_argument("--branch", "-b", help="Single branch name (legacy mode)")
    
    args = parser.parse_args()
    logger.info("Starting sync-upstream")

    # Check if running in legacy single repo mode
    if args.repo and args.owner and args.token:
        logger.info(f"Running in legacy single repo mode: {args.owner}/{args.repo}")
        github_api = GitHubAPI(args.token)
        branch = args.branch if args.branch else "master"
        
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
                logger.info(f"Upstream found: {repo.upstream}")
            
            sync = Synchronizer(github_api)
            success = sync.sync_repository(repo, [branch])
            sys.exit(0 if success else 1)
        else:
            logger.error(f"Repository {args.owner}/{args.repo} not found")
            sys.exit(1)

    # Load configuration
    try:
        if args.config:
            logger.info(f"Loading configuration from file: {args.config}")
            config = ConfigLoader.load_from_file(args.config)
        else:
            logger.info("Loading configuration from environment variables")
            config = ConfigLoader.load_from_env()
        
        if args.token:
            config.github_token = args.token
        if args.owner:
            config.owner = args.owner
        
        if not config.github_token:
            logger.error("GitHub token is required. Set via --token, config file, or GITHUB_TOKEN environment variable.")
            parser.print_help()
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error loading configuration: {e}", exc_info=True)
        sys.exit(1)

    # Initialize components
    logger.info("Initializing components")
    github_api = GitHubAPI(config.github_token)
    scanner = RepositoryScanner(config, github_api)
    synchronizer = Synchronizer(github_api)

    # Scan repositories
    try:
        repos = scanner.scan()
    except Exception as e:
        logger.error(f"Error scanning repositories: {e}", exc_info=True)
        sys.exit(1)

    if not repos:
        logger.info("No repositories to sync")
        sys.exit(0)

    # Sync repositories
    logger.info(f"Starting sync for {len(repos)} repositories")
    repo_configs = config.repositories.get("included", [])
    results = synchronizer.sync_repositories(repos, repo_configs)

    # Print results
    logger.info("\n" + "=" * 50)
    logger.info(f"Sync complete: {results['success']} succeeded, {results['failed']} failed")
    logger.info("=" * 50)

    for detail in results["details"]:
        status = "✓" if detail["success"] else "✗"
        if detail["success"]:
            logger.info(f"{status} {detail['repo']}")
        else:
            error_msg = f"{status} {detail['repo']}"
            if "error" in detail:
                error_msg += f" - {detail['error']}"
            logger.error(error_msg)

    sys.exit(0 if results["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
