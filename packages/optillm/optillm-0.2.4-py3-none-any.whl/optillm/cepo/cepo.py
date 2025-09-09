import re
import yaml
import json
import optillm
from optillm import conversation_logger

from dataclasses import dataclass
from typing import Literal, Any, Optional
from cerebras.cloud.sdk import BadRequestError as CerebrasBadRequestError
from openai import BadRequestError as OpenAIBadRequestError


@dataclass
class CepoConfig:
    bestofn_n: int  # number of responses to be generated in best of n stage
    bestofn_temperature: float  # temperature for verifier in best of n stage
    bestofn_max_tokens: int  # maximum number of tokens for verifier in best of n stage
    bestofn_rating_type: Literal["absolute", "pairwise"]  # type of rating in best of n stage
    planning_n: int  # number of plans generated in planning stage
    planning_m: int  # number of attempts to generate n plans in planning stage
    planning_temperature_step1: float  # temperature for generator in step 1 of planning stage
    planning_temperature_step2: float  # temperature for generator in step 2 of planning stage
    planning_temperature_step3: float  # temperature for generator in step 3 of planning stage
    planning_temperature_step4: float  # temperature for generator in step 4 of planning stage
    planning_max_tokens_step1: int  # maximum number of tokens in step 1 of planning stage
    planning_max_tokens_step2: int  # maximum number of tokens in step 2 of planning stage
    planning_max_tokens_step3: int  # maximum number of tokens in step 3 of planning stage
    planning_max_tokens_step4: int  # maximum number of tokens in step 4 of planning stage
    use_plan_diversity: bool  # whether to use plan diversity
    rating_model: Optional[str] = None # model to be used for rating
    print_output: bool = False  # whether to print the output of each stage


# given command line arguments which includes a yaml file path, initialize a CePO configuration
def init_cepo_config(cmd_line_args: dict) -> CepoConfig:
    # get the command line arguments
    cepo_args = {
        key.split("cepo_")[1]: value
        for key, value in cmd_line_args.items()
        if "cepo" in key and "cepo_config_file" != key and value is not None
    }

    # get the yaml file arguments
    cepo_config_yaml = {}
    if cmd_line_args.get("cepo_config_file", None):
        with open(cmd_line_args["cepo_config_file"], "r") as yaml_file:
            cepo_config_yaml = yaml.safe_load(yaml_file)

    # merge cepo args from command line and yaml file, args from command line will overwrite the ones from yaml file
    cepo_args = {**cepo_config_yaml, **cepo_args}
    return CepoConfig(**cepo_args)


def extract_question_only(task: str) -> str:
    """We noticed that sometimes if the task includes specific formatting instructions, they may interfere with the reasoning flow. This
    is a temporary workaround to extract the question only from the task. Work in progress.
    """
    question_only = task.replace('\n## Question: \n\n', '')
    question_only = question_only.replace('\n\n\n## Instruction \n\nPlease answer this question by first reasoning and then providing your answer.\nPresent your reasoning and solution in the following json format. \nPlease show your final answer in the `answer` field, e.g.,`"answer": "42"`.\n\n```json\n{\n    "reasoning": "___",\n    "answer": "___"\n}\n```\n', '')
    return question_only


