import glob
import os

import pandas as pd

# ====== 你需要设置的路径 ======
BASELINE_GLOB = "python/data/phenotype/sub-stroke*/ses-01/*baseline*.xlsx"
OUTCOME_GLOB = "python/data/phenotype/sub-stroke*/ses-02/*outcome*.xlsx"
OUTPUT_CSV = "python/datasets/clinical_metadata.csv"

# ====== 需要映射到模型的字段名（按你提供的字段标准） ======
BASELINE_COLUMN_MAP = {
    "Center": "center",
    "Sex": "sex",
    "Age": "age",
    "Atrial fibrillation": "atrial_fibrillation",
    "Hypertension": "hypertension",
    "Diabetes": "diabetes",
    "Hyperlipidemia": "hyperlipidemia",
    "Anticoagulation": "anticoagulation",
    "Lipid lowering drugs": "lipid_lowering_drugs",
    "PAIs": "pais",
    "Glucose": "glucose",
    "Leucocytes": "leucocytes",
    "CRP": "crp",
    "INR": "inr",
    "Wake-up": "wake_up",
    "In-House": "in_house",
    "Referral": "referral",
    "Onset to door": "onset_to_door",
    "Alert to door": "alert_to_door",
    "NIHSS at admission": "nihss_at_admission",
    "mRS at admission": "mrs_at_admission",
    "mRS premorbid": "mrs_premorbid",
    "Door to imaging": "door_to_imaging",
    "Door to groin": "door_to_groin",
    "Door to first series": "door_to_first_series",
    "Time of intervention": "time_of_intervention",
    "Door to recanalization": "door_to_recanalization",
}

OUTCOME_COLUMN = "mRS 3 months"

TIME_COLUMNS = {
    "onset_to_door",
    "alert_to_door",
    "door_to_imaging",
    "door_to_groin",
    "door_to_first_series",
    "time_of_intervention",
    "door_to_recanalization",
}


def patient_id_from_path(path):
    return path.split(os.sep)[-3]


def load_excel(path):
    return pd.read_excel(path)


def parse_minutes(value):
    if pd.isna(value) or value == "":
        return pd.NA
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return pd.to_timedelta(value).total_seconds() / 60.0
    except (ValueError, TypeError):
        return pd.NA


def normalize_sex(value):
    if pd.isna(value):
        return pd.NA
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"m", "male"}:
            return 1
        if normalized in {"f", "female"}:
            return 0
    return value


def collect_records():
    baseline_files = {patient_id_from_path(p): p for p in glob.glob(BASELINE_GLOB)}
    outcome_files = {patient_id_from_path(p): p for p in glob.glob(OUTCOME_GLOB)}

    patient_ids = sorted(set(baseline_files) | set(outcome_files))
    if not patient_ids:
        print("No baseline/outcome files found. Check BASELINE_GLOB/OUTCOME_GLOB.")
        return []

    records = []
    for patient_id in patient_ids:
        baseline_path = baseline_files.get(patient_id)
        outcome_path = outcome_files.get(patient_id)

        if not baseline_path or not outcome_path:
            print(f"[SKIP] {patient_id}: missing baseline or outcome file.")
            continue

        baseline_df = load_excel(baseline_path)
        outcome_df = load_excel(outcome_path)

        baseline_row = {}
        for source_col, target_col in BASELINE_COLUMN_MAP.items():
            if source_col not in baseline_df.columns:
                print(f"[SKIP] {patient_id}: missing column {source_col} in baseline.")
                baseline_row = None
                break
            baseline_row[target_col] = baseline_df.loc[0, source_col]

        if baseline_row is None:
            continue

        if OUTCOME_COLUMN not in outcome_df.columns:
            print(f"[SKIP] {patient_id}: missing column {OUTCOME_COLUMN} in outcome.")
            continue

        for col in TIME_COLUMNS:
            baseline_row[col] = parse_minutes(baseline_row[col])

        baseline_row["sex"] = normalize_sex(baseline_row["sex"])

        mrs_3m = outcome_df.loc[0, OUTCOME_COLUMN]
        mrs_binary = 1 if mrs_3m >= 3 else 0

        record = {"PATIENT_ID": patient_id, **baseline_row, "mRs90_binary": mrs_binary}
        records.append(record)

    return records


def main():
    records = collect_records()
    if not records:
        return

    df = pd.DataFrame(records)
    categorical_cols = [
        "sex",
        "atrial_fibrillation",
        "hypertension",
        "diabetes",
        "hyperlipidemia",
        "anticoagulation",
        "lipid_lowering_drugs",
        "pais",
        "wake_up",
        "in_house",
        "referral",
    ]
    df["sex"] = df["sex"].replace({"M": 1, "F": 0, "m": 1, "f": 0})
    df[categorical_cols] = df[categorical_cols].fillna(0).astype(int)
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved {len(df)} rows -> {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
