import argparse
import logging
import os
import sys
import json
import random

from camel.typing import ModelType

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


def load_json(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


def generate_random_game_prompt():
    classic_games = load_json("classic_games.json")["classic_games"]
    oblique_strategies = load_json("oblique_strategies.json")["oblique_strategies"]

    game = random.choice(classic_games)
    strategy = random.choice(oblique_strategies)
    return f"Modify '{game}' by applying: {strategy}"


parser = argparse.ArgumentParser(description='ChatDev Runner')
parser.add_argument('--config', type=str, default="Default",
                    help="Configuration name under CompanyConfig/")
parser.add_argument('--org', type=str, default="DefaultOrganization",
                    help="Organization name, output in WareHouse/name_org_timestamp")
parser.add_argument('--task', type=str, default=None,
                    help="Task prompt, auto-generated if --random-game is set")
parser.add_argument('--name', type=str, default="Gomoku",
                    help="Software name, output in WareHouse/name_org_timestamp")
parser.add_argument('--model', type=str, default="GPT_3_5_TURBO",
                    help="GPT Model selection")
parser.add_argument('--path', type=str, default="",
                    help="Directory for incremental mode")
parser.add_argument('--random-game', action='store_true',
                    help="Enable random game and strategy selection")
args = parser.parse_args()

if args.random_game:
    args.task = generate_random_game_prompt()
    print(f"[INFO] Generated Task: {args.task}")

# Start ChatDev
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
