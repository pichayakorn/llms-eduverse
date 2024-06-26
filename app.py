import openai
import random
import os
import re
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
get_general_hint_prompt_template = open(Path("prompts/get_general_hint.txt"), "r").read()
get_final_hint_prompt_template = open(Path("prompts/get_final_hint.txt"), "r").read()

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

def detect_multiple_placeholders(sentence):
    # Define a pattern to match placeholders like ________
    pattern = r'_+'

    # Find all occurrences of the pattern in the sentence
    matches = re.findall(pattern, sentence)

    # Check the number of matches
    if len(matches) > 1:
        return True
    else:
        return False

def has_duplicates(word_list):
    seen = set()
    for word in word_list:
        word_lower = word.lower()
        if word_lower in seen:
            return True
        seen.add(word_lower)
    return False

def rand_word(word_list: list):
    if isinstance(word_list, list) and len(word_list) == 20:
      # Use random.sample to pick 10 unique elements from word_list
        selected_words = random.sample(word_list, 10)
        return selected_words
    else:
        return ValueError("Input should be a list of exactly 20 words.")

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
            "description": "Get ten word semantic similarity scores.",
            "parameters": {
                "type": "object",
                "properties": {
                    "score_list": {
                        "type": "array",
                        "items": {
                            "type": "number"
                        },
                        "description": "A list of ten semantic similarity scores between 0 to 1. 0 indicates that the two texts have no semantic similarity. This means that the meanings of the texts are completely different or unrelated. 1 indicates that the two texts are semantically identical. e",
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
            "description": "Get two fill-in-the-blank questions where the missing word can be filled in anywhere in the sentence. The questions should be based on the group that contains the target word, so the correct answer can be any word in that group. Ensure that every word in the group can fill in the missing word and the other group cannot fill in the missing word.",
            "parameters": {
                "type": "object",
                "properties": {
                    "hint_list": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": """Two fill-in-the-blank questions where the missing word can be filled in anywhere in the sentence. The missing position must have only one place in the sentence denote with four underscore symbols. The element type is string e.g. ["1st fill-in-the-blank question", "2nd fill-in-the-blank question"]""",
                    }
                },
                "required": ["hint_list"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_general_hint",
            "description": "Get one general fill-in-the-blank question where the missing place is somewhere in the sentence. All words in the list is correct answer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "general_hint": {
                        "type": "string",
                        "description": """General fill-in-the-blank question where the missing place is somewhere in the sentence. The missing position must have only one place in the sentence denote with four underscore symbols. The element type is string e.g. 'general-fill-in-the-blank question'""",
                    }
                },
                "required": ["general_hint"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_final_hint",
            "description": "Get one fill-in-the-blank question where the missing place is somewhere in the sentence. The correct answer can only be one word, and the rest will be wrong.",
            "parameters": {
                "type": "object",
                "properties": {
                    "final_hint": {
                        "type": "string",
                        "description": """One general fill-in-the-blank question where the missing place is somewhere in the sentence. The missing position must have only one place in the sentence denote with four underscore symbols. The element type is string e.g. 'specific-fill-in-the-blank question'""",
                    }
                },
                "required": ["final_hint"]
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
                        if has_duplicates(word_list):
                            regen = True
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

    print("-------------------")
    print(word_list, ",", len(word_list), "words")
    print("-------------------")

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

    get_general_hint_prompt = get_general_hint_prompt_template.replace("<WORD_LIST>", combined_list)
    get_hint_prompt = get_hint_prompt_template.replace("<TARGET_WORD>", target_word).replace("<WORD_LIST>", combined_list)
    get_final_hint_prompt = get_final_hint_prompt_template.replace("<TARGET_WORD>", target_word).replace("<INCORRECT_WORD_LIST>", ', '.join(word_list[1:]))

    print("-------------------")
    print(get_general_hint_prompt)
    print("-------------------")
    print(get_hint_prompt)
    print("-------------------")
    print(get_final_hint_prompt)
    print("-------------------")

    # Get general hint from the model
    regen = True
    general_hint = None
    while(regen):
      if (regen):

        messages = []
        messages.append({"role": "user", "content": get_general_hint_prompt})
        response = chat_completion_request(
            messages=messages,
            tools=tools,
            tool_choice={"type": "function", "function": {"name": "get_general_hint"}}
        )

        regen = False
        print(response.choices[0].message.tool_calls)

        general_hint = None
        try:
            tool_calls = response.choices[0].message.tool_calls
            if tool_calls:
              tool_function_name = tool_calls[0].function.name
              general_hint = eval(tool_calls[0].function.arguments)['general_hint']
            #   if ("__" not in general_hint):
            #     regen = True
              if detect_multiple_placeholders(general_hint) or target_word in general_hint:
                regen = True
            
        except Exception as e:
            return jsonify({'error': 'Failed to parse the response', 'details': str(e)}), 500

    # Get hints from the model
    regen = True
    hint_list = None
    while(regen):
      if (regen):
        messages = []
        messages.append({"role": "user", "content": get_hint_prompt})
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
            if len(hint_list) == 2:
                for i in range(len(hint_list)):
                    # if ("__" not in hint_list[i]):
                    #     regen = True
                    if detect_multiple_placeholders(hint_list[i]) or target_word in hint_list[i]:
                        regen = True
                        break
            else:
                regen = True
                
        except Exception as e:
            return jsonify({'error': 'Failed to parse the response', 'details': str(e)}), 500

    # Get final hint from the model
    regen = True
    final_hint = None
    while(regen):
      if (regen):

        messages = []
        messages.append({"role": "user", "content": get_final_hint_prompt})
        response = chat_completion_request(
            messages=messages,
            tools=tools,
            tool_choice={"type": "function", "function": {"name": "get_final_hint"}}
        )

        regen = False
        print(response.choices[0].message.tool_calls)

        final_hint = None
        try:
            tool_calls = response.choices[0].message.tool_calls
            if tool_calls:
              tool_function_name = tool_calls[0].function.name
              final_hint = eval(tool_calls[0].function.arguments)['final_hint']
            #   if ("__" not in final_hint):
            #     regen = True
              if detect_multiple_placeholders(final_hint) or target_word in final_hint:
                regen = True
            
        except Exception as e:
            return jsonify({'error': 'Failed to parse the response', 'details': str(e)}), 500

    hint_list.insert(0, general_hint)
    hint_list.append(final_hint)
    print("-------------------")
    print(hint_list)
    print("-------------------")
    print("Hint list")
    for i in range(len(hint_list)):
        print("ID", i+1, ": ", hint_list[i])
    print("Choices:")
    print(word_list)



    return to_final_json(word_list, score_list, hint_list)