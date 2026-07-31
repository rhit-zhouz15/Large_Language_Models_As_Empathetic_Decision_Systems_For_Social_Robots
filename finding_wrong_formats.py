import os
import json

def find_malformed_scores():
    path = "data_logs_with_dimension_scores"
    for f in os.scandir(path):
        if f.is_file():
            with open(f.path, "r") as file:
                data = json.load(file)
            for i, interaction in enumerate(data):
                for key in ["PAM Scores", "Control Scores"]:
                    val = interaction.get(key)
                    if not isinstance(val, dict):
                        print(f"File: {f.name}, Turn: {interaction.get('Turn')}, "
                              f"Key: '{key}' is type {type(val).__name__}, value: {val!r}")

find_malformed_scores()