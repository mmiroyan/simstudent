########################################################
# EXPERIMENT 1
########################################################

EXP_1_WITHOUT_CONTEXT_INPUT_TEMPLATE = """PROBLEM INSTRUCTIONS:
{instructions}

FIXED CODE:
<code>{fixed_code}</code>

TODO CODE:
<code>{skeleton_code}</code>

{timestamp}:
"""

EXP_1_WITH_CONTEXT_INPUT_TEMPLATE = """PAST PROBLEM SUBMISSIONS:
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

EXP_2_WITHOUT_CONTEXT_INPUT_TEMPLATE = """PROBLEM INSTRUCTIONS:
{instructions}

FIXED CODE:
<code>{fixed_code}</code>

TODO CODE:
<code>{skeleton_code}</code>

SUBMISSIONS:
{curr_problem_prior_submissions}
"""

EXP_2_WITH_CONTEXT_INPUT_TEMPLATE = """PAST PROBLEM SUBMISSIONS:
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
