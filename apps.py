from flask import Flask,render_template,url_for, request,session,send_file,redirect
from PIL import Image
import openai
import re, os
import urllib.request
from gtts import gTTS
from moviepy.editor import *

from moviepy.video.VideoClip import ImageClip, TextClip

app = Flask(__name__)
app.secret_key = 'OVT2V'

openai.api_key = ""


@app.route('/')
def text():
    return render_template('index.html')


@app.route('/save', methods=['POST'])
def save():
    text = request.form['text']

    # Save the text to a notepad.txt file
    with open('notepad.txt', 'a') as file:
        file.write(text + '\n')

    # Process the text
    paragraphs = re.split(r"[,.]", text)

    # Create folders for audio, images, and videos
    os.makedirs("audio", exist_ok=True)
    os.makedirs("images", exist_ok=True)
    os.makedirs("videos", exist_ok=True)

    # Loop through each paragraph and process it
    i = 1
    for para in paragraphs:
        response = openai.Image.create(
            prompt=para.strip(),
            n=1,
            size="1024x1024"
        )
        print("Generate New AI Image from Paragraph...")
        image_url = response['data'][0]['url']
        urllib.request.urlretrieve(image_url, f"images/image{i}.jpg")
        print("The Generated Image Saved in Images Folder!")

        # Audio processing and save in folder
        tts = gTTS(text=para, lang="en", slow=False)
        tts.save(f"audio/voiceover{i}.mp3")
        print("The Paragraph Converted into Voiceover & Saved in Audio Folder!")

        # Load the audio file using moviepy
        print("Extract VoiceOver and Get Duration...")
        audio_clip = AudioFileClip(f"audio/voiceover{i}.mp3")
        audio_duration = audio_clip.duration

        # Load the images file using moviepy
        print("Extract Image Clip and Set Duration...")
        image_clip = ImageClip(f"images/image{i}.jpg").set_duration(audio_duration)

        # Create a text clip from the paragraph
        print("Customize The Text Clip...")
        text_clip = TextClip(para, fontsize=40, color="white")
        text_clip = text_clip.set_pos('center').set_duration(audio_duration)

        # Combine all the audio, image, and text to create the final video clip using moviepy
        print("Concatenate Audio, Image, Text to Create Final Clip...")
        clip = image_clip.set_audio(audio_clip)
        videos = CompositeVideoClip([clip, text_clip])

        # Save the final video in a file
        video = videos.write_videofile(f"videos/video{i}.mp4", fps=24)
        print(f"The Video{i} Has Been Created Successfully!")
        i += 1

    clips = []
    l_files = os.listdir("videos")
    for file in l_files:
        clip = VideoFileClip(f"videos/{file}")
        clips.append(clip)

    print("Concatenate All the Clips to Create a Final Video...")
    final_video = concatenate_videoclips(clips, method="compose")
    final_video = final_video.write_videofile("final_video.mp4")
    print("The Final Video Has Been Created Successfully!")

    return redirect(url_for('index'))


@app.route('/download')
def download():
    return send_file('final_video.mp4', as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
