import os
import json
import matplotlib.pyplot as plt

def analyze_by_interaction():
  path = "data_logs_with_dimension_scores"

  interactions = []
  PAM_wins = []
  control_wins = []
  ties = []
  nones = []

  PAM = 0
  control = 0
  tie = 0
  none = 0
  interaction_index = 0

  for f in os.scandir(path):
    if f.is_file():
      with open(f.path, "r") as file:
        data = json.load(file)

        for interaction in data:
          pick = interaction["LLM Judge Pick"].lower()
          if pick == "pam":
            PAM += 1
          elif pick == "control":
            control += 1
          elif pick == "tie":
            tie += 1
          else:
            none += 1
          interaction_index += 1

          PAM_wins.append(PAM)
          control_wins.append(control)
          ties.append(tie)
          nones.append(none)
          interactions.append(interaction_index)

  plt.figure(figsize=(10, 6))

  plt.plot(interactions, PAM_wins, label="PAM Tutor Wins")
  plt.plot(interactions, control_wins, label="Control Tutor Wins")
  plt.plot(interactions, ties, label="Ties")
  plt.plot(interactions, nones, label="Wrong format/Other Errors")

  plt.title("LLM Judge Picks Over Interactions")
  plt.xlabel("Interactions")
  plt.ylabel("Cumulative Picks")
  plt.legend()
  plt.grid(True)

  plt.tight_layout()
  plt.show()

  total = len(interactions)
  PAM_percentage = (PAM / total) * 100
  control_percentage = (control / total) * 100
  tie_percentage = (tie / total) * 100
  none_percentage = (none / total) * 100

  print("Analysis by each interaction per conversation")
  print(f"Percent of PAM Wins: {PAM_percentage}%")
  print(f"Percent of Control Wins: {control_percentage}%")
  print(f"Percent of Ties: {tie_percentage}%")
  print(f"Percent of Nones {none_percentage}%")
  print("----------------------------------------------------------------------------------------------------")

def analyze_by_conversation():
  path = "data_logs_with_dimension_scores"

  conversations = []
  PAM_wins = []
  control_wins = []
  ties = []

  PAM = 0
  control = 0
  tie = 0
  conversation_index = 0

  for f in os.scandir(path):
    if f.is_file():
      with open(f.path, "r") as file:
        data = json.load(file)

        PAM_wins_convo = 0
        control_wins_convo = 0

        for interaction in data:
          pick = interaction["LLM Judge Pick"].lower()
          if pick == "pam":
            PAM_wins_convo += 1
          elif pick == "control":
            control_wins_convo += 1

        conversation_index += 1

        if PAM_wins_convo > control_wins_convo:
          PAM += 1
        elif control_wins_convo > PAM_wins_convo:
          control += 1
        else:
          tie += 1

        PAM_wins.append(PAM)
        control_wins.append(control)
        ties.append(tie)
        conversations.append(conversation_index)

  plt.figure(figsize=(10, 6))

  plt.plot(conversations, PAM_wins, label="PAM Tutor Wins")
  plt.plot(conversations, control_wins, label="Control Tutor Wins")
  plt.plot(conversations, ties, label="Ties")

  plt.title("Best Tutor by Majority Picks Over the Course of a 10 Turn Conversation")
  plt.xlabel("Conversations")
  plt.ylabel("Majority Wins")
  plt.legend()
  plt.grid(True)

  plt.tight_layout()
  plt.show()

  total = len(conversations)
  PAM_percentage = (PAM / total) * 100
  control_percentage = (control / total) * 100
  tie_percentage = (tie / total) * 100

  print("Analysis by which model won the majority of the interactions in a conversation (one winner per conversation)")
  print(f"Percent of PAM Wins: {PAM_percentage}%")
  print(f"Percent of Control Wins: {control_percentage}%")
  print(f"Percent of Ties: {tie_percentage}%")

if __name__ == "__main__":
  analyze_by_interaction()
  analyze_by_conversation()