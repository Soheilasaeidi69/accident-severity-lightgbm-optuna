"""Turn the raw US-Accidents file into the table used for modelling.

Follows the steps of the Methodology section of the paper. Each step is
numbered in the code so it can be checked against the text.

    python src/preprocess.py --input data/US_Accidents_Dec20.csv --output data/model_table.csv.gz
"""
import argparse
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

from config import CLASS_SIZES, PERIOD_END, PERIOD_START, SEED

# Columns the paper removes because they carry no information or have little
# relation to severity. Columns that do not exist in a given release of the
# dataset (the 2023 release has no TMC or Number) are skipped.
DROP_FIRST = ["ID", "Source", "TMC", "Description", "End_Time", "End_Lat", "End_Lng",
              "Distance(mi)", "Number", "Wind_Chill(F)", "Country", "Turning_Loop"]
NEED_VALUE = ["City", "Zipcode", "Timezone", "Airport_Code", "Sunrise_Sunset",
              "Civil_Twilight", "Nautical_Twilight", "Astronomical_Twilight"]
NUM_WEATHER = ["Temperature(F)", "Humidity(%)", "Pressure(in)", "Visibility(mi)", "Wind_Speed(mph)"]
CAT_WEATHER = ["Wind_Direction", "Weather_Condition"]
RARE_FLAGS = ["Bump", "Give_Way", "No_Exit", "Roundabout", "Traffic_Calming"]
TWILIGHT = ["Civil_Twilight", "Nautical_Twilight", "Astronomical_Twilight"]
FREQ_COLS = ["Street", "City", "County", "Zipcode", "Airport_Code"]
BOXCOX_COLS = ["Pressure(in)", "Visibility(mi)", "Wind_Speed(mph)"]
ONE_HOT = ["Side", "State", "Wind_Direction", "Weekday", "Month", "Hour", "Sunrise_Sunset"]

WIND = {"Calm": "CALM", "CALM": "CALM", "Variable": "VAR", "VAR": "VAR",
        "North": "N", "NNW": "N", "NNE": "N", "N": "N",
        "South": "S", "SSW": "S", "SSE": "S", "S": "S",
        "East": "E", "ESE": "E", "ENE": "E", "E": "E",
        "West": "W", "WSW": "W", "WNW": "W", "W": "W",
        "NE": "NE", "NW": "NW", "SE": "SE", "SW": "SW"}

# Weather_Condition (over 100 labels) merged into seven general groups.
WEATHER = {
    "Clear": "Clear|Fair",
    "Cloud": "Cloud|Overcast",
    "Rain": "Rain|Drizzle|Storm|Thunder",
    "Heavy_Rain": "Heavy Rain|Rain Shower|Heavy T-Storm|Heavy Thunderstorm",
    "Snow": "Snow|Sleet|Ice|Hail|Wintry",
    "Heavy_Snow": "Heavy Snow|Heavy Sleet|Heavy Ice Pellets|Snow Shower|Squall",
    "Fog": "Fog|Mist|Haze",
}


def _fill_by_group(df, col, how):
    """Fill missing values with the median (numbers) or the most common value
    (categories) of records from the same weather station and month."""
    grp = df.groupby(["Airport_Code", "Month"])[col]
    if how == "median":
        fill = grp.transform("median")
    else:
        mode = grp.agg(lambda s: s.mode().iloc[0] if s.notna().any() else np.nan)
        fill = pd.Series(pd.MultiIndex.from_frame(df[["Airport_Code", "Month"]]).map(mode), index=df.index)
    df[col] = df[col].where(df[col].notna(), fill)


