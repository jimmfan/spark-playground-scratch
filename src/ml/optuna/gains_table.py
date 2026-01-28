import numpy as np
import pandas as pd
import logging

from sklearn.base import clone
from sklearn.metrics import precision_recall_curve, auc
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
import xgboost as xgb
import optuna


def gains_table_pd(df, target_col, probability_col, amount_col, bin_size):

    df["score"] = (df["prob_score"] * 1000).round(0) 
    df["good"] = df[target_col].apply(lambda x:1 if x==0 else 0)

    df["bad"] = df[target_col]
    df["total"] = 1
    df["good_amount"] = df["good"] * df[amount_col] 
    df["bad_amount"] = df["bad"] * df[amount_col]

    total_count = df.shape[0]
    total_good = df["good"].sum()
    total_bad = df["bad"].sum()
    total_good_amt = df[df["good"] == 1][amount_col].sum()
    total_bad_amt = df[df["bad"] == 1][amount_col].sum()

    if bin_size > 1: 
        bins = np.arange(0, 1001, bin_size)
        
        df["score_bins"] = 0 
        
        if bin_size > 1:
            for i in range(len(bins) - 1): 
                df.loc[
                    df["score"].between(bins[i], bins[i + 1], "left"), "score_bins"
                ] = bins[i]
                score_col = "score_bins" 
        elif bin_size == 1: 
            score_col = "score"
        else: 
            print("bin_size must be greater or equal to 1")

    gains_df = (
        df.groupby(score_col)
        .agg(
            min_score=(probability_col, "min"),
            max_score=(probability_col, "max"),
            goods=("good", "sum"), 
            bads=("bad", "sum"), 
            totals=("total", "sum"), 
            good_amt=("good_amount", "sum"),
            bad_amt=("bad_amount", "sum"),
            total_amt=(amount_col, "sum"),
        )
        .sort_values(by=score_col, ascending=False)
    )

    gains_df["odds"] = gains_df.apply( lambda row: row["goods"] / row["bads"] if row["bads"] != 0 else None, axis=1, )
    gains_df["cum_goods"] = gains_df["goods"].cumsum()
    gains_df["cum_bads"] = gains_df["bads"].cumsum()
    gains_df["cum_totals"] = gains_df["totals"].cumsum()
    gains_df["cum_total_pct"] = gains_df["cum_totals"] / total_count 
    gains_df["cum_goods_amt"] = gains_df["good_amt"].cumsum()
    gains_df["cum_bads_amt"] = gains_df["bad_amt"].cumsum() 
    gains_df["cum_totals_amt"] = gains_df["total_amt"].cumsum()
    gains_df["cum_goods_to_bads_amt_ratio"] = gains_df.apply(
        lambda row: row["cum_goods_amt"] / row["cum_bads_amt"] if row["cum_bads_amt"] != 0 else None, axis=1, 
    )
    gains_df["cum_good_pct"] = gains_df["cum_goods"] / total_good
    gains_df["cum_bad_pct"] = gains_df["cum_bads"] / total_bad 
    gains_df["cum_good_amt_pct"] = gains_df["cum_goods_amt"] / total_good_amt
    gains_df["cum_bad_amt_pct"] = gains_df["cum_bads_amt"] / total_bad_amt

    return gains_df.reset_index()


