import os
import platform
import json

DEFAULT_CONFIG = {
    "mass_transformation": 0.00574,
    "mass_cutoff": 20,
    "peak_width_cutoff": 5,
    "peak_distance_cutoff": 5,
    "raw_data_folder": "~/research/lifescale_raw_data_test/development_raw_data_folder"
}

LINUX_PATH = "./dev_config.json"
WINDOWS_PATH = r"C:\Users\LifeScale\Documents\peak_caller_config\peak_caller_config.json"

def load_config():
    if platform.system() == "Linux":
        try:
            with open(LINUX_PATH, "r") as f:
                config = json.load(f)
            return config, None
        except FileNotFoundError as e:
            config = DEFAULT_CONFIG
            with open(LINUX_PATH, "w") as f:
                json.dump(config, f)
            return config, LINUX_PATH
    elif platform.system() == "Windows":
        try:
            with open(WINDOWS_PATH, "r") as f:
                config = json.load(f)
            return config, None
        except FileNotFoundError as e:
            config = DEFAULT_CONFIG
            with open(WINDOWS_PATH, "w") as f:
                json.dump(config, f)
            return config, WINDOWS_PATH

def configure_peakcaller(raw_data_folder, mass_transformation, mass_cutoff, peak_width_cutoff, peak_distance_cutoff, config, command):
    print(locals())
    new_config = {k:v for k,v in locals().items() if k != "config" and k != "command" and v is not None}
    print(new_config)
    old_config = locals()["config"]
    merged_config = {k:new_config[k] if k in new_config else old_config[k] for k in old_config}
    if platform.system() == "Linux":
        with open(LINUX_PATH, "w") as f:
            json.dump(merged_config, f)
    elif platform.system() == "Windows":
        with open(WINDOWS_PATH, "w") as f:
            json.dump(merged_config, f)
    return merged_config
