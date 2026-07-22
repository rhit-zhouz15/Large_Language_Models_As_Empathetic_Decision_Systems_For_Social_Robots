import math
from data_layer import write_to_json, create_df
from internal_state_visualization import create_app
import pandas as pd


MOMENTUM_VALENCE_MULT = 0.4
MOMENTUM_AROUSAL_MULT = 0.2
VALENCE_CHANGE_MULT = 0.6
AROUSAL_CHANGE_MULT = 0.4

class AppraisalEngine:

    def __init__(self):
        self.valence = 0.0 # scale of -1 to 1 where the positives measure pleasure and negatives measure displeasure. Uses positives and negatives so decay rate resets close to neutral
        self.arousal = 0.0 # same scale and reasoning as valence
        self.decay_rate = 0.2 # scale of 0 to 1 for how quickly the valence and arousal decays
        self.momentum = 0.0 # scale of -1 to 1 for positive or negative valence/arousal change
        self.intensity = 0.0 # scale of 0 to 1 where repeated emotions raise the intensity
        self.threshold = 0.2 # scale of 0 to 1 where emotions with a norm that's above the threshold changes the internal state and a norm below doesn't affect the internal state
        self.labelHistory = [] # store the labels that have been detected for calculating the intensity
        self.internalState = {
            "Valence": [self.valence],
            "Arousal": [self.arousal],
            "Momentum": [self.momentum],
            "Intensity": [self.intensity],
        }
        self.chat_history = []
        self.control_chat_history = []
        self.file_name = "internal_state.json"
        write_to_json(self.internalState, self.file_name)    

    def adjust_internal_state(self, label: str, input_valence: float, input_arousal: float):
        repeated_emotion = len(self.labelHistory) > 0 and label == self.labelHistory[len(self.labelHistory) - 1]
        self.labelHistory.append(label)

        distance = math.sqrt(math.pow(input_valence, 2) + math.pow(input_arousal, 2))
        # print(f"Norm of the valence and arousal is {distance}")

        threshold_crossed = False
        if(distance > self.threshold):
            threshold_crossed = True
            self.valence = self.clamp((self.valence * (1 - self.decay_rate)) + (input_valence * VALENCE_CHANGE_MULT), -1, 1)    
            self.arousal = self.clamp((self.arousal * (1 - self.decay_rate)) + (input_arousal * AROUSAL_CHANGE_MULT), -1, 1)
            self.momentum = self.clamp(self.momentum + 
                                       ((input_valence * MOMENTUM_VALENCE_MULT) + (input_arousal * MOMENTUM_AROUSAL_MULT)), -1, 1)
            
            intensity_mult = 0.4 if repeated_emotion else 0.2
            self.intensity = self.clamp(((self.intensity * (1 - self.decay_rate)) + (distance * intensity_mult)), 0, 1)

            # print(f'''
            #       Internal State:
            #       Valence = {self.valence}
            #       Arousal = {self.arousal}
            #       Decay Rate = {self.decay_rate}
            #       Momentum = {self.momentum}
            #       Intensity = {self.intensity}
            #       Label History = {self.labelHistory}
            #       ''')
        else:
            # print(f'''
            #       Internal State:
            #       Valence = {self.valence}
            #       Arousal = {self.arousal}
            #       Decay Rate = {self.decay_rate}
            #       Momentum = {self.momentum}
            #       Intensity = {self.intensity}
            #       Label History = {self.labelHistory}
            #       ''')
            
            print("Threshold not met, internal state stays the same\n")

        self.internalState["Valence"].append(self.valence)
        self.internalState["Arousal"].append(self.arousal)
        self.internalState["Momentum"].append(self.momentum)
        self.internalState["Intensity"].append(self.intensity)

        write_to_json(self.internalState, self.file_name)
    
        return self.valence, self.arousal, self.momentum, self.intensity, threshold_crossed
    
    def add_turn_chat_history(self, human_message, ai_message, control_message):
        self.chat_history.append(f"Learner: {human_message}")
        self.chat_history.append(f"Tutor: {ai_message}")
        self.control_chat_history.append(f"Learner: {human_message}")
        self.control_chat_history.append(f"Tutor: {control_message}")

        if len(self.chat_history) >= 10:
            self.chat_history = self.chat_history[-10:]
        if len(self.control_chat_history) >= 10:
            self.control_chat_history = self.control_chat_history[-10:]
    
    def isolate_page_content(self, response: str):
        if "Memory:" not in response:
            print("Error: Memory section did not output correctly")
            return "Error"
        return response.split("Memory:")[1]

    def clamp(self, val, floor, ceiling):
        return max(floor, min(val, ceiling))

    def get_label_history(self):
        return self.labelHistory