def generate_completion(system_prompt: str, task: str, client: Any, model: str, cepo_config: CepoConfig, approach: Optional[str] = None, request_id: str = None) -> str:
    """
    Generates a completion based on the provided system prompt and task.

    Parameters:
        system_prompt (str): The system prompt to guide the model.
        task (str): The task or question to be addressed.
        client (Any): The client instance for interacting with the AI model.
        model (str): The model name to be used for generating completions.
        cepo_config (CepoConfig): Configuration parameters for CePO flow.
        approach (str|None): optional approach that is used to seed plan generation.

    Returns:
        Tuple[str, int, dict]: The generated completion, number of tokens used, and a log dictionary.
    """
    completion_tokens = 0
    question_only = extract_question_only(task)
    cb_log = {}
    plans = []

    for i in range(cepo_config.planning_m):  # m is the maximum number of attempts to generate n plans
        # Step 1 - Generate a plan
        if cepo_config.use_plan_diversity:
            assert approach
            assert isinstance(approach, str)
            content = f"To answer this question, can you come up with a concise plan using to solve it step-by-step but do not provide the "\
                      f"final answer. Here is the approach you need to follow to generate the plan: {approach}. "\
                      f"Also, for each step, provide your confidence in the correctness of that step as well as your ability "\
                      f"to execute it correctly. Here is the question:\n{question_only}\nRead the question again:\n\n{question_only}"
        else:
            assert not approach
            content = f"To answer this question, can you come up with a concise plan to solve it step-by-step but do not provide the "\
                      f"final answer. Also, for each step, provide your confidence in the correctness of that step as well as your ability "\
                      f"to execute it correctly. Here is the question:\n{question_only}\nRead the question again:\n\n{question_only}" 

        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": content}]
        
        # Prepare request for logging
        provider_request = {
            "model": model,
            "messages": messages,
            "max_tokens": cepo_config.planning_max_tokens_step1,
            "temperature": cepo_config.planning_temperature_step1,
            "stream": False,
        }
        
        response = client.chat.completions.create(**provider_request)
        
        # Log provider call if conversation logging is enabled
        if hasattr(optillm, 'conversation_logger') and optillm.conversation_logger and request_id:
            response_dict = response.model_dump() if hasattr(response, 'model_dump') else response
            optillm.conversation_logger.log_provider_call(request_id, provider_request, response_dict)
        completion_tokens += response.usage.completion_tokens

        if response.choices[0].finish_reason == "length":
            # Skipping plan generation due to exceeding the token budget. Usually it means the plan is incomplete.
            continue

        # Step 2 - Execute the plan
        content = f"Can you execute the above plan step-by-step to produce the final answer. "\
                  f"Be extra careful when executing steps where your confidence is lower."
        messages.extend([{"role": "assistant", "content": response.choices[0].message.content}, {"role": "user", "content": content}])
        
        # Prepare request for logging
        provider_request = {
            "model": model,
            "messages": messages,
            "max_tokens": cepo_config.planning_max_tokens_step2,
            "temperature": cepo_config.planning_temperature_step2,
            "stream": False,
        }
        
        response = client.chat.completions.create(**provider_request)
        
        # Log provider call if conversation logging is enabled
        if hasattr(optillm, 'conversation_logger') and optillm.conversation_logger and request_id:
            response_dict = response.model_dump() if hasattr(response, 'model_dump') else response
            optillm.conversation_logger.log_provider_call(request_id, provider_request, response_dict)
        completion_tokens += response.usage.completion_tokens

        if response.choices[0].finish_reason == "length":
            messages.append({"role": "assistant", "content": response.choices[0].message.content})
            cb_log[f"messages_planning_{i}_rejected_due_to_length"] = messages
            if cepo_config.print_output:
                print(f"\nCePO: Plan proposal rejected due to length. Attempt {i + 1} out of {cepo_config.planning_m}.\nMessages: {messages}")
            continue

        plans.append(response.choices[0].message.content)
        messages.append({"role": "assistant", "content": response.choices[0].message.content})
        cb_log[f"messages_planning_{i}"] = messages
        if cepo_config.print_output:
            print(f"\nCePO: Plan proposal generated. Attempt {i + 1} out of {cepo_config.planning_m}.\nMessages: {messages}")
        
        if len(plans) == cepo_config.planning_n:
            break

    if not plans:
        # If no plans were generated succesfully, take the last one even if it was rejected due to length
        plans.append(response.choices[0].message.content)
        messages.append({"role": "assistant", "content": response.choices[0].message.content})
        cb_log[f"messages_planning_{i}_no_plans_so_taking_the_last_one"] = messages
        if cepo_config.print_output:
            print(f"\nCePO: No plans generated successfully. Taking the last one from rejected due to length.\nMessages: {messages}")

    # Step 3 - Review and address inconsistencies
    try:
        plans_message = ""
        for i, plan in enumerate(plans):
            plans_message += f"Response {i + 1}:\n{plan}\n\n"
        plans_message = plans_message[:-2]  # remove the last 2x newline
        content = f"Can you review your last {len(plans)} responses and identify any inconsistency between them. After that, can you address "\
                  f"it and present a final step-by-step solution to the problem? Here is the question:\n{question_only}"
        messages = [{"role": "assistant", "content": plans_message}, {"role": "user", "content": content}]

        # Prepare request for logging
        provider_request = {
            "model": model,
            "messages": messages,
            "max_tokens": cepo_config.planning_max_tokens_step3,
            "temperature": cepo_config.planning_temperature_step3,
            "stream": False,
        }
        
        response = client.chat.completions.create(**provider_request)
        
        # Log provider call if conversation logging is enabled
        if hasattr(optillm, 'conversation_logger') and optillm.conversation_logger and request_id:
            response_dict = response.model_dump() if hasattr(response, 'model_dump') else response
            optillm.conversation_logger.log_provider_call(request_id, provider_request, response_dict)
        final_solution = response.choices[0].message.content
        completion_tokens += response.usage.completion_tokens
    except (CerebrasBadRequestError, OpenAIBadRequestError) as e:
        # In case of an error, take the first plan as the final solution
        final_solution = plans[0]
        messages = []

    # Step 4 - Answer the question
    content = f"Use your final solution from above to correctly answer the question. Here is the question:\n{task}"
    messages = [{"role": "assistant", "content": final_solution}, {"role": "user", "content": content}]

    # Prepare request for logging
    provider_request = {
        "model": model,
        "messages": messages,
        "max_tokens": cepo_config.planning_max_tokens_step4,
        "temperature": cepo_config.planning_temperature_step4,
        "stream": False,
    }
    
    response = client.chat.completions.create(**provider_request)
    
    # Log provider call if conversation logging is enabled
    if hasattr(optillm, 'conversation_logger') and optillm.conversation_logger and request_id:
        response_dict = response.model_dump() if hasattr(response, 'model_dump') else response
        optillm.conversation_logger.log_provider_call(request_id, provider_request, response_dict)
    completion_tokens += response.usage.completion_tokens

    cb_log["messages"] = messages
    if cepo_config.print_output:
        print(f"\nCePO: Answer generated.\nMessages: {messages}")
    return response.choices[0].message.content, completion_tokens, cb_log


