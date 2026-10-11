"""Hyperparameter search with Optuna (Table 4 and Fig. 25 of the paper).

Each trial trains LightGBM on stratified K folds of the training set and returns the mean
multi_logloss on the held-out folds; Optuna minimizes it and prunes poor trials.

    python src/tune.py --data data/model_table.csv.gz --out results/run --trials 50 --folds 10
"""
import argparse
import json
import os
import time
import warnings

import lightgbm as lgb
import numpy as np
import optuna
from optuna_integration import LightGBMPruningCallback
from sklearn.metrics import log_loss
from sklearn.model_selection import StratifiedKFold

from common import load_split
from config import EARLY_STOPPING_ROUNDS, N_FOLDS, N_TRIALS, SEED, suggest_params

warnings.filterwarnings('ignore')


def objective(trial, X, y, folds):
    params = suggest_params(trial)
    cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=SEED)
    scores = np.empty(folds)
    for k, (tr, va) in enumerate(cv.split(X, y)):
        model = lgb.LGBMClassifier(objective='multiclass', random_state=SEED, verbose=-1, **params)
        model.fit(X[tr], y[tr], eval_set=[(X[va], y[va])], eval_metric='multi_logloss',
                  callbacks=[lgb.early_stopping(EARLY_STOPPING_ROUNDS, verbose=False),
                             LightGBMPruningCallback(trial, 'multi_logloss')])
        scores[k] = log_loss(y[va], model.predict_proba(X[va]))
    return float(scores.mean())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--data', default='data/model_table.csv.gz')
    ap.add_argument('--out', default='results/run')
    ap.add_argument('--trials', type=int, default=N_TRIALS)
    ap.add_argument('--folds', type=int, default=N_FOLDS)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    X_tr, _, y_tr, _ = load_split(a.data)
    X, y = X_tr.values, y_tr.values
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study = optuna.create_study(direction='minimize', study_name='LGBM Classifier',
                                sampler=optuna.samplers.TPESampler(seed=SEED))
    t0 = time.time()
    study.optimize(lambda t: objective(t, X, y, a.folds), n_trials=a.trials,
                   callbacks=[lambda s, t: print(f'trial {t.number:3d}  {t.state.name:8s}  value {t.value if t.value is not None else float("nan"):.4f}  best {s.best_value:.4f}', flush=True)])
    elapsed = time.time() - t0

    best = dict(study.best_params)
    try:
        imp = {k: round(float(v), 4) for k, v in optuna.importance.get_param_importances(study).items()}
    except Exception:                                    # too few completed trials
        imp = {}
    json.dump(dict(best_params=best, best_value=study.best_value, best_trial=study.best_trial.number,
                   n_trials=a.trials, n_folds=a.folds, seconds=round(elapsed, 1), param_importance=imp),
              open(os.path.join(a.out, 'best_params.json'), 'w'), indent=1)
    study.trials_dataframe().to_csv(os.path.join(a.out, 'trials.csv'), index=False)
    print(f'best multi_logloss {study.best_value:.4f} (trial {study.best_trial.number}) in {elapsed / 60:.1f} min')


if __name__ == '__main__':
    main()
