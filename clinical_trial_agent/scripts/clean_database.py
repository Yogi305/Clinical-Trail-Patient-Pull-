import pandas as pd
import os
import json

def perform_eda_and_cleaning():
    """Headless cleaning logic for UI and automation."""
    db_path = "https://clinicaldata-765366202501-ap-southeast-2-an.s3.ap-southeast-2.amazonaws.com/healthcare_dataset.csv"
    
    # Load
    df = pd.read_csv(db_path)
    
    # Clean
    df.drop_duplicates(inplace=True)
    df['Billing Amount'] = df['Billing Amount'].abs()
    df = df[(df['Age'] >= 0) & (df['Age'] <= 120)]
    
    # Standardize
    categorical_columns = ['Gender', 'Blood Type', 'Medical Condition', 'Admission Type', 'Medication', 'Test Results']
    ontology = {}
    for col in categorical_columns:
        df[col] = df[col].astype(str).str.strip().str.title()
        if col == 'Blood Type':
            df[col] = df[col].str.upper()
        ontology[col] = sorted(df[col].dropna().unique().tolist())

    # Save to resources (Single Source of Truth)
    base_dir = os.path.dirname(os.path.dirname(__file__))
    res_dir = os.path.join(base_dir, "resources")
    
    df.to_csv(os.path.join(res_dir, "healthcare_dataset_cleaned.csv"), index=False)
    with open(os.path.join(res_dir, "ontology_dictionary.json"), "w") as f:
        json.dump(ontology, f, indent=4)
        
    return len(df)

if __name__ == "__main__":
    perform_eda_and_cleaning()
