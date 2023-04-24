import random
random.seed(38724)

import PIL

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
character_name = "Pac-Man" if character_name == '' else character_name


GENERATE_FOLDER = f'generate/{character_name.replace(" ", "")}'
if os.path.exists(GENERATE_FOLDER):
    shutil.rmtree(GENERATE_FOLDER)

time.sleep(1)

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

prompt = f'You are a short-form video creator who makes videos about the strange history behind the development, writing, and creation of video game characters. Write an energetic script about {character_name}. Speaking the script should take about 45 seconds. Do not include quotation marks. The script should not include a greeting or salutation at the beginning. Do not say "hey there" at the beginning. Begin the script by saying the character\'s name'

message_history = [{"role": "user", "content": prompt}]

script_response = openai.ChatCompletion.create(model="gpt-4", messages=message_history, temperature=0.15, max_tokens=300)

text = script_response['choices'][0]['message']['content']
text = text.replace('\\', '').replace("Narrator:", ' ').replace('"','').replace('\n', ' ')
import re
text = re.sub(r"\s+", " ", text)

print(script_response)
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

text = text.replace('-', ' ').replace('–', ' ')
text = re.sub(r"\s+", " ", text)

# Generate speech from text
with open(f'{GENERATE_FOLDER}/voiceover.mp3', 'wb') as audio_file:
    response = text_to_speech.synthesize(
        text=f'<prosody pitch="-25%" rate="+5%">{text}</prosody>',
        accept='audio/mp3',
        voice='en-AU_JackExpressive',
    ).get_result()
    audio_file.write(response.content)


def find_word_index(text, char_index):
    words = text.split()
    index = 0
    for i, word in enumerate(words):
        if char_index >= index and char_index < index + len(word):
            return i
        index += len(word) + 1  # add 1 for the space between words
    return len(words)  # char_index was out of range


import spacy

# load the English language model
nlp = spacy.load("en_core_web_lg")
# define a sentence with a multi-word proper noun
# process the sentence with spaCy
doc = nlp(text)
# identify named entities and combine multi-word entities
p_nouns = doc.ents

i_nouns = [token for token in doc if token.pos_ in ["NOUN"]]

proper_nouns = []
for i in p_nouns:
    pstart = find_word_index(text, i.start_char)
    ptext = i.text
    while pstart > 0:  # exception for Mr./Mrs./Dr. etc
        if doc[pstart].pos_ == 'PROPN':
            ptext = doc[pstart].text + ' ' + ptext
            pstart -= 1
        else:
            break
    proper_nouns.append((ptext, pstart))
improper_nouns = [(i.text, find_word_index(text, i.idx)) for i in i_nouns]
nouns = sorted(improper_nouns + proper_nouns, key=lambda x: x[1])
print("NOUNS: ", nouns)


# Download images from duckduckgo

from ImageDownloader import download

for n in [character_name] + [a[0] for a in nouns]:
    print("Searching for:", n)
    download(f'{n}', limit=3, downloads_folder=f'{GENERATE_FOLDER}/downloads/', replace={"character":character_name})




aligned = align(f'{GENERATE_FOLDER}/voiceover.mp3', text)

print(aligned['words'])


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
    sent = str(sent)
    s = sent.split(' ')
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

images = []
def load(n):
    attempts = 0
    try:
        files = os.listdir(f'{GENERATE_FOLDER}/downloads/{n}/')
    except:
        print(f'Could not find {n}, downloading again')
        download(f'{n}', limit=3, downloads_folder=f'{GENERATE_FOLDER}/downloads/',
                 replace={"character": character_name})
        try:
            files = os.listdir(f'{GENERATE_FOLDER}/downloads/{n}/')
        except:
            return

    if len(files) == 0:
        print(f'No files in {n}')
        return

    success = False
    slide_picture: PIL.Image = None
    while not success:
        try:
            file = random.choice(files)
            slide_picture = Image.open(f'{GENERATE_FOLDER}/downloads/{n}/{file}')
            success = True
        except:
            print("Error could not load", files)

    box = slide_picture.getbbox()
    slide_picture = slide_picture.resize((int(box[2] * 1920 / box[3]), 1920))
    images.append((slide_picture, frame_counter, n))

# load(character_name)

from pydub import AudioSegment
audio = AudioSegment.from_mp3(f'{GENERATE_FOLDER}/voiceover.mp3')
length_in_secs = len(audio) / 1000.0
print(f'Audio Length: {length_in_secs}')
total_frames = int(length_in_secs*100 + 0.5)

for e, caption_text in enumerate(captions):
    caption_text = str(caption_text).split(' ')
    for i in range(len(caption_text)):
        if len(nouns) > 0 and word_counter >= nouns[0][1]:
            n = nouns.pop(0)
            load(n[0])

        word_counter += 1

        if word_counter >= len(aligned['words']):
            break
        else:
            gent_word = aligned['words'][word_counter]


        if gent_word['case'] == 'success':
            end = gent_word['start']
        else:
            while gent_word['case'] != 'success':
                word_counter += 1
                if word_counter == len(aligned['words']):
                    gent_word = {'end': total_frames, 'start': total_frames, 'case':'success'}
                    break
                gent_word = aligned['words'][word_counter]
            end = gent_word['start']

        frame_counter = int(end * 100)


slide_picture = images[0][0]
word_counter = 0
frame_counter = 0

pan_start = 0
pan_end = images[0][1]

img = None
font = ImageFont.truetype('KOMIKAX_.ttf', size=text_size)

p_bar = tqdm(range(total_frames))
p_bar.n = 0
p_bar.refresh()
print([(i[1], i[2]) for i in images])
for e, caption_text in enumerate(captions):
    dummy_text_box = textwrap.wrap(" ".join(caption_text), width=caption_width)
    word_counter += caption_text.count(' ') + 1
    if word_counter >= len(aligned['words']):
        break

    gent_word = aligned['words'][word_counter]

    if gent_word['case'] == 'success':
        end = gent_word['start']
    else:
        offset = 0
        while gent_word['case'] != 'success':
            print(gent_word)
            if gent_word['case'] != 'not-found-in-audio':
                word_counter += 1
            else:
                offset += 1

            if word_counter + offset >= len(aligned['words']):
                gent_word = {'start': total_frames, "word":"empty"}
                break

            gent_word = aligned['words'][word_counter+offset]
        end = gent_word['start']
    print(caption_text, frame_counter, end, gent_word['word'])
    num_frames = int(100*end - frame_counter)
    for i in range(num_frames):
        if len(images) == 0:
            pass
        elif len(images) == 1 and frame_counter >= images[0][1]:
            slide_picture = images[0][0]
            pan_start = frame_counter
            pan_end = total_frames
            images.pop(0)
        elif frame_counter >= images[0][1]:
            slide_picture = images[0][0]

            images.pop(0)
            pan_start = frame_counter
            pan_end = images[0][1]
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

        lines = textwrap.wrap(caption_text, width=caption_width)
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

    if word_counter >= len(aligned['words']):
        break

for i in range(total_frames-frame_counter):
    num_str = "{:09d}".format(frame_counter)
    img.save(f'{GENERATE_FOLDER}/caption_{num_str}.png')
    frame_counter += 1
    p_bar.n = frame_counter
    p_bar.refresh()

ffmpeg_command = f'ffmpeg -framerate 100 -i {GENERATE_FOLDER}/caption_%09d.png -r 100 -i {GENERATE_FOLDER}/voiceover.mp3 {character_name.replace(" ", "_")}.mp4'
print(ffmpeg_command)
os.system(ffmpeg_command)

print(f'Done in {int(time.time()-start)} seconds')