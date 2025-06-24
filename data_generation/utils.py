import re
from templates import *

def process_instructions(instructions):
    instructions = re.sub(r"\n+", "\n", instructions)
    return instructions.strip()

def process_stage(stage, prompt_template="ft"):
    if prompt_template == "ft":
        return " ".join(stage.split("_")).upper()
    else:
        mapping = {
            "submission_q0": "first",
            "submission_q1": "mid-point",
            "submission_q2": "final",    
        }
        return mapping[stage]


########################################################
# EXPERIMENT 1
########################################################

##################
# without context
##################

def process_input_exp1_without_context(example, prompt_template="ft"):
    input = example["INPUT"]
    template = EXP_1_WITHOUT_CONTEXT_INPUT_TEMPLATE_FT if prompt_template == "ft" else EXP_1_WITHOUT_CONTEXT_INPUT_TEMPLATE_PROMPTING
    processed_input = template.format(
        instructions=process_instructions(input["instructions"]),
        fixed_code=input["skeleton_code_fixed"].strip(),
        skeleton_code=input["skeleton_code_todo"].strip(),
        timestamp=process_stage(input["stage"], prompt_template)
    )
    return {"input": processed_input}

def process_output_exp1_without_context(example):
    student_code = f"<code>{example['OUTPUT'].strip()}</code>"
    return {"output": student_code}


##################
# with context
##################

def process_past_problem_submissions_exp1_with_context(example):
    past_problem_submissions = example["past_problem_submissions"]
    processed_past_submissions = ""
    for submission in past_problem_submissions:
        processed_past_submissions += (f"PROBLEM NAME: {submission['question_name']}\n"
                                       f"<code>{submission['submission'].strip()}</code>\n\n")
    return processed_past_submissions.strip()

def process_input_exp1_with_context(example, prompt_template="ft"):
    input = example["INPUT"]
    template = EXP_1_WITH_CONTEXT_INPUT_TEMPLATE_FT if prompt_template == "ft" else EXP_1_WITH_CONTEXT_INPUT_TEMPLATE_PROMPTING
    processed_input = template.format(
        past_problem_submissions=process_past_problem_submissions_exp1_with_context(input),
        instructions=process_instructions(input["instructions"]),
        fixed_code=input["skeleton_code_fixed"].strip(),
        skeleton_code=input["skeleton_code_todo"].strip(),
        timestamp=process_stage(input["stage"], prompt_template)
    )
    return {"input": processed_input}

def process_output_exp1_with_context(example):
    student_code = f"<code>{example['OUTPUT'].strip()}</code>"
    return {"output": student_code}


########################################################
# EXPERIMENT 2
########################################################

##################
# without context
##################

def process_curr_problem_prior_submissions_exp2_without_context(example):
    curr_problem_prior_submissions = example["curr_problem_prior_submissions"]
    processed_curr_submissions = ""
    for submission in curr_problem_prior_submissions:
        processed_curr_submissions += f"<code>{submission.strip()}</code>"
    return processed_curr_submissions

def process_input_exp2_without_context(example, prompt_template="ft"):
    input = example["INPUT"]
    template = EXP_2_WITHOUT_CONTEXT_INPUT_TEMPLATE_FT if prompt_template == "ft" else EXP_2_WITHOUT_CONTEXT_INPUT_TEMPLATE_PROMPTING
    processed_input = template.format(
        instructions=process_instructions(input["instructions"]),
        fixed_code=input["skeleton_code_fixed"].strip(),
        skeleton_code=input["skeleton_code_todo"].strip(),
        curr_problem_prior_submissions=process_curr_problem_prior_submissions_exp2_without_context(input)
    )
    return {"input": processed_input}

def process_output_exp2_without_context(example):
    student_code = f"<code>{example['OUTPUT'].strip()}</code>"
    return {"output": student_code}


##################
# with context
##################

def process_past_problem_submissions_exp2_with_context(example):
    past_problem_submissions = example["past_problem_submissions"]
    processed_past_submissions = ""
    for submission in past_problem_submissions:
        processed_past_submissions += (f"PROBLEM NAME: {submission['question_name']}\n")
        for submission_t in submission["submissions"]:
            processed_past_submissions += f"<code>{submission_t.strip()}</code>"
        processed_past_submissions += "\n\n"
    return processed_past_submissions.strip()

def process_curr_problem_prior_submissions_exp2_with_context(example):
    curr_problem_prior_submissions = example["curr_problem_prior_submissions"]
    processed_curr_submissions = ""
    for submission_t in curr_problem_prior_submissions:
        processed_curr_submissions += f"<code>{submission_t.strip()}</code>"
    return processed_curr_submissions

def process_input_exp2_with_context(example, prompt_template="ft"):
    input = example["INPUT"]
    template = EXP_2_WITH_CONTEXT_INPUT_TEMPLATE_FT if prompt_template == "ft" else EXP_2_WITH_CONTEXT_INPUT_TEMPLATE_PROMPTING
    processed_input = template.format(
        past_problem_submissions=process_past_problem_submissions_exp2_with_context(input),
        instructions=process_instructions(input["instructions"]),
        fixed_code=input["skeleton_code_fixed"].strip(),
        skeleton_code=input["skeleton_code_todo"].strip(),
        curr_problem_prior_submissions=process_curr_problem_prior_submissions_exp2_with_context(input)
    )
    return {"input": processed_input}

def process_output_exp2_with_context(example):
    student_code = f"<code>{example['OUTPUT'].strip()}</code>"
    return {"output": student_code}
