import time
import random
import json
import pandas as pd
from pathlib import Path
from typing import List, Tuple
from .config import logger, EvalConfig

try:
    # Import parallm for efficient response collection
    from parallm import query_model_all, query_model
    HAS_PARALLM = True
    llm = None  # We won't use llm when parallm is available
except ImportError:
    # This should not happen with normal installation as parallm is now a core dependency
    logger.error("Could not import 'parallm' module. This is a required dependency for SlopRank.")
    logger.error("Please ensure parallm is installed with: pip install parallm")
    logger.warning("Falling back to llm or mock response generation (not recommended for production).")
    HAS_PARALLM = False
    try:
        # If you have a custom LLM module that provides get_model()
        import llm
    except ImportError:
        logger.warning("Could not import 'llm' module. Provide your own LLM interface or mock it.")
        llm = None

def collect_responses(prompt_pairs: List[Tuple[str, str]], config: EvalConfig) -> pd.DataFrame:
    """
    Query each model with each prompt, skipping existing entries in responses.csv.
    """
    resp_path = config.output_dir / "responses.csv"
    if resp_path.exists():
        existing_df = pd.read_csv(resp_path)
    else:
        existing_df = pd.DataFrame(columns=["prompt","model"])

    # Extract prompts and answer keys
    prompts = [p[0] for p in prompt_pairs]
    answer_keys = [p[1] for p in prompt_pairs]

    # If we have parallm, use it for batch processing
    if HAS_PARALLM:
        logger.info(f"Using parallm to query {len(config.model_names)} models for {len(prompts)} prompts...")
        
        # Create a temporary CSV with the prompts using the "Questions" column
        prompts_df = pd.DataFrame({"Questions": prompts})
        temp_prompts_path = config.output_dir / "temp_prompts.csv"
        prompts_df.to_csv(temp_prompts_path, index=False)
        
        # Add "prompt" column for parallm compatibility
        prompts_df["prompt"] = prompts_df["Questions"]
        temp_prompts_modified_path = config.output_dir / "temp_prompts_modified.csv"
        prompts_df.to_csv(temp_prompts_modified_path, index=False)
        
        # Use parallm to query all models at once with the modified CSV
        responses_df = query_model_all(str(temp_prompts_modified_path), config.model_names)
        
        # Check if output.csv was created by parallm and use that instead if it exists
        output_path = Path("output.csv")
        if output_path.exists():
            logger.info(f"Using outputs from {output_path}")
            responses_df = pd.read_csv(output_path)
            # Clean up parallm's output file
            import os
            os.remove(output_path)
        
        # Add answer keys and additional metadata
        responses_df['Answer_key'] = responses_df['prompt'].map(dict(zip(prompts, answer_keys)))
        responses_df['is_valid'] = responses_df['response'].apply(lambda x: bool(x and len(str(x).strip()) >= 10))
        responses_df['token_count'] = responses_df['response'].apply(lambda x: len(str(x).split()) if x else 0)
        responses_df['response_time'] = 0.0  # Default value since parallm doesn't track this
        responses_df['error'] = None  # Default value
        
        # Clean up temp files
        import os
        for path in [temp_prompts_path, temp_prompts_modified_path]:
            if os.path.exists(path):
                logger.info(f"Cleaning up temporary file: {path}")
                os.remove(path)
    else:
        # Fall back to original implementation
        new_rows = []
        for i, (prompt, answer_key) in enumerate(prompt_pairs, start=1):
            logger.info(f"Processing prompt {i}/{len(prompt_pairs)}: {prompt[:50]}...")

            for model_name in config.model_names:
                # Check if we already have a response
                subset = existing_df[
                    (existing_df["prompt"] == prompt) &
                    (existing_df["model"] == model_name)
                ]
                if not subset.empty:
                    logger.info(f"Skipping existing response for model={model_name}, prompt={prompt[:40]}...")
                    continue

                start_time = time.time()
                logger.info(f"Querying {model_name} for new response...")
                raw_response = None
                tokens_used = 0
                valid = False
                error_msg = None

                try:
                    if llm is not None:
                        model = llm.get_model(model_name)
                        response_obj = model.prompt(prompt)
                        raw_response = response_obj.text()
                    else:
                        # fallback mock
                        raw_response = f"[MOCK] {model_name} responding to: {prompt[:40]}"

                    valid = (raw_response and len(raw_response.strip()) >= 10)
                    tokens_used = len(raw_response.split()) if valid else 0

                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"Error from {model_name}: {error_msg}")

                elapsed = time.time() - start_time

                new_rows.append({
                    'prompt': prompt,
                    'model': model_name,
                    'response': raw_response if valid else None,
                    'is_valid': valid,
                    'response_time': elapsed,
                    'Answer_key': answer_key,
                    'token_count': tokens_used,
                    'error': error_msg
                })

                if config.request_delay > 0:
                    time.sleep(config.request_delay)

        responses_df = pd.DataFrame(new_rows)

    # Combine with existing responses
    combined_df = pd.concat([existing_df, responses_df], ignore_index=True)
    combined_df.drop_duplicates(subset=["prompt","model"], keep="first", inplace=True)
    combined_df.to_csv(resp_path, index=False)
    logger.info(f"Responses saved to {resp_path}")
    return combined_df

