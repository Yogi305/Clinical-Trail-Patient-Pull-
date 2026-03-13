import os
import json
import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer

def init_faiss_ontology():
    print("Initializing FAISS Ontology Database...")
    
    ontology_path = os.path.join(os.path.dirname(__file__), "ontology_dictionary.json")
    if not os.path.exists(ontology_path):
        print(f"Error: Ontology dictionary not found at {ontology_path}")
        return
        
    with open(ontology_path, "r") as f:
        ontology = json.load(f)
        
    # Flatten ontology values into a single list of distinct terms
    all_terms = []
    # keep track of semantic categories to help with debugging or context if needed (optional)
    term_mapping = [] 
    
    for category, values in ontology.items():
        for val in values:
            if str(val).lower() not in ['nan', 'unknown', 'none', 'n/a']:
                all_terms.append(str(val))
                term_mapping.append({"category": category, "term": str(val)})
                
    if not all_terms:
        print("No terms to embed.")
        return
        
    print(f"Loaded {len(all_terms)} distinct terminology values from the database schema.")
    
    # Initialize the embedding model
    print("Loading embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Generate embeddings
    print("Generating vector embeddings...")
    embeddings = model.encode(all_terms)
    
    # FAISS expects float32
    embeddings = np.array(embeddings).astype('float32')
    
    # Create the FAISS index (L2 distance aka euclidean)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    
    # Add vectors to index
    index.add(embeddings)
    
    # Save the index and the mapping
    index_path = os.path.join(os.path.dirname(__file__), "ontology.index")
    mapping_path = os.path.join(os.path.dirname(__file__), "ontology_mapping.pkl")
    
    faiss.write_index(index, index_path)
    
    with open(mapping_path, "wb") as f:
        pickle.dump(term_mapping, f)
        
    print(f"Success! Saved FAISS index with {index.ntotal} vectors to {index_path}")
    print(f"Saved mapping payload to {mapping_path}")

if __name__ == "__main__":
    init_faiss_ontology()
