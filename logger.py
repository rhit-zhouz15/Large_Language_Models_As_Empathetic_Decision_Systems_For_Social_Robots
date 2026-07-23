import json
from data_layer import write_to_json, load_from_json
import os
from datetime import datetime
from pathlib import Path

def get_next_filename():
    dir = Path("logs")
    dir.mkdir(exist_ok=True)

    existing_logs = dir.glob("conversation_*.json")

    numbers = []
    for file in existing_logs:
        try:
            number = int(file.stem.split("_")[-1])
            numbers.append(number)
        except ValueError:
            pass

    next_number = max(numbers, default=0) + 1

    return f"logs/conversation_{next_number}.json"

def log_single_turn(file_name: str, turn: int, user_input: str, control_output: str, PAM_output: str, LLM_pick: str, LLM_rationale: str):
    turn_data = {"Turn": turn, "User Input": user_input, "Control Tutor": control_output, 
                 "PAM Tutor": PAM_output, "LLM Judge Pick": LLM_pick, "Judge Rationale": LLM_rationale}
    
    if os.path.exists(file_name):
        data = load_from_json(file_name)
    else:
        data = []

    data.append(turn_data)
    write_to_json(data, file_name)