import json
import random
from pathlib import Path

import numpy as np
import torch
import yaml


def load_config(config_path="configs/config.yaml"):
    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r") as file:
        return yaml.safe_load(file)


def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)


def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def get_device(device_name="cpu"):
    if device_name == "cuda" and torch.cuda.is_available():
        return torch.device("cuda")

    return torch.device("cpu")


def save_class_mapping(class_names, path):
    ensure_dir(Path(path).parent)

    with open(path, "w") as file:
        json.dump(class_names, file, indent=4)


def load_class_mapping(path):
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Class mapping not found: {path}")

    with open(path, "r") as file:
        return json.load(file)


def save_metrics(metrics, path):
    ensure_dir(Path(path).parent)

    with open(path, "w") as file:
        json.dump(metrics, file, indent=4)


def is_image_file(file_path, extensions):
    return Path(file_path).suffix.lower() in extensions