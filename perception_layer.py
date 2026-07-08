import os
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"

from transformers import AutoModelForSequenceClassification, pipeline

emotions_to_va = {"anger": (-0.7, 0.7),
                  "cheeky": (0.5, 0.6),
                  "confuse": (-0.4, 0.4),
                  "curious": (0.3, 0.4),
                  "disgust": (-0.6, 0.4),
                  "empathetic": (0.5, 0.2),
                  "energetic": (0.6, 0.9),
                  "fear": (-0.8, 0.9),
                  "grumpy": (-0.5, -0.2),
                  "guilty": (-0.6, -0.1),
                  "impatient": (-0.4, 0.7),
                  "joy": (0.9, 0.7),
                  "love": (0.9, 0.4),
                  "neutral": (0.0, 0.0),
                  "sadness": (-0.7, -0.5),
                  "serious": (-0.1, -0.2),
                  "surprise": (0.0, 0.8),
                  "suspicious": (-0.4, 0.3),
                  "think": (0.0, -0.2),
                  "whiny": (-0.5, 0.2)
                  }

# Loading the emotion-english model from huggingface
model_name = "jitesh/emotion-english"
model = AutoModelForSequenceClassification.from_pretrained(model_name)
classifier = pipeline("text-classification", model=model, tokenizer=model_name, top_k=None, return_all_scores=True)

def emotion_detection(user_input: str):
    # Detect emotion from user input
    prediction = classifier(user_input)[0]

    weighted_valence = 0.0
    weighted_arousal = 0.0
    for pred in prediction:
        label = pred["label"]
        score = pred["score"]
        weighted_valence += emotions_to_va[label][0] * score
        weighted_arousal += emotions_to_va[label][1] * score

    dominant_emotion = max(prediction, key=lambda x: x["score"])
    dominant_label = dominant_emotion["label"]
    dominant_score = dominant_emotion["score"]
 
    weighted_va = (weighted_valence, weighted_arousal)

    return [dominant_label, dominant_score, weighted_va]
