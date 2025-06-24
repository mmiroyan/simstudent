import os
import re
import glob
import json
from tqdm import tqdm

import torch
from sentence_transformers import SentenceTransformer

INPUT_DIR = "../data/formatted/"
OUTPUT_DIR = "../data/formatted_embeddings/"
MODELS = ["gpt_4_1", "llama_3_8b", "qwen_2_5_coder_3b", "qwen_2_5_coder_7b", "qwen_2_5_coder_7b_inst", "qwen_3_8b"]
EMBEDDING_MODEL_NAME = "Salesforce/SFR-Embedding-Code-400M_R"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
EMBEDDING_MODEL = SentenceTransformer(EMBEDDING_MODEL_NAME, trust_remote_code=True, device=device)

########################################################
# Utils
########################################################

def get_exp_type(file_path):
    if re.search(r"exp\d_1_", file_path):
        return "1"
    elif re.search(r"exp\d_2_", file_path):
        return "2"
    elif re.search(r"exp\d_3_", file_path):
        return "3"
    else:
        raise ValueError(f"Unknown experiment type in {file_path}")
    
def load_data(file_path):
    data = []
    with open(file_path, "r") as f:
        for line in f:
            data.append(json.loads(line))
    return data

def save_data(data, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        for item in data:
            f.write(json.dumps(item) + "\n")

def embed_codes(codes: list[str]):
    return EMBEDDING_MODEL.encode(codes)

def embed_data(input_data: dict, batch_size: int = 72):
    data = input_data["data"]
    if input_data["exp_type"] == "1" or input_data["exp_type"] == "3":
        exp_batch_size = max(1, batch_size//2)
        for i in tqdm(range(0, len(data), exp_batch_size)):
            batch_data = data[i:i+exp_batch_size]
            gt_codes = [item.get("gt_code_block", "") for item in batch_data]
            synthetic_codes = [item.get("synthetic_code_block", "") for item in batch_data]
            codes = gt_codes + synthetic_codes
            embeddings = embed_codes(codes)
            assert len(embeddings) == len(codes)
            for j, item in enumerate(batch_data):
                if item["is_processed"]:
                    item["embeddings"] = {}
                    item["embeddings"]["gt_code_block"] = embeddings[j].tolist()
                    item["embeddings"]["synthetic_code_block"] = embeddings[j+len(batch_data)].tolist()
    
    elif input_data["exp_type"] == "2":
        exp_batch_size = max(1, batch_size//6)
        for i in tqdm(range(0, len(data), exp_batch_size)):
            batch_data = data[i:i+exp_batch_size]
            gt_codes_q0 = [item.get("gt_code_block_q0", "") for item in batch_data]
            gt_codes_q1 = [item.get("gt_code_block_q1", "") for item in batch_data]
            gt_codes_q2 = [item.get("gt_code_block_q2", "") for item in batch_data]
            synthetic_codes_q0 = [item.get("synthetic_code_block_q0", "") for item in batch_data]
            synthetic_codes_q1 = [item.get("synthetic_code_block_q1", "") for item in batch_data]
            synthetic_codes_q2 = [item.get("synthetic_code_block_q2", "") for item in batch_data]
            codes = gt_codes_q0 + gt_codes_q1 + gt_codes_q2 + synthetic_codes_q0 + synthetic_codes_q1 + synthetic_codes_q2
            embeddings = embed_codes(codes)
            assert len(embeddings) == len(codes)
            for j, item in enumerate(batch_data):
                if item["is_processed"]:
                    item["embeddings"] = {}
                    item["embeddings"]["gt_code_block_q0"] = embeddings[j].tolist()
                    item["embeddings"]["gt_code_block_q1"] = embeddings[j+len(batch_data)].tolist()
                    item["embeddings"]["gt_code_block_q2"] = embeddings[j+2*len(batch_data)].tolist()
                    item["embeddings"]["synthetic_code_block_q0"] = embeddings[j+3*len(batch_data)].tolist()
                    item["embeddings"]["synthetic_code_block_q1"] = embeddings[j+4*len(batch_data)].tolist()
                    item["embeddings"]["synthetic_code_block_q2"] = embeddings[j+5*len(batch_data)].tolist()

def main():
    print(f"STARTING PROCESSING...\n")
    for model in MODELS:
        print(f'EMBEDDING {model.upper()} OUTPUTS...\n{"#" * 50}\n')
        dir_path = os.path.join(INPUT_DIR, model)    
        input_files = glob.glob(os.path.join(dir_path, "*.jsonl"))
        model_data = [{"file_path": file, "model": model, "exp_type": get_exp_type(file), "data": load_data(file)} for file in input_files]
        for data in model_data:
            print(f'PROCESSING {data["file_path"]} (model: {data["model"]}, exp_type: {data["exp_type"]}, size: {len(data["data"])})...\n{"#" * 50}\n')
            embed_data(data)
            save_data(data['data'], os.path.join(OUTPUT_DIR, model, os.path.basename(data["file_path"])))
            print(f'DONE EXPERIMENT! SAVED TO {os.path.join(OUTPUT_DIR, model, os.path.basename(data["file_path"]))}\n{"#" * 50}\n')
        print(f'DONE MODEL! EMBEDDED {model.upper()} OUTPUTS\n{"#" * 50}\n')
    print(f"DONE PROCESSING!\n")

if __name__ == "__main__":
    main()
