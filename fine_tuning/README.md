# Fine-tuning

## Data

We do not release our data pipeline as the filtering and processing logic is specific to the course. The resulting data has the following schemas:

### **Experiment 1** (low-resolution setting)
`"OUTPUT"` is the student's code submission. `"skeleton_code_fixed"` is helper functions provided to the student that are not supposed to be changed. `"skeleton_code_todo"` is the starter code that needs to be implemented by the student. `"stage"` is `"submission_first"`, `"submission_mid"`, `"submission_last"`, indicating the position of the output code in the student's submission stream. ` "past_problem_submissions"` contains the student's code submission for a past problem; used in the with-context experiment only.

Datasets: `train_exp1_without_context.json`, `train_exp1_with_context.json`.
```
{
    "INPUT":
    {
        "student_id": str,
        "semester: str,
        "assignment_name": str,
        "question_name": str,
        "instructions": str,
        "skeleton_code_fixed": str,
        "skeleton_code_todo": str,
        "stage": str,
        "past_problem_submissions": List[{"question_name": str, "submission": str}]
    }
    "OUTPUT": str
}
```

### **Experiment 2** (high-resolution setting)
`"curr_problem_prior_submissions"` contains the student's past `k` submissions for the current problem (`k=1,3`). `"past_problem_submissions"` contains the segment (`len=k+1`) of the student's submission stream for a past problem (same relative position in the stream as the current `"OUTPUT"` code); used in the with-context experiments only.

Datasets: `train_exp2_without_context_k1.json`, `train_exp2_without_context_k3.json`, `train_exp2_with_context_k1.json`, `train_exp2_with_context_k3.json`. 

```
{
    "INPUT":
    {
        "student_id": str,
        "semester: str,
        "assignment_name": str,
        "question_name": str,
        "instructions": str,
        "skeleton_code_fixed": str,
        "skeleton_code_todo": str,
        "curr_problem_prior_submissions": List[str],
        "past_problem_submissions": List[{"question_name": str, "submissions": List[str]}]
    }
    "OUTPUT": str
}
```

## Training

`templates.py`: Input and output text templates for formatting input / output pairs for experiments 1 and 2.

`utils.py`: Helper functions for data preparation used in `fine_tune.py`.

`fine_tune.py`: Fine-tuning script:
- Data: The dataset (`dataset_file`) should have the schema described above.
- Fine-tuning: Loss is computed only on the completion tokens (i.e., output code). LoRA fine-tuning with the causal LM objective.
