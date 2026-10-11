"""Train LightGBM with given hyperparameters and evaluate it as in the paper (Table 6, Figs. 18, 22 and 24).

    python src/train.py --data data/model_table.csv.gz --params paper --out results/run
    python src/train.py --data data/model_table.csv.gz --params results/run/best_params.json --out results/run_tuned
"""
import argparse
import json
import os
import time
import warnings

import lightgbm as lgb
import matplotlib
import numpy as np
from sklearn.metrics import (accuracy_score, classification_report, confusion_matrix, log_loss, precision_recall_fscore_support,
                             roc_auc_score, roc_curve)
from sklearn.preprocessing import label_binarize

from common import CLASSES, load_split
from config import PAPER_PARAMS, SEED

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*eval_set.*")

matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

plt.rcParams.update({'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False, 'legend.frameon': False})
COL = ['#1f3fd1', '#f26a1b', '#1b7f3b', '#b3121a']


def figures(out, ev, y_te, proba, cm, model, feat):
    # learning curves (Fig. 18)
    fig, ax = plt.subplots(1, 2, figsize=(7.5, 2.8))
    for a, m in zip(ax, ['multi_logloss', 'multi_error']):
        a.plot(ev['training'][m], color='#555555', label='training'); a.plot(ev['valid_1'][m], color=COL[0], label='test')
        a.set_xlabel('Iteration'); a.set_ylabel(m); a.legend()
    fig.tight_layout(); fig.savefig(f'{out}/learning_curves.png', dpi=200); plt.close(fig)
    # ROC curves (Fig. 22)
    yb = label_binarize(y_te, classes=range(4))
    fig, a = plt.subplots(figsize=(4.2, 3.8))
    for k in range(4):
        fpr, tpr, _ = roc_curve(yb[:, k], proba[:, k])
        a.plot(fpr, tpr, color=COL[k], label=f'Severity {k + 1} (AUC {roc_auc_score(yb[:, k], proba[:, k]):.2f})')
    a.plot([0, 1], [0, 1], ls=':', color='#999999'); a.set_xlabel('False positive rate'); a.set_ylabel('True positive rate'); a.legend(loc='lower right')
    fig.tight_layout(); fig.savefig(f'{out}/roc_curves.png', dpi=200); plt.close(fig)
    # confusion matrix, row-normalized
    cmn = cm / cm.sum(axis=1, keepdims=True)
    fig, a = plt.subplots(figsize=(4.0, 3.6))
    a.imshow(cmn, cmap='Blues', vmin=0, vmax=1)
    for i in range(4):
        for j in range(4):
            a.text(j, i, f'{cmn[i, j]:.2f}\n({cm[i, j]:,})', ha='center', va='center', fontsize=7.5, color='white' if cmn[i, j] > 0.55 else '#1a1a1a')
    a.set_xticks(range(4), [f'{c}' for c in CLASSES]); a.set_yticks(range(4), [f'{c}' for c in CLASSES])
    a.set_xlabel('Predicted severity'); a.set_ylabel('Actual severity')
    fig.tight_layout(); fig.savefig(f'{out}/confusion_matrix.png', dpi=200); plt.close(fig)
    # feature importance (gain), top 20
    gain = model.booster_.feature_importance('gain'); idx = np.argsort(gain)[::-1][:20]
    fig, a = plt.subplots(figsize=(5.5, 4.6))
    a.barh(range(len(idx)), gain[idx] / gain.sum() * 100, color=COL[0]); a.set_yticks(range(len(idx)), [feat[i] for i in idx], fontsize=7.5)
    a.invert_yaxis(); a.set_xlabel('Share of total gain (%)')
    fig.tight_layout(); fig.savefig(f'{out}/feature_importance.png', dpi=200); plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--data', default='data/model_table.csv.gz')
    ap.add_argument('--params', default='paper', help="'paper' (Table 5) or a best_params.json written by tune.py")
    ap.add_argument('--out', default='results/run')
    ap.add_argument('--save-model', action='store_true')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    params = dict(PAPER_PARAMS) if a.params == 'paper' else json.load(open(a.params))['best_params']

    X_tr, X_te, y_tr, y_te = load_split(a.data)
    model = lgb.LGBMClassifier(objective='multiclass', random_state=SEED, verbose=-1, **params)
    t0 = time.time()
    model.fit(X_tr, y_tr, eval_set=[(X_tr, y_tr), (X_te, y_te)], eval_metric=['multi_logloss', 'multi_error'])
    t_train = time.time() - t0
    t0 = time.time(); proba = model.predict_proba(X_te); pred = proba.argmax(axis=1); t_test = time.time() - t0
    pred_tr = model.predict(X_tr)

    yb = label_binarize(y_te, classes=range(4))
    p, r, f, _ = precision_recall_fscore_support(y_te, pred, average=None, zero_division=0)
    cm = confusion_matrix(y_te, pred)
    res = dict(
        params=params, n_train=int(len(y_tr)), n_test=int(len(y_te)), n_features=int(X_tr.shape[1]),
        accuracy_train=accuracy_score(y_tr, pred_tr), accuracy_test=accuracy_score(y_te, pred),
        precision_macro=float(np.mean(p)), recall_macro=float(np.mean(r)), f1_macro=float(np.mean(f)),
        precision_weighted=precision_recall_fscore_support(y_te, pred, average='weighted', zero_division=0)[0],
        recall_weighted=precision_recall_fscore_support(y_te, pred, average='weighted', zero_division=0)[1],
        f1_weighted=precision_recall_fscore_support(y_te, pred, average='weighted', zero_division=0)[2],
        roc_auc_macro=roc_auc_score(yb, proba, average='macro'), roc_auc_micro=roc_auc_score(yb, proba, average='micro'),
        log_loss_test=log_loss(y_te, proba), trees=int(model.booster_.num_trees() // 4),
        per_class={str(c): dict(precision=float(p[k]), recall=float(r[k]), f1=float(f[k]), auc=float(roc_auc_score(yb[:, k], proba[:, k])),
                                support=int((y_te == k).sum())) for k, c in enumerate(CLASSES)},
        confusion_matrix=cm.tolist(), seconds_train=round(t_train, 2), seconds_test=round(t_test, 2))
    res = {k: (float(v) if isinstance(v, np.floating) else v) for k, v in res.items()}
    json.dump(res, open(f'{a.out}/metrics.json', 'w'), indent=1)
    open(f'{a.out}/classification_report.txt', 'w').write(classification_report(y_te, pred, target_names=[f'Severity {c}' for c in CLASSES], digits=3))
    figures(a.out, model.evals_result_, y_te.values, proba, cm, model, list(X_tr.columns))
    if a.save_model: model.booster_.save_model(f'{a.out}/model.txt')
    print(f"accuracy train {res['accuracy_train']:.3f} test {res['accuracy_test']:.3f} | ROC-AUC macro {res['roc_auc_macro']:.3f} micro {res['roc_auc_micro']:.3f} "
          f"| F1 macro {res['f1_macro']:.3f} weighted {res['f1_weighted']:.3f} | log loss {res['log_loss_test']:.3f} | train {t_train:.1f} s, test {t_test:.2f} s")


if __name__ == '__main__':
    main()
