# Jobs Overview

This directory contains all scheduled or batch jobs used for feature generation, 
model development, and evaluation.

## jobs/features/
Jobs that write feature tables to the data lake or warehouse.

## jobs/population/
Jobs that assemble the model population or OOT evaluation populations.

## jobs/training/
Jobs that train final models using the current training dataset.

## jobs/tuning/
Jobs that run hyperparameter optimization (Optuna) for models.

## jobs/evaluation/
Jobs that evaluate trained models against OOT datasets, drift metrics, or 
model monitoring reports.
