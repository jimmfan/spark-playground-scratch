import numpy as np
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import roc_auc_score, average_precision_score

def _order_with_tiebreak(score, tie_break=None):
    # Sort by score desc, then tie_break desc (if provided), deterministic
    score = np.asarray(score, dtype=float)
    if tie_break is None:
        tie_break = np.zeros_like(score)
    else:
        tie_break = np.asarray(tie_break, dtype=float)
    return np.lexsort((-tie_break, -score))

def capture_at_frac(y_true, y_score, frac=0.01, tie_break=None):
    n = len(y_score)
    k = max(1, int(np.floor(frac * n)))
    order = _order_with_tiebreak(y_score, tie_break)
    idx = order[:k]
    return float((y_true[idx] == 1).sum())

def cv_head_metric_with_stability(
    model, X, y, dates, fracs=(0.01,), n_splits=5, tie_breaker=None
):
    # Time-aware splits for risk
    order = np.argsort(np.asarray(dates))
    X, y = X.iloc[order], y.iloc[order]
    if tie_breaker is not None:
        tie_breaker = np.asarray(tie_breaker)[order]

    tscv = TimeSeriesSplit(n_splits=n_splits)
    caps_by_frac = {f: [] for f in fracs}
    aucs, aucprs = [], []

    for tr, va in tscv.split(X):
        Xtr, Xva = X.iloc[tr], X.iloc[va]
        ytr, yva = y.iloc[tr], y.iloc[va]
        model.fit(
            Xtr, ytr,
            eval_set=[(Xva, yva)],
            eval_metric="aucpr",
            early_stopping_rounds=100,
            verbose=False,
        )
        p = model.predict_proba(Xva)[:, 1]
        tb = None if tie_breaker is None else tie_breaker[va]

        for f in fracs:
            caps_by_frac[f].append(capture_at_frac(yva.values, p, f, tb))
        aucs.append(roc_auc_score(yva, p))
        aucprs.append(average_precision_score(yva, p))

    # mean & std across folds
    cap_means = {f: float(np.mean(v)) for f, v in caps_by_frac.items()}
    cap_stds  = {f: float(np.std(v))  for f, v in caps_by_frac.items()}
    return cap_means, cap_stds, float(np.mean(aucs)), float(np.mean(aucprs))

def objective(trial):
    from xgboost import XGBClassifier
    params = {
        "tree_method": "hist",
        "n_estimators": trial.suggest_int("n_estimators", 400, 1500),
        "max_depth": trial.suggest_int("max_depth", 3, 8),
        "learning_rate": trial.suggest_float("learning_rate", 1e-3, 0.3, log=True),
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
        "min_child_weight": trial.suggest_float("min_child_weight", 1e-2, 10, log=True),
        "gamma": trial.suggest_float("gamma", 1e-3, 10, log=True),
        "reg_lambda": trial.suggest_float("reg_lambda", 1e-3, 100, log=True),
        "reg_alpha": trial.suggest_float("reg_alpha", 1e-4, 10, log=True),
        "random_state": 42,
    }
    model = XGBClassifier(**params)

    # Simple: optimize across 1%..5% (average), still penalize instability
    fracs = (0.01, 0.02, 0.03, 0.05)
    cap_means, cap_stds, auc_mean, aucpr_mean = cv_head_metric_with_stability(
        model, X_train, y_train, dates=date_col, fracs=fracs, n_splits=5,
        tie_breaker=(X_train["amount_base"].values if "amount_base" in X_train.columns else None)
    )

    # Scalarize: mean of means minus lambda * mean of stds (keeps it simple)
    cap_mean_avg = float(np.mean(list(cap_means.values())))
    cap_std_avg  = float(np.mean(list(cap_stds.values())))
    lam = trial.suggest_float("stability_penalty", 0.0, 1.0)
    obj = cap_mean_avg - lam * cap_std_avg

    # Log useful attrs
    trial.set_user_attr("cap_means", cap_means)
    trial.set_user_attr("cap_stds", cap_stds)
    trial.set_user_attr("auc_mean", auc_mean)
    trial.set_user_attr("aucpr_mean", aucpr_mean)
    return obj  # study.direction = "maximize"
