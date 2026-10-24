# -*- coding: utf-8 -*-

import json
import os

CONFIG_FILE = "config.json"

DEFAULT = {
    "dorm_building": "1",
    "dorm_room": "101",
    "low_power_threshold": 10.0,
    "check_interval_minutes": 30,
    "cookie": "",
}


def load_config() -> dict:
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT)
        return dict(DEFAULT)
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    # 合并默认值，防止旧配置缺少新字段
    for k, v in DEFAULT.items():
        cfg.setdefault(k, v)
    return cfg


def save_config(cfg: dict) -> None:
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4, ensure_ascii=False)
