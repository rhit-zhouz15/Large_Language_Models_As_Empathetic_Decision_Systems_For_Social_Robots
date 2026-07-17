from perception_layer import emotion_detection
from agent_chain import response_pipeline
from pprint import PrettyPrinter
from consistency_evaluator import ConsistencyEvaluator
from response_evaluator import ResponseEvaluator
from appraisal_evaluator import AppraisalEvaluator
from langsmith import evaluate
import yaml

def target(inputs: dict):
        user_input = inputs["user_input"]

        # Detects emotion from input, returns a list that has the label, confidence, and tuple of valence and arousal scaled by the confidence score
        results = emotion_detection(user_input=user_input)
        #print(results)

        label = results[0]
        valence = results[2][0]
        arousal = results[2][1]

        return response_pipeline(
                user_input,
                label,
                valence,
                arousal
        )

def run_manually(consistency_evaluator: ConsistencyEvaluator, response_evaluator: ResponseEvaluator, appraisal_evaluator: AppraisalEvaluator):
        while(True):
                user_input = input()
                print("\n==============================================================================================================\n")


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
                print("==============================================================================================================\n")

                print(f"{output}\n")
                print("==============================================================================================================\n")

                evaluations = run_evaluation(pipeline, consistency_evaluator, response_evaluator, appraisal_evaluator)
                print(evaluations)                
                print("==============================================================================================================\n")
                

def run_evaluation(outputs: str, consistency_evaluator: ConsistencyEvaluator, response_evaluator: ResponseEvaluator, appraisal_evaluator: AppraisalEvaluator):
       appr_eval = appraisal_evaluator.judge_appraisal({}, outputs)
       resp_eval = response_evaluator.judge_response({}, outputs)
       cons_eval = consistency_evaluator.judge_consistency({}, outputs)

       result = f"""
        Appraisal Evaluation: {appr_eval}\n
        Response Evaluation: {resp_eval}\n
        Consistency Evaluation: {cons_eval}\n
       """

       return result     

if __name__ == "__main__":
    with open("config/evaluator_prompts.yaml", "r", encoding="utf-8") as f:
           eval_prompts = yaml.safe_load(f)
    
    consistency_prompts = eval_prompts["consistency_eval_prompt"]
    response_prompts = eval_prompts["response_eval_prompt"]
    appraisal_prompts = eval_prompts["appraisal_eval_prompt"]

    consistency_evaluator = ConsistencyEvaluator(consistency_prompts["system"], consistency_prompts["human"])
    response_evaluator = ResponseEvaluator(response_prompts["system"], response_prompts["human"])
    appraisal_evaluator = AppraisalEvaluator(appraisal_prompts["system"], appraisal_prompts["human"])

    consistency_eval_results = evaluate(
        target,
        data="Varying Valence LLM Tutor Test Script",
        evaluators=[response_evaluator.judge_response, appraisal_evaluator.judge_appraisal, consistency_evaluator.judge_consistency],
        experiment_prefix="testing",
    )

#     run_manually(consistency_evaluator, response_evaluator, appraisal_evaluator)