project/
  pyproject.toml
  README.md
  .gitignore

  # optional: env / tooling helpers
  .env.example
  uv.lock

  scripts/
    run_all_tests.sh
    format_check.sh
    lint_check.sh

  src/
    project/
      __init__.py

      # ======================
      # 1. CONFIG (YAML only)
      # ======================
      config/
        __init__.py

        data_sources.yaml            # snowflake db/schema, s3 buckets, stages, etc.

        population/
          dev_population.yaml        # dev window, filters, min history
          oot_population.yaml        # OOT window, filters
          scoring_population.yaml    # prod / real-time scoring population rules (if needed)

        features/
          deposit_features_daily.yaml        # which feature blocks to run, lookback windows
          transaction_features_daily.yaml
          third_party_features_monthly.yaml

        modeling/
          model.yaml            # model-level configs: objective, metrics, seeds
          common_model_defaults.yaml

        tuning/
          xgb.yaml              # search space + early stopping + cutoffs
          lgbm.yaml
          generic_xgb_small_data.yaml

        evaluation/
          oot.yaml              # which OOT slices, metrics, thresholds
          monitoring_thresholds.yaml         # PSI / drift thresholds, alert configs

      # ======================
      # 2. LIBRARY CODE
      #    (importable, no scheduling)
      # ======================

      data_sources/
        __init__.py
        source1.py              
        
      features/
        __init__.py

        deposit/
          build_deposit_features.py  # pure functions: population_df -> features_df
          deposit_feature_blocks.py  # reusable column expressions / blocks

        transactions/
          build_transaction_features.py
          transaction_feature_blocks.py

        third_party/
          build_vendor_features.py

      population/
        __init__.py
        build_deposit_population.py  # base dev/train population
        build_oot_population.py      # OOT populations
        business_day_mapping.py      # prev-business-day mapping utilities

      labels/
        __init__.py
        build_deposit_labels.py      # label construction, windows, maturity

      modeling/
        __init__.py
        build_preprocessor.py        # ColumnTransformer, imputers, OHE, passthrough
        build_xgb_model.py           # XGBClassifier wrapper
        build_pipeline.py            # sklearn Pipeline (preprocessor + model)
        metrics.py                   # gains table, slice_top_cutoff_metrics, etc.
        calibration.py               # CalibratedClassifierCV helpers
        onnx_export.py               # convert trained model -> ONNX

      tuning/
        __init__.py
        optuna_objectives.py         # objective functions (uses config/tuning/*.yaml)
        search_spaces.py             # helpers to map YAML search space -> trial.suggest_*
        study_utils.py               # create_study, callbacks, logging

      evaluation/
        __init__.py
        eval_oot_utils.py            # functions to evaluate models on OOT sets
        drift_metrics.py             # PSI, feature drift, etc.
        report_builders.py           # assemble evaluation/monitoring dataframes

      utils/
        __init__.py
        logging_utils.py
        date_utils.py
        config_loader.py             # generic YAML loader (by domain/name)
        paths.py

      # ======================
      # 3. JOBS (entrypoints)
      #    thin scripts that glue config + library code
      # ======================
      jobs/
        __init__.py

        features/
          write_deposit_features_daily.py
          write_transaction_features_daily.py
          write_third_party_features_monthly.py

        population/
          write_deposit_population_daily.py
          write_oot_population_snapshot.py

        training/
          train_model.py          # main offline training job
          train_shadow_model.py   # shadow vs prod training

        tuning/
          run_xgb_tuning.py
          run_lgbm_tuning.py
          run_generic_xgb_small_data_tuning.py

        evaluation/
          eval_oot.py             # OOT test run
          eval_shadow_vs_prod.py  # compare models
          generate_monitoring_report.py        # drift/PSI + performance report

  tests/
    unit/
      test_features_deposit.py
      test_features_transactions.py
      test_population_builders.py
      test_modeling_pipeline.py
      test_tuning_search_spaces.py
      test_evaluation_metrics.py

    integration/
      test_job_write_deposit_features_daily.py
      test_job_train_model.py
      test_job_eval_oot.py
