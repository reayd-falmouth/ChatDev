import sys
from json import loads

import argparse
import logging
import os
from datetime import datetime

from camel.typing import ModelType
from chatdev.game_ideation import *

root = os.path.dirname(__file__)
sys.path.append(root)

from chatdev.chat_chain import ChatChain

try:
    from openai.types.chat.chat_completion_message_tool_call import ChatCompletionMessageToolCall
    from openai.types.chat.chat_completion_message import FunctionCall

    openai_new_api = True  # new openai api version
except ImportError:
    openai_new_api = False  # old openai api version
    print(
        "Warning: Your OpenAI version is outdated. \n "
        "Please update as specified in requirement.txt. \n "
        "The old API interface is deprecated and will no longer be supported.")


def get_config(company):
    """
    return configuration json files for ChatChain
    user can customize only parts of configuration json files, other files will be left for default
    Args:
        company: customized configuration name under CompanyConfig/
    Returns:
        path to three configuration jsons: [config_path, config_phase_path, config_role_path]
    """
    config_dir = os.path.join(root, "CompanyConfig", company)
    default_config_dir = os.path.join(root, "CompanyConfig", "Default")

    config_files = [
        "ChatChainConfig.json",
        "PhaseConfig.json",
        "RoleConfig.json"
    ]

    config_paths = []
    for config_file in config_files:
        company_config_path = os.path.join(config_dir, config_file)
        default_config_path = os.path.join(default_config_dir, config_file)
        if os.path.exists(company_config_path):
            config_paths.append(company_config_path)
        else:
            config_paths.append(default_config_path)
    return tuple(config_paths)


def run_chatdev(args):
    config_path, config_phase_path, config_role_path = get_config(args.config)
    args2type = {
        'GPT_3_5_TURBO': ModelType.GPT_3_5_TURBO,
        'GPT_4': ModelType.GPT_4,
        'GPT_4_TURBO': ModelType.GPT_4_TURBO,
        'GPT_4O': ModelType.GPT_4O,
        'GPT_4O_MINI': ModelType.GPT_4O_MINI,
    }
    if openai_new_api:
        args2type['GPT_3_5_TURBO'] = ModelType.GPT_3_5_TURBO_NEW

    chat_chain = ChatChain(config_path=config_path,
                           config_phase_path=config_phase_path,
                           config_role_path=config_role_path,
                           task_prompt=args.task,
                           project_name=args.name,
                           org_name=args.org,
                           model_type=args2type[args.model],
                           code_path=args.path)

    # Init Log
    logging.basicConfig(filename=chat_chain.log_filepath, level=logging.INFO,
                        format='[%(asctime)s %(levelname)s] %(message)s',
                        datefmt='%Y-%d-%m %H:%M:%S', encoding="utf-8")

    # Pre Processing
    chat_chain.pre_processing()

    # Personnel Recruitment
    chat_chain.make_recruitment()

    # Chat Chain Execution
    chat_chain.execute_chain()

    # Post Processing
    chat_chain.post_processing()


def save_args_to_json(data, timestamp, name=None):
    """Save arguments to a timestamped JSON file, ensuring the directory exists."""
    if name:
        game_id = create_game_id(name)
    else:
        game_id = f"game_{timestamp}"

    # Define directory path
    dir_path = os.path.join("Branding", game_id)

    # Ensure the directory exists
    os.makedirs(dir_path, exist_ok=True)

    # Define file path
    filename = os.path.join(dir_path, "metadata.json")

    # Save data to JSON
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print(f"Saved run output to {filename}")


def parse_arguments():
    parser = argparse.ArgumentParser(description='ChatDev Runner')
    parser.add_argument('--config', type=str, default="Default",
                        help="Name of config, which is used to load configuration under CompanyConfig/")
    parser.add_argument('--org', type=str, default="DefaultOrganization",
                        help="Name of organization, your software will be generated in WareHouse/name_org_timestamp")
    parser.add_argument('--task', type=str, default="Develop a basic Gomoku game.",
                        help="Prompt of software")
    parser.add_argument('--name', type=str, default="Gomoku",
                        help="Name of software, your software will be generated in WareHouse/name_org_timestamp. "
                             "auto-generated if --random-game is set")
    parser.add_argument('--model', type=str, default="GPT_3_5_TURBO",
                        help="GPT Model, choose from {'GPT_3_5_TURBO', 'GPT_4', 'GPT_4_TURBO', 'GPT_4O', 'GPT_4O_MINI'}")
    parser.add_argument('--path', type=str, default="",
                        help="Your file directory, ChatDev will build upon your software in the Incremental mode")
    parser.add_argument('--random-game', action='store_true',
                        help="Enable random game and strategy selection")
    parser.add_argument('--oblique-strategy', action='store_true',
                        help="Apply one of Brian Eno's Oblique Strategies to the development")
    parser.add_argument('--dry-run', action='store_true',
                        help="Perform a dry run, printing arguments without running ChatDev")
    parser.add_argument('--branding', action='store_true',
                        help="Generates the Cover image, descriptions and tags.")
    return parser.parse_args()


def main():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    args = parse_arguments()

    if args.random_game:
        args.task = generate_random_game_prompt()

    if args.oblique_strategy:
        args.task = apply_oblique_strategy(args.task)
        args.name = generate_name(f"{args.task}").strip()

    # Store branding output in a separate variable
    branding_data = generate_branding(args.task, args.name) if args.branding else None
    if args.branding:
        branding_data = generate_branding(f"{args.task}", f"{args.name}")
        print(f"Branding Data: {branding_data}")
        generate_cover(f"{args.task}", f"{args.name}", timestamp)

    output = vars(args)  # Convert args namespace to a dictionary

    if branding_data:
        output["branding_data"] = loads(branding_data)  # Include branding data if it exists

    # Always save the arguments to a JSON file
    save_args_to_json(output, timestamp, f"{args.name}")

    # Dry run: Print arguments including branding data if available
    if args.dry_run:
        print("[DRY RUN] Arguments:")
        print(json.dumps(output, indent=4))
        return

    # create the game
    run_chatdev(args)


if __name__ == "__main__":
    main()
