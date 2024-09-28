import logging
import sys
from pathlib import Path
from git_handler import GitHandler
from gitlab_handler import GitLabHandler
from config_handler import ConfigHandler
from diff_handler import DiffHandler
import json

HEADER = """
██████╗ ██╗███████╗███████╗██████╗ ███████╗██╗    ██╗██╗███╗   ██╗██████╗ 
██╔══██╗██║██╔════╝██╔════╝██╔══██╗██╔════╝██║    ██║██║████╗  ██║██╔══██╗
██║  ██║██║█████╗  █████╗  ██████╔╝█████╗  ██║ █╗ ██║██║██╔██╗ ██║██║  ██║
██║  ██║██║██╔══╝  ██╔══╝  ██╔══██╗██╔══╝  ██║███╗██║██║██║╚██╗██║██║  ██║
██████╔╝██║██║     ██║     ██║  ██║███████╗╚███╔███╔╝██║██║ ╚████║██████╔╝
╚═════╝ ╚═╝╚═╝     ╚═╝     ╚═╝  ╚═╝╚══════╝ ╚══╝╚══╝ ╚═╝╚═╝  ╚═══╝╚═════╝ 
"""

def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    print(HEADER)

    if len(sys.argv) != 2:
        logger.error("Usage: python3 main.py <path-to-git-project>")
        return

    repo_path = Path(sys.argv[1])
    git_handler = GitHandler(repo_path)

    if not git_handler.is_valid_repo():
        logger.error(f"The git repository directory '{repo_path}' was not found.")
        return

    config_handler = ConfigHandler('config.json')
    config = config_handler.load_config()

    if config is None:
        logger.error("Failed to load or create configuration.")
        return

    gitlab_handler = GitLabHandler(config['instance'], config['token'])
    project_id = gitlab_handler.get_project_id(git_handler.get_origin_url())

    if not project_id:
        logger.error("Could not determine project ID.")
        return

    gitlab_handler.project_id = project_id  

    branches = git_handler.get_branches()
    diff_handler = DiffHandler(gitlab_handler, git_handler)
    stacked_diffs = diff_handler.group_stacked_diffs(branches)
    print(stacked_diffs)

    if stacked_diffs:
        print("Stacked diffs:")
        selection_map = {}
        for i, (base_name, branches_info) in enumerate(stacked_diffs.items(), start=1):
            print(f"[ {i} ] > {base_name}")
            selection_map[i] = (base_name, branches_info)

        option = input("Select which stacked diff to restore (1,2,3...) > ")
        try:
            selected_index = int(option)
            if selected_index in selection_map:
                base_name, branches_info = selection_map[selected_index]
                print(f"Branches for {base_name}:")
                for branch_info in branches_info:
                    branch, iid, created_at = branch_info
                    print(f"    - {branch} (MR IID: {iid}, Created at: {created_at})")

                diff_handler.create_stack_json(branches_info, base_name)
            else:
                logger.error("Invalid option selected.")
        except ValueError:
            logger.error("Invalid input. Please enter a number.")
    else:
        print("No stacked diffs found.")

if __name__ == '__main__':
    main()