"""Shared helpers: load the modelling table and split it as in the paper (67 % / 33 %)."""
import pandas as pd
from sklearn.model_selection import train_test_split

from config import SEED, TEST_SIZE

CLASSES = [1, 2, 3, 4]


def load_split(path):
    df = pd.read_csv(path)
    y = df.pop('Severity').astype(int) - 1          # LightGBM expects classes 0..3
    X_tr, X_te, y_tr, y_te = train_test_split(df, y, test_size=TEST_SIZE, stratify=y, random_state=SEED)
    return X_tr, X_te, y_tr, y_te
