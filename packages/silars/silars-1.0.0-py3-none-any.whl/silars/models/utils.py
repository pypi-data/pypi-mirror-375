# Copyright (c) ZhangYundi.
# Licensed under the MIT License. 
# Created on 2025/9/3 14:33
# Description:

import hashlib
import json
from typing import Sequence

def generate_model_version(train_dates: list[str],
                           valid_dates: list[str],
                           feature_config: dict[str, list[str]],
                           target_config: dict[str, dict[str, str]],
                           seeds: Sequence[int] = (42, 888),
                           diff: bool = True,
                           **model_params):
    params = {
        "train_dates": sorted(train_dates),
        "valid_dates": sorted(valid_dates),
        "feature_config": {k.replace("_a/", "/"): sorted(feature_config[k]) for k in sorted(feature_config.keys())},
        "target_config": {k.replace("_a/", "/"): {k_: target_config[k][k_] for k_ in sorted(target_config[k].keys())} for k in sorted(target_config.keys())},
        "seeds": sorted(seeds),
        "diff": diff,
        "model_params": {k: model_params[k] for k in sorted(model_params.keys())}
    }
    # 序列化参数
    params_str = json.dumps(params, sort_keys=True, separators=(',', ':'))
    # 生成md5哈希
    hash_obj = hashlib.md5(params_str.encode("utf-8"))
    version = hash_obj.hexdigest()
    return version


