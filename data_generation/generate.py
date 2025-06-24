import time
import os
import json
import argparse
from tqdm import tqdm
import concurrent.futures

from litellm import completion
from openai import AzureOpenAI  

import torch
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM

from dotenv import load_dotenv
load_dotenv()

from utils import *

parser = argparse.ArgumentParser()
parser.add_argument("--config", type=str)
args = parser.parse_args()

with open(args.config, "r") as f:
    config_data = json.load(f)

class ScriptArguments:
    def __init__(self, config_dict):
        for key, value in config_dict.items():
            setattr(self, key, value)
script_args = ScriptArguments(config_data)
    

########################################################
# dataset
########################################################

def prepare_dataset(script_args: ScriptArguments):
    dataset = load_dataset("json", data_files=[script_args.input_data_path], split="train")
    if script_args.experiment_name == "exp1_without_context":
        dataset = dataset.map(lambda x: process_input_exp1_without_context(x, script_args.prompt_template), load_from_cache_file=False)
        dataset = dataset.map(process_output_exp1_without_context, load_from_cache_file=False)
    elif script_args.experiment_name == "exp1_with_context":
        dataset = dataset.map(lambda x: process_input_exp1_with_context(x, script_args.prompt_template), load_from_cache_file=False)
        dataset = dataset.map(process_output_exp1_with_context, load_from_cache_file=False)
    elif script_args.experiment_name == "exp2_without_context":
        dataset = dataset.map(lambda x: process_input_exp2_without_context(x, script_args.prompt_template), load_from_cache_file=False)
        dataset = dataset.map(process_output_exp2_without_context, load_from_cache_file=False)
    elif script_args.experiment_name == "exp2_with_context":
        dataset = dataset.map(lambda x: process_input_exp2_with_context(x, script_args.prompt_template), load_from_cache_file=False)
        dataset = dataset.map(process_output_exp2_with_context, load_from_cache_file=False)
    else:
        raise ValueError(f"Experiment name {script_args.experiment_name} not supported")
    dataset = dataset.remove_columns(["INPUT", "OUTPUT"])
    return dataset

dataset = prepare_dataset(script_args)
print(dataset)

########################################################
# model
########################################################

if script_args.model_type == "local":
    tokenizer = AutoTokenizer.from_pretrained(
        script_args.model_id,
        trust_remote_code=True,
        padding_side="left",
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.pad_token_id = tokenizer.eos_token_id
        
    model = AutoModelForCausalLM.from_pretrained(
        script_args.model_id,
        device_map="auto",
        torch_dtype=torch.bfloat16,
        trust_remote_code=True,
    )
    model.eval()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    sampling_params = {
        "do_sample": script_args.do_sample,
        "temperature": script_args.temperature,
        "top_p": script_args.top_p,
        "top_k": script_args.top_k,
        "min_p": script_args.min_p,
        "max_new_tokens": script_args.max_new_tokens,
        "pad_token_id": tokenizer.eos_token_id,
    }

    results = []
    for start_idx in tqdm(range(0, len(dataset), script_args.batch_size)):
        batch = dataset[start_idx:(start_idx+script_args.batch_size)]
        input_texts = batch["input"]
        output_texts_gt = batch["output"]
        inputs = tokenizer(
            input_texts,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=script_args.max_seq_length,
        ).to(device)
        
        with torch.no_grad():
            output_ids = model.generate(
                **inputs,
                **sampling_params,
            )
        decoded_outputs = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
        for idx, full_text in enumerate(decoded_outputs):
            input_text = input_texts[idx]
            output_text = full_text[len(input_text):]
            result = {
                "input": input_text,
                "output_synthetic": output_text,
                "output_gt": output_texts_gt[idx],
            }
            results.append(result)
            with open(script_args.output_data_path, "a") as f:
                f.write(json.dumps(result, ensure_ascii=False) + "\n")
                
elif script_args.model_type == "azure_openai":
    results = []
    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_API_BASE"),
        api_key=os.getenv("AZURE_API_KEY"),
        api_version=os.getenv("AZURE_API_VERSION"),
    )
    def process_example_azure(example, max_retries=5):
        input_text = example["input"]
        output_text_gt = example["output"]
        num_retries = 0
        while True:
            try:
                response = client.chat.completions.create(
                    model=script_args.model_id,
                    messages=[
                        {"role": "system", "content": [{"type": "text", "text": script_args.system_prompt}]},
                        {"role": "user", "content": [{"type": "text", "text": input_text}]}
                    ],
                    max_tokens=script_args.max_new_tokens,
                    temperature=script_args.temperature,
                    top_p=script_args.top_p,
                )
                output_text = response.choices[0].message.content
                break
            except Exception as e:
                if num_retries < max_retries:
                    num_retries += 1
                    time.sleep(30)
                    continue
                else:
                    print(f"Error processing example: {e}")
                    output_text = f"ERRORED ({e})"
                    break
        return {
            "input": input_text,
            "output_synthetic": output_text,
            "output_gt": output_text_gt,
        }

    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        results = list(tqdm(executor.map(process_example_azure, dataset), total=len(dataset)))

elif script_args.model_type == "vllm":
    results = []

    def process_example_vllm(example):
        input_text = example["input"]
        output_text_gt = example["output"]
        try:
            response = completion(
                model=f"hosted_vllm/{script_args.model_id}",
                messages=[
                    {"role": "system", "content": script_args.system_prompt},
                    {"role": "user", "content": input_text}
                ],
                api_base=script_args.api_base,
                max_tokens=script_args.max_new_tokens,
                temperature=script_args.temperature,
                top_p=script_args.top_p,
                top_k=script_args.top_k,
                min_p=script_args.min_p,
            )
            output_text = response["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Error processing example: {e}")
            output_text = f"ERRORED ({e})"
        return {
            "input": input_text,
            "output_synthetic": output_text,
            "output_gt": output_text_gt,
        }

    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        results = list(tqdm(executor.map(process_example_vllm, dataset), total=len(dataset)))

else:
    raise ValueError(f"Model type {script_args.model_type} not supported")

with open(script_args.output_data_path, "w") as f:
    for result in results:
        f.write(json.dumps(result, ensure_ascii=False) + "\n")
        
print(f"Results saved to {script_args.output_data_path}")
