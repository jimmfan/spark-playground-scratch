

def objective(
    trial, optuna_params, model_name, X_train_bal,
    y_train_bal, X_train, y_train, X_test, y_test, test_df, 
) :
    classifier = getattr(
        importlib.import_module(optuna_params[model_name].classifier_module), 
        optuna_params[model_namel].classifier_name
    )

    params_dict = {
        "eta": trial.suggest_float("eta", 0.01, 0.1),
        "max_depth": trial.suggest_int("max_depth", 2,9), 
        "n_estimators": trial.suggest_int("n-estimators", 30,200), 
        "gamma" : trial.suggest_float("gamma", 0.1, 1), 
        "min_child_weight": trial.suggest_int("min_child_weight", 30, 200), 
        "scale_pos_weight": trial.suggest_int("scale-pos_weight", 1, 450), 
        "subsample" : trial.suggest_float('subsample', 0.7, 1)
    }

    model = classifier (**params_dict, random_state=optuna_params.seed, n_jobs=-1)


    # .. rest of code
