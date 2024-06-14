import openai
import random
import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

client = openai.OpenAI()

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY") 

GPT_MODEL = "gpt-3.5-turbo"
CATEGORIES = [
    "animal",
    "fruit",
    "sport",
    "color",
    "country",
    "vehicle",
    "city",
    "food",
    "furniture"
    "music genre",
    "language",
    "planet",
    "body part",
    "weather phenomenon",
    "tree",
    "flower",
    "vegetable",
    "beverage",
    "cuisine",
    "instrument",
    "bird",
    "reptile",
    "ocean",
    "furniture",
    "clothing",
    "technology"
]

get_word_prompt_template = open(Path("prompts/get_word.txt"), "r").read()
get_word_score_prompt_template = open(Path("prompts/get_word_score.txt"), "r").read()
get_hint_prompt_template = open(Path("prompts/get_hint.txt"), "r").read()

def chat_completion_request(messages, tools=None, tool_choice=None, model=GPT_MODEL):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e

def rand_word(word_list: list):
  if isinstance(word_list, list) and len(word_list) == 20:
      shuffled_list = word_list.copy()
      random.shuffle(shuffled_list)
      return shuffled_list[:10]

  else:
    raise ValueError("word_list must be a list of 20 words")

def to_final_json(word_list: list, score_list: list, hint_list: list):
  hints = [{"ID": idx + 1, "question": hint_list[idx]} for idx in range(len(hint_list))]
    
  words = [
      {"ID": idx + 1, "word": word, "score": score}
      for idx, (word, score) in enumerate(zip(word_list, score_list))
  ]
    
  return jsonify({
      "hint": hints,
      "words": words
  })

tools = [
    {
        "type": "function",
        "function": {
            "name": "rand_word",
            "description": "Randomly pick a word from the provided list",
            "parameters": {
                "type": "object",
                "properties": {
                    "word_list": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "Python list of 20 words",
                    }
                },
                "required": ["word_list"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_word_score",
            "description": "Get words semantic similarity scores.",
            "parameters": {
                "type": "object",
                "properties": {
                    "score_list": {
                        "type": "array",
                        "items": {
                            "type": "number"
                        },
                        "description": "Python dictionary of word and semantic similarity score between 0 to 1",
                    }
                },
                "required": ["score_list"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_hint",
            "description": "Get 4 hint questions that must be fill in the blank question type.",
            "parameters": {
                "type": "object",
                "properties": {
                    "hint_list": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": """4 hint questions list consist of fill in the blank question, the question that has an underscore symbol somewhere in the sentence that denotes the missing word. The word first word in the provided list must be the missing word for all 4 hint questions. The choices are picked from 5 of 10 in the word list. The sentences consist of around 10 words. The missing position must have only one place in the sentence. The element type is string e.g. ["1st hint-blank-question", "2nd hint-blank-question", "3rd hint-blank-question", "4th hint-blank-question"]""",
                    }
                },
                "required": ["hint_list"]
            }
        }
    },
]

@app.route('/generate_words', methods=['GET'])
def generate_words():
    category = random.choice(CATEGORIES)

    get_word_prompt = get_word_prompt_template.replace("<CATEGORY>", category)

    messages = []
    messages.append({"role": "user", "content": get_word_prompt})

    # Get words from the model
    regen: bool = True
    word_list = None
    while(regen):
        if(regen):
            response = chat_completion_request(
                messages=messages,
                tools=tools,
                tool_choice={"type": "function", "function": {"name": "rand_word"}}
            )
            regen = False
            print(response.choices[0].message.tool_calls)

            try:
                tool_calls = response.choices[0].message.tool_calls
                if tool_calls:
                  tool_function_name = tool_calls[0].function.name
                  full_word_list = eval(tool_calls[0].function.arguments)['word_list']
                  if tool_function_name == 'rand_word':
                    if len(full_word_list) == 20:
                        word_list = rand_word(full_word_list)
                    else:
                        regen = True
                else:
                    return jsonify({'error': 'Response did not contain a list of 20 words'}), 500
            except Exception as e:
                return jsonify({'error': 'Failed to parse the response', 'details': str(e)}), 500

    target_word = word_list[0]
    combined_list = ', '.join(word_list)
    get_word_score_prompt = get_word_score_prompt_template.replace("<TARGET_WORD>", target_word)
    get_word_score_prompt = get_word_score_prompt.replace("<WORD_LIST>", combined_list)

    messages = []
    messages.append({"role": "user", "content": get_word_score_prompt})

    # Get scores from the model
    regen = True
    score_list = None
    while(regen):
        if (regen):
            response = chat_completion_request(
                messages=messages,
                tools=tools,
                tool_choice={"type": "function", "function": {"name": "get_word_score"}}
            )
            regen = False
            print(response.choices[0].message.tool_calls)

            try:
                tool_calls = response.choices[0].message.tool_calls
                if tool_calls:
                  tool_function_name = tool_calls[0].function.name
                  score_list = eval(tool_calls[0].function.arguments)['score_list']
                  if score_list:
                    if len(score_list) == 10:
                        regen = False
                    else:
                        regen = True
            except Exception as e:
                return jsonify({'error': 'Failed to parse the response', 'details': str(e)}), 500

    get_hint_prompt = get_hint_prompt_template.replace("<TARGET_WORD>", target_word)
    get_hint_prompt = get_hint_prompt.replace("<WORD_LIST>", combined_list)

    messages = []
    messages.append({"role": "user", "content": get_hint_prompt})

    # Get hints from the model
    regen = True
    hint_list = None
    while(regen):
      if (regen):

        response = chat_completion_request(
            messages=messages,
            tools=tools,
            tool_choice={"type": "function", "function": {"name": "get_hint"}}
        )
        regen = False
        print(response.choices[0].message.tool_calls)

        hint_list = None
        try:
            tool_calls = response.choices[0].message.tool_calls
            if tool_calls:
              tool_function_name = tool_calls[0].function.name
              hint_list = eval(tool_calls[0].function.arguments)['hint_list']
            for i in range(len(hint_list)):
              if ("_" not in hint_list[i]):
                regen = True
                break
            
        except Exception as e:
            return jsonify({'error': 'Failed to parse the response', 'details': str(e)}), 500


    return to_final_json(word_list, score_list, hint_list)