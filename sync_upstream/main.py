#!/usr/bin/env python3
import argparse
import logging
import sys

from .config import ConfigLoader
from .github_api import GitHubAPI
from .scanner import RepositoryScanner
from .sync import Synchronizer


class EmojiLogFormatter(logging.Formatter):
    """Custom log formatter with friendly emojis"""

    LEVEL_EMOJIS = {
        logging.DEBUG: "🔍",
        logging.INFO: "✅",
        logging.WARNING: "⚠️",
        logging.ERROR: "❌",
        logging.CRITICAL: "🔥",
    }

    def format(self, record):
        emoji = self.LEVEL_EMOJIS.get(record.levelno, "")
        record.emoji = emoji
        return super().format(record)


# Configure logging
handler = logging.StreamHandler()
formatter = EmojiLogFormatter("%(emoji)s %(message)s")
handler.setFormatter(formatter)

root_logger = logging.getLogger()
root_logger.addHandler(handler)
root_logger.setLevel(logging.INFO)

# Reduce log noise from other modules
for logger_name in ["urllib3", "requests"]:
    logging.getLogger(logger_name).setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Sync upstream repositories")
    parser.add_argument("--config", "-c", help="Path to config file")
    parser.add_argument("--token", "-t", help="GitHub personal access token")
    parser.add_argument("--owner", "-o", help="Repository owner")

    args = parser.parse_args()

    print("")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                    🔄 Sync Upstream Tool                     ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print("")

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
            logger.error(
                "GitHub token is required. Set via --token, config file, or "
                "GITHUB_TOKEN environment variable."
            )
            parser.print_help()
            sys.exit(1)

        if not config.repositories:
            logger.error("No repositories configured. Please specify repositories in config file.")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        sys.exit(1)

    # Initialize components
    github_api = GitHubAPI(config.github_token)
    scanner = RepositoryScanner(config, github_api)
    synchronizer = Synchronizer(github_api)

    # Scan repositories
    try:
        repos = scanner.scan()
    except Exception as e:
        logger.error(f"Error scanning repositories: {e}")
        sys.exit(1)

    if not repos:
        logger.info("No repositories to sync")
        sys.exit(0)

    # Sync repositories
    logger.info(f"Starting sync for {len(repos)} repositories")
    repo_configs = config.repositories
    results = synchronizer.sync_repositories(repos, repo_configs)

    # Print results
    print("")
    print("╔══════════════════════════════════════════════════════════════╗")
    print(f"║  Sync complete: {results['success']:2d} succeeded, {results['failed']:2d} failed  ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print("")

    for detail in results["details"]:
        status = "✅" if detail["success"] else "❌"
        if detail["success"]:
            print(f"  {status} {detail['repo']}")
        else:
            error_msg = f"  {status} {detail['repo']}"
            if "error" in detail:
                error_msg += f" - {detail['error']}"
            print(error_msg)

    print("")

    sys.exit(0 if results["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