def objective(
    trial,
    pipeline_template,
    train_df_balance,
    train_df,
    test_df,
    cut_off=0.005,
    scale_pos_weight=155,
):

    # 1. Ask Optuna for hyperparams
    params_dict = {
        "eta": trial.suggest_float("eta", 0.01, 0.1),
        "max_depth": trial.suggest_int("max_depth", 2, 9),
        "n_estimators": trial.suggest_int("n_estimators", 30, 200),
        "gamma": trial.suggest_float("gamma", 0.1, 1.0),
        "min_child_weight": trial.suggest_int("min_child_weight", 30, 200),
        # "scale_pos_weight": trial.suggest_int("scale_pos_weight", 1, 450),
        "subsample": trial.suggest_float("subsample", 0.7, 1.0),
    }

    # 2. clone a fresh pipeline for THIS trial
    model_pipe = clone(pipeline_template)

    # 3. inject hyperparams into the model step
    model_pipe.set_params(
        model__eta=params_dict["eta"],
        model__max_depth=params_dict["max_depth"],
        model__n_estimators=params_dict["n_estimators"],
        model__gamma=params_dict["gamma"],
        model__min_child_weight=params_dict["min_child_weight"],
        model__scale_pos_weight=scale_pos_weight,
        model__subsample=params_dict["subsample"],
    )

    # 4. fit using the balanced training data
    model_pipe.fit(data_bundle.X_train_bal, data_bundle.y_train_bal)

    y_preds_train = model_pipe.predict_proba(X_train)[:, 1]
    y_preds_test = model_pipe.predict_proba(X_test)[:, 1]
    pr_auc_train_bal = pr_auc_scorer(y_train_bal, y_preds_train_bal)

    pr_auc_train = pr_auc_scorer(y_train, y_preds_train)

    pr_auc_test = pr_auc_scorer(y_test, y_preds_test)
    trial.set_user_attr("pr_auc_train_bal", pr_auc_train_bal)
    trial.set_user_attr("pr_auc_train", pr_auc_train)
    trial.set_user_attr("pr_auc_test", pr_auc_test)
    logging.info(f"Trial {trial.number}: PR_AUC_TRAIN_BAL - <pr_auc_train_bal'")
    logging.info(f"Trial {trial.number}: PR_AUC_TRAIN - <pr_auc_train")
    logging.info(f"Trial {trial.number}': PR_AUC_TEST - (pr_auc_test)")
    train_test_drop_rate = abs(pr_auc_train - pr_auc_test) / pr_auc_train 
    logging.info(f"Trial {trial.number}: TRAIN_TEST_DROP_RATE - (train_test_drop_rate")


    test_df["prob_score"] = y_preds_test
    gains_table_test = gains_table_pd(test_df, "label", "prob_score", "amount_base", 1)
    gains_pct = gains_table_test[gains_table_test["cum_total_pct"] <= cut_off].tail(1)
    score = gains_pct["score"].values[0] 
    cum_total_pct = gains_pct["cum_total_pct"].values[0] 
    cum_bad_pct = gains_pct["cum_bad_pct"].values[0] 
    cum_bad_amt_pct = gains_pct["cum_bad_amt_pct"].values[0]
    cum_goods_amt = gains_pct["cum_goods_amt"].values[0] 
    cum_bads_amt = gains_pct["cum_bads_amt"].values[0]
    trial.set_user_attr("score", score) 
    trial.set_user_attr("cum_total_pct", cum_total_pct) 
    trial.set_user_attr("cum_bad_pct", cum_bad_pct)
    trial.set_user_attr("cum_bad_amt_pct", cum_bad_amt_pct)

    logging.info(f"Trial (trial.number): CUM_TOTAL_PCT - (cum_total_pct)")
    logging.info(f"Trial (trial.number): SCORE - (score)")
    logging.info(f"Trial (trial.number): CUM_BAD_PCT - (cum_bad_pct)")
    logging.info(f"Trial ftrial.number): CUM-BAD_AMT_PCT - (cum_bad_amt_pct)") 
    logging.info(f"Trial (trial.number): CUM_GOODS_AMT - (cum_goods_amt)") 
    logging.info(f"Trial (trial.number): CUM_BADS_AMT - (cum_bads_amt)")

    return train_test_drop_rate, cum_goods_amt, cum_bads_amt,

model_template = xgb.XGBClassifier(
    random_state=123, n-jobs=-1,
)
pipeline_template = Pipeline([
    ("prep", preprocessor), ("model", model_template)
])
study = optuna.create_study(directions=["minimize", "minimize", "maximize"])
all_trials_info = []
for cut_off in [0.05, 0.01]: 
    func = lambda trial: objective(
        trial, pipeline_template, train_df_balance, train_df, test_df, cut_off,
    )
    study.optimize(func, n_trials=50)

