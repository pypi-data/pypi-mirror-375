import json

def load_config(config_path):
    with open(config_path, "r") as f:
        return json.load(f)

def save_config(cfg, out_path):
    with open(out_path, "w") as f:
        json.dump(cfg, f, indent=2)
