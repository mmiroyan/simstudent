import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent.parent 

train_path = root / "data_processing/data/output/train.jsonl"
test_path  = root / "data_processing/data/output/processed_test/test_exp1_1_prior1.json"
output_dir = root / "evals" / "test_class"
output_dir.mkdir(parents=True, exist_ok=True)

with open(train_path) as f:
    train = [json.loads(line) for line in f]
with open(test_path) as f:
    test = json.load(f)

train_students   = set(x.get("student_id") for x in train)
train_questions  = set(x.get("question_name") for x in train)
test1, test2, test3, test4 = [], [], [], []

for x in test:
    x = x.get("INPUT", {}) 

    sid = x.get("student_id")
    qname = x.get("question_name")

    if sid not in train_students and qname in train_questions:
        test1.append((sid, qname))
    elif sid in train_students and qname not in train_questions:
        test2.append((sid, qname))
    elif sid not in train_students and qname not in train_questions:
        test3.append((sid, qname))
    elif sid in train_students and qname in train_questions:
        test4.append((sid, qname))

(json_path := output_dir / "test1.json").write_text(json.dumps(test1, indent=2))
(json_path := output_dir / "test2.json").write_text(json.dumps(test2, indent=2))
(json_path := output_dir / "test3.json").write_text(json.dumps(test3, indent=2))
(json_path := output_dir / "test4.json").write_text(json.dumps(test4, indent=2))

print("Saved 4 test sets.")
