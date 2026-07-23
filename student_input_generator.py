from langsmith import Client
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langsmith import traceable

class StudentInputGenerator:
  def __init__(self, student_system_prompt, student_human_prompt):
    self.client = Client()
    self.llm_student = ChatOllama(
      model="phi4:14b",
      base_url="http://localhost:11434",
      temperature=1.0,
      num_ctx=16384
    )

    self.prompt = ChatPromptTemplate.from_messages([
      ("system", student_system_prompt),
      ("human", student_human_prompt)
    ])

    self.chain = self.prompt | self.llm_student

  def generate_input_for_tutor(self, inputs: dict, outputs: dict):
    if len(outputs) == 0:
      PAM_history = ""
      control_history = ""
      PAM_output = ""
      control_model_output = ""
      user_input = ""
    else:
      PAM_history = outputs["chat_history_A"]
      control_history = outputs["chat_history_B"]
      PAM_output = outputs["PAM_response"]
      control_model_output = outputs["control_response"]
      user_input = outputs["user_input"]

    student_input = self.chain.invoke({
      "chat_history_A": PAM_history,
      "chat_history_B": control_history,
      "user_input": user_input,
      "response_A": PAM_output,
      "response_B": control_model_output
    })

    return student_input.content
