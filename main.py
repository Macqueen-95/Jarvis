import speech_recognition as sr
import webbrowser
import pyttsx3
from openai import OpenAI
import os
import pygame
from gtts import gTTS
import subprocess
import urllib.parse
from youtubesearchpython import VideosSearch

# Opens the systems app
def open_mac_app(app_name):
    try:
        subprocess.call(["open", "-a", app_name])
        speak(f"Opening {app_name}")
    except Exception as e:
        speak(f"Sorry, I couldn't open {app_name}")
        print("Error:", e)

# Setup pyttsx3 (for English, male voice)
engine = pyttsx3.init()
voices = engine.getProperty('voices')

# Set male voice if available
for voice in voices:
    if "male" in voice.name.lower():
        engine.setProperty('voice', voice.id)

# Initialize pygame mixer once
pygame.mixer.init()

# Language detection (very basic)
def detect_language(text):
    hindi_keywords = [
        "mujhe", "gana", "sunao", "kar", "karo", "kaise", "kyun", "hai", "tha", "hun", 
        "chalu", "band", "theek", "acha", "nahi", "haan", "jarvis", "sun", "batao"
    ]
    if any(word in text.lower() for word in hindi_keywords):
        return 'hi'
    return 'en'

# Smart speak function
def speak(text):
    """Speak English with pyttsx3 male voice or Hindi with gTTS."""
    lang = detect_language(text)
    print(f"[JARVIS speaking in {lang.upper()}]: {text}")
    
    if lang == 'en':
        # Use pyttsx3 for English (male voice)
        engine.say(text)
        engine.runAndWait()
    else:
        # Use gTTS for Hindi or other languages
        tts = gTTS(text=text, lang=lang)
        tts.save("voice.mp3")
        pygame.mixer.music.load("voice.mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue
        pygame.mixer.music.unload()
        os.remove("voice.mp3")       

# Integrating OpenAI to talk freely
def aiProcess(command):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) #--> USE YOUR OWN API KEY OF OpenAI

    completion = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You are a virtual assistant named jarvis skilled in general tasks like Alexa and Google assistant. Give short responses please"},
            {"role": "user", "content":command}
        ]
    )
    return completion.choices[0].message.content 

def processCommand(c):
    chat = c.lower()

    # ---------- open websites ----------
    if "open google" in chat:
        webbrowser.open("https://google.com")
        return
    elif "open insta" in chat:
        webbrowser.open("https://instagram.com")
        return
    elif "open youtube" in chat:
        webbrowser.open("https://youtube.com")
        return
    elif "open spotify" in chat:
        webbrowser.open("https://spotify.com")
        return

    # ---------- play local music from "Spotify" or "YouTube" ----------
    elif chat.startswith("play"):
        song_name = chat.split("play", 1)[1].strip()

        query = urllib.parse.quote(song_name)

        if "spotify" in chat:
            webbrowser.open(f"https://open.spotify.com/search/{query}")
            speak(f"Searching {song_name} on Spotify.")
        else:
            # YouTube autoplay using first result
            results = VideosSearch(song_name, limit=2).result()
            if results and results['result']:
                first_video_url = results['result'][0]['link']
                webbrowser.open(first_video_url)
                speak(f"Playing {song_name} on YouTube.")
            else:
                speak("Sorry, I couldn't find the song on YouTube.")
        exit()

    # ---------- polite chatter ----------
    elif "thank you" in chat:
        speak("You're welcome, sir.")
        return
    elif "who made you" in chat:
        speak("You did, boss.")
        return

    # ---------- open Mac apps ----------
    elif "open" in chat and any(app in chat for app in
                              ["safari", "whatsapp", "calculator", "notes",
                               "vscode", "visual studio", "system preferences"]):
        if "safari" in chat:
            open_mac_app("Safari")
        elif "whatsapp" in chat:
            open_mac_app("Whatsapp")
        elif "calculator" in chat:
            open_mac_app("Calculator")
        elif "notes" in chat:
            open_mac_app("Notes")
        elif "vscode" in chat or "visual studio" in chat:
            open_mac_app("Visual Studio Code")
        elif "system preferences" in chat or "settings" in chat:
            open_mac_app("System Preferences")
        return

    # ---------- catch-all: let GPT handle it ----------
    else:
        try:
            output = aiProcess(c)
        except Exception:
            output = "Sorry, OpenAI is busy right now."
        speak(output)


if __name__ == "__main__":
    speak("Initializing Jarvis....")

    recognizer = sr.Recognizer()

    def listen_command(timeout=5):
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.3)
            print("Listening...")
            audio = recognizer.listen(source, timeout=timeout)
        return recognizer.recognize_google(audio)

    while True:
        try:
            print("Say 'Hey Jarvis' to activate...")
            word = listen_command(timeout=2)
            if "jarvis" in word.lower():
                speak("Yes, I am listening")
                
                # Chat mode ON
                while True:
                    try:
                        command = listen_command(timeout=5)
                        print("You said:", command)
                        
                        if any(kw in command.lower() for kw in ["sleep now", "go to sleep", "shutdown"]):
                            speak("Going to sleep, sir.")
                            break
                        
                        processCommand(command)

                    except sr.WaitTimeoutError:
                        speak("No response detected. Going to sleep.")
                        break
                    except sr.UnknownValueError:
                        speak("Sorry, I didn’t understand.")
                    except Exception as e:
                        print("ERROR:", e)
                        break
            if "exit" in word.lower():
                break    

        except sr.WaitTimeoutError:
            continue
        except sr.UnknownValueError:
            continue
        except Exception as e:
            print("ERROR:", e)
