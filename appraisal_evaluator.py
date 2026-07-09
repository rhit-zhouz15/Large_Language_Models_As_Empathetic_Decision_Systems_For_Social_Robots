from langsmith import Client
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langsmith import traceable


class AppraisalEvaluator:
    def __init__(self, appraisal_system_prompt, appraisal_human_prompt):
        self.client = Client()
        self.llm_judge = ChatOllama(
            model="deepseek-r1:14b",
            base_url="http://localhost:11434",
            temperature=0
        )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", appraisal_system_prompt),
            ("human", appraisal_human_prompt)
        ])

        self.chain = self.prompt | self.llm_judge
    
    @traceable(name="appraisal_evaluation")
    def judge_appraisal(self, inputs: dict, outputs: dict):
        detected_emotion = outputs["detected_emotion"]
        valence = outputs["valence"]
        arousal = outputs["arousal"]
        appraisal_engine_output = outputs["appraisal"]

        appraisal_eval = self.chain.invoke({
            "detected_emotion": detected_emotion,
            "valence": valence,
            "arousal": arousal,
            "appraisal_engine_output": appraisal_engine_output
        })

        scores = []
        for line in appraisal_eval.content.split("\n"):
            try:
                scores.append(float(line.split(":")[1].split("|")[0].strip()))
            except (IndexError, ValueError):
                pass
        
        if len(scores) == 0:
            print("Division by 0")
            print(appraisal_eval.content)
            cumulative_score = 0
        else:
            cumulative_score = sum(scores) / len(scores)

        # print(consistency_eval.content)
                
        return {
            "key": "appraisal_evaluation",
            "score": cumulative_score,
            "comment": appraisal_eval.content
        }