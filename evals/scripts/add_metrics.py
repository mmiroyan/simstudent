import json
import ast
import pycodestyle
from tqdm import tqdm
import os
import argparse
import signal
import warnings
import multiprocessing as mp
mp.set_start_method("fork")

from autograder import Autograder

parser = argparse.ArgumentParser()
parser.add_argument("--input_dir", required=True)
parser.add_argument("--output_dir", required=True)
args = parser.parse_args()

INPUT_DIR  = args.input_dir
OUTPUT_DIR = args.output_dir
TEST_FILES_DIR = "../doc_tests"
TEST_CLASS_DIR = "../test_class"


os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.makedirs(OUTPUT_DIR, exist_ok=True)

warnings.filterwarnings("ignore", message=".*optimum is not installed.*")
style_guide     = pycodestyle.StyleGuide(quiet=True)

def _timeout_handler(signum, frame):
    raise TimeoutError("entry timed out")

test_class_map = {}
for fname in os.listdir(TEST_CLASS_DIR):
    if not fname.endswith(".json"):
        continue
    cls = os.path.splitext(fname)[0]
    path = os.path.join(TEST_CLASS_DIR, fname)
    with open(path) as tf:
        pairs = json.load(tf)
    for sid, qn in pairs:
        test_class_map[(sid, qn)] = cls


feature_cache = {}

class CaptureReport(pycodestyle.BaseReport):
    def __init__(self, options):
        super().__init__(options)
        self.errors = []

    def error(self, line_number, offset, text, check):
        code = super().error(line_number, offset, text, check)
        if code:
            self.errors.append({
                "line": line_number,
                "col": offset,
                "msg": text
            })
        return code

def count_pep8_violations(code):
    if not code.endswith('\n'):
        code += '\n'

    wrapper = "def _tmp_func():\n"
    for line in code.strip().splitlines():
        wrapper += f"    {line.rstrip()}\n"

    report = CaptureReport(style_guide.options)
    checker = pycodestyle.Checker(
        lines=wrapper.splitlines(),
        report=report
    )
    checker.check_all()
    return {
        "count": checker.report.total_errors,
        "messages": report.errors
    }


def get_ast_tree_metrics(code):
    try:
        tree = ast.parse(code.strip())
    except:
        return -1, -1, -1, -1

    max_depth = node_count = total_children = non_leaf = 0
    widths = {}
    def visit(node, depth=0):
        nonlocal max_depth, node_count, total_children, non_leaf
        max_depth = max(max_depth, depth)
        widths[depth] = widths.get(depth, 0) + 1
        node_count += 1
        children = list(ast.iter_child_nodes(node))
        total_children += len(children)
        if children:
            non_leaf += 1
        for c in children:
            visit(c, depth+1)
    visit(tree)
    avg_branch = total_children / non_leaf if non_leaf else 0
    max_width  = max(widths.values()) if widths else 0
    return max_depth, max_width, node_count, avg_branch

def extract_features(code: str):
    key = code.strip()
    if key.upper() == "NONE" or key == "":
        return None
    if key in feature_cache:
        return feature_cache[key]

    cleaned = code.strip()
    depth, width, nodes, branch = get_ast_tree_metrics(code)

    feat = {
        "loc": cleaned.count("\n") + 1,
        "char_count": len(cleaned),
        "pep8_violations": count_pep8_violations(cleaned),
        "ast_depth": depth,
        "ast_width": width,
        "ast_node_count": nodes,
        "ast_avg_branching": branch
    }
    feature_cache[key] = feat
    return feat

if __name__ == "__main__":
    for filename in os.listdir(INPUT_DIR):

        in_path  = os.path.join(INPUT_DIR,  filename)
        out_path = os.path.join(
            OUTPUT_DIR,
            filename.replace("_formatted", "_with_features")
        )

        if os.path.exists(out_path):
            print(f"Skipping {filename} — already processed.")
            continue

        with open(in_path) as f:
            data = [json.loads(line) for line in f if line.strip()]


        results = []

        for row in tqdm(data, desc=filename):
            if row["question_name"] == "Mint" or row.get("is_processed") is False:
                results.append(row)
                continue

            signal.signal(signal.SIGALRM, _timeout_handler)
            signal.alarm(30)

            try:
                tc = test_class_map.get((row["student_id"], row["question_name"]), None)
                test_file = f"{row['semester']}_{row['question_name']}.py"
                test_path = os.path.join(TEST_FILES_DIR, test_file)

                if "_1_" in filename or "_3_" in filename:
                    for side in ["synthetic", "gt"]:
                        key = f"{side}_code_block"
                        code = row.get(key, "").strip()
                        if code == "" or code.upper() == "NONE":
                            row[f"{key}_features"] = None
                            row[f"{key}_autograder"] = None
                        else:
                            row[f"{key}_features"] = extract_features(code)
                            row[f"{key}_autograder"] = Autograder.grade_submission(code, test_path)

                elif "_2_" in filename:
                    for i in range(3):
                        for side in ["synthetic", "gt"]:
                            key = f"{side}_code_block_q{i}"
                            code = row.get(key, "").strip()
                            if code == "" or code.upper() == "NONE":
                                row[f"{key}_features"] = None
                                row[f"{key}_autograder"] = None
                            else:
                                row[f"{key}_features"] = extract_features(code)
                                row[f"{key}_autograder"] = Autograder.grade_submission(code, test_path)

                new_row = {"test_class": tc}
                for k, v in row.items():
                    new_row[k] = v
                results.append(new_row)


            except TimeoutError:
                if "_2_" in filename:
                    for i in range(3):
                        for side in ["gt", "synthetic"]:
                            key = f"{side}_code_block_q{i}"
                            row[f"{key}_features"] = None
                            row[f"{key}_autograder"] = None
                else:
                    for side in ["gt", "synthetic"]:
                        key = f"{side}_code_block"
                        row[f"{key}_features"] = None
                        row[f"{key}_autograder"] = None

                new_row = {"test_class": tc}
                for k, v in row.items():
                    new_row[k] = v
                results.append(new_row)


            finally:
                signal.alarm(0)


        with open(out_path, "w") as f:
            for row in results:
                f.write(json.dumps(row) + "\n")