def clean(df, keep_freq=False, log=print):
    info = {"rows_raw": int(len(df))}

    # 1. Study period, and time variables built from Start_Time.
    t = pd.to_datetime(df["Start_Time"].astype(str).str.slice(0, 19), errors="coerce")
    df = df[(t >= PERIOD_START) & (t < PERIOD_END)].copy()
    t = t.loc[df.index]
    df["Month"], df["Weekday"], df["Hour"] = t.dt.month, t.dt.weekday, t.dt.hour
    info["rows_in_period"] = int(len(df))

    # 2. Remove identifiers, single-valued columns and columns with little
    #    relation to severity. Wind_Chill is 0.99 correlated with Temperature.
    #    Year and Duration are built in the paper and then removed again, so
    #    they are not built here.
    df = df.drop(columns=[c for c in DROP_FIRST + ["Start_Time", "Weather_Timestamp"] if c in df.columns])

    # 3. Precipitation is missing for more than half of the records: keep it,
    #    add a "was missing" indicator, fill with the median.
    df["Precipitation_NA"] = df["Precipitation(in)"].isna().astype(int)
    df["Precipitation(in)"] = df["Precipitation(in)"].fillna(df["Precipitation(in)"].median())

    # 4. Columns with under 1 % missing: delete those records.
    df = df.dropna(subset=[c for c in NEED_VALUE if c in df.columns])

    # 5. Weather values: fill by weather station (Airport_Code) and month,
    #    median for numbers and most common value for categories; delete the
    #    few records that still have no value.
    for c in NUM_WEATHER:
        _fill_by_group(df, c, "median")
    for c in CAT_WEATHER:
        _fill_by_group(df, c, "mode")
    df = df.dropna(subset=NUM_WEATHER + CAT_WEATHER + ["Street"])
    info["rows_after_missing"] = int(len(df))

    # 6. Merge wind direction and weather condition into general groups.
    df["Wind_Direction"] = df["Wind_Direction"].map(WIND).fillna("VAR")
    for name, pattern in WEATHER.items():
        df[name] = df["Weather_Condition"].str.contains(pattern, case=False, na=False).astype(int)
    df = df.drop(columns=["Weather_Condition", "Timezone"])

    # 7. Box-Cox transformation of the skewed weather variables (shifted so the
    #    smallest value is one, because Box-Cox needs positive values).
    info["boxcox_lambda"] = {}
    for c in BOXCOX_COLS:
        x = df[c] - df[c].min() + 1                 # shift to a minimum of 1 so that Box-Cox is defined
        y, lam = stats.boxcox(x)
        df[c] = (y - y.mean()) / y.std()            # standardized; trees are unaffected, values stay readable
        info["boxcox_lambda"][c] = round(float(lam), 4)

    # 8. Frequency encoding with a log transformation. The paper's text says
    #    these variables were then excluded for high correlation, while its
    #    Fig. 12 shows them among the processed variables; they are kept only
    #    with --keep-freq.
    for c in FREQ_COLS:
        if keep_freq:
            df[c + "_Freq"] = np.log(df[c].map(df[c].value_counts(normalize=True)))
        df = df.drop(columns=c)

    # 9. Remove the heavily imbalanced road flags and the three twilight
    #    variables that repeat Sunrise_Sunset.
    df = df.drop(columns=RARE_FLAGS + TWILIGHT)

    # 10. One-hot encoding.
    bool_cols = df.select_dtypes("bool").columns
    df[bool_cols] = df[bool_cols].astype(int)
    df = pd.get_dummies(df, columns=[c for c in ONE_HOT if c in df.columns], dtype=int)
    df.columns = [c.replace("(", "_").replace(")", "").replace("%", "pct") for c in df.columns]

    info["rows_clean"] = int(len(df))
    info["n_features"] = int(df.shape[1] - 1)
    info["class_counts_clean"] = {int(k): int(v) for k, v in df["Severity"].value_counts().sort_index().items()}
    log(f"clean table: {len(df):,} records, {df.shape[1] - 1} input variables")
    return df, info


def draw_sample(df, scale="auto", log=print):
    """Draw the modelling sample with the class sizes of the paper.

    With the full dataset scale is 1. When a class has fewer records than the
    paper used, every class is scaled down by the same factor so the class
    shares stay the same (3 % / 54 % / 32 % / 10 %)."""
    counts = df["Severity"].value_counts()
    if scale == "auto":
        scale = min(1.0, min(counts.get(k, 0) / v for k, v in CLASS_SIZES.items()))
    parts = [df[df["Severity"] == k].sample(n=int(v * scale), random_state=SEED) for k, v in CLASS_SIZES.items()]
    out = pd.concat(parts).sample(frac=1, random_state=SEED).reset_index(drop=True)
    log(f"modelling sample: {len(out):,} records (scale {scale:.4f} of the paper's sample)")
    return out, float(scale)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", required=True, help="raw US-Accidents CSV file")
    ap.add_argument("--output", default="data/model_table.csv.gz")
    ap.add_argument("--scale", default="auto", help="'auto' or a number between 0 and 1")
    ap.add_argument("--keep-freq", action="store_true", help="keep the frequency-encoded location variables")
    a = ap.parse_args()

    raw = pd.read_csv(a.input)
    table, info = clean(raw, keep_freq=a.keep_freq)
    sample, scale = draw_sample(table, a.scale if a.scale == "auto" else float(a.scale))
    info.update(scale=scale, rows_sample=int(len(sample)), input_file=os.path.basename(a.input),
                keep_freq=bool(a.keep_freq),
                class_counts_sample={int(k): int(v) for k, v in sample["Severity"].value_counts().sort_index().items()})
    os.makedirs(os.path.dirname(a.output) or ".", exist_ok=True)
    sample.to_csv(a.output, index=False)
    with open(a.output.replace(".csv.gz", "").replace(".csv", "") + "_info.json", "w") as f:
        json.dump(info, f, indent=1)


if __name__ == "__main__":
    main()
