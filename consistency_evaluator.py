from langsmith import Client
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langsmith import traceable


class ConsistencyEvaluator:
    def __init__(self, consistency_system_prompt, consistency_human_prompt):
        self.client = Client()
        self.llm_judge = ChatOllama(
            model="deepseek-r1:14b",
            base_url="http://localhost:11434",
            temperature=0
        )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", consistency_system_prompt),
            ("human", consistency_human_prompt)
        ])
    
    @traceable(name="consistency_evaluation")
    def judge_consistency(self, inputs: dict, outputs: dict):
        appraisal_engine_output = outputs["appraisal"]
        response_model_output = outputs["response"]

        chain = self.prompt | self.llm_judge

        consistency_eval = chain.invoke({
            "appraisal_engine_output": appraisal_engine_output,
            "response_model_output": response_model_output
        })

        scores = []
        for line in consistency_eval.content.split("\n"):
            try:
                scores.append(float(line.split(":")[1].split("|")[0].strip()))
            except (IndexError, ValueError):
                pass
        
        if len(scores) == 0:
            print("Division by 0")
            print(consistency_eval.content)
            cumulative_score = 0
        else:
            cumulative_score = sum(scores) / len(scores)

        # print(consistency_eval.content)
                
        return {
            "key": "consistency_evaluation",
            "score": cumulative_score,
            "comment": consistency_eval.content
        }