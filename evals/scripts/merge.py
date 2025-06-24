import os
import json

meta_dir = "../../data_processing/data/output/processed_test"
gen_dir = "../../data_generation/data/qwen_3_8b"
output_dir = "../data/merged/qwen_3_8b"

os.makedirs(output_dir, exist_ok=True)

for filename in os.listdir(meta_dir):
    if not filename.endswith(".json"):
        continue

    base_name = filename.replace(".json", "")
    jsonl_filename = base_name + ".jsonl"

    meta_path = os.path.join(meta_dir, filename)
    gen_path = os.path.join(gen_dir, jsonl_filename)
    merged_path = os.path.join(output_dir, base_name + "_merged.jsonl")

    if not os.path.exists(gen_path):
        print(f"Skipping {filename}, no matching .jsonl file.")
        continue

    with open(meta_path, "r") as f:
        meta_data = json.load(f)

    with open(gen_path, "r") as f:
        gen_lines = [json.loads(line) for line in f]

    assert len(meta_data) == len(gen_lines), f"Length mismatch in {filename}"

    merged = []
    for meta, gen in zip(meta_data, gen_lines):
        meta_info = meta["INPUT"]
        for k in ["student_id", "semester", "assignment_name", "question_name"]:
            gen[k] = meta_info.get(k)
        if meta_info.get("quantile") is not None:
            gen["quantile"] = meta_info["quantile"]


        merged.append(gen)

    with open(merged_path, "w") as f:
        for item in merged:
            f.write(json.dumps(item) + "\n")

    print(f"Merged: {jsonl_filename} → {merged_path}")