def generate_approaches(system_prompt: str, initial_query: str, num_approach: int, client: Any, model: str, cepo_config: CepoConfig, max_retry: int = 2, request_id: str = None) -> tuple[list[str], int]:
    completion_tokens = 0
    question_only = extract_question_only(initial_query)
    approaches = []
    content = f'To answer the question: "{question_only}", please propose {num_approach} different high-level approaches to solve the problem. '\
              f'All approaches should be fundamentally different from each other and easily excecutable without too much steps. Do not include a '\
              f'step-by-step plan or the final answer. You must present the approaches in the following JSON format which is directly loadable:\n'\
              f'{{\n'\
              f'    "approach_1": "<Description of approach 1>",\n'\
              f'    "approach_2": "<Description of approach 2>",\n'\
              f'    "approach_3": "<Description of approach 3>",\n'\
              f'    ...\n'\
              f'}}'
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": content}]
    
    retries = 0
    while retries < max_retry:
        try:
            # Prepare request for logging
            provider_request = {
                "model": model,
                "messages": messages,
                "max_tokens": cepo_config.planning_max_tokens_step0,
                "temperature": cepo_config.planning_temperature_step0,
                "stream": False,
            }
            
            response = client.chat.completions.create(**provider_request)
            
            # Log provider call if conversation logging is enabled
            if hasattr(optillm, 'conversation_logger') and optillm.conversation_logger and request_id:
                response_dict = response.model_dump() if hasattr(response, 'model_dump') else response
                optillm.conversation_logger.log_provider_call(request_id, provider_request, response_dict)
            completion_tokens += response.usage.completion_tokens
            completion = response.choices[0].message.content 

            # Try to parse the completion as JSON, escape latex math symbols
            cleaned_completion = completion.replace('\\', '\\\\').replace('json','').replace("```", "")
            for _, value in json.loads(cleaned_completion).items():
                approaches.append(value.replace('\\\\', '\\'))
            break  # Exit the loop if parsing is successful

        except json.JSONDecodeError as e:
            # If there's an error, print a message and regenerate the content
            print(e)
            print(f"Parsing Error when generating diverse approaches, retrying... ({retries + 1}/{max_retry})")
           
            retries += 1

    if retries == max_retry:
        print("Max retry attempts reached, returning empty list.")
        return [], 0  # Default approach
 
    return approaches, completion_tokens


