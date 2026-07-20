from dotenv import load_dotenv
import os
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"), override=True)


from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from memory import store_memory, retrieve_memory
from appraisal_engine import AppraisalEngine
from langsmith import traceable
import yaml

with open("config/tutor_prompts.yaml", "r", encoding="utf-8") as f:
        tutor_prompts = yaml.safe_load(f)

appraisal_prompts = tutor_prompts["context_prompt"]
response_prompts = tutor_prompts["response_prompt"]

affective_model = ChatOllama(
        model="gemma4:e4b",
        base_url="http://localhost:11434",
        reasoning=False,
        keep_alive=-1,
        num_ctx=8192
    )

context_prompt = ChatPromptTemplate.from_messages([
    ("system", appraisal_prompts["system"]),
    ("human", appraisal_prompts["human"])
])

response_prompt = ChatPromptTemplate.from_messages([
    ("system", response_prompts["system"]),
    (MessagesPlaceholder(variable_name="chat_history")),
    ("human", response_prompts["human"])
])

response_model = ChatOllama(
        model="gemma4:e4b",
        base_url="http://localhost:11434",
        reasoning=True,
        keep_alive=-1,
        temperature=1.0,
        top_p=0.95,
        top_k=64,
        num_ctx=8192,
    )

context_chain = context_prompt | affective_model
response_chain = response_prompt | response_model

appraisal_engine = AppraisalEngine()

@traceable(name="context_generator")
def generate_context(user_input: str, label: str, input_valence: float, input_arousal: float):
        valence, arousal, momentum, intensity, threshold_crossed = appraisal_engine.adjust_internal_state(label, input_valence, input_arousal)

        context_from_memory = retrieve_memory(user_input, "kelvin")
        #print(f"Context from RAG: {context_from_memory}\n")

        context = context_chain.invoke({
            "user_input": user_input,
            "valence": round(valence, 3),
            "arousal": round(arousal, 3),
            "momentum": round(momentum, 3),
            "intensity": round(intensity, 3),
            "threshold": threshold_crossed,
            "label": label,
            "input_valence": round(input_valence, 3),
            "input_arousal": round(input_arousal, 3),
            "rag_context": context_from_memory
        })

        rag_summary = appraisal_engine.isolate_page_content(context.content)
        # print(f"Summary to store in db: {rag_summary}\n")
        store_memory(rag_summary, len(appraisal_engine.get_label_history()), label, round(valence, 3), round(arousal, 3))

        return context.content, context_from_memory

@traceable(name="response_generator")
def generate_response(user_input: str, context_from_memory: str, appraisal_output: str):        
        response = response_chain.invoke({
            "user_input": user_input,
            "rag_context": context_from_memory,
            "appraisal_output": appraisal_output,
            "chat_history": appraisal_engine.chatHistory
        })

        return response.content

@traceable(name="full_pipeline")
def response_pipeline(user_input: str, label: str, input_valence: float, input_arousal: float):
        # Pass the information from the perception layer to the appraisal engine
        appraisal, context_from_memory = generate_context(user_input, label, input_valence, input_arousal)
        # print(f"{appraisal}\n")

        # Using the appraisal, get the response model's output
        response = generate_response(user_input, context_from_memory, appraisal)
        # print(f"{response}\n")

        # Update the chat history after each turn
        appraisal_engine.add_turn_chat_history(user_input, response)

        return {"detected_emotion": label, "valence": input_valence, "arousal": input_arousal,"response": response, "appraisal": appraisal}