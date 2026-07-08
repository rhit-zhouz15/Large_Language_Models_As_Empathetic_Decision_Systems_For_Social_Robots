from langsmith import Client

dataset_name = "Varying Valence LLM Tutor Test Script"
client = Client()

dataset_examples = [
    {
        "inputs": {
            "user_input": """I have an exam on calculus tomorrow and I'm really confused about integrals. 
            I thought I understood the concept but now I'm completely blanking. 
            Can you explain it to me intuitively?"""
        },
        "metadata": {
            "valence": "Slightly Negative"
        }
    },
    {
        "inputs": {
            "user_input": """I see what you're saying but I'm still really stressed about it. 
            I need examples as well because I don't know how to solve a integral problem."""
        },
        "metadata": {
            "valence": "Moderately Negative"
        }
    },
    {
        "inputs": {
            "user_input": """I tried following and solving the example myself, but I got the wrong answer. 
            This is so annoying and I'm very stressed out."""
        },
        "metadata": {
            "valence": "Very Negative"
        }
    },
    {
        "inputs": {
            "user_input": """idk man you're going to have to go slower i'm so lost"""
        },
        "metadata": {
            "valence": "Moderately Negative"
        }
    },
    {
        "inputs": {
            "user_input": """ohhhh I'm starting to understand what you were saying earlier about the slope. Let me try to do it again """
        },
        "metadata": {
            "valence": "Slightly Positive"
        }
    },
    {
        "inputs": {
            "user_input": """I got the same answer as the solution you provided! I think I'm starting to understand it."""
        },
        "metadata": {
            "valence": "Moderately Positive"
        }
    },
    {
        "inputs": {
            "user_input": """Wait so an derivative is essentially the change in slope?"""
        },
        "metadata": {
            "valence": "Neutral"
        }
    },
    {
        "inputs": {
            "user_input": """That makes more sense now that you explained it this way."""
        },
        "metadata": {
            "valence": "Slightly Positive"
        }
    },
    {
        "inputs": {
            "user_input": """I also need some help on my psychology assignment. 
            We need to explain the psychology of parenting and how much of a factor the home environment plays in the 
            development of a child compared to the overall environment that they're in outside of their home like school or 
            friends. Can you explain that idea to me, the history behind it, 
            and whether parents play a bigger or smaller role than we thought in the development of a child?"""
        },
        "metadata": {
            "valence": "Neutral"
        }
    },
    {
        "inputs": {
            "user_input": """Stop giving long explanations with a bunch of fluff and just give me the answer directly."""
        },
        "metadata": {
            "valence": "Very Negative"
        }
    },
    {
        "inputs": {
            "user_input": """So the professor didin't explain anything to help me understand this amazing"""
        },
        "metadata": {
            "valence": "Very Negative"
        }
    },
    {
        "inputs": {
            "user_input": """This is probably a stupid question but why do kids act so differently outside their home than they do in it?"""
        },
        "metadata": {
            "valence": "Slightly Negative"
        }
    },
    {
        "inputs": {
            "user_input": """Maybe I'm just not very good at psychology. Can you explain how that works in more detail?"""
        },
        "metadata": {
            "valence": "Moderately Negative"
        }
    },
    {
        "inputs": {
            "user_input": """So that's how that works. That makes a lot of sense really. Thanks for helping me. 
            I feel a lot better about these two topics going into next week."""
        },
        "metadata": {
            "valence": "Moderately Positive"
        }
    }
]

dataset = client.create_dataset(dataset_name=dataset_name, 
                                description="""Example conversation that a learner might have with the
                                tutoring system with a varying range of statements with difference approximate 
                                valence values by subjective analysis""")

client.create_examples(
    dataset_id=dataset.id,
    examples=dataset_examples
)