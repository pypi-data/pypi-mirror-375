import os
import yaml
import logging

CONFIG_FILE = "config.symbols.yaml"
GLOBAL_CONFIG_FILE = "config.global.yaml"

logging.basicConfig(level=logging.INFO)


def load_symbol_cfg():
    """โหลด symbol config จาก YAML"""
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if not isinstance(data, dict):
                return {}
            return data
    except Exception as e:
        logging.error(f"[CONFIG] load_symbol_cfg error: {e}")
        return {}


def load_global_cfg():
    """โหลด global config จาก YAML"""
    if not os.path.exists(GLOBAL_CONFIG_FILE):
        return {}
    try:
        with open(GLOBAL_CONFIG_FILE, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if not isinstance(data, dict):
                return {}
            return data
    except Exception as e:
        logging.error(f"[CONFIG] load_global_cfg error: {e}")
        return {}
