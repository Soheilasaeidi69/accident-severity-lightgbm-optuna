"""Write docs/index.html: a one-page results dashboard (paper results and the demo run).

    python src/make_dashboard.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = lambda *p: json.load(open(os.path.join(ROOT, 'results', *p)))

paper = R('paper_results.json')
demo = R('demo', 'paper_params', 'metrics.json')
freq = R('demo', 'location_vars', 'metrics.json')
tuned = R('demo', 'tuned', 'metrics.json') if os.path.exists(os.path.join(ROOT, 'results', 'demo', 'tuned', 'metrics.json')) else None
tuning = R('demo', 'tuning', 'best_params.json') if os.path.exists(os.path.join(ROOT, 'results', 'demo', 'tuning', 'best_params.json')) else None
prep = R('demo', 'model_table_info.json')

data = dict(paper=paper, demo=demo, freq=freq, tuned=tuned, tuning=tuning, prep=prep)

HTML = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="LightGBM-Optuna classification of US road accident severity: results reported in the paper and a reproducible run on a public sample.">
<title>Accident Severity LightGBM-Optuna</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap">
<style>
:root{
  --bg:#f5f5f2; --surface:#ffffff; --ink:#16181d; --muted:#5b616b; --rule:#dcdde0; --soft:#eef0f2;
  --head:#22262e; --head-ink:#ffffff; --accent:#e8590c;
  --s-paper:#3b5bdb; --s-demo:#e8590c; --s-freq:#1098ad;
  --body:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif; --mono:"IBM Plex Mono",ui-monospace,Menlo,Consolas,monospace;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#101216; --surface:#17191f; --ink:#e9ebef; --muted:#a2a8b3; --rule:#2b2f37; --soft:#1f232a;
  --head:#0b0d10; --head-ink:#ffffff; --accent:#e8590c;
  --s-paper:#4c6ef5; --s-demo:#e8590c; --s-freq:#1098ad; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#101216; --surface:#17191f; --ink:#e9ebef; --muted:#a2a8b3; --rule:#2b2f37; --soft:#1f232a;
  --head:#0b0d10; --head-ink:#ffffff; --accent:#e8590c;
  --s-paper:#4c6ef5; --s-demo:#e8590c; --s-freq:#1098ad; color-scheme:dark}
*{box-sizing:border-box}
html{color-scheme:light}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--body);font-size:15px;line-height:1.55}
.wrap{max-width:1060px;margin:0 auto;padding:20px 16px 56px;display:flex;flex-direction:column;gap:20px}
h1,h2,h3{margin:0;text-wrap:balance}
h2{font-size:1.3rem;font-weight:700}
h3{font-size:1rem;font-weight:600}
p{margin:0;max-width:70ch}
a{color:var(--s-paper)}
.muted{color:var(--muted)}
.num{font-family:var(--mono);font-variant-numeric:tabular-nums}
.eyebrow{font-size:.72rem;letter-spacing:.12em;text-transform:uppercase;font-weight:600;color:var(--muted)}
header.top{background:var(--head);color:var(--head-ink);border-radius:10px;padding:22px 22px 20px;display:flex;flex-direction:column;gap:10px;border-left:8px solid var(--accent)}
header.top .eyebrow{color:#c7ccd4}
header.top h1{font-size:clamp(1.35rem,3.2vw,2rem);font-weight:700;line-height:1.2}
header.top p{color:#dfe3e8}
header.top a{color:#ffd8a8}
.tags{display:flex;gap:8px;flex-wrap:wrap}
.tag{font-size:.75rem;border:1px solid rgba(255,255,255,.4);border-radius:4px;padding:2px 8px;font-weight:500}
.panel{background:var(--surface);border:1px solid var(--rule);border-radius:10px;padding:18px;display:flex;flex-direction:column;gap:14px;min-width:0}
.steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px;counter-reset:s}
.step{border:1px solid var(--rule);border-radius:8px;padding:12px;background:var(--bg);display:flex;flex-direction:column;gap:6px;min-width:0}
.step h3::before{counter-increment:s;content:counter(s);display:inline-grid;place-items:center;width:22px;height:22px;border-radius:50%;background:var(--accent);color:#fff;font-size:.78rem;margin-right:8px;vertical-align:1px}
.step p{font-size:.88rem;color:var(--muted)}
.legend{display:flex;gap:16px;flex-wrap:wrap;font-size:.84rem;color:var(--muted)}
.legend span{display:inline-flex;align-items:center;gap:6px}
.sw{width:12px;height:12px;border-radius:2px;display:inline-block}
.chart{width:100%;overflow-x:auto}
svg text{fill:var(--muted);font-family:var(--body);font-size:11px}
svg .ink{fill:var(--ink)}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(420px,100%),1fr));gap:18px}
.tip{position:fixed;pointer-events:none;background:var(--ink);color:var(--bg);padding:6px 9px;border-radius:6px;font-size:.8rem;max-width:260px;z-index:10;line-height:1.35}
.tablewrap{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:.87rem}
th,td{padding:7px 9px;border-bottom:1px solid var(--rule);text-align:left;vertical-align:top}
th{font-weight:600;color:var(--muted);font-size:.8rem}
td.r,th.r{text-align:right}
.cm{display:grid;grid-template-columns:auto repeat(4,minmax(56px,1fr));gap:3px;font-size:.82rem;max-width:460px}
.cm div{padding:8px 4px;text-align:center;border-radius:4px}
.cm .h{color:var(--muted);font-weight:600;background:none}
ul.clean{margin:0;padding-left:18px;display:flex;flex-direction:column;gap:6px}
ul.clean li{max-width:75ch}
pre{margin:0;background:var(--soft);border:1px solid var(--rule);border-radius:8px;padding:12px;overflow-x:auto;font-family:var(--mono);font-size:.82rem;line-height:1.5}
.note{border-left:3px solid var(--accent);padding:8px 12px;background:var(--soft);border-radius:0 6px 6px 0;font-size:.9rem}
footer{font-size:.82rem;color:var(--muted);text-align:center}
</style>
</head>
<body>
<div class="wrap">

<header class="top">
  <span class="eyebrow">Road accident severity · machine learning</span>
  <h1>A hybrid LightGBM-Optuna algorithm for road accident severity classification, United States 2016–2020</h1>
  <p>Soheil Rezashoar, Ehsan Kashi and Soheila Saeidi. <i>Innovative Infrastructure Solutions</i> 9, 319 (2024). <a href="https://doi.org/10.1007/s41062-024-01626-y">doi.org/10.1007/s41062-024-01626-y</a></p>
  <div class="tags"><span class="tag">US-Accidents data</span><span class="tag">4 severity classes</span><span class="tag">LightGBM</span><span class="tag">Optuna, 50 trials</span><span class="tag">Stratified 10-fold CV</span></div>
</header>

<section class="panel" aria-labelledby="h-method">
  <h2 id="h-method">Method</h2>
  <p class="muted">The paper predicts the severity of a road accident (1 = least, 4 = most impact on traffic) from location, time, weather and road features. This repository implements the same steps.</p>
  <div class="steps">
    <div class="step"><h3>Data</h3><p>US-Accidents (Moosavi et al.), February 2016 to December 2020, 49 states.</p></div>
    <div class="step"><h3>Preprocessing</h3><p>Time variables, missing values by weather station and month, grouped weather and wind, Box-Cox, frequency and one-hot encoding.</p></div>
    <div class="step"><h3>Sampling</h3><p>14,800 / 248,000 / 148,000 / 48,000 records of severity 1 to 4; 67 % training, 33 % testing.</p></div>
    <div class="step"><h3>Optuna</h3><p>11 hyperparameters, 50 trials, stratified 10-fold CV, multi-class log loss, pruning.</p></div>
    <div class="step"><h3>LightGBM</h3><p>400 trees with the best hyperparameters; evaluated with accuracy, precision, recall, F1 and ROC-AUC.</p></div>
  </div>
</section>

<section class="panel" aria-labelledby="h-head">
  <h2 id="h-head">Headline results</h2>
  <p class="muted">Paper values are from its Table 6. The demo runs this code on a public 500,000-record sample of a later release of the data (see "Data and limits"), so the numbers are a check of the method, not a copy of the paper.</p>
  <div class="legend" id="leg1"></div>
  <div class="chart" id="c-head"></div>
</section>

<section class="panel" aria-labelledby="h-class">
  <h2 id="h-class">Results by severity class</h2>
  <p class="muted">Classes 2 and 3 are predicted well; the model misses most of the severity 4 accidents (recall about 0.25 in the paper), the main weakness the paper also reports.</p>
  <div class="legend" id="leg2"></div>
  <div class="grid2" id="c-class"></div>
</section>

<section class="panel" aria-labelledby="h-cm">
  <h2 id="h-cm">Confusion matrix of the demo run</h2>
  <p class="muted">Share of each actual class (rows) predicted as each class (columns); counts in parentheses. Paper's hyperparameters, location variables excluded.</p>
  <div class="cm" id="cm"></div>
</section>

<section class="panel" aria-labelledby="h-hp">
  <h2 id="h-hp">Hyperparameters</h2>
  <p class="muted">Search ranges from the paper's code (Fig. 25), the optimum it reports (Table 5), and the optimum of the demo search.</p>
  <div class="tablewrap"><table id="t-hp"></table></div>
  <p class="note" id="tune-note"></p>
  <h3>Which hyperparameters matter most</h3>
  <div class="legend" id="leg3"></div>
  <div class="chart" id="c-imp"></div>
</section>

<section class="panel" aria-labelledby="h-data">
  <h2 id="h-data">Data and limits of the demo</h2>
  <ul class="clean" id="limits"></ul>
  <div class="note">To reproduce the paper exactly, use the December 2020 release of US-Accidents (about 4.2 million records) with the class sizes above. It is not included here because of its size and licence.</div>
</section>

<section class="panel" aria-labelledby="h-run">
  <h2 id="h-run">Run it</h2>
<pre>pip install -r requirements.txt
python src/preprocess.py --input data/US_Accidents_Dec20.csv --output data/model_table.csv.gz
python src/tune.py  --data data/model_table.csv.gz --out results/run --trials 50 --folds 10
python src/train.py --data data/model_table.csv.gz --params paper --out results/run_paper
python src/train.py --data data/model_table.csv.gz --params results/run/best_params.json --out results/run_tuned</pre>
</section>

<footer>Code and dashboard for the article above. Data: US-Accidents by Sobhan Moosavi et al., CC BY-NC-SA 4.0.</footer>
</div>
<div class="tip" id="tip" hidden></div>
<script>
const D = __DATA__;
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const tip = document.getElementById('tip');
function showTip(e, html){ tip.innerHTML = html; tip.hidden = false; const x = Math.min(e.clientX + 12, innerWidth - 270); tip.style.left = x + 'px'; tip.style.top = (e.clientY + 12) + 'px'; }
function hideTip(){ tip.hidden = true; }
const S = [
  {key:'paper', name:'Paper (Table 6)', col:'--s-paper'},
  {key:'demo', name:'Demo, location variables excluded', col:'--s-demo'},
  {key:'freq', name:'Demo, location variables kept', col:'--s-freq'}];
function legend(id, series){ document.getElementById(id).innerHTML = series.map(s => `<span><i class="sw" style="background:var(${s.col})"></i>${s.name}</span>`).join(''); }
const NS = 'http://www.w3.org/2000/svg';
function el(t, a, parent){ const e = document.createElementNS(NS, t); for (const k in a) e.setAttribute(k, a[k]); if (parent) parent.appendChild(e); return e; }

// headline grouped bars
const P = D.paper.table6;
const M = [['Accuracy (test)', P.accuracy_test, D.demo.accuracy_test, D.freq.accuracy_test],
           ['ROC-AUC, micro', P.roc_auc_micro, D.demo.roc_auc_micro, D.freq.roc_auc_micro],
           ['ROC-AUC, macro', P.roc_auc_macro, D.demo.roc_auc_macro, D.freq.roc_auc_macro],
           ['Precision, weighted', P.precision_weighted, D.demo.precision_weighted, D.freq.precision_weighted],
           ['Recall, weighted', P.recall_weighted, D.demo.recall_weighted, D.freq.recall_weighted],
           ['F1, weighted', P.f1_weighted, D.demo.f1_weighted, D.freq.f1_weighted],
           ['F1, macro', P.f1_macro, D.demo.f1_macro, D.freq.f1_macro]];
function grouped(host, rows, series, opts){
  const w = Math.max(host.clientWidth, 260), lab = opts.lab || 150, bh = 9, gap = 2, gh = series.length * (bh + gap) + 12, mx = opts.max || 1;
  const h = rows.length * gh + 26, x0 = lab, x1 = w - 40, sx = v => x0 + (x1 - x0) * v / mx;
  const svg = el('svg', {width:w, height:h, viewBox:`0 0 ${w} ${h}`, role:'img', 'aria-label': opts.aria});
  const step = mx / 4; for (let t = 0; t <= mx + 1e-9; t += step){ el('line', {x1:sx(t), x2:sx(t), y1:0, y2:h - 20, stroke:css('--rule'), 'stroke-width':1}, svg); const tx = el('text', {x:sx(t), y:h - 6, 'text-anchor':'middle'}, svg); tx.textContent = t.toFixed(2); }
  rows.forEach((r, i) => {
    const y = i * gh + 4; const tl = el('text', {x:x0 - 8, y:y + gh / 2, 'text-anchor':'end', 'dominant-baseline':'middle', class:'ink'}, svg); tl.textContent = r[0];
    series.forEach((s, k) => {
      const v = r[k + 1]; if (v == null) return; const yy = y + k * (bh + gap);
      const rect = el('rect', {x:x0, y:yy, width:Math.max(1, sx(v) - x0 - 2), height:bh, rx:2, fill:`var(${s.col})`}, svg);
      const vt = el('text', {x:sx(v) + 4, y:yy + bh / 2 + 0.5, 'dominant-baseline':'middle', class:'ink', 'font-size':'10'}, svg); vt.textContent = v.toFixed(2);
      const hit = el('rect', {x:x0, y:yy - 1, width:x1 - x0, height:bh + 2, fill:'transparent'}, svg);
      hit.addEventListener('mousemove', e => showTip(e, `<b>${r[0]}</b><br>${s.name}: ${v.toFixed(3)}`)); hit.addEventListener('mouseleave', hideTip);
    });
  });
  host.innerHTML = ''; host.appendChild(svg);
}
// per-class small multiples
function perClass(){
  const host = document.getElementById('c-class'); host.innerHTML = '';
  const pc = D.paper.per_class_fig24, auc = D.paper.per_class_auc_fig22;
  [['precision', 'Precision'], ['recall', 'Recall'], ['f1', 'F1 score'], ['auc', 'ROC-AUC (one class against the rest)']].forEach(([m, title]) => {
    const box = document.createElement('div'); const h = document.createElement('h3'); h.textContent = title; box.appendChild(h);
    const c = document.createElement('div'); c.className = 'chart'; box.appendChild(c); host.appendChild(box);
    const rows = ['1', '2', '3', '4'].map(k => [`Severity ${k}`, m === 'auc' ? auc[k] : pc[k][m], D.demo.per_class[k][m], D.freq.per_class[k][m]]);
    requestAnimationFrame(() => grouped(c, rows, S, {lab:78, aria:`${title} by severity class`}));
  });
}
function cm(){
  const m = D.demo.confusion_matrix, host = document.getElementById('cm'); let html = '<div class="h"></div>' + [1,2,3,4].map(k => `<div class="h">Pred. ${k}</div>`).join('');
  const base = css('--s-paper');
  m.forEach((row, i) => { const n = row.reduce((a, b) => a + b, 0); html += `<div class="h">Actual ${i + 1}</div>`;
    row.forEach((v, j) => { const s = v / n; const dark = s > 0.65; html += `<div class="num" style="background:color-mix(in srgb, var(--s-paper) ${Math.round(s * 85 + 4)}%, var(--surface));color:${dark ? '#fff' : 'var(--ink)'}">${s.toFixed(2)}<br><span style="font-size:.72rem;opacity:.85">(${v.toLocaleString()})</span></div>`; }); });
  host.innerHTML = html;
}
function hp(){
  const rng = {n_estimators:'400 (fixed)', learning_rate:'0.01–0.3', num_leaves:'20–3000, step 20', max_depth:'3–12', min_data_in_leaf:'200–10000, step 100',
    lambda_l1:'0–100, step 5', lambda_l2:'0–100, step 5', min_gain_to_split:'0–15', bagging_fraction:'0.2–0.9, step 0.1', bagging_freq:'1 (fixed)', feature_fraction:'0.2–0.9, step 0.1'};
  const pb = D.paper.table5_best_params, tb = D.tuning ? D.tuning.best_params : {};
  const f = v => v == null ? '–' : (Number.isInteger(v) ? v.toLocaleString() : (+v).toFixed(3));
  let h = '<thead><tr><th>Hyperparameter</th><th>Search range</th><th class="r">Paper optimum</th><th class="r">Demo optimum</th></tr></thead><tbody>';
  Object.keys(rng).forEach(k => { h += `<tr><td class="num">${k}</td><td>${rng[k]}</td><td class="r num">${f(pb[k])}</td><td class="r num">${f(tb[k])}</td></tr>`; });
  h += '</tbody>'; document.getElementById('t-hp').innerHTML = h;
  if (D.tuned) document.getElementById('tune-note').textContent = `On this sample the demo search did not beat the paper's hyperparameters: with the demo optimum the test log loss is ${D.tuned.log_loss_test.toFixed(3)} and the accuracy ${D.tuned.accuracy_test.toFixed(2)}, against ${D.demo.log_loss_test.toFixed(3)} and ${D.demo.accuracy_test.toFixed(2)} with the paper's values. A longer search, or one that starts from the paper's values, would be needed to improve on them.`;
  else document.getElementById('tune-note').hidden = true;
  const pi = D.paper.fig20_param_importance, di = D.tuning ? D.tuning.param_importance : {};
  const keys = Object.keys(pi);
  const rows = keys.map(k => [k, pi[k], di[k] != null ? di[k] : null]);
  const ser = [{key:'paper', name:'Paper (Fig. 20)', col:'--s-paper'}, {key:'demo', name:'Demo search', col:'--s-demo'}];
  const mxi = Math.max(...rows.flatMap(r => [r[1], r[2] || 0])); legend('leg3', ser); grouped(document.getElementById('c-imp'), rows, ser, {lab:140, max:Math.ceil(mxi * 10) / 10 || 0.4, aria:'Hyperparameter importance'});
}
function limits(){
  const p = D.prep, t = D.tuning;
  const items = [
    `Data: the public 500,000-record sample of the March 2023 release of US-Accidents (the paper used the December 2020 release with about 4.2 million records). Records from February 2016 to December 2020: ${p.rows_in_period.toLocaleString()}; after cleaning: ${p.rows_clean.toLocaleString()}.`,
    `Sample: the paper's class sizes scaled by ${p.scale.toFixed(3)}, because the sample has only ${p.class_counts_clean['1'].toLocaleString()} severity 1 records: ${Object.values(p.class_counts_sample).map(v => v.toLocaleString()).join(' / ')} records of severity 1 to 4 (${p.rows_sample.toLocaleString()} in total).`,
    `Both versions are run here: with and without the frequency-encoded location variables (street, city, county, zip code, airport). With them, the results are much closer to the paper's.`,
    t ? `Demo search: ${t.n_trials} trials, ${t.n_folds}-fold CV, best multi-class log loss ${t.best_value.toFixed(3)} (trial ${t.best_trial}), ${(t.seconds / 60).toFixed(0)} minutes on two processor cores.` : 'Demo search: not run.',
    'The 2023 release has no TMC, Number or Side columns, so they are skipped. Timezone is dropped because State carries the same information.'];
  document.getElementById('limits').innerHTML = items.map(s => `<li>${s}</li>`).join('');
}
function draw(){ legend('leg1', S); legend('leg2', S); grouped(document.getElementById('c-head'), M, S, {lab:150, aria:'Headline metrics: paper and demo'}); perClass(); cm(); hp(); limits(); }
draw(); let rt; addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(draw, 150); });
matchMedia('(prefers-color-scheme: dark)').addEventListener('change', draw);
</script>
</body>
</html>
'''

os.makedirs(os.path.join(ROOT, 'docs'), exist_ok=True)
open(os.path.join(ROOT, 'docs', 'index.html'), 'w').write(HTML.replace('__DATA__', json.dumps(data)))
print('wrote docs/index.html')
