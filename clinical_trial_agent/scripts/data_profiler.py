import pandas as pd
import os
import json

def profile_and_clean_database():
    print("=== phase 0: Data Profiling & Cleaning ===")
    db_path = "https://clinicaldata-765366202501-ap-southeast-2-an.s3.ap-southeast-2.amazonaws.com/healthcare_dataset.csv"
    
    print(f"Loading database from: {db_path}")
    try:
        df = pd.read_csv(db_path)
    except Exception as e:
        print(f"Error: Database not found at {db_path} - {e}")
        return
    
    print("\n--- 1. Basic Schema ---")
    print(f"Total Records: {len(df)}")
    print(f"Columns: {df.columns.tolist()}")
    
    print("\n--- 2. Data Types & Missing Values ---")
    info_df = pd.DataFrame({
        'Data Type': df.dtypes,
        'Missing Values': df.isnull().sum(),
        'Missing %': (df.isnull().sum() / len(df) * 100).round(2)
    })
    print(info_df)
    
    print("\n--- 3. Categorical Unique Values (Ontology Extraction) ---")
    categorical_columns = ['Gender', 'Blood Type', 'Medical Condition', 'Admission Type', 'Medication', 'Test Results']
    
    ontology = {}
    for col in categorical_columns:
        if col in df.columns:
            unique_vals = df[col].dropna().unique().tolist()
            ontology[col] = unique_vals
            print(f"- {col} ({len(unique_vals)} unique): {unique_vals}")
            
    print("\n--- 4. Identifying Anomalies ---")
    print("Checking Age bounds (Expected 0 - 120):")
    if 'Age' in df.columns:
        invalid_ages = df[(df['Age'] < 0) | (df['Age'] > 120)]
        print(f"Found {len(invalid_ages)} records with invalid age.")
        if len(invalid_ages) > 0:
            print(invalid_ages[['Name', 'Age']].head())
            
    print("\nChecking Billing Amount bounds (Expected >= 0):")
    if 'Billing Amount' in df.columns:
        invalid_billing = df[df['Billing Amount'] < 0]
        print(f"Found {len(invalid_billing)} records with negative billing.")
        
    print("\n--- 5. Generating Cleaned Database ---")
    # Basic automated cleaning based on anomalies found
    cleaned_df = df.copy()
    
    # Fill N/As in categorical columns with 'Unknown'
    for col in categorical_columns:
        if col in cleaned_df.columns:
            cleaned_df[col] = cleaned_df[col].fillna('Unknown')
            
    cleaned_db_path = os.path.join(os.path.dirname(__file__), "..", "Healthcare Database", "healthcare_dataset_cleaned.csv")
    cleaned_df.to_csv(cleaned_db_path, index=False)
    print(f"Saved cleaned database to: {cleaned_db_path}")
    
    print("\n--- 6. Saving Extracted Ontology ---")
    ontology_path = os.path.join(os.path.dirname(__file__), "..", "resources", "ontology_dictionary.json")
    with open(ontology_path, "w") as f:
        json.dump(ontology, f, indent=4)
    print(f"Saved Ontology JSON to: {ontology_path}")
    
if __name__ == "__main__":
    profile_and_clean_database()