def collect_raw_evaluations(responses_df: pd.DataFrame, config: EvalConfig) -> pd.DataFrame:
    """
    Each model in config.model_names evaluates the others' answers.
    Results are stored in raw_evaluations.csv as [prompt, judge_model, raw_judgment, model_mapping].
    """
    raw_eval_path = config.output_dir / "raw_evaluations.csv"
    if raw_eval_path.exists():
        existing_df = pd.read_csv(raw_eval_path)
    else:
        existing_df = pd.DataFrame(columns=["prompt","judge_model","model_mapping"])

    # Collect all evaluation prompts
    eval_tasks = []
    unique_prompts = responses_df['prompt'].unique()

    for prompt in unique_prompts:
        subset = responses_df[responses_df['prompt'] == prompt]
        answer_key = subset['Answer_key'].iloc[0] if 'Answer_key' in subset.columns else None
        model_response_map = subset.set_index('model')['response'].to_dict()

        for judge_model in config.model_names:
            # Exclude judge's own or missing responses
            other_models = [m for m in config.model_names
                           if m != judge_model and model_response_map.get(m)]
            if not other_models:
                continue
            if config.use_subset_evaluation:
                sample_size = min(config.evaluators_subset_size, len(other_models))
                other_models = random.sample(other_models, sample_size)

            model_to_anon = {m: f"Model_{i+1}" for i,m in enumerate(other_models)}
            answers_section = "\n".join([
                f"{model_to_anon[m]}:\n{model_response_map[m]}\n---"
                for m in other_models
            ])
            answer_key_text = f"The Answer Key is:\n{answer_key}\n---\n" if answer_key else ""

            model_mapping_str = json.dumps(model_to_anon, sort_keys=True)
            found_match = existing_df[
                (existing_df["prompt"] == prompt) &
                (existing_df["judge_model"] == judge_model) &
                (existing_df["model_mapping"] == model_mapping_str)
            ]
            if not found_match.empty:
                logger.info(f"Skipping existing raw eval for judge={judge_model}, prompt={prompt[:40]}...")
                continue

            instructions = f"""
You are an evaluator. Score each model's answer (1-10) in JSON format.

Important! Your response MUST be a valid JSON object with the exact format:
{{"Model_1": 7, "Model_2": 9}}

Problem:
{prompt}

Answers:
{answers_section}

{answer_key_text}

After reading each answer, assign a score from 1-10. Return your scores in JSON format ONLY without explanations.
"""

            eval_tasks.append({
                "prompt": prompt,
                "judge_model": judge_model,
                "evaluation_prompt": instructions,
                "model_mapping": model_mapping_str
            })

    # If no new evaluations needed, return existing ones
    if not eval_tasks:
        logger.info("No new evaluations needed, returning existing data")
        return existing_df

    new_judgments = []
    
    # Process all evaluation tasks individually - simpler and more reliable
    logger.info(f"Processing {len(eval_tasks)} evaluation tasks individually")
    
    # Group tasks by judge_model for better organization in logs
    judge_models = set(task["judge_model"] for task in eval_tasks)
    for judge_model in judge_models:
        model_tasks = [task for task in eval_tasks if task["judge_model"] == judge_model]
        logger.info(f"Processing {len(model_tasks)} evaluations for judge={judge_model}")
        
        for i, task in enumerate(model_tasks):
            logger.info(f"Evaluation {i+1}/{len(model_tasks)} for {judge_model}")
            
            raw_judgment = None
            try:
                # Use parallm's query_model if available (correct parameter order)
                if HAS_PARALLM:
                    logger.info(f"Querying {judge_model} with evaluation prompt")
                    raw_judgment = query_model(task["evaluation_prompt"], judge_model)
                elif llm is not None:
                    logger.info(f"Querying {judge_model} via llm")
                    judge_obj = llm.get_model(judge_model)
                    judge_resp = judge_obj.prompt(task["evaluation_prompt"])
                    raw_judgment = judge_resp.text()
                else:
                    # fallback mock data
                    raw_judgment = '{"Model_1": 8, "Model_2": 6}'
                
                # Log successful query
                logger.info(f"Received response from {judge_model}: {raw_judgment[:50]}...")
                
            except Exception as e:
                logger.error(f"Error querying {judge_model}: {str(e)}")
                # Use fallback values on error
                raw_judgment = '{"Model_1": 5, "Model_2": 5}'
            
            # Add to new judgments
            new_judgments.append({
                "prompt": task["prompt"],
                "judge_model": task["judge_model"],
                "raw_judgment": raw_judgment,
                "model_mapping": task["model_mapping"],
                "raw_judgment_token_count": len(raw_judgment.split()) if raw_judgment else 0
            })

    new_df = pd.DataFrame(new_judgments)
    # Only create combined_df if there are new judgments
    if not new_df.empty:
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        combined_df.drop_duplicates(subset=["prompt","judge_model","model_mapping"], keep="first", inplace=True)
        combined_df.to_csv(raw_eval_path, index=False)
        logger.info(f"Raw evaluations saved to {raw_eval_path}")
        return combined_df
    else:
        logger.info("No new evaluations were created")
        return existing_df