def generate_n_completions(system_prompt: str, initial_query: str, client: Any, model: str, cepo_config: CepoConfig) -> tuple[list[str], int, dict]:
    """
    Generates n completions for the Best of N step of CePO.

    Parameters:
        system_prompt (str): The system prompt to guide the model.
        initial_query (str): The task or question to be addressed.
        client (Any): The client instance for interacting with the AI model.
        model (str): The model name to be used for generating completions.
        cepo_config (CepoConfig): Configuration parameters for CePO flow.

    Returns:
        Tuple[str, int, dict]: The generated completion, number of tokens used, and a log dictionary.
    """
    completion_tokens = 0
    cb_log = {}
    cb_log["system_prompt"] = system_prompt
    cb_log["initial_query"] = initial_query
    completions = []
    approaches = None

    # Generate Approach and Descriptions
    if cepo_config.use_plan_diversity:
        approaches, approach_completion_tokens = generate_approaches(
            system_prompt=system_prompt,
            initial_query=initial_query,
            num_approach=cepo_config.bestofn_n,
            client=client,
            model=model,
            cepo_config=cepo_config,
            request_id=request_id
        )
        cb_log["approaches"] = approaches
        completion_tokens += approach_completion_tokens
        if cepo_config.print_output:
            print(f"\nCePO: Plan diversity approaches ({cepo_config.bestofn_n}):\n{approaches}\n")

    for i in range(cepo_config.bestofn_n):
        if cepo_config.print_output:
            print(f"\nCePO: Generating completion {i + 1} out of {cepo_config.bestofn_n} \n")
        approach = approaches[i] if approaches else None
        response_i, completion_tokens_i, cb_log_i = generate_completion(system_prompt, initial_query, client, model, cepo_config, approach, request_id)
        completions.append(response_i)
        completion_tokens += completion_tokens_i
        cb_log[f"completion_{i}_response"] = response_i
        cb_log[f"completion_{i}_log"] = cb_log_i
        cb_log[f"completion_{i}_completion_tokens"] = completion_tokens_i

    return completions, completion_tokens, cb_log


def rate_completions_absolute(system_prompt: str, initial_query: str, client: Any, model: str, completions: list[str], cepo_config: CepoConfig, cb_log: dict, request_id: str = None) -> tuple[str, int, dict]:
    """
    Rates completions for the Best of N step of CePO. Each completion is rated on a scale of 1 to 10 individually.

    Parameters:
        system_prompt (str): The system prompt to guide the model.
        initial_query (str): The task or question to be addressed.
        client (Any): The client instance for interacting with the AI model.
        model (str): The model name to be used for generating completions.
        completions (list[str]): List of completions to be rated.
        cepo_config (CepoConfig): Configuration parameters for CePO flow.

    Returns:
        Tuple[str, int, dict]: The generated completion, number of tokens used, and a log dictionary.
    """
    completion_tokens = 0
    content = "Please act as an impartial judge and evaluate the accuracy of the response provided by an AI assistant to "\
              "the user question displayed below. Your evaluation should consider only correctness and accuracy as the primary factor. "\
              "Evaluation Criteria:\n"\
              "- Correctness: How free is it from errors or mistakes?\n"\
              "- Accuracy: Are the information and explanations factually correct?\n"\
              "Evaluation Process:\n"\
              "1. Carefully review the user question and the AI assistant's response.\n"\
              "2. Assess the response for any inaccuracies in reasoning as well as execution.\n"\
              "3. Provide a detailed explanation of your step-by-step evaluation.\n"\
              "4. Identify if the final answer is correct or not. \n"\
              "Begin your evaluation by thinking through the given problem and response step-by-step. "\
              "VERY IMPORTANT: Re-do any calculations present and check if you arrive at the same answer. "\
              "Throughly check for any inaccuracies in reasoning and calculations for each step. "\
              "Be as objective as possible. After providing your detailed explanation, "\
              "please rate the response as 0 or 1, (0 for incorrect and 1 for correct) by strictly following this format: "\
              "\"Rating: [[rating]]\", for example: \"Rating: [[0]]\""
    rating_messages = [{"role": "system", "content": system_prompt + content},
                       {"role": "user", "content": initial_query}]
    
    ratings = []
    for i, completion in enumerate(completions):
        rating_messages.append({"role": "assistant", "content": completion})
        content = "Rate the above response beginning with the detailed explanation followed by a rating of 0 or 1 "\
                  "by strictly following this format: \"Explanation: <reason for your rating>\n\nRating: [[rating]]\"."
        rating_messages.append({"role": "user", "content": content})

        # Prepare request for logging
        provider_request = {
            "model": model,
            "messages": rating_messages,
            "max_tokens": cepo_config.bestofn_max_tokens,
            "temperature": cepo_config.bestofn_temperature
        }
        
        rating_response = client.chat.completions.create(**provider_request)
        
        # Log provider call if conversation logging is enabled
        if hasattr(optillm, 'conversation_logger') and optillm.conversation_logger and request_id:
            response_dict = rating_response.model_dump() if hasattr(rating_response, 'model_dump') else rating_response
            optillm.conversation_logger.log_provider_call(request_id, provider_request, response_dict)
        completion_tokens += rating_response.usage.completion_tokens
        
        rating_response = rating_response.choices[0].message.content.strip()
        cb_log[f"rating_response_{i}"] = rating_response
        if cepo_config.print_output:
            print(f"\nCePO: Rating response for completion {i}: {rating_response}")

        pattern = r"Rating: \[\[(\d+)\]\]"
        match = re.search(pattern, rating_response)
        rating_response = match.group(1) if match else "-1"  # parsing error results in a rating of -1

        try:
            ratings.append(float(rating_response))
        except ValueError:
            ratings.append(-1)
        
        rating_messages = rating_messages[:-2]  # clear the last two messages to start over in the next iteration
    
    best_index = ratings.index(max(ratings))
    cb_log["ratings"] = ratings
    cb_log["best_index"] = best_index
    if cepo_config.print_output:
        print(f"\nCePO: Finished rating completions. Ratings: {ratings}, best completion index: {best_index}")
    return completions[best_index], completion_tokens, cb_log


