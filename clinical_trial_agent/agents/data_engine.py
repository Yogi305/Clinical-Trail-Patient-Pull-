"""
agents/data_engine.py
---------------------
Agent 3: The Deterministic Data Engine

100% deterministic Pandas-based patient filtering — no LLM involved here.
LLMs translate language; Pandas executes the search with mathematical precision.
This guarantees zero hallucinations and 100% data accuracy in returned patients.
"""

import pandas as pd
from agents.shared import patient_df


def apply_pandas_filter(
    patient_database: pd.DataFrame,
    criteria: dict,
    field_name: str,
    df_column: str,
    is_exclusion: bool = False,
    transform=None,
) -> tuple[pd.DataFrame, str]:
    """
    Shared utility to apply a single inclusive or exclusive Pandas filter.
    Returns (filtered_dataframe, log_message) or (unchanged_df, None) if skipped.

    Guard clause: skips any field that is missing, null, or ambiguous — 
    we never pass uncertain values into the deterministic engine.
    """
    if field_name not in criteria:
        return patient_database, None

    val = criteria[field_name]
    if not val or str(val).lower() in ("none", "n/a", "any", "null") or str(val).startswith("AMBIGUOUS_RAW:"):
        return patient_database, None

    val = transform(val) if transform else str(val)

    if is_exclusion:
        filtered = patient_database[patient_database[df_column] != val]
        log = f"After `{df_column} != '{val}'` (EXCLUDED): **{len(filtered)}** patients remain."
        return filtered, log

    # Age range requires numerical comparison, not equality
    if df_column == "Age" and field_name == "age_min":
        filtered = patient_database[patient_database[df_column] >= val]
        log = f"After `Age >= {val}`: **{len(filtered)}** patients remain."
    elif df_column == "Age" and field_name == "age_max":
        filtered = patient_database[patient_database[df_column] <= val]
        log = f"After `Age <= {val}`: **{len(filtered)}** patients remain."
    else:
        filtered = patient_database[patient_database[df_column] == val]
        log = f"After `{df_column} == '{val}'`: **{len(filtered)}** patients remain."

    return filtered, log


def execute_deterministic_patient_search(mapped_criteria: dict) -> dict:
    """
    Applies all inclusion and exclusion criteria in sequence via Pandas filters.
    Returns {"eligible_patients": DataFrame, "filter_log": [...], "total_matched": int}.
    """
    patient_database = patient_df.copy()
    filter_log = [f"🟢 Starting with **{len(patient_database)}** patient records."]

    # Ordered list of (json_field, df_column, optional_transform)
    inclusive_filters = [
        ("medical_condition", "Medical Condition", None),
        ("age_min",           "Age",               int),
        ("age_max",           "Age",               int),
        ("gender",            "Gender",             lambda x: str(x).title()),
        ("admission_type",    "Admission Type",     None),
        ("blood_type",        "Blood Type",         lambda x: str(x).upper()),
        ("medication",        "Medication",         None),
        ("test_results",      "Test Results",       None),
    ]

    for field_name, df_column, transform in inclusive_filters:
        patient_database, log = apply_pandas_filter(
            patient_database, mapped_criteria, field_name, df_column, False, transform
        )
        if log:
            filter_log.append(log)

    filter_log.append("🔴 **Applying Exclusion Criteria...**")

    exclusion_filters = [
        ("exclude_medication",     "Medication",     None),
        ("exclude_test_results",   "Test Results",   None),
        ("exclude_admission_type", "Admission Type", None),
    ]

    for field_name, df_column, transform in exclusion_filters:
        patient_database, log = apply_pandas_filter(
            patient_database, mapped_criteria, field_name, df_column, True, transform
        )
        if log:
            filter_log.append(log)

    filter_log.append(f"🏁 **Final Result: {len(patient_database)} eligible patients found.**")

    return {
        "eligible_patients": patient_database,
        "filter_log": filter_log,
        "total_matched": len(patient_database),
    }
