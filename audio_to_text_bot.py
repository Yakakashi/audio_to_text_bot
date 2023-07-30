import telebot
from telebot import types
import speech_recognition as sr
import requests
import subprocess, os


TOKEN = "##########:####################################"

f1 = """/start - что я такое?
Приветствую! Я перевожу твои аудио сообщения в текст.
Для тех, кто не любит "голосовухи".
Просто отправь в чат голосовое сообщение.
"""

ffmpeg = r"E:\Programming\ffmpeg-4.0.2-win64-static\ffmpeg-4.0.2-win64-static\bin\ffmpeg.exe"

def convert_to_wav(ffmmpeg_path, input_file):
    output_file = input_file[:-4] + ".wav"
    p = subprocess.Popen(ffmmpeg_path + " -i " + input_file + " -acodec pcm_s16le -ac 1 -ar 16000 " + output_file)
    p.communicate()

def audio_recognition(file):
    recognizer = sr.Recognizer()
    audio_file = sr.AudioFile(file)
    with audio_file as source_audio:
        res_audio = recognizer.record(source_audio)
    try:
        text = recognizer.recognize_google(res_audio, language="ru-RU")
    except Exception:
        text = "не распознал фразу"
    return text
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, f1)

@bot.message_handler(content_types=['voice', 'text'])
def recognize_speech(message):
    # получаем информацию о голосовом сообщении
    voice_info = bot.get_file(message.voice.file_id)
    # обращение к api telegram, Все запросы к Telegram Bot API должны осуществляться через HTTPS в следующем виде: https://api.telegram.org/bot<token>/НАЗВАНИЕ_МЕТОДА
    url = f"https://api.telegram.org/file/bot{TOKEN}/{voice_info.file_path}"
    file = requests.get(url)
    # сохранение голосовухи в файл формата wav, для последующего распознавания
    with open ("voice.ogg", "wb") as voice_mess:
        voice_mess.write(file.content)
    convert_to_wav(ffmpeg, "voice.ogg")
    out_text = audio_recognition("voice.wav")
    bot.send_message(message.chat.id, out_text)
    try:
        os.remove("voice.wav")
    except FileNotFoundError:
        bot.send_message(message.chat.id, "не распознал фразу")

bot.polling(none_stop=True)