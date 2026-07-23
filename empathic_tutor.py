from perception_layer import emotion_detection
from agent_chain import response_pipeline
from pprint import PrettyPrinter
from consistency_evaluator import ConsistencyEvaluator
from response_evaluator import ResponseEvaluator
from appraisal_evaluator import AppraisalEvaluator
from langsmith import evaluate, traceable
import yaml
from rich.console import Console
from rich.markdown import Markdown
from rich.live import Live
from comparison_evaluator import ComparisonEvaluator
from student_input_generator import StudentInputGenerator
from langsmith import Client
from logger import get_next_filename, log_single_turn
import json


def target(inputs: dict):
    user_input = inputs["user_input"]

    # Detects emotion from input, returns a list that has the label, confidence, and tuple of valence and arousal scaled by the confidence score
    results = emotion_detection(user_input=user_input)
    # print(results)

    label = results[0]
    valence = results[2][0]
    arousal = results[2][1]

    return response_pipeline(user_input, label, valence, arousal)


def run_manually(
    consistency_evaluator: ConsistencyEvaluator,
    response_evaluator: ResponseEvaluator,
    appraisal_evaluator: AppraisalEvaluator,
    console: Console,
):
    while True:
        user_input = input()
        print(
            "\n==============================================================================================================\n"
        )

        if user_input == "exit":
            return

        perception_result = emotion_detection(user_input=user_input)

        label = perception_result[0]
        valence = perception_result[2][0]
        arousal = perception_result[2][1]

        pipeline = response_pipeline(user_input, label, valence, arousal)
        output = pipeline["response"]
        appraisal = pipeline["appraisal"]

        print(f"{appraisal}\n")
        print(
            "==============================================================================================================\n"
        )

        console.print(Markdown(output))
        print(
            "\n==============================================================================================================\n"
        )

        # evaluations = run_evaluation(pipeline, consistency_evaluator, response_evaluator, appraisal_evaluator)
        # print(evaluations)
        # print("==============================================================================================================\n")


def run_evaluation(
    outputs: str,
    consistency_evaluator: ConsistencyEvaluator,
    response_evaluator: ResponseEvaluator,
    appraisal_evaluator: AppraisalEvaluator,
):
    appr_eval = appraisal_evaluator.judge_appraisal({}, outputs)
    resp_eval = response_evaluator.judge_response({}, outputs)
    cons_eval = consistency_evaluator.judge_consistency({}, outputs)

    result = f"""
        Appraisal Evaluation: {appr_eval}\nz
        Response Evaluation: {resp_eval}\n
        Consistency Evaluation: {cons_eval}\n
       """

    return result


def evaluate_interatively(examples, comparison_evaluator: ComparisonEvaluator):
    file_name = get_next_filename()
    for example in examples:
        conversation = example.inputs["conversation"]
        sorted_examples = sorted(conversation, key=lambda t: t["turn"])

        for ind, turn in enumerate(sorted_examples):
            print(f"Example {ind+1}")
            user_input = turn["user_input"]

            perception_result = emotion_detection(user_input=user_input)

            label = perception_result[0]
            valence = perception_result[2][0]
            arousal = perception_result[2][1]

            pipeline = response_pipeline(user_input, label, valence, arousal)
            PAM_output = pipeline["PAM_response"]
            control_output = pipeline["control_response"]

            compare_evaluator_output = comparison_evaluator.compare_responses({}, pipeline)
            comment_data = json.loads(compare_evaluator_output["comment"])
            preferred_system = comment_data["preferred_system"]
            rationale = comment_data["rationale"]

            log_single_turn(file_name, ind+1, user_input, control_output, PAM_output, preferred_system, rationale)

def evaluate_LLMAS(LLMAS: StudentInputGenerator, comparison_evaluator: ComparisonEvaluator):
    user_input = LLMAS.generate_input_for_tutor({}, {})
    file_name = get_next_filename()

    for i in range(10):
        print(f"Interaction {i+1}: {user_input}\n")
        perception_result = emotion_detection(user_input=user_input)
            
        label = perception_result[0]
        valence = perception_result[2][0]
        arousal = perception_result[2][1]
    
        pipeline = response_pipeline(user_input, label, valence, arousal)
        PAM_output = pipeline["PAM_response"]
        control_output = pipeline["control_response"]

        compare_evaluator_output = comparison_evaluator.compare_responses({}, pipeline)
        comment_data = json.loads(compare_evaluator_output["comment"])
        preferred_system = comment_data["preferred_system"]
        rationale = comment_data["rationale"]

        log_single_turn(file_name, i+1, user_input, control_output, PAM_output, preferred_system, rationale)
        user_input = LLMAS.generate_input_for_tutor({}, pipeline)

        


if __name__ == "__main__":
    with open("config/evaluator_prompts.yaml", "r", encoding="utf-8") as f:
        eval_prompts = yaml.safe_load(f)
    with open("config/student_prompts.yaml", "r", encoding="utf-8") as f:
        LLM_student_prompts = yaml.safe_load(f)

    consistency_prompts = eval_prompts["consistency_eval_prompt"]
    response_prompts = eval_prompts["response_eval_prompt"]
    appraisal_prompts = eval_prompts["appraisal_eval_prompt"]
    comparison_prompts = eval_prompts["compare_eval_prompt"]
    student_prompts = LLM_student_prompts["student_input_prompt"]

    consistency_evaluator = ConsistencyEvaluator(
        consistency_prompts["system"], consistency_prompts["human"]
    )
    response_evaluator = ResponseEvaluator(
        response_prompts["system"], response_prompts["human"]
    )
    appraisal_evaluator = AppraisalEvaluator(
        appraisal_prompts["system"], appraisal_prompts["human"]
    )
    comparison_evaluator = ComparisonEvaluator(
        comparison_prompts["system"], comparison_prompts["human"]
    )

    console = Console()

    client = Client()
    dataset = client.read_dataset(dataset_name="Varying Valence LLM Tutor Test Script")
    examples = list(client.list_examples(dataset_id=dataset.id))

    # evaluate_interatively(examples, comparison_evaluator)
    
    student = StudentInputGenerator(student_prompts["system"], student_prompts["human"])
    evaluate_LLMAS(student, comparison_evaluator)

#     consistency_eval_results = evaluate(
#         target,
#         data="Varying Valence LLM Tutor Test Script",
#         evaluators=[comparison_evaluator.compare_responses],
#         experiment_prefix="testing",
#     )

#     run_manually(consistency_evaluator, response_evaluator, appraisal_evaluator, console)
