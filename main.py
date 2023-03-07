import openai

from dotenv import dotenv_values

character_name = input("Character Name: ")
character_name = "Super Mario" if character_name == '' else character_name

env = dict(dotenv_values(".env"))
openai.api_key = env["OPENAI_API_KEY"]


response = openai.Completion.create(model="text-davinci-003", prompt=f"write an energetic script for a tik tok video about the strange history of {character_name}", temperature=0.2, max_tokens=200)
print(response)