import os
import sys
import docx
import urllib.request
import json
from agent import run_gatekeeper, run_extractor

def main():
    print("Downloading BRD 2...")
    url = "https://clinicaldata-765366202501-ap-southeast-2-an.s3.ap-southeast-2.amazonaws.com/BRD%202.docx"
    doc_path = "test_brd_2.docx"
    if not os.path.exists(doc_path):
        urllib.request.urlretrieve(url, doc_path)
    
    print("Reading BRD 2...")
    doc = docx.Document(doc_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    user_input = '\n'.join(full_text)
    
    print(f"Loaded {len(user_input.split())} words.")
    
    print("\n--- Gatekeeper ---")
    gate_res = run_gatekeeper(user_input)
    print(gate_res)
    
    print("\n--- Extractor ---")
    try:
        extract_res = run_extractor(user_input)
        print(json.dumps(extract_res, indent=2))
        
        # Check if it returned a default empty dictionary
        is_empty = all(v is None for v in extract_res.get('extracted_json', {}).values())
        if is_empty:
            print("\nWARNING: Extractor returned an entirely empty schema!")
    except Exception as e:
        print(f"Extractor failed with exception: {e}")

if __name__ == "__main__":
    main()
