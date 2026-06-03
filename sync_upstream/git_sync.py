import os
import subprocess
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class GitSync:
    @staticmethod
    def sync_repository(local_path: str, branch: str, upstream_url: Optional[str] = None) -> bool:
        """
        Sync a local git repository with upstream using git commands
        
        Args:
            local_path: Path to local git repository
            branch: Branch to sync
            upstream_url: Optional upstream URL (if not provided, will try to get from git)
        
        Returns:
            True if sync successful, False otherwise
        """
        if not os.path.exists(local_path):
            logger.error(f"Local repository path does not exist: {local_path}")
            return False
        
        if not os.path.exists(os.path.join(local_path, ".git")):
            logger.error(f"Not a git repository: {local_path}")
            return False
        
        try:
            # Change to repository directory
            original_dir = os.getcwd()
            os.chdir(local_path)
            
            logger.info(f"Starting git sync for {local_path} branch {branch}")
            
            # Check current branch
            current_branch = GitSync._run_git_command(["rev-parse", "--abbrev-ref", "HEAD"])
            logger.info(f"Current branch: {current_branch}")
            
            # Checkout the target branch if not already on it
            if current_branch.strip() != branch:
                logger.info(f"Checking out branch {branch}")
                GitSync._run_git_command(["checkout", branch])
            
            # Fetch latest from upstream
            logger.info("Fetching from upstream")
            GitSync._run_git_command(["fetch", "upstream"])
            
            # Merge upstream changes (fast-forward only to avoid merge commits)
            logger.info(f"Merging upstream/{branch}")
            GitSync._run_git_command(["merge", "--ff-only", f"upstream/{branch}"])
            
            # Push to origin
            logger.info("Pushing to origin")
            GitSync._run_git_command(["push", "origin", branch])
            
            logger.info(f"Successfully synced {local_path} branch {branch}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Git command failed: {e.cmd}")
            logger.error(f"Error output: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Error syncing repository: {e}", exc_info=True)
            return False
        finally:
            # Change back to original directory
            os.chdir(original_dir)
    
    @staticmethod
    def _run_git_command(args: list) -> str:
        """Run a git command and return the output"""
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
