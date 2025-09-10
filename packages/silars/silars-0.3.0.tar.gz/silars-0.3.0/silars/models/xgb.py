# Copyright (c) ZhangYundi.
# Licensed under the MIT License. 
# Created on 2025/8/26 21:48
# Description:
import warnings
from pathlib import Path
from typing import Sequence

import logair
import numpy as np
import polars as pl
import xgboost as xgb
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import GridSearchCV

logger = logair.get_logger("silars.models.xgb")


def train_xgboost(train_df: pl.DataFrame,
                  valid_df: pl.DataFrame,
                  features: list[str],
                  target: str,
                  seeds: Sequence[int] = (42, 888),
                  cv_jobs: int = 1,
                  device: str = "cuda:5",
                  grid_params: dict[str, dict[str, ...]]=None,
                  grid_jobs: int = 5,
                  early_stopping_rounds: int = 10,
                  cv: int = 3):
    X_train = train_df.select(features).to_numpy()
    y_train = train_df.select(target).to_numpy()
    X_valid = valid_df.select(features).to_numpy()
    y_valid = valid_df.select(target).to_numpy()

    if grid_params is None:
        grid_params = {
            "gblinear": {
                "n_estimators": [50, 100],
                "learning_rate": [0.01, 0.05],
            },
            "gbtree": {
                "n_estimators": [50, 100],
                "max_depth": [3, 5, ],
                "learning_rate": [0.01, 0.05, ],
                "subsample": [0.8, 1, ],
                "max_leaves": [16, 32, ],
            },
        }

    # 创建xgboost回归器
    grid_searches = list()
    for seed in seeds:
        for booster_type, params_grid in grid_params.items():
            mdl = xgb.XGBRegressor(booster=booster_type,
                                   device=device,
                                   early_stopping_rounds=early_stopping_rounds, seed=seed, )
            param_grid = {**params_grid, "booster": [booster_type, ]}
            grid_searches.append(
                GridSearchCV(estimator=mdl,
                             param_grid=param_grid,
                             cv=cv,
                             scoring="neg_mean_squared_error",
                             # scoring=make_scorer(lambda y_true, y_pred: np.mean())
                             n_jobs=grid_jobs,
                             verbose=1,))

    # 创建DMatrix用于评估集
    eval_set = [(X_train, y_train), (X_valid, y_valid)]

    logger.info("Fitting...")

    # 模型训练
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        [grid.fit(X_train, y_train, eval_set=eval_set, verbose=False) for grid in grid_searches]
    best_models = [grid.best_estimator_ for grid in grid_searches]

    return best_models


def predict(models: list[xgb.XGBRegressor],
            data,
            features,
            target,
            index: Sequence[str] = ("date", "time", "asset"),
            eval: bool = False,
            data_name: str = "test", ):
    X_test = data.select(features).to_numpy()
    logger.info("Predicting...")
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        pred = {str(i): best_mdl.predict(X_test) for i, best_mdl in enumerate(models)}
    pred = pl.DataFrame(pred).mean_horizontal()
    pred = data.select(index).with_columns(pred=pred,
                                           true=data[target],
                                           ret=data["ret"])
    perf = None
    if eval:
        logger.info(f"Evaluating dataset.{data_name}: mse/rmse/r2/win_ratio/ic...")
        # 计算评估指标
        y_true = pred["true"].to_numpy()
        y_pred = pred["pred"].to_numpy()

        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        r2 = np.mean([best_model.score(X_test, data.select(target).to_numpy()) for best_model in models])
        # 计算胜率
        sign_correct = pred.select((pl.col("pred").sign() == pl.col("true").sign()).sum()).item(0, 0)
        win_ratio = sign_correct / len(y_true)
        # ic
        ic_pred = pred.drop_nans(subset=["pred", "true"]).drop_nulls(subset=["pred", "true"])
        ic = ic_pred.select(pl.corr("pred", "true", method="spearman")).item(0, 0)
        perf = pl.DataFrame({"metric": ["mse", "rmse", "r2", "win_ratio", "ic"],
                             data_name: [mse, rmse, r2, win_ratio, ic]})

    return pred, perf


def load_models(fname):
    fname = Path(fname)
    models = []
    for file_path in fname.glob("*.mdl"):
        mdl = xgb.XGBRegressor()
        mdl.load_model(fname=file_path)
        models.append(mdl)
    return models


def save_models(models: list[xgb.XGBRegressor], fname):
    fname = Path(fname)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        for i, mdl in enumerate(models):
            mdl.save_model(fname / f"xgb_{i + 1}.mdl")
