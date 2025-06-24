import os
import json
from glob import glob
from tqdm import tqdm

FORMATTED_DIR = "../data/formatted_embeddings"
FEATURES_DIR = "../data/with_features"
OUTPUT_DIR = "../data/with_features_with_embeddings"


REQUIRED_KEYS = [
    "student_id",
    "semester",
    "assignment_name",
    "question_name",
    "is_processed",
]
OPTIONAL_KEYS = ["quantile", "block_num","is_submitted_syn", "is_submitted_gt"]

os.makedirs(OUTPUT_DIR, exist_ok=True)

formatted_files = glob(f"{FORMATTED_DIR}/**/*.jsonl", recursive=True)

merged_count = 0
skipped_count = 0

for formatted_path in tqdm(formatted_files, desc="Merging files", unit="file"):
    rel_path = os.path.relpath(formatted_path, FORMATTED_DIR)
    features_filename = os.path.basename(rel_path).replace("_formatted.jsonl", "_with_features.jsonl")
    features_path = os.path.join(FEATURES_DIR, os.path.dirname(rel_path), features_filename)

    output_path = os.path.join(OUTPUT_DIR, os.path.dirname(rel_path), features_filename)


    if not os.path.exists(features_path):
        print(f"⚠️ Missing features file: {rel_path}")
        skipped_count += 1
        continue

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(formatted_path, "r") as f1, open(features_path, "r") as f2:
        formatted_lines = [json.loads(line) for line in f1]
        features_lines = [json.loads(line) for line in f2]

    if len(formatted_lines) != len(features_lines):
        print(f"Line count mismatch in {rel_path} — formatted: {len(formatted_lines)}, features: {len(features_lines)}")
        skipped_count += 1
        continue

    all_pass = True
    merged_rows = []
    for i, (row_f, row_feat) in enumerate(zip(formatted_lines, features_lines)):
        for key in REQUIRED_KEYS:
            if row_f.get(key) != row_feat.get(key):
                print(f"Metadata mismatch at line {i} in {rel_path} — key: {key}")
                all_pass = False
                break

        for key in OPTIONAL_KEYS:
            if key in row_f or key in row_feat:
                if row_f.get(key) != row_feat.get(key):
                    print(f"Optional metadata mismatch at line {i} in {rel_path} — key: {key}")
                    all_pass = False
                    break

        if "_2_" in rel_path:
            for q in ["q0", "q1", "q2"]:
                gt_key = f"gt_code_block_{q}"
                syn_key = f"synthetic_code_block_{q}"
                if row_f.get(gt_key) != row_feat.get(gt_key):
                    print(f"GT code mismatch at line {i} in {rel_path} — key: {gt_key}")
                    all_pass = False
                    break
                if row_f.get(syn_key) != row_feat.get(syn_key):
                    print(f"Synthetic code mismatch at line {i} in {rel_path} — key: {syn_key}")
                    all_pass = False
                    break
        else:
            if row_f.get("gt_code_block") != row_feat.get("gt_code_block"):
                print(f"GT code mismatch at line {i} in {rel_path}")
                all_pass = False
                break
            if row_f.get("synthetic_code_block") != row_feat.get("synthetic_code_block"):
                print(f"Synthetic code mismatch at line {i} in {rel_path}")
                all_pass = False
                break


        if not all_pass:
            break

        if row_f.get("is_processed") and "embeddings" in row_f:
            row_feat["embeddings"] = row_f["embeddings"]


        merged_rows.append(row_feat)

    if all_pass:
        with open(output_path, "w") as out:
            for row in merged_rows:
                out.write(json.dumps(row) + "\n")
        merged_count += 1
    else:
        print(f"Skipped: {rel_path} due to metadata mismatch\n")
        skipped_count += 1

print(f"\nDone. Merged: {merged_count}, Skipped: {skipped_count}")
