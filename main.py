import random

random.seed(38724)

import openai
import os
from dotenv import dotenv_values
import requests
import os

from tqdm import tqdm

if not os.path.exists("captions"):
    os.mkdir("captions")


def align(audio, text) -> dict:
    # while not os.path.isfile(audio):
    #     pass
    # while not os.path.isfile(text):
    #     pass

    # get output from gentle
    url = 'http://localhost:8765/transcriptions?async=false'
    files = {'audio': open(audio, 'rb'),
             'transcript': open(text, 'rb')}
    try:
        r = requests.post(url, files=files)
    except requests.exceptions.RequestException as e:
        raise Exception('[ALIGN ERROR] Failed to post to Gentle: Make sure Docker Desktop is running...')

    return r.json()


env = dict(dotenv_values(".env"))

character_name = input("Character Name: ")
character_name = "Super Mario" if character_name == '' else character_name

openai.api_key = env["OPENAI_API_KEY"]
#
#
# script_response = openai.Completion.create(model="text-davinci-003", prompt=f"write an energetic script for a tik tok video about the strange history of {character_name}", temperature=0.2, max_tokens=200)
# print(script_response)


script_response = {
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

text = script_response['choices'][0]['text']
with open('script.txt', 'w+') as f:
    f.write(text)
    f.flush()
    f.close()
print(text)

import ibm_watson
from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# # Set up the Text to Speech service
# authenticator = IAMAuthenticator(env['WATSON_API_KEY'])
# text_to_speech = TextToSpeechV1(
#     authenticator=authenticator
# )
#
# text_to_speech.set_service_url(env['WATSON_TTS_URL'])
#
# # Generate speech from text
# with open('output.mp3', 'wb') as audio_file:
#     response = text_to_speech.synthesize(
#         text=text,
#         accept='audio/mp3',
#         voice='en-AU_JackExpressive',
#     ).get_result()
#     audio_file.write(response.content)
# print('---------')


import spacy

# load the English language model
nlp = spacy.load("en_core_web_sm")
# define a sentence with a multi-word proper noun
# process the sentence with spaCy
doc = nlp(text)
# identify named entities and combine multi-word entities
p_nouns = doc.ents
i_nouns = [token for token in doc if token.pos_ in ["NOUN"]]

pc = 0
ic = 0
nouns = []
while pc < len(p_nouns) and ic < len(i_nouns):
    if p_nouns[pc].start < i_nouns[ic].i:

        t = p_nouns[pc].text
        s = p_nouns[pc].start
        while s > 0:  # exception for Mr./Mrs./Dr. etc
            if doc[s - 1].pos_ == 'PROPN':
                t = doc[s - 1].text + ' ' + t
                s -= 1
            else:
                break

        nouns.append(t)
        pc += 1
    else:
        nouns.append(i_nouns[ic].text)
        ic += 1
while pc < len(p_nouns):
    t = p_nouns[pc].text
    s = p_nouns[pc].start
    while s > 0:  # exception for Mr./Mrs./Dr. etc
        if doc[s - 1].pos_ == 'PROPN':
            t = doc[s - 1].text + ' ' + t
            s -= 1
        else:
            break

    nouns.append(t)
    pc += 1
while ic < len(i_nouns):
    nouns.append(i_nouns[ic].text)
    ic += 1
print("NOUNS: ", nouns)

# Download images from duckduckgo
#
# from ImageDownloader import download
#
# for n in nouns:
#     print("Searching for:", n)
#     download(f'{n}', limit=10)

single_nouns = [a.split(' ')[0] for a in nouns]

# aligned = align('output.mp3', 'script.txt')
aligned = {
    'transcript': "\n\nHey everyone! \n\nToday I'm here to talk about the strange history of Super Mario!\n\nDid you know that Mario was originally created as a character for the 1981 arcade game Donkey Kong? He was known as Jumpman and was a carpenter, not a plumber!\n\nMario's first appearance as a plumber was in the 1983 classic Super Mario Bros. But did you know that Mario was originally called Mr. Video? It wasn't until the game was released in Japan that he was given the name Mario!\n\nMario has come a long way since then. He's been in over 200 games, and he's even been featured in movies, TV shows, and cartoons!\n\nSo there you have it, the strange history of Super Mario! Thanks for watching!",
    'words': [{'alignedWord': 'hey', 'case': 'success', 'end': 0.39, 'endOffset': 5,
               'phones': [{'duration': 0.1, 'phone': 'hh_B'}, {'duration': 0.14, 'phone': 'ey_E'}], 'start': 0.15,
               'startOffset': 2, 'word': 'Hey'},
              {'alignedWord': 'everyone', 'case': 'success', 'end': 1.06, 'endOffset': 14,
               'phones': [{'duration': 0.11, 'phone': 'eh_B'}, {'duration': 0.11, 'phone': 'v_I'},
                          {'duration': 0.05, 'phone': 'r_I'}, {'duration': 0.07, 'phone': 'iy_I'},
                          {'duration': 0.06, 'phone': 'w_I'}, {'duration': 0.1, 'phone': 'ah_I'},
                          {'duration': 0.15, 'phone': 'n_E'}], 'start': 0.41, 'startOffset': 6, 'word': 'everyone'},
              {'alignedWord': 'today', 'case': 'success', 'end': 1.5499999999999998, 'endOffset': 23,
               'phones': [{'duration': 0.07, 'phone': 't_B'}, {'duration': 0.05, 'phone': 'ah_I'},
                          {'duration': 0.08, 'phone': 'd_I'}, {'duration': 0.17, 'phone': 'ey_E'}], 'start': 1.18,
               'startOffset': 18, 'word': 'Today'},
              {'alignedWord': "i'm", 'case': 'success', 'end': 1.74, 'endOffset': 27,
               'phones': [{'duration': 0.09, 'phone': 'ah_B'}, {'duration': 0.1, 'phone': 'm_E'}], 'start': 1.55,
               'startOffset': 24, 'word': "I'm"},
              {'alignedWord': 'here', 'case': 'success', 'end': 1.96, 'endOffset': 32,
               'phones': [{'duration': 0.06, 'phone': 'hh_B'}, {'duration': 0.09, 'phone': 'iy_I'},
                          {'duration': 0.07, 'phone': 'r_E'}], 'start': 1.74, 'startOffset': 28, 'word': 'here'},
              {'alignedWord': 'to', 'case': 'success', 'end': 2.07, 'endOffset': 35,
               'phones': [{'duration': 0.06, 'phone': 't_B'}, {'duration': 0.05, 'phone': 'ah_E'}], 'start': 1.96,
               'startOffset': 33, 'word': 'to'},
              {'alignedWord': 'talk', 'case': 'success', 'end': 2.3499999999999996, 'endOffset': 40,
               'phones': [{'duration': 0.09, 'phone': 't_B'}, {'duration': 0.12, 'phone': 'ao_I'},
                          {'duration': 0.07, 'phone': 'k_E'}], 'start': 2.07, 'startOffset': 36, 'word': 'talk'},
              {'alignedWord': 'about', 'case': 'success', 'end': 2.58, 'endOffset': 46,
               'phones': [{'duration': 0.05, 'phone': 'ah_B'}, {'duration': 0.05, 'phone': 'b_I'},
                          {'duration': 0.06, 'phone': 'aw_I'}, {'duration': 0.06, 'phone': 't_E'}], 'start': 2.36,
               'startOffset': 41, 'word': 'about'},
              {'alignedWord': 'the', 'case': 'success', 'end': 2.67, 'endOffset': 50,
               'phones': [{'duration': 0.03, 'phone': 'dh_B'}, {'duration': 0.06, 'phone': 'ah_E'}], 'start': 2.58,
               'startOffset': 47, 'word': 'the'},
              {'alignedWord': 'strange', 'case': 'success', 'end': 3.06, 'endOffset': 58,
               'phones': [{'duration': 0.05, 'phone': 's_B'}, {'duration': 0.08, 'phone': 't_I'},
                          {'duration': 0.07, 'phone': 'r_I'}, {'duration': 0.09, 'phone': 'ey_I'},
                          {'duration': 0.04, 'phone': 'n_I'}, {'duration': 0.06, 'phone': 'jh_E'}], 'start': 2.67,
               'startOffset': 51, 'word': 'strange'},
              {'alignedWord': 'history', 'case': 'success', 'end': 3.43, 'endOffset': 66,
               'phones': [{'duration': 0.05, 'phone': 'hh_B'}, {'duration': 0.06, 'phone': 'ih_I'},
                          {'duration': 0.05, 'phone': 's_I'}, {'duration': 0.06, 'phone': 't_I'},
                          {'duration': 0.1, 'phone': 'er_I'}, {'duration': 0.05, 'phone': 'iy_E'}], 'start': 3.06,
               'startOffset': 59, 'word': 'history'},
              {'alignedWord': 'of', 'case': 'success', 'end': 3.54, 'endOffset': 69,
               'phones': [{'duration': 0.05, 'phone': 'ah_B'}, {'duration': 0.06, 'phone': 'v_E'}], 'start': 3.43,
               'startOffset': 67, 'word': 'of'},
              {'alignedWord': 'super', 'case': 'success', 'end': 3.86, 'endOffset': 75,
               'phones': [{'duration': 0.1, 'phone': 's_B'}, {'duration': 0.08, 'phone': 'uw_I'},
                          {'duration': 0.06, 'phone': 'p_I'}, {'duration': 0.08, 'phone': 'er_E'}], 'start': 3.54,
               'startOffset': 70, 'word': 'Super'},
              {'alignedWord': 'mario', 'case': 'success', 'end': 4.43, 'endOffset': 81,
               'phones': [{'duration': 0.06, 'phone': 'm_B'}, {'duration': 0.12, 'phone': 'aa_I'},
                          {'duration': 0.09, 'phone': 'r_I'}, {'duration': 0.1, 'phone': 'iy_I'},
                          {'duration': 0.2, 'phone': 'ow_E'}], 'start': 3.86, 'startOffset': 76, 'word': 'Mario'},
              {'alignedWord': 'did', 'case': 'success', 'end': 4.74, 'endOffset': 87,
               'phones': [{'duration': 0.11, 'phone': 'd_B'}, {'duration': 0.04, 'phone': 'ih_I'},
                          {'duration': 0.08, 'phone': 'd_E'}], 'start': 4.51, 'startOffset': 84, 'word': 'Did'},
              {'alignedWord': 'you', 'case': 'success', 'end': 4.9, 'endOffset': 91,
               'phones': [{'duration': 0.09, 'phone': 'y_B'}, {'duration': 0.07, 'phone': 'uw_E'}], 'start': 4.74,
               'startOffset': 88, 'word': 'you'},
              {'alignedWord': 'know', 'case': 'success', 'end': 5.09, 'endOffset': 96,
               'phones': [{'duration': 0.09, 'phone': 'n_B'}, {'duration': 0.09, 'phone': 'ow_E'}], 'start': 4.91,
               'startOffset': 92, 'word': 'know'},
              {'alignedWord': 'that', 'case': 'success', 'end': 5.29, 'endOffset': 101,
               'phones': [{'duration': 0.07, 'phone': 'dh_B'}, {'duration': 0.05, 'phone': 'ae_I'},
                          {'duration': 0.08, 'phone': 't_E'}], 'start': 5.09, 'startOffset': 97, 'word': 'that'},
              {'alignedWord': 'mario', 'case': 'success', 'end': 5.69, 'endOffset': 107,
               'phones': [{'duration': 0.04, 'phone': 'm_B'}, {'duration': 0.11, 'phone': 'aa_I'},
                          {'duration': 0.08, 'phone': 'r_I'}, {'duration': 0.09, 'phone': 'iy_I'},
                          {'duration': 0.08, 'phone': 'ow_E'}], 'start': 5.29, 'startOffset': 102, 'word': 'Mario'},
              {'alignedWord': 'was', 'case': 'success', 'end': 5.880000000000001, 'endOffset': 111,
               'phones': [{'duration': 0.05, 'phone': 'w_B'}, {'duration': 0.06, 'phone': 'ah_I'},
                          {'duration': 0.08, 'phone': 'z_E'}], 'start': 5.69, 'startOffset': 108, 'word': 'was'},
              {'alignedWord': 'originally', 'case': 'success', 'end': 6.49, 'endOffset': 122,
               'phones': [{'duration': 0.17, 'phone': 'er_B'}, {'duration': 0.08, 'phone': 'ih_I'},
                          {'duration': 0.09, 'phone': 'jh_I'}, {'duration': 0.03, 'phone': 'n_I'},
                          {'duration': 0.07, 'phone': 'ah_I'}, {'duration': 0.07, 'phone': 'l_I'},
                          {'duration': 0.08, 'phone': 'iy_E'}], 'start': 5.9, 'startOffset': 112, 'word': 'originally'},
              {'alignedWord': 'created', 'case': 'success', 'end': 7.0200000000000005, 'endOffset': 130,
               'phones': [{'duration': 0.1, 'phone': 'k_B'}, {'duration': 0.08, 'phone': 'r_I'},
                          {'duration': 0.07, 'phone': 'iy_I'}, {'duration': 0.09, 'phone': 'ey_I'},
                          {'duration': 0.06, 'phone': 't_I'}, {'duration': 0.06, 'phone': 'ah_I'},
                          {'duration': 0.07, 'phone': 'd_E'}], 'start': 6.49, 'startOffset': 123, 'word': 'created'},
              {'alignedWord': 'as', 'case': 'success', 'end': 7.1499999999999995, 'endOffset': 133,
               'phones': [{'duration': 0.08, 'phone': 'ae_B'}, {'duration': 0.05, 'phone': 'z_E'}], 'start': 7.02,
               'startOffset': 131, 'word': 'as'},
              {'alignedWord': 'a', 'case': 'success', 'end': 7.220000000000001, 'endOffset': 135,
               'phones': [{'duration': 0.07, 'phone': 'ah_S'}], 'start': 7.15, 'startOffset': 134, 'word': 'a'},
              {'alignedWord': 'character', 'case': 'success', 'end': 7.6899999999999995, 'endOffset': 145,
               'phones': [{'duration': 0.12, 'phone': 'k_B'}, {'duration': 0.06, 'phone': 'eh_I'},
                          {'duration': 0.07, 'phone': 'r_I'}, {'duration': 0.05, 'phone': 'ih_I'},
                          {'duration': 0.03, 'phone': 'k_I'}, {'duration': 0.08, 'phone': 't_I'},
                          {'duration': 0.06, 'phone': 'er_E'}], 'start': 7.22, 'startOffset': 136, 'word': 'character'},
              {'alignedWord': 'for', 'case': 'success', 'end': 7.8500000000000005, 'endOffset': 149,
               'phones': [{'duration': 0.05, 'phone': 'f_B'}, {'duration': 0.06, 'phone': 'er_E'}], 'start': 7.74,
               'startOffset': 146, 'word': 'for'},
              {'alignedWord': 'the', 'case': 'success', 'end': 7.9399999999999995, 'endOffset': 153,
               'phones': [{'duration': 0.01, 'phone': 'dh_B'}, {'duration': 0.08, 'phone': 'ah_E'}], 'start': 7.85,
               'startOffset': 150, 'word': 'the'},
              {'alignedWord': '<unk>', 'case': 'success', 'end': 8.89, 'endOffset': 158,
               'phones': [{'duration': 0.95, 'phone': 'oov_S'}], 'start': 7.94, 'startOffset': 154, 'word': '1981'},
              {'alignedWord': 'arcade', 'case': 'success', 'end': 9.239999, 'endOffset': 165,
               'phones': [{'duration': 0.01, 'phone': 'aa_B'}, {'duration': 0.06, 'phone': 'r_I'},
                          {'duration': 0.1, 'phone': 'k_I'}, {'duration': 0.1, 'phone': 'ey_I'},
                          {'duration': 0.08, 'phone': 'd_E'}], 'start': 8.889999, 'startOffset': 159, 'word': 'arcade'},
              {'alignedWord': 'game', 'case': 'success', 'end': 9.46, 'endOffset': 170,
               'phones': [{'duration': 0.06, 'phone': 'g_B'}, {'duration': 0.09, 'phone': 'ey_I'},
                          {'duration': 0.07, 'phone': 'm_E'}], 'start': 9.24, 'startOffset': 166, 'word': 'game'},
              {'alignedWord': 'donkey', 'case': 'success', 'end': 9.770000000000001, 'endOffset': 177,
               'phones': [{'duration': 0.06, 'phone': 'd_B'}, {'duration': 0.04, 'phone': 'aa_I'},
                          {'duration': 0.07, 'phone': 'ng_I'}, {'duration': 0.07, 'phone': 'k_I'},
                          {'duration': 0.07, 'phone': 'iy_E'}], 'start': 9.46, 'startOffset': 171, 'word': 'Donkey'},
              {'alignedWord': 'kong', 'case': 'success', 'end': 10.08, 'endOffset': 182,
               'phones': [{'duration': 0.06, 'phone': 'k_B'}, {'duration': 0.11, 'phone': 'ao_I'},
                          {'duration': 0.14, 'phone': 'ng_E'}], 'start': 9.77, 'startOffset': 178, 'word': 'Kong'},
              {'alignedWord': 'he', 'case': 'success', 'end': 10.36, 'endOffset': 186,
               'phones': [{'duration': 0.11, 'phone': 'hh_B'}, {'duration': 0.08, 'phone': 'iy_E'}], 'start': 10.17,
               'startOffset': 184, 'word': 'He'},
              {'alignedWord': 'was', 'case': 'success', 'end': 10.54, 'endOffset': 190,
               'phones': [{'duration': 0.05, 'phone': 'w_B'}, {'duration': 0.06, 'phone': 'ah_I'},
                          {'duration': 0.07, 'phone': 'z_E'}], 'start': 10.36, 'startOffset': 187, 'word': 'was'},
              {'alignedWord': 'known', 'case': 'success', 'end': 10.79, 'endOffset': 196,
               'phones': [{'duration': 0.08, 'phone': 'n_B'}, {'duration': 0.11, 'phone': 'ow_I'},
                          {'duration': 0.06, 'phone': 'n_E'}], 'start': 10.54, 'startOffset': 191, 'word': 'known'},
              {'alignedWord': 'as', 'case': 'success', 'end': 10.909999999999998, 'endOffset': 199,
               'phones': [{'duration': 0.06, 'phone': 'eh_B'}, {'duration': 0.06, 'phone': 'z_E'}], 'start': 10.79,
               'startOffset': 197, 'word': 'as'},
              {'alignedWord': '<unk>', 'case': 'success', 'end': 11.37, 'endOffset': 207,
               'phones': [{'duration': 0.43, 'phone': 'oov_S'}], 'start': 10.94, 'startOffset': 200, 'word': 'Jumpman'},
              {'alignedWord': 'and', 'case': 'success', 'end': 11.45, 'endOffset': 211,
               'phones': [{'duration': 0.01, 'phone': 'ae_B'}, {'duration': 0.01, 'phone': 'n_I'},
                          {'duration': 0.06, 'phone': 'd_E'}], 'start': 11.37, 'startOffset': 208, 'word': 'and'},
              {'alignedWord': 'was', 'case': 'success', 'end': 11.58, 'endOffset': 215,
               'phones': [{'duration': 0.04, 'phone': 'w_B'}, {'duration': 0.04, 'phone': 'ah_I'},
                          {'duration': 0.05, 'phone': 'z_E'}], 'start': 11.45, 'startOffset': 212, 'word': 'was'},
              {'alignedWord': 'a', 'case': 'success', 'end': 11.64, 'endOffset': 217,
               'phones': [{'duration': 0.06, 'phone': 'ah_S'}], 'start': 11.58, 'startOffset': 216, 'word': 'a'},
              {'alignedWord': 'carpenter', 'case': 'success', 'end': 12.249998999999999, 'endOffset': 227,
               'phones': [{'duration': 0.11, 'phone': 'k_B'}, {'duration': 0.03, 'phone': 'aa_I'},
                          {'duration': 0.06, 'phone': 'r_I'}, {'duration': 0.05, 'phone': 'p_I'},
                          {'duration': 0.05, 'phone': 'ah_I'}, {'duration': 0.07, 'phone': 'n_I'},
                          {'duration': 0.07, 'phone': 't_I'}, {'duration': 0.17, 'phone': 'er_E'}], 'start': 11.639999,
               'startOffset': 218, 'word': 'carpenter'},
              {'alignedWord': 'not', 'case': 'success', 'end': 12.51, 'endOffset': 232,
               'phones': [{'duration': 0.11, 'phone': 'n_B'}, {'duration': 0.06, 'phone': 'aa_I'},
                          {'duration': 0.05, 'phone': 't_E'}], 'start': 12.29, 'startOffset': 229, 'word': 'not'},
              {'alignedWord': 'a', 'case': 'success', 'end': 12.559999000000001, 'endOffset': 234,
               'phones': [{'duration': 0.05, 'phone': 'ah_S'}], 'start': 12.509999, 'startOffset': 233, 'word': 'a'},
              {'alignedWord': 'plumber', 'case': 'success', 'end': 12.969999, 'endOffset': 242,
               'phones': [{'duration': 0.08, 'phone': 'p_B'}, {'duration': 0.04, 'phone': 'l_I'},
                          {'duration': 0.06, 'phone': 'ah_I'}, {'duration': 0.07, 'phone': 'm_I'},
                          {'duration': 0.16, 'phone': 'er_E'}], 'start': 12.559999, 'startOffset': 235,
               'word': 'plumber'}, {'alignedWord': "mario's", 'case': 'success', 'end': 13.65, 'endOffset': 252,
                                    'phones': [{'duration': 0.12, 'phone': 'm_B'}, {'duration': 0.08, 'phone': 'aa_I'},
                                               {'duration': 0.08, 'phone': 'r_I'}, {'duration': 0.09, 'phone': 'iy_I'},
                                               {'duration': 0.07, 'phone': 'ow_I'}, {'duration': 0.12, 'phone': 'z_E'}],
                                    'start': 13.09, 'startOffset': 245, 'word': "Mario's"},
              {'alignedWord': 'first', 'case': 'success', 'end': 13.94, 'endOffset': 258,
               'phones': [{'duration': 0.07, 'phone': 'f_B'}, {'duration': 0.13, 'phone': 'er_I'},
                          {'duration': 0.02, 'phone': 's_I'}, {'duration': 0.06, 'phone': 't_E'}], 'start': 13.66,
               'startOffset': 253, 'word': 'first'},
              {'alignedWord': 'appearance', 'case': 'success', 'end': 14.42, 'endOffset': 269,
               'phones': [{'duration': 0.06, 'phone': 'ah_B'}, {'duration': 0.08, 'phone': 'p_I'},
                          {'duration': 0.12, 'phone': 'ih_I'}, {'duration': 0.06, 'phone': 'r_I'},
                          {'duration': 0.05, 'phone': 'ah_I'}, {'duration': 0.07, 'phone': 'n_I'},
                          {'duration': 0.04, 'phone': 's_E'}], 'start': 13.94, 'startOffset': 259,
               'word': 'appearance'}, {'alignedWord': 'as', 'case': 'success', 'end': 14.56, 'endOffset': 272,
                                       'phones': [{'duration': 0.07, 'phone': 'eh_B'},
                                                  {'duration': 0.07, 'phone': 'z_E'}], 'start': 14.42,
                                       'startOffset': 270, 'word': 'as'},
              {'alignedWord': 'a', 'case': 'success', 'end': 14.609999, 'endOffset': 274,
               'phones': [{'duration': 0.05, 'phone': 'ah_S'}], 'start': 14.559999, 'startOffset': 273, 'word': 'a'},
              {'alignedWord': 'plumber', 'case': 'success', 'end': 15.01, 'endOffset': 282,
               'phones': [{'duration': 0.11, 'phone': 'p_B'}, {'duration': 0.08, 'phone': 'l_I'},
                          {'duration': 0.03, 'phone': 'ah_I'}, {'duration': 0.08, 'phone': 'm_I'},
                          {'duration': 0.1, 'phone': 'er_E'}], 'start': 14.61, 'startOffset': 275, 'word': 'plumber'},
              {'alignedWord': 'was', 'case': 'success', 'end': 15.169999, 'endOffset': 286,
               'phones': [{'duration': 0.05, 'phone': 'w_B'}, {'duration': 0.07, 'phone': 'ah_I'},
                          {'duration': 0.04, 'phone': 'z_E'}], 'start': 15.009999, 'startOffset': 283, 'word': 'was'},
              {'alignedWord': 'in', 'case': 'success', 'end': 15.29, 'endOffset': 289,
               'phones': [{'duration': 0.07, 'phone': 'ih_B'}, {'duration': 0.05, 'phone': 'n_E'}], 'start': 15.17,
               'startOffset': 287, 'word': 'in'},
              {'alignedWord': 'the', 'case': 'success', 'end': 15.409999999999998, 'endOffset': 293,
               'phones': [{'duration': 0.04, 'phone': 'dh_B'}, {'duration': 0.08, 'phone': 'ah_E'}], 'start': 15.29,
               'startOffset': 290, 'word': 'the'},
              {'alignedWord': '<unk>', 'case': 'success', 'end': 16.38, 'endOffset': 298,
               'phones': [{'duration': 0.97, 'phone': 'oov_S'}], 'start': 15.41, 'startOffset': 294, 'word': '1983'},
              {'alignedWord': 'classic', 'case': 'success', 'end': 16.769999, 'endOffset': 306,
               'phones': [{'duration': 0.06, 'phone': 'k_B'}, {'duration': 0.06, 'phone': 'l_I'},
                          {'duration': 0.06, 'phone': 'ae_I'}, {'duration': 0.08, 'phone': 's_I'},
                          {'duration': 0.05, 'phone': 'ih_I'}, {'duration': 0.07, 'phone': 'k_E'}], 'start': 16.389999,
               'startOffset': 299, 'word': 'classic'},
              {'alignedWord': 'super', 'case': 'success', 'end': 17.09, 'endOffset': 312,
               'phones': [{'duration': 0.11, 'phone': 's_B'}, {'duration': 0.07, 'phone': 'uw_I'},
                          {'duration': 0.08, 'phone': 'p_I'}, {'duration': 0.06, 'phone': 'er_E'}], 'start': 16.77,
               'startOffset': 307, 'word': 'Super'},
              {'alignedWord': 'mario', 'case': 'success', 'end': 17.429999, 'endOffset': 318,
               'phones': [{'duration': 0.07, 'phone': 'm_B'}, {'duration': 0.07, 'phone': 'aa_I'},
                          {'duration': 0.08, 'phone': 'r_I'}, {'duration': 0.09, 'phone': 'iy_I'},
                          {'duration': 0.01, 'phone': 'ow_E'}], 'start': 17.109999, 'startOffset': 313,
               'word': 'Mario'}, {'alignedWord': '<unk>', 'case': 'success', 'end': 18.02, 'endOffset': 323,
                                  'phones': [{'duration': 0.59, 'phone': 'oov_S'}], 'start': 17.43, 'startOffset': 319,
                                  'word': 'Bros'},
              {'alignedWord': 'but', 'case': 'success', 'end': 18.419999999999998, 'endOffset': 328,
               'phones': [{'duration': 0.07, 'phone': 'b_B'}, {'duration': 0.09, 'phone': 'ah_I'},
                          {'duration': 0.08, 'phone': 't_E'}], 'start': 18.18, 'startOffset': 325, 'word': 'But'},
              {'alignedWord': 'did', 'case': 'success', 'end': 18.670001, 'endOffset': 332,
               'phones': [{'duration': 0.11, 'phone': 'd_B'}, {'duration': 0.04, 'phone': 'ih_I'},
                          {'duration': 0.08, 'phone': 'd_E'}], 'start': 18.440001, 'startOffset': 329, 'word': 'did'},
              {'alignedWord': 'you', 'case': 'success', 'end': 18.8, 'endOffset': 336,
               'phones': [{'duration': 0.06, 'phone': 'y_B'}, {'duration': 0.07, 'phone': 'uw_E'}], 'start': 18.67,
               'startOffset': 333, 'word': 'you'},
              {'alignedWord': 'know', 'case': 'success', 'end': 18.990000000000002, 'endOffset': 341,
               'phones': [{'duration': 0.07, 'phone': 'n_B'}, {'duration': 0.1, 'phone': 'ow_E'}], 'start': 18.82,
               'startOffset': 337, 'word': 'know'},
              {'alignedWord': 'that', 'case': 'success', 'end': 19.189999999999998, 'endOffset': 346,
               'phones': [{'duration': 0.06, 'phone': 'dh_B'}, {'duration': 0.06, 'phone': 'ae_I'},
                          {'duration': 0.08, 'phone': 't_E'}], 'start': 18.99, 'startOffset': 342, 'word': 'that'},
              {'alignedWord': 'mario', 'case': 'success', 'end': 19.6, 'endOffset': 352,
               'phones': [{'duration': 0.04, 'phone': 'm_B'}, {'duration': 0.12, 'phone': 'aa_I'},
                          {'duration': 0.07, 'phone': 'r_I'}, {'duration': 0.1, 'phone': 'iy_I'},
                          {'duration': 0.08, 'phone': 'ow_E'}], 'start': 19.19, 'startOffset': 347, 'word': 'Mario'},
              {'alignedWord': 'was', 'case': 'success', 'end': 19.810000000000002, 'endOffset': 356,
               'phones': [{'duration': 0.08, 'phone': 'w_B'}, {'duration': 0.05, 'phone': 'ah_I'},
                          {'duration': 0.08, 'phone': 'z_E'}], 'start': 19.6, 'startOffset': 353, 'word': 'was'},
              {'alignedWord': 'originally', 'case': 'success', 'end': 20.389999999999997, 'endOffset': 367,
               'phones': [{'duration': 0.17, 'phone': 'er_B'}, {'duration': 0.08, 'phone': 'ih_I'},
                          {'duration': 0.08, 'phone': 'jh_I'}, {'duration': 0.04, 'phone': 'n_I'},
                          {'duration': 0.07, 'phone': 'ah_I'}, {'duration': 0.06, 'phone': 'l_I'},
                          {'duration': 0.08, 'phone': 'iy_E'}], 'start': 19.81, 'startOffset': 357,
               'word': 'originally'}, {'alignedWord': 'called', 'case': 'success', 'end': 20.66, 'endOffset': 374,
                                       'phones': [{'duration': 0.09, 'phone': 'k_B'},
                                                  {'duration': 0.07, 'phone': 'ao_I'},
                                                  {'duration': 0.05, 'phone': 'l_I'},
                                                  {'duration': 0.06, 'phone': 'd_E'}], 'start': 20.39,
                                       'startOffset': 368, 'word': 'called'},
              {'alignedWord': 'mr', 'case': 'success', 'end': 20.9, 'endOffset': 377,
               'phones': [{'duration': 0.06, 'phone': 'm_B'}, {'duration': 0.06, 'phone': 'ih_I'},
                          {'duration': 0.04, 'phone': 's_I'}, {'duration': 0.07, 'phone': 't_I'},
                          {'duration': 0.01, 'phone': 'er_E'}], 'start': 20.66, 'startOffset': 375, 'word': 'Mr'},
              {'alignedWord': 'video', 'case': 'success', 'end': 21.45, 'endOffset': 384,
               'phones': [{'duration': 0.11, 'phone': 'v_B'}, {'duration': 0.07, 'phone': 'ih_I'},
                          {'duration': 0.04, 'phone': 'd_I'}, {'duration': 0.11, 'phone': 'iy_I'},
                          {'duration': 0.22, 'phone': 'ow_E'}], 'start': 20.9, 'startOffset': 379, 'word': 'Video'},
              {'alignedWord': 'it', 'case': 'success', 'end': 21.73, 'endOffset': 388,
               'phones': [{'duration': 0.12, 'phone': 'ih_B'}, {'duration': 0.09, 'phone': 't_E'}], 'start': 21.52,
               'startOffset': 386, 'word': 'It'},
              {'alignedWord': "wasn't", 'case': 'success', 'end': 22.07, 'endOffset': 395,
               'phones': [{'duration': 0.12, 'phone': 'w_B'}, {'duration': 0.07, 'phone': 'aa_I'},
                          {'duration': 0.03, 'phone': 'z_I'}, {'duration': 0.06, 'phone': 'ah_I'},
                          {'duration': 0.03, 'phone': 'n_I'}, {'duration': 0.02, 'phone': 't_E'}],
               'start': 21.740000000000002, 'startOffset': 389, 'word': "wasn't"},
              {'alignedWord': 'until', 'case': 'success', 'end': 22.330000000000002, 'endOffset': 401,
               'phones': [{'duration': 0.07, 'phone': 'ah_B'}, {'duration': 0.05, 'phone': 'n_I'},
                          {'duration': 0.05, 'phone': 't_I'}, {'duration': 0.02, 'phone': 'ih_I'},
                          {'duration': 0.07, 'phone': 'l_E'}], 'start': 22.07, 'startOffset': 396, 'word': 'until'},
              {'alignedWord': 'the', 'case': 'success', 'end': 22.409999999999997, 'endOffset': 405,
               'phones': [{'duration': 0.03, 'phone': 'dh_B'}, {'duration': 0.05, 'phone': 'ah_E'}], 'start': 22.33,
               'startOffset': 402, 'word': 'the'},
              {'alignedWord': 'game', 'case': 'success', 'end': 22.69, 'endOffset': 410,
               'phones': [{'duration': 0.08, 'phone': 'g_B'}, {'duration': 0.12, 'phone': 'ey_I'},
                          {'duration': 0.08, 'phone': 'm_E'}], 'start': 22.41, 'startOffset': 406, 'word': 'game'},
              {'alignedWord': 'was', 'case': 'success', 'end': 22.830000000000002, 'endOffset': 414,
               'phones': [{'duration': 0.02, 'phone': 'w_B'}, {'duration': 0.05, 'phone': 'ah_I'},
                          {'duration': 0.07, 'phone': 'z_E'}], 'start': 22.69, 'startOffset': 411, 'word': 'was'},
              {'alignedWord': 'released', 'case': 'success', 'end': 23.229999999999997, 'endOffset': 423,
               'phones': [{'duration': 0.04, 'phone': 'r_B'}, {'duration': 0.07, 'phone': 'iy_I'},
                          {'duration': 0.09, 'phone': 'l_I'}, {'duration': 0.08, 'phone': 'iy_I'},
                          {'duration': 0.06, 'phone': 's_I'}, {'duration': 0.06, 'phone': 't_E'}], 'start': 22.83,
               'startOffset': 415, 'word': 'released'},
              {'alignedWord': 'in', 'case': 'success', 'end': 23.34, 'endOffset': 426,
               'phones': [{'duration': 0.04, 'phone': 'ih_B'}, {'duration': 0.07, 'phone': 'n_E'}], 'start': 23.23,
               'startOffset': 424, 'word': 'in'},
              {'alignedWord': 'japan', 'case': 'success', 'end': 23.78, 'endOffset': 432,
               'phones': [{'duration': 0.07, 'phone': 'jh_B'}, {'duration': 0.05, 'phone': 'ah_I'},
                          {'duration': 0.11, 'phone': 'p_I'}, {'duration': 0.12, 'phone': 'ae_I'},
                          {'duration': 0.09, 'phone': 'n_E'}], 'start': 23.34, 'startOffset': 427, 'word': 'Japan'},
              {'alignedWord': 'that', 'case': 'success', 'end': 23.89, 'endOffset': 437,
               'phones': [{'duration': 0.01, 'phone': 'dh_B'}, {'duration': 0.06, 'phone': 'ah_I'},
                          {'duration': 0.04, 'phone': 't_E'}], 'start': 23.78, 'startOffset': 433, 'word': 'that'},
              {'alignedWord': 'he', 'case': 'success', 'end': 24.009999999999998, 'endOffset': 440,
               'phones': [{'duration': 0.05, 'phone': 'hh_B'}, {'duration': 0.06, 'phone': 'iy_E'}], 'start': 23.9,
               'startOffset': 438, 'word': 'he'},
              {'alignedWord': 'was', 'case': 'success', 'end': 24.209999999999997, 'endOffset': 444,
               'phones': [{'duration': 0.05, 'phone': 'w_B'}, {'duration': 0.07, 'phone': 'ah_I'},
                          {'duration': 0.08, 'phone': 'z_E'}], 'start': 24.009999999999998, 'startOffset': 441,
               'word': 'was'}, {'alignedWord': 'given', 'case': 'success', 'end': 24.46, 'endOffset': 450,
                                'phones': [{'duration': 0.04, 'phone': 'g_B'}, {'duration': 0.07, 'phone': 'ih_I'},
                                           {'duration': 0.05, 'phone': 'v_I'}, {'duration': 0.03, 'phone': 'ih_I'},
                                           {'duration': 0.06, 'phone': 'n_E'}], 'start': 24.21, 'startOffset': 445,
                                'word': 'given'},
              {'alignedWord': 'the', 'case': 'success', 'end': 24.560000000000002, 'endOffset': 454,
               'phones': [{'duration': 0.04, 'phone': 'dh_B'}, {'duration': 0.06, 'phone': 'ah_E'}], 'start': 24.46,
               'startOffset': 451, 'word': 'the'},
              {'alignedWord': 'name', 'case': 'success', 'end': 24.84, 'endOffset': 459,
               'phones': [{'duration': 0.07, 'phone': 'n_B'}, {'duration': 0.11, 'phone': 'ey_I'},
                          {'duration': 0.1, 'phone': 'm_E'}], 'start': 24.56, 'startOffset': 455, 'word': 'name'},
              {'alignedWord': 'mario', 'case': 'success', 'end': 25.35, 'endOffset': 465,
               'phones': [{'duration': 0.01, 'phone': 'm_B'}, {'duration': 0.13, 'phone': 'aa_I'},
                          {'duration': 0.09, 'phone': 'r_I'}, {'duration': 0.12, 'phone': 'iy_I'},
                          {'duration': 0.16, 'phone': 'ow_E'}], 'start': 24.84, 'startOffset': 460, 'word': 'Mario'},
              {'alignedWord': 'mario', 'case': 'success', 'end': 26.020000000000003, 'endOffset': 473,
               'phones': [{'duration': 0.15, 'phone': 'm_B'}, {'duration': 0.1, 'phone': 'aa_I'},
                          {'duration': 0.09, 'phone': 'r_I'}, {'duration': 0.1, 'phone': 'iy_I'},
                          {'duration': 0.09, 'phone': 'ow_E'}], 'start': 25.490000000000002, 'startOffset': 468,
               'word': 'Mario'}, {'alignedWord': 'has', 'case': 'success', 'end': 26.26, 'endOffset': 477,
                                  'phones': [{'duration': 0.07, 'phone': 'hh_B'}, {'duration': 0.07, 'phone': 'ae_I'},
                                             {'duration': 0.07, 'phone': 'z_E'}], 'start': 26.05, 'startOffset': 474,
                                  'word': 'has'},
              {'alignedWord': 'come', 'case': 'success', 'end': 26.459999999999997, 'endOffset': 482,
               'phones': [{'duration': 0.07, 'phone': 'k_B'}, {'duration': 0.07, 'phone': 'ah_I'},
                          {'duration': 0.06, 'phone': 'm_E'}], 'start': 26.259999999999998, 'startOffset': 478,
               'word': 'come'}, {'alignedWord': 'a', 'case': 'success', 'end': 26.53, 'endOffset': 484,
                                 'phones': [{'duration': 0.07, 'phone': 'ah_S'}], 'start': 26.46, 'startOffset': 483,
                                 'word': 'a'},
              {'alignedWord': 'long', 'case': 'success', 'end': 26.86, 'endOffset': 489,
               'phones': [{'duration': 0.12, 'phone': 'l_B'}, {'duration': 0.11, 'phone': 'ao_I'},
                          {'duration': 0.1, 'phone': 'ng_E'}], 'start': 26.53, 'startOffset': 485, 'word': 'long'},
              {'alignedWord': 'way', 'case': 'success', 'end': 27.099999999999998, 'endOffset': 493,
               'phones': [{'duration': 0.12, 'phone': 'w_B'}, {'duration': 0.11, 'phone': 'ey_E'}],
               'start': 26.869999999999997, 'startOffset': 490, 'word': 'way'},
              {'alignedWord': 'since', 'case': 'success', 'end': 27.349999, 'endOffset': 499,
               'phones': [{'duration': 0.06, 'phone': 's_B'}, {'duration': 0.06, 'phone': 'ih_I'},
                          {'duration': 0.06, 'phone': 'n_I'}, {'duration': 0.07, 'phone': 's_E'}], 'start': 27.099999,
               'startOffset': 494, 'word': 'since'},
              {'alignedWord': 'then', 'case': 'success', 'end': 27.679999, 'endOffset': 504,
               'phones': [{'duration': 0.06, 'phone': 'dh_B'}, {'duration': 0.11, 'phone': 'eh_I'},
                          {'duration': 0.16, 'phone': 'n_E'}], 'start': 27.349999, 'startOffset': 500, 'word': 'then'},
              {'alignedWord': "he's", 'case': 'success', 'end': 28.03, 'endOffset': 510,
               'phones': [{'duration': 0.1, 'phone': 'hh_B'}, {'duration': 0.12, 'phone': 'iy_I'},
                          {'duration': 0.07, 'phone': 'z_E'}], 'start': 27.740000000000002, 'startOffset': 506,
               'word': "He's"}, {'alignedWord': 'been', 'case': 'success', 'end': 28.21, 'endOffset': 515,
                                 'phones': [{'duration': 0.05, 'phone': 'b_B'}, {'duration': 0.1, 'phone': 'ih_I'},
                                            {'duration': 0.03, 'phone': 'n_E'}], 'start': 28.03, 'startOffset': 511,
                                 'word': 'been'},
              {'alignedWord': 'in', 'case': 'success', 'end': 28.35, 'endOffset': 518,
               'phones': [{'duration': 0.06, 'phone': 'ih_B'}, {'duration': 0.08, 'phone': 'n_E'}], 'start': 28.21,
               'startOffset': 516, 'word': 'in'},
              {'alignedWord': 'over', 'case': 'success', 'end': 28.569999999999997, 'endOffset': 523,
               'phones': [{'duration': 0.13, 'phone': 'ow_B'}, {'duration': 0.06, 'phone': 'v_I'},
                          {'duration': 0.01, 'phone': 'er_E'}], 'start': 28.369999999999997, 'startOffset': 519,
               'word': 'over'}, {'alignedWord': '<unk>', 'case': 'success', 'end': 29.2, 'endOffset': 527,
                                 'phones': [{'duration': 0.63, 'phone': 'oov_S'}], 'start': 28.57, 'startOffset': 524,
                                 'word': '200'},
              {'alignedWord': 'games', 'case': 'success', 'end': 29.75, 'endOffset': 533,
               'phones': [{'duration': 0.09, 'phone': 'g_B'}, {'duration': 0.19, 'phone': 'ey_I'},
                          {'duration': 0.09, 'phone': 'm_I'}, {'duration': 0.17, 'phone': 'z_E'}], 'start': 29.21,
               'startOffset': 528, 'word': 'games'},
              {'alignedWord': 'and', 'case': 'success', 'end': 30.029999, 'endOffset': 538,
               'phones': [{'duration': 0.08, 'phone': 'ae_B'}, {'duration': 0.05, 'phone': 'n_I'},
                          {'duration': 0.05, 'phone': 'd_E'}], 'start': 29.849999, 'startOffset': 535, 'word': 'and'},
              {'alignedWord': "he's", 'case': 'success', 'end': 30.220000000000002, 'endOffset': 543,
               'phones': [{'duration': 0.05, 'phone': 'hh_B'}, {'duration': 0.07, 'phone': 'iy_I'},
                          {'duration': 0.07, 'phone': 'z_E'}], 'start': 30.03, 'startOffset': 539, 'word': "he's"},
              {'alignedWord': 'even', 'case': 'success', 'end': 30.48, 'endOffset': 548,
               'phones': [{'duration': 0.11, 'phone': 'iy_B'}, {'duration': 0.05, 'phone': 'v_I'},
                          {'duration': 0.03, 'phone': 'ih_I'}, {'duration': 0.06, 'phone': 'n_E'}], 'start': 30.23,
               'startOffset': 544, 'word': 'even'},
              {'alignedWord': 'been', 'case': 'success', 'end': 30.68, 'endOffset': 553,
               'phones': [{'duration': 0.03, 'phone': 'b_B'}, {'duration': 0.1, 'phone': 'ih_I'},
                          {'duration': 0.07, 'phone': 'n_E'}], 'start': 30.48, 'startOffset': 549, 'word': 'been'},
              {'alignedWord': 'featured', 'case': 'success', 'end': 31.089999000000002, 'endOffset': 562,
               'phones': [{'duration': 0.1, 'phone': 'f_B'}, {'duration': 0.1, 'phone': 'iy_I'},
                          {'duration': 0.1, 'phone': 'ch_I'}, {'duration': 0.04, 'phone': 'er_I'},
                          {'duration': 0.07, 'phone': 'd_E'}], 'start': 30.679999000000002, 'startOffset': 554,
               'word': 'featured'}, {'alignedWord': 'in', 'case': 'success', 'end': 31.21, 'endOffset': 565,
                                     'phones': [{'duration': 0.06, 'phone': 'ih_B'},
                                                {'duration': 0.06, 'phone': 'n_E'}], 'start': 31.09, 'startOffset': 563,
                                     'word': 'in'},
              {'alignedWord': 'movies', 'case': 'success', 'end': 31.69, 'endOffset': 572,
               'phones': [{'duration': 0.06, 'phone': 'm_B'}, {'duration': 0.11, 'phone': 'uw_I'},
                          {'duration': 0.07, 'phone': 'v_I'}, {'duration': 0.13, 'phone': 'iy_I'},
                          {'duration': 0.11, 'phone': 'z_E'}], 'start': 31.21, 'startOffset': 566, 'word': 'movies'},
              {'alignedWord': 'tv', 'case': 'success', 'end': 32.119999, 'endOffset': 576,
               'phones': [{'duration': 0.13, 'phone': 't_B'}, {'duration': 0.1, 'phone': 'iy_I'},
                          {'duration': 0.09, 'phone': 'v_I'}, {'duration': 0.08, 'phone': 'iy_E'}], 'start': 31.719999,
               'startOffset': 574, 'word': 'TV'},
              {'alignedWord': 'shows', 'case': 'success', 'end': 32.55, 'endOffset': 582,
               'phones': [{'duration': 0.15, 'phone': 'sh_B'}, {'duration': 0.14, 'phone': 'ow_I'},
                          {'duration': 0.14, 'phone': 'z_E'}], 'start': 32.12, 'startOffset': 577, 'word': 'shows'},
              {'alignedWord': 'and', 'case': 'success', 'end': 32.83, 'endOffset': 587,
               'phones': [{'duration': 0.06, 'phone': 'ae_B'}, {'duration': 0.04, 'phone': 'n_I'},
                          {'duration': 0.07, 'phone': 'd_E'}], 'start': 32.66, 'startOffset': 584, 'word': 'and'},
              {'alignedWord': 'cartoons', 'case': 'success', 'end': 33.51, 'endOffset': 596,
               'phones': [{'duration': 0.07, 'phone': 'k_B'}, {'duration': 0.04, 'phone': 'aa_I'},
                          {'duration': 0.05, 'phone': 'r_I'}, {'duration': 0.09, 'phone': 't_I'},
                          {'duration': 0.15, 'phone': 'uw_I'}, {'duration': 0.07, 'phone': 'n_I'},
                          {'duration': 0.21, 'phone': 'z_E'}], 'start': 32.83, 'startOffset': 588, 'word': 'cartoons'},
              {'alignedWord': 'so', 'case': 'success', 'end': 33.99, 'endOffset': 601,
               'phones': [{'duration': 0.18, 'phone': 's_B'}, {'duration': 0.16, 'phone': 'ow_E'}], 'start': 33.65,
               'startOffset': 599, 'word': 'So'},
              {'alignedWord': 'there', 'case': 'success', 'end': 34.209999, 'endOffset': 607,
               'phones': [{'duration': 0.07, 'phone': 'dh_B'}, {'duration': 0.05, 'phone': 'eh_I'},
                          {'duration': 0.06, 'phone': 'r_E'}], 'start': 34.029999000000004, 'startOffset': 602,
               'word': 'there'}, {'alignedWord': 'you', 'case': 'success', 'end': 34.339999, 'endOffset': 611,
                                  'phones': [{'duration': 0.05, 'phone': 'y_B'}, {'duration': 0.08, 'phone': 'uw_E'}],
                                  'start': 34.209998999999996, 'startOffset': 608, 'word': 'you'},
              {'alignedWord': 'have', 'case': 'success', 'end': 34.57, 'endOffset': 616,
               'phones': [{'duration': 0.1, 'phone': 'hh_B'}, {'duration': 0.08, 'phone': 'ae_I'},
                          {'duration': 0.05, 'phone': 'v_E'}], 'start': 34.34, 'startOffset': 612, 'word': 'have'},
              {'alignedWord': 'it', 'case': 'success', 'end': 34.68, 'endOffset': 619,
               'phones': [{'duration': 0.05, 'phone': 'ih_B'}, {'duration': 0.06, 'phone': 't_E'}], 'start': 34.57,
               'startOffset': 617, 'word': 'it'},
              {'alignedWord': 'the', 'case': 'success', 'end': 34.830000999999996, 'endOffset': 624,
               'phones': [{'duration': 0.06, 'phone': 'dh_B'}, {'duration': 0.08, 'phone': 'ah_E'}],
               'start': 34.690000999999995, 'startOffset': 621, 'word': 'the'},
              {'alignedWord': 'strange', 'case': 'success', 'end': 35.28, 'endOffset': 632,
               'phones': [{'duration': 0.05, 'phone': 's_B'}, {'duration': 0.09, 'phone': 't_I'},
                          {'duration': 0.08, 'phone': 'r_I'}, {'duration': 0.09, 'phone': 'ey_I'},
                          {'duration': 0.05, 'phone': 'n_I'}, {'duration': 0.09, 'phone': 'jh_E'}], 'start': 34.83,
               'startOffset': 625, 'word': 'strange'},
              {'alignedWord': 'history', 'case': 'success', 'end': 35.669999000000004, 'endOffset': 640,
               'phones': [{'duration': 0.06, 'phone': 'hh_B'}, {'duration': 0.06, 'phone': 'ih_I'},
                          {'duration': 0.05, 'phone': 's_I'}, {'duration': 0.06, 'phone': 't_I'},
                          {'duration': 0.11, 'phone': 'er_I'}, {'duration': 0.05, 'phone': 'iy_E'}],
               'start': 35.279999000000004, 'startOffset': 633, 'word': 'history'},
              {'alignedWord': 'of', 'case': 'success', 'end': 35.79, 'endOffset': 643,
               'phones': [{'duration': 0.05, 'phone': 'ah_B'}, {'duration': 0.07, 'phone': 'v_E'}], 'start': 35.67,
               'startOffset': 641, 'word': 'of'},
              {'alignedWord': 'super', 'case': 'success', 'end': 36.099999000000004, 'endOffset': 649,
               'phones': [{'duration': 0.09, 'phone': 's_B'}, {'duration': 0.08, 'phone': 'uw_I'},
                          {'duration': 0.07, 'phone': 'p_I'}, {'duration': 0.07, 'phone': 'er_E'}], 'start': 35.789999,
               'startOffset': 644, 'word': 'Super'},
              {'alignedWord': 'mario', 'case': 'success', 'end': 36.729999, 'endOffset': 655,
               'phones': [{'duration': 0.08, 'phone': 'm_B'}, {'duration': 0.1, 'phone': 'aa_I'},
                          {'duration': 0.09, 'phone': 'r_I'}, {'duration': 0.11, 'phone': 'iy_I'},
                          {'duration': 0.24, 'phone': 'ow_E'}], 'start': 36.109999, 'startOffset': 650,
               'word': 'Mario'},
              {'alignedWord': 'thanks', 'case': 'success', 'end': 37.099999000000004, 'endOffset': 663,
               'phones': [{'duration': 0.1, 'phone': 'th_B'}, {'duration': 0.06, 'phone': 'ae_I'},
                          {'duration': 0.06, 'phone': 'ng_I'}, {'duration': 0.05, 'phone': 'k_I'},
                          {'duration': 0.05, 'phone': 's_E'}], 'start': 36.779999000000004, 'startOffset': 657,
               'word': 'Thanks'}, {'alignedWord': 'for', 'case': 'success', 'end': 37.179999, 'endOffset': 667,
                                   'phones': [{'duration': 0.01, 'phone': 'f_B'}, {'duration': 0.06, 'phone': 'er_E'}],
                                   'start': 37.109999, 'startOffset': 664, 'word': 'for'},
              {'alignedWord': 'watching', 'case': 'success', 'end': 37.62, 'endOffset': 676,
               'phones': [{'duration': 0.07, 'phone': 'w_B'}, {'duration': 0.08, 'phone': 'aa_I'},
                          {'duration': 0.08, 'phone': 'ch_I'}, {'duration': 0.1, 'phone': 'ih_I'},
                          {'duration': 0.11, 'phone': 'ng_E'}], 'start': 37.18, 'startOffset': 668,
               'word': 'watching'}]}

print(aligned['words'])

###########################
## create caption images ##
###########################
import spacy
from PIL import Image, ImageDraw, ImageFont
import textwrap

caption_counter = 0
# load core english library
nlp = spacy.load("en_core_web_sm")
doc2 = nlp(text.replace('/n', ''))
text_size = 100
caption_width = 16
char_height = text_size + 20

captions = []
size = 3
for e, sent in enumerate(doc2.sents):
    sent = str(sent).replace('\n', '')
    s = sent.split(' ')
    print('---')
    print(sent)
    print(s)
    if len(s) < size + 1:
        captions += [sent]
    else:
        c = 0
        while True:
            c += size
            captions += [" ".join(s[c - size:min(c, len(sent))])]
            if c > len(sent):
                break
captions = [" ".join(str(a).split()).strip() for a in captions if a != '']

frame_counter = 0
word_counter = 0

print("CAPTIONS: ", captions)

p_bar = tqdm(range(int(aligned['words'][-1]['end'] * 100)))
p_bar.n = 0
p_bar.refresh()

slide_picture = Image.new('RGB', (500, 500), color=(0, 0, 200))

images = []
for e, caption_text in enumerate(captions):
    caption_text = str(caption_text).split(' ')
    for i in range(len(caption_text)):
        if len(single_nouns) > 0 and single_nouns[0].lower() in caption_text[i].lower():
            n = nouns.pop(0)
            single_nouns.pop(0)

            files = os.listdir(f'downloads/{n}/')
            file = random.choice(files)
            slide_picture = Image.open(f'downloads/{n}/{file}')
            box = slide_picture.getbbox()
            slide_picture = slide_picture.resize((int(box[2] * 1920 / box[3]), 1920))
            images.append((slide_picture, frame_counter))

        end = aligned['words'][word_counter]['end']
        frame_counter = int(end * 100)
        word_counter += 1


print(images)
slide_picture = images[0][0]
word_counter = 0
frame_counter = 0
for e, caption_text in enumerate(captions):
    caption_text = str(caption_text).split(' ')
    combo = ''

    dummy_text_box = textwrap.wrap(" ".join(caption_text), width=caption_width)

    for i in range(len(caption_text)):
        # combo += caption_text[i] + ' '
        combo = " ".join(caption_text)

        font = ImageFont.truetype('KOMIKAX_.ttf', size=text_size)

        img = Image.new('RGB', (1080, 1920), color=(0, 255, 0))

        if frame_counter >= images[0][1]:
            print(images, len(images))
            slide_picture = images[0][0]
            print(slide_picture)
            images.pop(0)

        img.paste(slide_picture)

        # Create a drawing context
        draw = ImageDraw.Draw(img)

        # Specify the font to use

        # Set the text to be drawn

        # Set the desired width of the text box
        textbox_width = 300

        # Set the position of the text box
        x = 60

        y = 1920 - len(dummy_text_box) * char_height - 200

        lines = textwrap.wrap(combo, width=caption_width)
        textbox_height = len(lines) * font.getbbox(" ")[1] + 20

        # Draw the text box

        # Draw the text inside the text box
        current_y = y + 10
        for line in lines:
            x = 1080 / 2 - font.getbbox(" ")[1] * (len(line) - 1) / 4
            draw.text((x, current_y), line, font=font, fill='white', stroke_fill=(0, 0, 0), stroke_width=8)
            current_y += font.getbbox(" ")[1]

        end = aligned['words'][word_counter]['end']

        num_frames = int(end * 100) - frame_counter
        for i in range(num_frames):
            # Save the image
            num_str = "{:09d}".format(frame_counter)
            img.save(f'captions/caption_{num_str}.png')
            frame_counter += 1
            p_bar.n = frame_counter
            p_bar.refresh()
        word_counter += 1
