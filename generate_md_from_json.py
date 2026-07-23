from data_layer import load_from_json

json_file_name = "conversation_5"
data = load_from_json(f"logs/{json_file_name}.json")
with open(f"logs/{json_file_name}.md", "w") as f:
  for turn in data:
    f.write(f"## Turn {turn['Turn']}\n\n")
    f.write(f"**User Input:**  \n{turn['User Input']}\n\n")
    f.write("---\n\n")
    f.write(f"### Control Tutor\n\n{turn['Control Tutor']}\n\n")
    f.write("---\n\n")
    f.write(f"### PAM Tutor\n\n{turn['PAM Tutor']}\n\n")
    f.write("---\n\n")
    f.write(f"**LLM Judge Pick:** `{turn['LLM Judge Pick']}`\n\n")
    f.write("---\n\n")
    f.write(f"**LLM Judge Rationale:** `{turn['Judge Rationale']}`\n\n")
    f.write("---\n\n")
