import speech_recognition as sr
from datetime import datetime
import webbrowser
import time
from gtts import gTTS
from playsound import playsound
import random
import os
from pyfirmata import Arduino, SERVO
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate('firestore-project-json-file')
firebase_admin.initialize_app(cred)
db = firestore.client()

r = sr.Recognizer()

port = 'COM5'
board = Arduino(port)

doorServopin = 9
windowServoPin = 6

board.digital[doorServopin].mode = SERVO
board.digital[windowServoPin].mode = SERVO


def rotateServo(pin, angle):
    board.digital[pin].write(angle)
    time.sleep(0.015)

rotateServo(doorServopin,90)
rotateServo(windowServoPin,90)

def record(ask = False):
    with sr.Microphone() as source:

        if ask:
            speak(ask)

        audio = r.listen(source)
        voice = ''
        try:
            time.sleep(1)
            voice = r.recognize_google(audio, language='tr-TR')

        except sr.UnknownValueError:
            speak('anlayamadım')
        except sr.RequestError:
            speak('sistem çalışmıyor')

        return voice

def response(voice):

    homeControl = db.collection('homeControl').document("Home").get()
    personalInfo = db.collection('personalInfo').document("Mag").get()
    dailyQuestion = db.collection('dailyQuestion').document("dailyQuestions").get()

    if homeControl.exists or personalInfo.exists or dailyQuestion.exists:
        onLed = homeControl.to_dict()['onLed']
        offLed = homeControl.to_dict()['offLed']
        openDoor = homeControl.to_dict()['openDoor']
        closeDoor = homeControl.to_dict()['closeDoor']
        openWindow = homeControl.to_dict()['openWindow']
        closeWindow = homeControl.to_dict()['closeWindow']

        name = personalInfo.to_dict()['name']
        favoriteFruit = personalInfo.to_dict()['favoriteFruit']

        HowAreYou = dailyQuestion.to_dict()['HowAreYou']
        whatsForDinner = dailyQuestion.to_dict()['whatsForDinner']


    if 'adın nedir' in voice:
        print(name)
        speak(name)
    if 'favori meyven nedir' in voice:
        print(favoriteFruit)
        speak(favoriteFruit)

    if 'nasılsın' in voice:
        print(HowAreYou)
        speak(HowAreYou)

    if 'akşam yemekte ne var' in voice:
        print(whatsForDinner)
        speak(whatsForDinner)

    if 'saat kaç' in voice:
        speak(datetime.now().strftime('%H:%M:%S'))

    if 'arama yap' in voice:
        search =  record("ne aramak istiyorsun")
        url = 'https://google.com/search?q=' + search
        webbrowser.get().open(url)
        speak(search + 'için bulduklarım')

    if 'pencere aç' in voice:
        print(openWindow)
        speak(openWindow)
        rotateServo(windowServoPin,0)

    if 'pencere kapat' in voice:
        print(closeWindow)
        speak(closeWindow)
        rotateServo(windowServoPin, 90)

    if 'kapıyı açabilir misin' in voice:
        print(openDoor)
        speak(openDoor)
        rotateServo(doorServopin, 0)

    if 'kapıyı kapatabilir misin' in voice:
        print(closeDoor)
        speak(closeDoor)
        rotateServo(doorServopin, 90)

    if 'lambayı yak' in voice:
        print(onLed)
        speak(onLed)
        board.digital[13].write(1)

    if 'lamba kapat' in voice:
        print(offLed)
        speak(offLed)
        board.digital[13].write(0)

    if 'tamamdır' in voice:
        speak('görüşürüz')
        exit()

def speak(string):
    tts = gTTS(string, lang='tr')
    rand = random.randint(1,10000)
    file = 'audio-' + str(rand) + '.mp3'
    tts.save(file)
    playsound(file)
    os.remove(file)

speak('Nasıl yardımcı olabilirim ?')
time.sleep(0.5)

while 1:

    voice = record()
    print(voice.lower())
    response(voice)