def rate_completions_pairwise(system_prompt: str, initial_query: str, client: Any, model: str, completions: list[str], cepo_config: CepoConfig, cb_log: dict, request_id: str = None) -> tuple[str, int, dict]:
    """
    Rates completions for the Best of N step of CePO. Completions are rated pairwise against each other in both orders (A vs B and B vs A).

    Parameters:
        system_prompt (str): The system prompt to guide the model.
        initial_query (str): The task or question to be addressed.
        client (Any): The client instance for interacting with the AI model.
        model (str): The model name to be used for generating completions.
        completions (list[str]): List of completions to be rated.
        cepo_config (CepoConfig): Configuration parameters for CePO flow.

    Returns:
        Tuple[str, int, dict]: The generated completion, number of tokens used, and a log dictionary.
    """
    completion_tokens = 0
    rating_messages = [{"role": "system", "content": system_prompt},
                       {"role": "user", "content": initial_query}]
    content = "Please act as an impartial judge and compare the quality of the two responses provided by the AI assistant " \
              "to the user's question displayed below. Evaluation Criteria:\n" \
              "- Helpfulness: How effectively does the response meet the user's needs?\n" \
              "- Relevance: How directly does the response address the original question?\n" \
              "- Accuracy: Are the information and explanations factually correct?\n" \
              "- Depth: Does the response provide comprehensive and meaningful insights?\n" \
              "- Creativity: Does the response offer unique or innovative perspectives?\n" \
              "- Clarity: Is the response well-organized, coherent, and easy to understand?\n" \
              "Evaluation Process:\n" \
              "1. Carefully review the user's question and the AI assistant's responses.\n" \
              "2. Compare the responses against each other for each criterion.\n" \
              "3. Provide a concise explanation of your overall evaluation.\n" \
              "4. Select the response that is superior based on the above criteria.\n" \
              "Reply with \"Better Response: [[response id]]\".\n" \
              "If the first response is better, reply with \"Better Response: [[0]]\". " \
              "If the second response is better, reply with \"Better Response: [[1]]\"."
    rating_messages.append({"role": "system", "content": content})

    ratings = [0] * cepo_config.bestofn_n
    pairs = [(i, j) for i in range(cepo_config.bestofn_n) for j in range(cepo_config.bestofn_n) if i != j]
    for pair in pairs:
        responses_pair = f"Response 0: {completions[pair[0]]}\n\nResponse 1: {completions[pair[1]]}"
        rating_messages.append({"role": "assistant", "content": responses_pair})
        content =  "Reply with \"Better Response: [[response id]]\".\n" \
                   "If the first response is better, reply with \"Better Response: [[0]]\". " \
                   "If the second response is better, reply with \"Better Response: [[1]]\"."
        rating_messages.append({"role": "system", "content": content})

        # Prepare request for logging
        provider_request = {
            "model": model,
            "messages": rating_messages,
            "max_tokens": cepo_config.bestofn_max_tokens,
            "temperature": cepo_config.bestofn_temperature
        }
        
        rating_response = client.chat.completions.create(**provider_request)
        
        # Log provider call if conversation logging is enabled
        if hasattr(optillm, 'conversation_logger') and optillm.conversation_logger and request_id:
            response_dict = rating_response.model_dump() if hasattr(rating_response, 'model_dump') else rating_response
            optillm.conversation_logger.log_provider_call(request_id, provider_request, response_dict)
        completion_tokens += rating_response.usage.completion_tokens
        
        rating_response = rating_response.choices[0].message.content.strip()
        cb_log[f"rating_response_for_pair_{pair[0]}_{pair[1]}"] = rating_response
        if cepo_config.print_output:
            print(f"\nCePO: Rating response for pair {pair}: {rating_response}")

        pattern = r"Better Response: \[\[(\d+)\]\]"
        match = re.search(pattern, rating_response)
        if match:
            rating_response = match.group(1)
            try:
                rating = int(rating_response)
                ratings[pair[rating]] += 1
            except ValueError:
                ratings[pair[0]] += 1  # if parsing unsuccessful, default to the first response
        else:
            ratings[pair[0]] += 1  # if parsing unsuccessful, default to the first response

        rating_messages = rating_messages[:-2]
    
    best_index = ratings.index(max(ratings))
    cb_log["ratings"] = ratings
    cb_log["best_index"] = best_index
    if cepo_config.print_output:
        print(f"\nCePO: Finished rating completions. Ratings: {ratings}, best completion index: {best_index}")
    return completions[best_index], completion_tokens, cb_log


