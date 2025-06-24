import os
import json
import re

INPUT_DIR = "../data/merged/qwen_3_8b"
OUTPUT_DIR = "../data/formatted/qwen_3_8b"
MODEL_NAME = "qwen_3_8b"
os.makedirs(OUTPUT_DIR, exist_ok=True)

total_skipped = 0


def extract_code_blocks(text, is_gt=False):
    text = text.strip()
    text = re.sub(r"</code>", "<code>", text)
    
    if not is_gt:
        text = re.sub(r"```python", "<code>", text)
        text = re.sub(r"```", "<code>", text)
        
        if MODEL_NAME == "llama_3_8b":
            def_match = re.search(r"\b([A-Za-z_]\w*\s*\(.*)", text, re.DOTALL)
            if def_match:
                snippet = def_match.group(1).strip()
                text = f"<code>def {snippet}"
    return re.findall(r"<code>(.*?)<code>", text, re.DOTALL)

def extract_quantile_from_input(text):
    match = re.search(r"submission_q\d+", text)
    return match.group(0) if match else None

def process_type_1(row):
    gt_blocks = extract_code_blocks(row.get("output_gt", ""), is_gt=True)[:1]
    syn_blocks = extract_code_blocks(row.get("output_synthetic", ""), is_gt=False)[:1]

    block = row.copy()
    block["is_processed"] = len(gt_blocks) == len(syn_blocks)
    block["quantile"] = row.get("quantile") or extract_quantile_from_input(row.get("input", ""))

    block["synthetic_code_block"] = syn_blocks[0].replace("<SUBMIT>", "").strip() if syn_blocks else ""
    block["gt_code_block"] = gt_blocks[0].replace("<SUBMIT>", "").strip() if gt_blocks else ""

    return [block]

def process_type_2(row):
    gt_blocks = extract_code_blocks(row.get("output_gt", ""), is_gt=True)[:3]
    syn_blocks = extract_code_blocks(row.get("output_synthetic", ""), is_gt=False)[:3]

    block = row.copy()
    block["is_processed"] = len(gt_blocks) == len(syn_blocks) == 3

    if not block["is_processed"]:
        return [block]

    for i in range(3):
        block[f"synthetic_code_block_q{i}"] = syn_blocks[i].replace("<SUBMIT>", "").strip()
        block[f"gt_code_block_q{i}"] = gt_blocks[i].replace("<SUBMIT>", "").strip()

    return [block]


def process_type_3(row, counter_dict, file_tag):
    gt_blocks = extract_code_blocks(row.get("output_gt", ""), is_gt=True)[:1]
    syn_blocks = extract_code_blocks(row.get("output_synthetic", ""), is_gt=False)[:1]

    if len(gt_blocks) != len(syn_blocks) or len(gt_blocks) == 0:
        block = row.copy()
        key = (row["student_id"], row["question_name"])
        counter_dict.setdefault(key, 1)
        block["is_processed"] = False
        block["synthetic_code_block"] = ""
        block["gt_code_block"] = ""
        block["block_num"] = counter_dict[key]
        block["is_submitted_syn"] = "<SUBMIT>" in row.get("output_synthetic", "")
        block["is_submitted_gt"] = "<SUBMIT>" in row.get("output_gt", "")
        counter_dict[key] += 1
        return [block]

    key = (row["student_id"], row["question_name"])
    counter_dict.setdefault(key, 1)
    rows = []

    for i in range(len(gt_blocks)):
        gt = gt_blocks[i]
        syn = syn_blocks[i]

        block = row.copy()
        block["is_processed"] = True
        block["is_submitted_syn"] = "<SUBMIT>" in syn
        block["is_submitted_gt"] = "<SUBMIT>" in gt
        block["block_num"] = counter_dict[key]
        block["synthetic_code_block"] = syn.replace("<SUBMIT>", "").strip()
        block["gt_code_block"] = gt.replace("<SUBMIT>", "").strip()
        counter_dict[key] += 1
        rows.append(block)

    return rows

def process_file(input_path, output_path):
    with open(input_path) as f:
        lines = [json.loads(line) for line in f if line.strip()]

    file_tag = os.path.basename(input_path)
    out_rows = []
    block_counters = {}

    for row in lines:
        if "_1_" in file_tag:
            out_rows.extend(process_type_1(row))
        elif "_2_" in file_tag:
            out_rows.extend(process_type_2(row))
        elif "_3_" in file_tag:
            out_rows.extend(process_type_3(row, block_counters, file_tag))

    with open(output_path, "w") as f:
        for row in out_rows:
            f.write(json.dumps(row) + "\n")
    
    input_count = len(lines)
    output_count = len(out_rows)
    print(f"{os.path.basename(input_path)} → {os.path.basename(output_path)} ({output_count} rows, input = {input_count})")

    if "_1_" in file_tag or "_2_" in file_tag:
        if input_count != output_count:
            print(f"Row count mismatch: input={input_count}, output={output_count}")
        else:
            print("Input and output row count match")

    unprocessed = [i for i, r in enumerate(out_rows) if not r.get("is_processed", True)]
    global total_skipped
    total_skipped += len(unprocessed)

    if unprocessed:
        print(f"Skipped in this file: {len(unprocessed)}")
        for idx in unprocessed:
            r = out_rows[idx]
            print(f"  - index: {idx}, student_id: {r.get('student_id')}, question: {r.get('question_name')}, block_num: {r.get('block_num', '?')}")


for fname in os.listdir(INPUT_DIR):
    if fname.endswith(".jsonl"):
        in_path = os.path.join(INPUT_DIR, fname)
        out_path = os.path.join(OUTPUT_DIR, fname.replace(".jsonl", "_formatted.jsonl"))
        process_file(in_path, out_path)

print(f"\nTotal skipped across all files: {total_skipped}")

