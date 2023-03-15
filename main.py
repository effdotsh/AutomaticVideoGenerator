import random

random.seed(38724)

import openai
import os
from dotenv import dotenv_values
import requests
import os

from tqdm import tqdm
import time

start = time.time()

import shutil


character_name = input("Character Name: ")
character_name = "Super Mario" if character_name == '' else character_name


GENERATE_FOLDER = f'generate_{character_name.replace(" ", "")}'
if os.path.exists(GENERATE_FOLDER):
    shutil.rmtree(GENERATE_FOLDER)
os.makedirs(f'{GENERATE_FOLDER}/downloads')

def align(audio, text) -> dict:
    # get output from gentle
    url = 'http://localhost:8765/transcriptions?async=false'
    files = {'audio': open(audio, 'rb'),
             'transcript': str.encode(text)}
    try:
        r = requests.post(url, files=files)
    except requests.exceptions.RequestException as e:
        raise Exception('[ALIGN ERROR] Failed to post to Gentle: Make sure Docker Desktop is running...')

    return r.json()


env = dict(dotenv_values(".env"))



openai.api_key = env["OPENAI_API_KEY"]

prompt = f"Write an energetic script for a short-form video about the strange history of how {character_name}. Speaking the script should take about 30 seconds. Do not include quotation marks."
message_history = [{"role": "user", "content": prompt}]

#davinci
# script_response = openai.Completion.create(model="text-davinci-003", prompt=prompt, temperature=0.1, max_tokens=300)
# text = script_response['choices'][0]['text']


script_response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=message_history, temperature=0.1, max_tokens=300)
text = script_response['choices'][0]['message']['content']
text = text.replace('\\', '').replace("Narrator:", '').replace('"','')

print(script_response)
#Cache:
# script_response = {
#   "choices": [
#     {
#       "finish_reason": "stop",
#       "index": 0,
#       "logprobs": None,
#       "text": "\n\nHey everyone! \n\nToday I'm here to tell you about the strange history of Super Mario! \n\nIt all started in 1981 when Nintendo released the arcade game Donkey Kong. The main character was a carpenter named Jumpman, who was later renamed Mario. \n\nMario then starred in his own game, Mario Bros., in 1983. This game introduced his brother Luigi and the iconic green pipes. \n\nIn 1985, Super Mario Bros. was released and it changed the gaming world forever. This game introduced the world to the Mushroom Kingdom and the power-ups that we all know and love. \n\nSince then, Mario has starred in over 200 games and has become one of the most recognizable characters in the world. \n\nSo, that's the strange history of Super Mario! \n\n#supermario #gaming #history #nintendo #videogames"
#     }
#   ],
#   "created": 1678763700,
#   "id": "cmpl-6tpPoKXaKKfaj4ZRJOggTPaIvsgyH",
#   "model": "text-davinci-003",
#   "object": "text_completion",
#   "usage": {
#     "completion_tokens": 186,
#     "prompt_tokens": 18,
#     "total_tokens": 204
#   }
# }
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
with open(f'{GENERATE_FOLDER}/voiceover.mp3', 'wb') as audio_file:
    response = text_to_speech.synthesize(
        text=f'<prosody pitch="-25%" rate="+5%">{text}</prosody>',
        accept='audio/mp3',
        voice='en-AU_JackExpressive',
    ).get_result()
    audio_file.write(response.content)



import spacy

# load the English language model
nlp = spacy.load("en_core_web_lg")
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
from ImageDownloader import download

for n in [character_name] + nouns:
    print("Searching for:", n)
    download(f'{n}', limit=10, downloads_folder=f'{GENERATE_FOLDER}/downloads/')

single_nouns = [a.split(' ')[0] for a in nouns]

aligned = align(f'{GENERATE_FOLDER}/voiceover.mp3', text)

print(aligned['words'])

###########################
## create caption images ##
###########################
import spacy
from PIL import Image, ImageDraw, ImageFont
import textwrap

caption_counter = 0
# load core english library
nlp = spacy.load("en_core_web_lg")
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

slide_picture = Image.new('RGB', (500, 500), color=(0, 0, 200))

images = []
def load(n):
    files = os.listdir(f'{GENERATE_FOLDER}/downloads/{n}/')
    if len(files) == 0:
        print(f'No files in {n}')
        return
    file = random.choice(files)
    slide_picture = Image.open(f'{GENERATE_FOLDER}/downloads/{n}/{file}')
    box = slide_picture.getbbox()
    slide_picture = slide_picture.resize((int(box[2] * 1920 / box[3]), 1920))
    images.append((slide_picture, frame_counter))

load(character_name)

for e, caption_text in enumerate(captions):
    caption_text = str(caption_text).split(' ')
    for i in range(len(caption_text)):
        if len(single_nouns) > 0 and single_nouns[0].lower() in caption_text[i].lower():
            n = nouns.pop(0)
            single_nouns.pop(0)
            load(n)

        gent_word = aligned['words'][word_counter]
        word_counter += 1

        if gent_word['case'] != 'success':
            continue
        end = gent_word['end']
        frame_counter = int(end * 100)

total_frames = int(aligned['words'][-1]['end'] * 100)
p_bar = tqdm(range(total_frames))
p_bar.n = 0
p_bar.refresh()

slide_picture = images[0][0]
word_counter = 0
frame_counter = 0

pan_start = 0
images.pop()
pan_end = images[0][1]
for e, caption_text in enumerate(captions):
    caption_text = str(caption_text).split(' ')
    combo = ''

    dummy_text_box = textwrap.wrap(" ".join(caption_text), width=caption_width)

    for i in range(len(caption_text)):
        # combo += caption_text[i] + ' '
        combo = " ".join(caption_text)

        font = ImageFont.truetype('KOMIKAX_.ttf', size=text_size)


        if len(images) > 0 and frame_counter >= images[0][1]:
            slide_picture = images[0][0]
            pan_start = frame_counter
            images.pop(0)
            pan_end = images[0][1] if len(images) > 0 else total_frames

        gent_word = aligned['words'][word_counter]
        if gent_word['case']=='success':
            end = gent_word['end']
        else:
            while gent_word['case'] != 'success':
                word_counter += 1
                if word_counter == len(aligned['words']):
                    gent_word = {'end': total_frames}
                    break
                gent_word = aligned['words'][word_counter]
            end = gent_word['start']
        num_frames = int(end * 100) - frame_counter
        for i in range(num_frames):
            img = Image.new('RGB', (1080, 1920), color=(255, 255, 255))

            total_pan = slide_picture.getbbox()[2] - 1080
            pan = int((frame_counter - pan_start) / (pan_end - pan_start) * total_pan)

            img.paste(slide_picture, (-pan, 0))

            # Create a drawing context
            draw = ImageDraw.Draw(img)

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

            # Save the image
            num_str = "{:09d}".format(frame_counter)
            img.save(f'{GENERATE_FOLDER}/caption_{num_str}.png')
            frame_counter += 1
            p_bar.n = frame_counter
            p_bar.refresh()
        word_counter += 1

ffmpeg_command = f'ffmpeg -framerate 100 -i {GENERATE_FOLDER}/caption_%09d.png -c:v h264 -r 100 -i {GENERATE_FOLDER}/voiceover.mp3 {character_name.replace(" ", "_")}.mp4'
print(ffmpeg_command)
os.system(ffmpeg_command)

print(f'Done in {int(time.time()-start)} seconds')