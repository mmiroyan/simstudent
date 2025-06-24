import os
import json

# specify the target pairs for each semester

TARGET_PAIRS = {
    "sp21": ["two_of_three", "accumulate", "count_coins", "has_path", "store_digits"],
    "fa21": ["two_of_three", "accumulate", "count_coins", "has_path", "store_digits", "Mint"],
    "sp22": ["two_of_three", "accumulate", "count_coins", "has_path", "Mint"],
    "fa22": ["two_of_three", "accumulate", "count_coins", "has_path", "store_digits", "Mint"],
}

INPUT_PATH = "../data_processing/data/output/assignments_sp21_fa22_edited.jsonl"
OUTPUT_DIR = "../evals/doc_tests"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_pair_key(sample):
    return sample.get("semester"), sample.get("question_name")

def extract_codes(sample):
    return sample.get("skeleton_code_fixed", "").strip(), sample.get("skeleton_code_todo", "").strip()

def main():
    seen = set()
    with open(INPUT_PATH, "r") as f:
        samples = [json.loads(line) for line in f]

    for sample in samples:
        semester, question = extract_pair_key(sample)
        if semester not in TARGET_PAIRS or question not in TARGET_PAIRS[semester]:
            continue
        if (semester, question) in seen:
            continue
        seen.add((semester, question))

        fixed, todo = extract_codes(sample)
        if not todo:
            continue

        out_path = os.path.join(OUTPUT_DIR, f"{semester}_{question}.py")
        with open(out_path, "w") as out:
            if fixed:
                out.write("# === SKELETON CODE FIXED ===\n")
                out.write(f"{fixed}\n\n")
            out.write("# === SKELETON CODE TODO ===\n\n")
            out.write(f"{todo}\n")
        print(f"Generated: {out_path}")

if __name__ == "__main__":
    main()
