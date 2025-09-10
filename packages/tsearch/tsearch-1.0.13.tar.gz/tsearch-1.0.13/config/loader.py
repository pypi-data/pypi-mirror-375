import yaml
import json
import sys
import os
from pathlib import Path

curren_dir = str(Path(__file__).resolve().parent.parent)


def load_env():
    with open(curren_dir + "/env.json") as stream:
        env_cfg = json.load(stream)
        return env_cfg["env"]


env = load_env()


def load_config():
    file_name = curren_dir + f"/config/config.{env}.yaml"
    with open(file_name, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


cfg = load_config()


class CFG:
    distance_type = cfg["distance_type"]
