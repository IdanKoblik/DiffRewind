import logging
import sys
from pathlib import Path
from typing import Dict
from git_handler import GitHandler
from gitlab_handler import GitLabHandler
from config_handler import ConfigHandler
from diff_handler import DiffHandler

HEADER = """
██████╗ ██╗███████╗███████╗██████╗ ███████╗██╗    ██╗██╗███╗   ██╗██████╗ 
██╔══██╗██║██╔════╝██╔════╝██╔══██╗██╔════╝██║    ██║██║████╗  ██║██╔══██╗
██║  ██║██║█████╗  █████╗  ██████╔╝█████╗  ██║ █╗ ██║██║██╔██╗ ██║██║  ██║
██║  ██║██║██╔══╝  ██╔══╝  ██╔══██╗██╔══╝  ██║███╗██║██║██║╚██╗██║██║  ██║
██████╔╝██║██║     ██║     ██║  ██║███████╗╚███╔███╔╝██║██║ ╚████║██████╔╝
╚═════╝ ╚═╝╚═╝     ╚═╝     ╚═╝  ╚═╝╚══════╝ ╚══╝╚══╝ ╚═╝╚═╝  ╚═══╝╚═════╝ 
"""

def setup_logging() -> None:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def get_repo_path() -> Path:
    if len(sys.argv) != 2:
        raise ValueError("Usage: python3 main.py <path-to-git-project>")
    return Path(sys.argv[1])

def initialize_handlers(repo_path: Path) -> tuple[GitHandler, GitLabHandler, DiffHandler]:
    git_handler = GitHandler(repo_path)
    if not git_handler.is_valid_repo():
        raise ValueError(f"The git repository directory '{repo_path}' was not found.")

    config_handler = ConfigHandler('config.json')
    config = config_handler.load_config()
    if config is None:
        raise ValueError("Failed to load or create configuration.")

    gitlab_handler = GitLabHandler(config['instance'], config['token'])
    project_id = gitlab_handler.get_project_id(git_handler.get_origin_url())
    if not project_id:
        raise ValueError("Could not determine project ID.")
    gitlab_handler.project_id = project_id

    diff_handler = DiffHandler(gitlab_handler, git_handler)
    return git_handler, gitlab_handler, diff_handler

def display_stacked_diffs(stacked_diffs: Dict[str, list]) -> None:
    print("Stacked diffs:")
    for i, (base_name, branches_info) in enumerate(stacked_diffs.items(), start=1):
        print(f"[ {i} ] > {base_name}")
        for branch, iid, created_at in branches_info:
            print(f"    - {branch} (MR IID: {iid}, Created at: {created_at})")

def get_user_selection(stacked_diffs: Dict[str, list]) -> tuple[str, list]:
    while True:
        try:
            selection = int(input("Select which stacked diff to restore (1,2,3...) > "))
            if 1 <= selection <= len(stacked_diffs):
                return list(stacked_diffs.items())[selection - 1]
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def main() -> None:
    setup_logging()
    logger = logging.getLogger(__name__)

    print(HEADER)

    try:
        repo_path = get_repo_path()
        git_handler, gitlab_handler, diff_handler = initialize_handlers(repo_path)

        branches = git_handler.get_branches()
        stacked_diffs = diff_handler.group_stacked_diffs(branches)

        if stacked_diffs:
            display_stacked_diffs(stacked_diffs)
            base_name, branches_info = get_user_selection(stacked_diffs)
            diff_handler.create_stack_json(branches_info, base_name)
        else:
            print("No stacked diffs found.")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()