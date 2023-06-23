import openai
import os
from constants import OPENAI_API_KEY
import json

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
openai.api_key = OPENAI_API_KEY


# with this we dont need to extract the text from the gpt response
example_user_input = 'Hier is een dictionary: {name:none, age:none, salary:none}. Bedenk voor elke key een passende vraag en vul dat in als value. Zodra je de vragen hebt stuur dan de dictionary terug waarbij none is vervangen door de bijpassende vraag, stuur alleen de dictionary terug.'

# YOU NEED TO THINK HOW WOULD I DESCRIBE A FUNCTION
completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-0613",
    messages=[{"role": "user", "content": example_user_input}],
        functions= [
        {
            "name": "get_questions",
            # how does the function works
            "description": "Extract list with questions",
            # parameters of funtion
            "parameters": {
                "type": "object",
                "properties": {
                    "response": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "description": "questions extracted from the values from the dictionary "
                        },
                        # describe the parameter
                        "description": "The questions extracted from the response to a user's query"
                    }
                },
                "required": ["response"]
            }
        }
        ],
    # gpt need to respond with the parameters.
        function_call= {"name": "get_questions"}
)

reply = completion.choices[0].message
funcs = reply.to_dict()['function_call']['arguments']
funcs = json.loads(funcs)



# completion = openai.ChatCompletion.create(
#     model="gpt-3.5-turbo-0613",
#     messages=[{"role": "user", "content": example_user_input}],
#         functions=[
#         {
#             "name": "get_commands",
#             # how does the function works
#             "description": "Get the xml code",
#             # parameters of funtion
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "commands": {
#                         "type": "array",
#                         "items": {
#                             "type": "string",
#                             "description": "Response from gpt with xml code"
#                         },
#                         # describe the parameter
#                         "description": "Response with xml code"
#                     }
#                 },
#                 "required": ["commands"]
#             }
#         }
#         ],
#     # gpt need to respond with the parameters.
#         function_call= {"name": "get_commands"}
# )