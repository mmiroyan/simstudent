<div align="center">
  <img src="logo.png" width="200" height="200">

  <h1>SimStudent: Generating and Evaluating Realistic Student Code by Teaching LLMs to Struggle</h1>

</div>

---

**Paper**: [**SimStudent: Generating and Evaluating Realistic Student Code by Teaching LLMs to Struggle**](TODO)

**Authors**: [Mihran Miroyan*](https://mmiroyan.github.io/), [Rose Niousha*](https://www.linkedin.com/in/rose-niousha), [Joseph E. Gonzalez](https://people.eecs.berkeley.edu/~jegonzal/), [Gireeja Ranade](https://people.eecs.berkeley.edu/~gireeja/), [Narges Norouzi](https://nargesnorouzi.me//) (UC Berkeley)

TL;DR We study student modeling through generating student-like code submissions. We find that fine-tuning is important for "unlearning" professional code and learn how to code like a student. Evaluation is important for capturing different aspects of student-like code.

## Key Findings from SimStudent
1. Evaluation metrics. We introduce a set of metrics, including code semantics, error type, and code style, to evaluate the realism of “student-like” code.

2. Sequential code modeling. We fine-tune on low- and high-resolution student code streams to simulate realistic learning trajectories on different levels of granularity.

3. Fine-tuning vs. prompting. We find that when models are fine-tuned on student code to specific homework problems, they outperform prompting-only models along the proposed set of metrics.

Please read our paper for more details. This repo contains scripts for fine-tuning, generation, and evaluation code. We do not release real / synthetic data and our data processing pipeline due to student privacy.

## Repository Structure

Install all necessary dependencies: ``pip3 install -r requirements.txt``

**`fine_tuning/`**: Fine-tuning prompt templates and the training script (see more details in [`fine_tuning/README.md`](./fine_tuning/README.md))

**`data_generation/`**: Prompt templates and script for data generation (see more details in [`data_generation/README.md`](./data_generation/README.md)).

**`evals/`**: Scripts for running evaluations, computing metrics, and visualizing results (see more details in [`evals/README.md`](./evals/README.md)).

## Citations
```
TODO
```