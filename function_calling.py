import openai
import json
import os
from constants import OPENAI_API_KEY

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
openai.api_key = OPENAI_API_KEY


def get_current_weather(location, unit="fahrenheit"):
    weather_info = {
        "location": location,
        "temperature": "72",
        "unit": unit,
        "forecast": ["sunny", "windy"],
    }


# Can have a lot of functions, no limit.
# function does need to exist.
# need to make the description clear so gpt knows it is a function and not just question.

completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-0613",
    messages=[{"role": "user", "content": "what's the weather like in boston on the 5th of february?"}],
    functions=[
        {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                # one parameter = location
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "The date",
                    }
                    # "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
                },
                "required": ["date"],
            }
        }
    ],
    # auto = gpt determines if you want to run this function.
    # none = not use any of the functions.
    # nameequals: function = it will run the function. You can force it to fill in the form
    function_call="auto"
)

# reply = completion.choices[0].message
# funcs = reply.to_dict()['function_call']['arguments']
# funcs = json.loads(funcs)
# print(funcs)
# print(funcs['location'])


# with this we dont need to extract the text from the gpt response
example_user_input = "How do I install Tensorflow for my GPU?"

# YOU NEED TO THINK HOW WOULD I DESCRIBE A FUNCTION
completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-0613",
    messages=[{"role": "user", "content": example_user_input}],
        functions=[
        {
            "name": "get_commands",
            # how does the function works
            "description": "Get a list of bash commands on an Ubuntu machine",
            # parameters of funtion
            "parameters": {
                "type": "object",
                "properties": {
                    "commands": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "description": "A terminal command string"
                        },
                        # describe the parameter
                        "description": "List of terminal command strings to be executed"
                    }
                },
                "required": ["commands"]
            }
        }
        ],
    # gpt need to respond with the parameters.
        function_call= {"name": "get_commands"}
)

# reply = completion.choices[0].message
# funcs = reply.to_dict()['function_call']['arguments']
# funcs = json.loads(funcs)
#
# print(funcs['commands'])

example_user_input = 'Can I drink 20 liters of beer'
completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-0613",
    messages=[{"role": "user", "content": example_user_input}],
    functions=[
    {
        "name": "get_varied_personality_responses",
        "description": "ingest the various personality responses",
        "parameters": {
            "type": "object",
            "properties": {
                "sassy_and_sarcastic": {
                    "type": "string",
                    "description": "A sassy and sarcastic version of the response to a user's query",
                },
                "happy_and_helpful": {
                    "type": "string",
                    "description": "A happy and helpful version of the response to a user's query",
                },
            },
            "required": ["sassy_and_sarcastic", "happy_and_helpful"],
        },
    }
        ],
        function_call = {"name": "get_varied_personality_responses"},
)

reply_content = completion.choices[0].message['function_call']['arguments']
# reply_content

page_builder_func = {
    "name": "page_builder",
    "description": "Creates product web pages",
    "parameters": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "The name of the product"
            },
            "copy_text": {
                "type": "string",
                "description": "Marketing copy that describes and sells the product"
            }
        },
        "required": ["title", "copy_text"]
    }
}


prompt = "Create a web page for a new cutting edge mango cutting machine"

res = openai.ChatCompletion.create(
    model='gpt-4-0613',  # swap for gpt-3.5-turbo-0613 if needed
    messages=[{"role": "user", "content": prompt}],
    functions=[page_builder_func]
)

if res['choices'][0]["finish_reason"] == "function_call":
    print("We should call a function!")

# This will give you the title and the description in nice order based on the prompt
name = res['choices'][0]['message']['function_call']['name']
args = json.loads(res['choices'][0]['message']['function_call']['arguments'])


page_builder_func = {
    "name": "page_builder",
    "description": "Creates product web pages",
    "parameters": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "The name of the product"
            },
            "copy_text": {
                "type": "string",
                "description": "Marketing copy that describes and sells the product"
            },
            "image_desc": {
                "type": "string",
                "description": "Concise description of the product image using descriptive language, no more than two sentences long"
            }
        },
        "required": ["title", "copy_text", "image_desc"]
    }
}


def query(prompt: str):
    res = openai.ChatCompletion.create(
        model='gpt-4-0613',  # swap for gpt-3.5-turbo-0613 if needed
        messages=[{"role": "user", "content": prompt}],
        functions=[page_builder_func]
    )
    if res['choices'][0]["finish_reason"] == "function_call":
        # this means we should call a function
        name = res['choices'][0]['message']['function_call']['name']
        args = json.loads(res['choices'][0]['message']['function_call']['arguments'])
        if name == 'page_builder':
            page_builder(**args)
        else:
            raise ValueError(f"Function name `{name}` not recognized!")
        return HTML('index.html')


query(prompt)


# Kan de functie toevoegen in de chat geschiedenis.
second_response = openai.ChatCompletion.create(
    model="gpt-4-0613",
    messages=[
        {"role": "user", "content": user_query},
        ai_response_message,
        {
            "role": "function",
            "name": "get_current_weather",
            "content": function_response,
        },
    ],
)