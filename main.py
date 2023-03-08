import openai

from dotenv import dotenv_values
env = dict(dotenv_values(".env"))

# character_name = input("Character Name: ")
# character_name = "Super Mario" if character_name == '' else character_name
#
# openai.api_key = env["OPENAI_API_KEY"]
#
#
# response = openai.Completion.create(model="text-davinci-003", prompt=f"write an energetic script for a tik tok video about the strange history of {character_name}", temperature=0.2, max_tokens=200)
# print(response)


response = {
  "choices": [
    {
      "finish_reason": "stop",
      "index": 0,
      "logprobs": None,
      "text": "\n\nHey everyone! \n\nToday I'm here to talk about the strange history of Super Mario!\n\nDid you know that Mario was originally created as a character for the 1981 arcade game Donkey Kong? He was known as Jumpman and was a carpenter, not a plumber!\n\nMario's first appearance as a plumber was in the 1983 classic Super Mario Bros. But did you know that Mario was originally called Mr. Video? It wasn't until the game was released in Japan that he was given the name Mario!\n\nMario has come a long way since then. He's been in over 200 games, and he's even been featured in movies, TV shows, and cartoons!\n\nSo there you have it, the strange history of Super Mario! Thanks for watching!"
    }
  ],
  "created": 1678232696,
  "id": "cmpl-6rbHEWNr62dRfrN93WtsWB3qtbG8R",
  "model": "text-davinci-003",
  "object": "text_completion",
  "usage": {
    "completion_tokens": 163,
    "prompt_tokens": 19,
    "total_tokens": 182
  }
}


text = response['choices'][0]['text']
print(text)


import ibm_watson
from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# Set up the Text to Speech service
authenticator = IAMAuthenticator(env['WATSON_API_KEY'])
text_to_speech = TextToSpeechV1(
    authenticator=authenticator
)

text_to_speech.set_service_url(env['WATSON_TTS_URL'])

# Generate speech from text
with open('output.mp3', 'wb') as audio_file:
    response = text_to_speech.synthesize(
        text=text,
        accept='audio/mp3',
        voice='en-AU_JackExpressive',
    ).get_result()
    audio_file.write(response.content)

