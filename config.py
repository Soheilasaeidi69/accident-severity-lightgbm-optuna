"""Settings taken from the paper (Rezashoar, Kashi and Saeidi, 2024).

Table and figure numbers refer to the published article:
https://doi.org/10.1007/s41062-024-01626-y
"""

# Study period: February 2016 to December 2020.
PERIOD_START = "2016-02-01"
PERIOD_END = "2021-01-01"          # exclusive

# Records drawn per severity class for modelling (Methodology section).
CLASS_SIZES = {1: 14_800, 2: 248_000, 3: 148_000, 4: 48_000}

TEST_SIZE = 0.33                   # 67 % training, 33 % testing
SEED = 1

# Table 5: hyperparameter values chosen by Optuna (best trial, number 43).
PAPER_PARAMS = dict(
    n_estimators=400,
    learning_rate=0.272545931,
    num_leaves=2780,
    max_depth=4,
    min_data_in_leaf=800,
    lambda_l1=5,
    lambda_l2=25,
    min_gain_to_split=0.60158,
    bagging_fraction=0.8,
    bagging_freq=1,
    feature_fraction=0.9,
)

# Table 4 and Fig. 25: Optuna settings.
N_TRIALS = 50
N_FOLDS = 10
EARLY_STOPPING_ROUNDS = 100


def suggest_params(trial):
    """Search space of Fig. 25 (11 hyperparameters)."""
    return {
        "n_estimators": trial.suggest_categorical("n_estimators", [400]),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3),
        "num_leaves": trial.suggest_int("num_leaves", 20, 3000, step=20),
        "max_depth": trial.suggest_int("max_depth", 3, 12),
        "min_data_in_leaf": trial.suggest_int("min_data_in_leaf", 200, 10000, step=100),
        "lambda_l1": trial.suggest_int("lambda_l1", 0, 100, step=5),
        "lambda_l2": trial.suggest_int("lambda_l2", 0, 100, step=5),
        "min_gain_to_split": trial.suggest_float("min_gain_to_split", 0, 15),
        # The paper writes the range as 0.2 to 0.95 in steps of 0.1; the last
        # value on that grid is 0.9, so 0.9 is written here.
        "bagging_fraction": trial.suggest_float("bagging_fraction", 0.2, 0.9, step=0.1),
        "bagging_freq": trial.suggest_categorical("bagging_freq", [1]),
        "feature_fraction": trial.suggest_float("feature_fraction", 0.2, 0.9, step=0.1),
    }
