import json
from pathlib import Path
import os

def load_config():
    """Load config.json and merge with local.config.json (if exists)."""
    root_dir = Path(__file__).resolve().parent.parent
    config_path = root_dir / "config.json"
    with open(config_path) as f:
        config = json.load(f)

    local_config_path = root_dir / "local.config.json"
    if local_config_path.exists():
        with open(local_config_path) as f:
            local_config = json.load(f)
            config.update(local_config)

    if "model" in config:
        for key in ["model_path", "embeddings_path"]:
            if key in config["model"]:
                config["model"][key] = str(
                    root_dir / config["model"][key]
                )

    if "paths" in config:
        for key in ["data_dir", "output_dir"]:
            if key in config["paths"]:
                config["paths"][key] = str(
                    root_dir / config["paths"][key]
                )
    
    return config