import json
import os

import yaml


def check_file_exist(file_path: str) -> None:
    if not os.path.isfile(file_path):
        message = f"This file('{file_path}') not found"
        raise FileNotFoundError(message)


def check_file_not_exist(file_path: str) -> None:
    if os.path.isfile(file_path):
        message = f"This file('{file_path}') already exists"
        raise FileExistsError(message)


def check_dir_not_exist(dir_path: str) -> None:
    if os.path.isdir(dir_path):
        message = f"This folder('{dir_path}') already exists"
        raise FileExistsError(message)


def read_text(text_file_path: str) -> str:
    with open(text_file_path, "r", encoding="utf-8") as f:
        return f.read()


def write_text(text_file_path: str, text_data: str) -> None:
    with open(text_file_path, "w", encoding="utf-8") as f:
        f.write(text_data)


def read_json(json_file_path: str) -> dict:
    with open(json_file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(json_file_path: str, json_data: dict) -> None:
    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4)


def read_yaml(yaml_file_path: str) -> dict:
    with open(yaml_file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
