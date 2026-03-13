import pandas as pd
import os
import json

def perform_eda_and_cleaning():
    print("="*60)
    print(" 🏥 CLINICAL TRIAL DATASET: EDA & CLEANING PIPELINE ")
    print("="*60)
    
    # ---------------------------------------------------------
    # STEP 1: DATA INGESTION & INITIAL EXPLORATION
    # ---------------------------------------------------------
    print("\n[STEP 1] Data Ingestion & Initial Exploration")
    db_path = "https://clinicaldata-765366202501-ap-southeast-2-an.s3.ap-southeast-2.amazonaws.com/healthcare_dataset.csv"
    
    try:
        df = pd.read_csv(db_path)
    except Exception as e:
        print(f"Error: Database not found at {db_path} - {e}")
        return
    print(f"-> Successfully loaded {len(df)} records and {len(df.columns)} columns.")
    print(f"-> Columns list: {df.columns.tolist()}")
    
    # ---------------------------------------------------------
    # STEP 2: EXPLORATORY DATA ANALYSIS (EDA) - FINDING ANOMALIES
    # ---------------------------------------------------------
    print("\n[STEP 2] Exploratory Data Analysis (EDA) - Identifying Anomalies")
    
    # 2.A: Missing Values Analysis
    print("\n--- A. Missing Values Check ---")
    missing_data = df.isnull().sum()
    if missing_data.sum() == 0:
        print("-> Excellent: No missing values detected in the dataset.")
    else:
        print("-> Alert! Missing values found:\n", missing_data[missing_data > 0])
        
    # 2.B: Duplicate Records Analysis
    print("\n--- B. Duplicate Records Check ---")
    duplicate_count = df.duplicated().sum()
    if duplicate_count > 0:
        print(f"-> Alert! Found {duplicate_count} exactly duplicated rows in the dataset.")
    else:
        print("-> No duplicate rows detected.")
    
    # 2.C: Logical Data Anomalies (Age & Billing Outliers)
    print("\n--- C. Logical Anomalies & Outlier Detection ---")
    invalid_ages = df[(df['Age'] < 0) | (df['Age'] > 120)]
    print(f"-> Age Constraint Check (0-120): Found {len(invalid_ages)} patients with unrealistic ages.")
    
    negative_billing = df[df['Billing Amount'] < 0]
    print(f"-> Billing Constraint Check (>= 0): Found {len(negative_billing)} records with negative billing amounts.")
    if not negative_billing.empty:
        print("   Sample of anomalies:\n", negative_billing[['Name', 'Billing Amount']].head(3))
        
    # 2.D: Categorical Schema Profiling (Ontology Extraction)
    print("\n--- D. Categorical Profiling (Extracting Ontology) ---")
    categorical_columns = ['Gender', 'Blood Type', 'Medical Condition', 'Admission Type', 'Medication', 'Test Results']
    ontology = {}
    
    for col in categorical_columns:
        if col in df.columns:
            # Standardizing text format across the board before extracting unique values
            df[col] = df[col].astype(str).str.strip().str.title()
            
            # Special formatting fix so we don't end up with 'O+' -> 'O+' and 'o+' -> 'O+' mismatches
            if col == 'Blood Type':
                df[col] = df[col].str.upper()
                
            unique_vals = df[col].dropna().unique().tolist()
            ontology[col] = unique_vals
            print(f"   -> {col} ({len(unique_vals)} unique values)")

    # ---------------------------------------------------------
    # STEP 3: DATA CLEANING & REMEDIATION
    # ---------------------------------------------------------
    print("\n[STEP 3] Executing Data Cleaning Operations")
    
    # Intervention 1: Remove Duplicates
    if duplicate_count > 0:
        df.drop_duplicates(inplace=True)
        print(f"-> Intervention: Dropped {duplicate_count} duplicate rows.")
        
    # Intervention 2: Fix Negative Billing (Absolute Value Transformation)
    if not negative_billing.empty:
        df['Billing Amount'] = df['Billing Amount'].abs()
        print("-> Intervention: Converted negative billing amounts to absolute (positive) values.")
        
    # Intervention 3: Filter Invalid Ages
    if not invalid_ages.empty:
        df = df[(df['Age'] >= 0) & (df['Age'] <= 120)]
        print(f"-> Intervention: Removed {len(invalid_ages)} rows with statistically invalid ages.")
        
    print(f"\n-> Standardized Categorical Fields (Title Case & Stripped Whitespace).")
    print(f"-> Cleaning Complete! Final Quality-Controlled Dataset Size: {len(df)} records.")

    # ---------------------------------------------------------
    # STEP 4: EXPORTING CLEANED ASSETS
    # ---------------------------------------------------------
    print("\n[STEP 4] Exporting Cleaned Database & FAISS Ontology Schema")
    cleaned_db_path = os.path.join(os.path.dirname(__file__), "..", "Healthcare Database", "healthcare_dataset_cleaned.csv")
    df.to_csv(cleaned_db_path, index=False)
    print(f"-> Success: Saved Cleaned Database to: {cleaned_db_path}")
    
    ontology_path = os.path.join(os.path.dirname(__file__), "ontology_dictionary.json")
    with open(ontology_path, "w") as f:
        json.dump(ontology, f, indent=4)
    print(f"-> Success: Saved FAISS Ontology Dictionary to: {ontology_path}")
    
    print("\n============================================================")
    print(" EDA & CLEANING PIPELINE FINISHED SUCCESSFULLY")
    print("============================================================")

if __name__ == "__main__":
    perform_eda_and_cleaning()
