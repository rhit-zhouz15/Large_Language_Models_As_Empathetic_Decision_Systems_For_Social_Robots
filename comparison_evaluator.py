from langsmith import Client
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langsmith import traceable
import yaml
import json
import random
import re


class ComparisonEvaluator:
    def __init__(self, comparison_system_prompt, comparison_human_prompt):
        self.client = Client()
        self.llm_judge = ChatOllama(
            model="deepseek-r1:14b",
            base_url="http://localhost:11434",
            temperature=0,
            num_ctx=16384
        )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", comparison_system_prompt),
            ("human", comparison_human_prompt)
        ])

        self.chain = self.prompt | self.llm_judge
    
    @traceable(name="comparison_evaluation", project_name="PAM_Comparison_Evals")
    def compare_responses(self, inputs: dict, outputs: dict):
        response_model_output = outputs["PAM_response"]
        control_model_output = outputs["control_response"]
        chat_history_A = outputs["chat_history_A"]
        chat_history_B = outputs["chat_history_B"]
        user_input = outputs["user_input"]

        # Randomize which system is "Tutor A" vs "Tutor B" for every interaction so the evaluator
        # has less bias in which system it is picking by the order the systems are in
        if random.random() < 0.5:
            response_a, response_b = response_model_output, control_model_output
            history_a, history_b = chat_history_A, chat_history_B
            label_map = {"tutor_a": "pam", "tutor_b": "control"}
        else:
            response_a, response_b = control_model_output, response_model_output
            history_a, history_b = chat_history_A, chat_history_B
            label_map = {"tutor_a": "control", "tutor_b": "pam"}

        # Not randomized (response model = A, control model = B)
        # history_a = chat_history_A
        # history_b = chat_history_B
        # response_a = response_model_output
        # response_b = control_model_output

        compare_eval = self.chain.invoke({
            "chat_history_A": history_a,
            "chat_history_B": history_b,
            "user_input": user_input,
            "response_a": response_a,
            "response_b": response_b
        })

        # Search for any instance of a JSON object and only parse the JSON part
        match = re.search(r"\{.*\}", compare_eval.content, re.DOTALL)
        if not match:
            raise ValueError("No JSON found in model output.")

        parsed = json.loads(match.group())

        # Map the evaluators response back to their true label (Control or PAM Model)
        # to display the right preferred model and not the ambiguous one that the evaluator decides between
        preferred_label = parsed.get("preferred")  # "tutor_a" | "tutor_b" | "tie"
        if preferred_label == "tie":
            preferred_system = "tie"
            score = 0.5
        else:
            preferred_system = label_map.get(preferred_label, "tie")
            score = 1.0 if preferred_system == "pam" else 0.0

        return {
            "key": "compare_evaluation",
            "score": score,  # 1 = PAM preferred, 0 = control model preferred, 0.5 = tie
            "comment": json.dumps({
                "preferred_system": preferred_system,
                "confidence": parsed.get("confidence"),
                "rationale": parsed.get("rationale"),
                "tutor_a_dimension_scores": parsed.get("tutor_a"),
                "tutor_b_dimension_scores": parsed.get("tutor_b"),
                "label_map": label_map,
            }),
        }