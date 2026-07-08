from langsmith import Client
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langsmith import traceable
import yaml


class ResponseEvaluator:
    def __init__(self, response_system_prompt, response_human_prompt):
        self.client = Client()
        self.llm_judge = ChatOllama(
            model="deepseek-r1:14b",
            base_url="http://localhost:11434",
            temperature=0
        )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", response_system_prompt),
            ("human", response_human_prompt)
        ])
    
    @traceable(name="response_evaluation")
    def judge_response(self, inputs: dict, outputs: dict):
        response_model_output = outputs["response"]

        chain = self.prompt | self.llm_judge

        response_eval = chain.invoke({
            "response_model_output": response_model_output
        })

        scores = []
        for line in response_eval.content.split("\n"):
            try:
                scores.append(float(line.split(":")[1].split("|")[0].strip()))
            except (IndexError, ValueError):
                pass
        
        if len(scores) == 0:
            print("Division by 0")
            print(response_eval.content)
            cumulative_score = 0
        else:
            cumulative_score = sum(scores) / len(scores)

        # print(consistency_eval.content)
                
        return {
            "key": "response_evaluation",
            "score": cumulative_score,
            "comment": response_eval.content
        }