def cepo(system_prompt: str, initial_query: str, client: Any, model: str, cepo_config: CepoConfig, request_id: str = None) -> tuple[str, int]:
    """
    Applies CePO reasoning flow for the given task. First, it generates multiple completions, and then rates them to select the best one.
    Each completion is generated as follows:
    
    Generate `planning_n` solution proposals:
        Step 1: Plan Generation - The model generates a detailed, step-by-step plan to solve the problem, along with its confidence level for 
                each step.
        Step 2: Initial Solution - Using the plan from Step 1, the model produces an initial solution.
    
    Step 3: Plan Refinement - The model reviews all generated solution proposals and their associated plans, identifying inconsistencies.
            Based on this analysis, a refined, final step-by-step plan is constructed.
    Step 4: Final Solution - The model uses the refined plan from Step 3 to produce the final answer.
    
    Parameters:
        system_prompt (str): The system prompt to guide the model.
        initial_query (str): The task or question to be addressed.
        client (Any): The client instance for interacting with the AI model.
        model (str): The model name to be used for generating completions.
        cepo_config (CepoConfig): Configuration parameters for CePO flow.

    Returns:
        Tuple[str, int, dict]: The generated completion, number of tokens used
    """

    # Generate completions
    completions, completion_tokens_planning, cb_log = generate_n_completions(system_prompt, initial_query, client, model, cepo_config)  # cb_log is a dictionary for debugging purposes
    
    # Rate the completions
    if cepo_config.bestofn_rating_type == "absolute":
        rate_completions_fn = rate_completions_absolute
    elif cepo_config.bestofn_rating_type == "pairwise":
        rate_completions_fn = rate_completions_pairwise
    else:
        raise ValueError("Invalid rating type in cepo_config")
    rating_model = cepo_config.rating_model if cepo_config.rating_model else model
    
    best_completion, completion_tokens_rating, cb_log = rate_completions_fn(system_prompt, initial_query, client, rating_model, completions, cepo_config, cb_log, request_id)
    
    return best_completion, completion_tokens_planning + completion_tokens_rating
