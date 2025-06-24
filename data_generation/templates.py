########################################################
# TEMPLATES FOR FINE-TUNED MODELS
########################################################

########################################################
# EXPERIMENT 1
########################################################

EXP_1_WITHOUT_CONTEXT_INPUT_TEMPLATE_FT = """PROBLEM INSTRUCTIONS:
{instructions}

FIXED CODE:
<code>{fixed_code}</code>

TODO CODE:
<code>{skeleton_code}</code>

{timestamp}:
"""

EXP_1_WITH_CONTEXT_INPUT_TEMPLATE_FT = """PAST PROBLEM SUBMISSIONS:
{past_problem_submissions}

PROBLEM INSTRUCTIONS:
{instructions}

FIXED CODE:
<code>{fixed_code}</code>

TODO CODE:
<code>{skeleton_code}</code>

{timestamp}:
"""

########################################################
# EXPERIMENT 2
########################################################

EXP_2_WITHOUT_CONTEXT_INPUT_TEMPLATE_FT = """PROBLEM INSTRUCTIONS:
{instructions}

FIXED CODE:
<code>{fixed_code}</code>

TODO CODE:
<code>{skeleton_code}</code>

SUBMISSIONS:
{curr_problem_prior_submissions}
"""

EXP_2_WITH_CONTEXT_INPUT_TEMPLATE_FT = """PAST PROBLEM SUBMISSIONS:
{past_problem_submissions}

PROBLEM INSTRUCTIONS:
{instructions}

FIXED CODE:
<code>{fixed_code}</code>

TODO CODE:
<code>{skeleton_code}</code>

SUBMISSIONS:
{curr_problem_prior_submissions}
"""


########################################################
# TEMPLATES FOR PROMPTING
########################################################

########################################################
# EXPERIMENT 1
########################################################

EXP_1_WITHOUT_CONTEXT_INPUT_TEMPLATE_PROMPTING = """PROBLEM INSTRUCTIONS:
{instructions}

FIXED CODE:
<code>{fixed_code}</code>

TODO CODE:
<code>{skeleton_code}</code>

You are simulating a student taking an introduction to Python programming course.
Generate the student's {timestamp} attempt at the TODO CODE of the current problem.
* You may only implement functions and classes in the TODO CODE. Do not include docstrings.
* FIXED CODE (if any) is provided for you. Do not modify or include it in your attempt. Do not include any other code.
* Wrap the generated code in <code> and </code> tags so that it can be easily extracted.
"""

EXP_1_WITH_CONTEXT_INPUT_TEMPLATE_PROMPTING = """PAST PROBLEM SUBMISSIONS:
{past_problem_submissions}

PROBLEM INSTRUCTIONS:
{instructions}

FIXED CODE:
<code>{fixed_code}</code>

TODO CODE:
<code>{skeleton_code}</code>

You are simulating a student taking an introduction to Python programming course.
Generate the student's {timestamp} attempt at the TODO CODE of the current problem.
* You may only implement functions and classes in the TODO CODE. Do not include docstrings.
* FIXED CODE (if any) is provided for you. Do not modify or include it in your attempt. Do not include any other code.
* You are also provided with the student's {timestamp} attempt for a past problem from a past homework. Use it as a reference to predict the student's {timestamp} attempt for the current problem.
* Wrap the generated code in <code> and </code> tags so that it can be easily extracted.
"""

########################################################
# EXPERIMENT 2
########################################################

EXP_2_WITHOUT_CONTEXT_INPUT_TEMPLATE_PROMPTING = """PROBLEM INSTRUCTIONS:
{instructions}

FIXED CODE:
<code>{fixed_code}</code>

TODO CODE:
<code>{skeleton_code}</code>

SUBMISSIONS SO FAR:
{curr_problem_prior_submissions}

You are simulating a student taking an introduction to Python programming course.
Generate the student's next attempt at the TODO CODE of the current problem conditioned on their SUBMISSIONS SO FAR.
* You may only implement functions and classes in the TODO CODE. Do not include docstrings.
* FIXED CODE (if any) is provided for you. Do not modify or include it in your attempt. Do not include any other code.
* You are provided with the student's previous attempts for the current problem (SUBMISSIONS SO FAR). Use that progress for generating the student's next attempt.
* If all previous attempts are None, generate a first attempt.
* If the generated next attempt is the student's final attempt, append "<SUBMIT>" to the end of your attempt.
* Wrap the generated code in <code> and </code> tags so that it can be easily extracted.
"""

EXP_2_WITH_CONTEXT_INPUT_TEMPLATE_PROMPTING = """PAST PROBLEM SUBMISSIONS:
##############################
{past_problem_submissions}
##############################

PROBLEM INSTRUCTIONS:
##############################
{instructions}
##############################

FIXED CODE:
##############################
<code>{fixed_code}</code>
##############################

TODO CODE:
##############################
<code>{skeleton_code}</code>
##############################

SUBMISSIONS SO FAR:
##############################
{curr_problem_prior_submissions}
##############################

You are simulating a student taking an introduction to Python programming course.
Generate the student's next attempt at the TODO CODE of the current problem based on the SUBMISSIONS SO FAR.
* You may only implement functions and classes in the TODO CODE. Do not include docstrings.
* FIXED CODE (if any) is provided for you. Do not modify or include it in your attempt. Do not include any other code.
* You are provided with the student's previous attempts for the current problem (SUBMISSIONS SO FAR). Use that progress for generating the student's next attempt.
* If the generated next attempt is the student's final attempt, append "<SUBMIT>" to the end of your attempt.
* If all previous attempts are None, generate a first attempt.
* You are also provided with the student's previous attempts for a past problem from a past homework. Use it as a reference to predict the student's next attempt for the current problem.
* Wrap the generated code in <code> and </code> tags so that it can be easily extracted.
"""
