import os
import wandb
from dataclasses import dataclass

from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    Trainer,
    TrainingArguments,
    DataCollatorForSeq2Seq,
)
from peft import (
    LoraConfig,
    get_peft_model,
)

from utils import *

from dotenv import load_dotenv
load_dotenv()

@dataclass
class ScriptArguments:
    experiment_name: str = "INSERT_EXPERIMENT_NAME"
    dataset_file: str = "INSERT_PATH_TO_DATASET"
    test_size: float = 0.1
    # wandb
    wandb_entity: str = "INSERT_ENTITY"
    wandb_project: str = "INSERT_PROJECT"
    
@dataclass
class ModelConfig:
    model_name: str = "Qwen/Qwen2.5-Coder-7B"
    max_seq_length: int = 8192
    # lora params
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    lora_target_modules: str = "all-linear"
    lora_bias: str = "none"
    
training_args = TrainingArguments(
    output_dir="INSERT_OUTPUT_DIR/",
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    gradient_accumulation_steps=4,
    gradient_checkpointing=True,
    bf16=True,
    tf32=True,
    num_train_epochs=1,
    learning_rate=1e-4,
    lr_scheduler_type="cosine",
    logging_steps=25,
    eval_strategy="steps",
    eval_steps=25,
    save_strategy="steps",
    save_steps=300,
    # integrations
    report_to="wandb",
    run_name="INSERT_RUN_NAME",
    push_to_hub=True,
    hub_strategy="all_checkpoints",
    hub_model_id="INSERT_HF_MODEL_ID",
    hub_private_repo=True,
    hub_token=os.environ["HF_TOKEN"],
)

def prepare_dataset(script_args: ScriptArguments):
    dataset = load_dataset("json", data_files=script_args.dataset_file, split="train")
    if script_args.experiment_name == "exp1_without_context":
        dataset = dataset.map(process_input_exp1_without_context, load_from_cache_file=False)
        dataset = dataset.map(process_output_exp1_without_context, load_from_cache_file=False)
    elif script_args.experiment_name == "exp1_with_context":
        dataset = dataset.map(process_input_exp1_with_context, load_from_cache_file=False)
        dataset = dataset.map(process_output_exp1_with_context, load_from_cache_file=False)
    elif script_args.experiment_name == "exp2_without_context":
        dataset = dataset.map(process_input_exp2_without_context, load_from_cache_file=False)
        dataset = dataset.map(process_output_exp2_without_context, load_from_cache_file=False)
    elif script_args.experiment_name == "exp2_with_context":
        dataset = dataset.map(process_input_exp1_with_context, load_from_cache_file=False)
        dataset = dataset.map(process_output_exp1_with_context, load_from_cache_file=False)
    else:
        raise ValueError(f"Experiment name {script_args.experiment_name} not supported")
    dataset = dataset.remove_columns(["INPUT", "OUTPUT"])
    return dataset

script_args = ScriptArguments()
model_args = ModelConfig()

wandb.init(
    entity=script_args.wandb_entity,
    project=script_args.wandb_project,
    name=training_args.run_name,
)

########################################################
# dataset
########################################################

dataset = prepare_dataset(script_args)
split = dataset.train_test_split(
    shuffle=True,
    test_size=script_args.test_size,
    seed=42,
)
train_dataset, eval_dataset = split["train"], split["test"]

print("EXAMPLE:")
print("-" * 100)
print("INPUT:")
print(train_dataset[0]["input"])
print("-" * 100)
print("OUTPUT:")
print(train_dataset[0]["output"])
print("-" * 100)

print("Dataset stats:")
print(f"Train dataset: {train_dataset}")
print(f"Eval dataset: {eval_dataset}")
print("-" * 100)

tokenizer = AutoTokenizer.from_pretrained(model_args.model_name, trust_remote_code=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.pad_token_id = tokenizer.eos_token_id

def preprocess(example):
    input_text, output_text = example["input"], example["output"]
    tokenized_full = tokenizer(
        input_text + output_text,
        truncation=True,
        max_length=model_args.max_seq_length,
        return_tensors="pt",
    )
    input_ids_full = tokenized_full["input_ids"][0]
    input_tokenized = tokenizer(
        input_text,
        truncation=True,
        max_length=model_args.max_seq_length,
        return_tensors="pt",
    )
    split_idx = len(input_tokenized["input_ids"][0])
    labels = [-100] * split_idx + input_ids_full[split_idx:].tolist()
    return {
        "input_ids": input_ids_full.tolist(),
        "attention_mask": tokenized_full["attention_mask"][0].tolist(),
        "labels": labels,
    }

train_dataset = train_dataset.map(
    preprocess,
    remove_columns=train_dataset.column_names,
    batched=False,
    load_from_cache_file=False,
)
eval_dataset = eval_dataset.map(
    preprocess,
    remove_columns=eval_dataset.column_names,
    batched=False,
    load_from_cache_file=False,
)

data_collator = DataCollatorForSeq2Seq(
    tokenizer=tokenizer,
    model=None,
    padding="longest",
    max_length=model_args.max_seq_length,
    pad_to_multiple_of=8,
    label_pad_token_id=-100,
)

########################################################
# model
########################################################

model = AutoModelForCausalLM.from_pretrained(
    model_args.model_name,
    device_map="auto",
    trust_remote_code=True,
)
model.config.pad_token_id = tokenizer.pad_token_id
model.enable_input_require_grads() # https://github.com/huggingface/transformers/issues/23170

lora_config = LoraConfig(
    r=model_args.lora_r,
    lora_alpha=model_args.lora_alpha,
    lora_dropout=model_args.lora_dropout,
    target_modules=model_args.lora_target_modules,
    bias=model_args.lora_bias,
    task_type="CAUSAL_LM",
)
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

########################################################
# training
########################################################

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    data_collator=data_collator,
    processing_class=tokenizer,
)

trainer.train()

if training_args.push_to_hub:
    trainer.push_to_hub()
wandb.finish()
