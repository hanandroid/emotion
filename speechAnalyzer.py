'''
 日本語で録音、IBMクラウドサービスで日本語へ変換、英語に翻訳してから、英文での感情分析

 You need to install pyaudio to run this example
 pip3 install pydub
 brew install portaudio
 pip3 install pyaudio
 install ffmpeg to your sys path
'''
import requests
import json
import pyaudio
import wave
import pydub
import numpy
import math

# IBM Cloud Service用
SPEECH_TO_TEXT_APIKEY='192f4J3_HM2rEAorCdeRiTYW3ccB3ZFqBkVs-It6uTbO'
SPEECH_TO_TEXT_URL='https://api.jp-tok.speech-to-text.watson.cloud.ibm.com/instances/670dbb03-540f-4957-8a39-40a72c510e17/v1/recognize'

LANGUAGE_TRANSLATOR_APIKEY='QCqXxkcVZxzoKanUY7Y9K2BE3JyakCxQ8iKKvTmJr50n'
LANGUAGE_TRANSLATOR_URL='https://api.us-south.language-translator.watson.cloud.ibm.com/instances/5b5ad742-38cc-42f0-889f-9a9597073372/v3/translate'

TONE_ANALYZER_APIKEY='SsvqEQ_riAWRGCGp1yGq02gjtugD1ftos9k5u1ns62IB'
TONE_ANALYZER_URL='https://api.us-south.tone-analyzer.watson.cloud.ibm.com/instances/d332a067-bb24-4bab-a728-267d6e26ca24/v3/tone'


# 入力音声ファイル
INPUT_SPEECH = "speech.mp3"
INPUT_SEC = 5
Inframes = []

# 解析結果
OUTPUT_RESULT = "speechAnalyzer.json"

########################
class IBM_Serice:
    def __init__(self):
        self.inFile = INPUT_SPEECH
        self.jaText = "サンプル"
        self.enText = "sample"
        print(self.inFile)

    # 音声ファイルー＞文字変換
    def speechToText(self):
        headers = {
            'Content-Type': 'audio/mp3',
        }
        params = (
            ('model', 'ja-JP_BroadbandModel'),
        )
        data = open(self.inFile, 'rb').read()

        response = requests.post(SPEECH_TO_TEXT_URL, headers=headers, params=params, data=data, auth=('apikey', SPEECH_TO_TEXT_APIKEY))
        #print(response.text)
        try:
            data = response.json()
            self.jaText = json.dumps(data["results"][0]["alternatives"][0]["transcript"], ensure_ascii=False)
            print(self.jaText)
        except:
            print("No response.")

    #　翻訳　日本語　ー＞　英語
    def translateText(self):
        headers = {
            'Content-Type': 'application/json',
        }
        params = (
            ('version', '2020-01-01'),
        )
        dict = {"text": self.jaText, "model_id":"ja-en"}
        data = json.dumps(dict)

        response = requests.post(LANGUAGE_TRANSLATOR_URL, headers=headers, params=params, data=data.encode("utf-8"), auth=('apikey', LANGUAGE_TRANSLATOR_APIKEY))
        #print(response.text)

        data = response.json()
        self.enText = json.dumps(data["translations"][0]["translation"])
        print(self.enText)

    #　英語　ー＞感情分析
    def toneAnalyzer(self):
        headers = {
            'Content-Type': 'application/json',
        }
        params = (
            ('version', '2020-01-01'),
            ('sentences', 'false'),
        )
        #data = open('/Users/user/user2020/Hackathon_Onejapan/tone.json', 'rb').read()
        dict = {"text": self.enText}
        data = json.dumps(dict)

        response = requests.post(TONE_ANALYZER_URL, headers=headers, params=params, data=data, auth=('apikey', TONE_ANALYZER_APIKEY))
        #print(response.text)

        # データ切り出し、保存
        data = response.json()
        result = json.dumps(data["document_tone"]["tones"], indent=2)
        print(result)

        f = open(OUTPUT_RESULT, "w")
        json.dump(data, f, ensure_ascii=False)
        print("* save json = ", OUTPUT_RESULT)


# 録音
def inputWave(fileName, sec):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16 # int16型
    CHANNELS = 1             # ステレオ
    RATE = 44100             # 44.1kHz
    RECORD_SECONDS = sec     # 5秒録音
    WAVE_OUTPUT_FILENAME = fileName.split('.')[0] + '.wav'
    MP3_OUTPUT_FILENAME = fileName

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("* recording")
    frames = []
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        if checkDB(data) > 0:
            frames.append(data) #データを追加
            print(".", end="")

    #print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    print("* save wave")

    # wav -> mp3
    sound = pydub.AudioSegment.from_wav(WAVE_OUTPUT_FILENAME)
    sound.export(MP3_OUTPUT_FILENAME, format="mp3")
    print("* save mp3 = ", MP3_OUTPUT_FILENAME)

# 音量チェック
def checkDB(data):
    result = numpy.frombuffer(data,dtype="int16")
    rms = (max(result))
    db = 20 * math.log10(rms)
    #print("RMS=", rms, f" ：{format(db, '3.1f')}[dB]")

    if db > 60:
        flg = 1
    else:
        flg = 0
    return flg


def doService():
    inputWave(INPUT_SPEECH, INPUT_SEC)
    service = IBM_Serice()
    service.speechToText()
    service.translateText()
    service.toneAnalyzer()

if __name__=='__main__':
    try:
        while True:
            doService()
    except KeyboardInterrupt:
        print("Emergency stop")
        sys.exit(0)
