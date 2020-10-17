'''
 IBMクラウドサービスで日本語へ変換、英語に翻訳してから、英文での感情分析
'''
import requests
import json
import os


# IBM Cloud Service用
SPEECH_TO_TEXT_APIKEY='192f4J3_HM2rEAorCdeRiTYW3ccB3ZFqBkVs-It6uTbO'
SPEECH_TO_TEXT_URL='https://api.jp-tok.speech-to-text.watson.cloud.ibm.com/instances/670dbb03-540f-4957-8a39-40a72c510e17/v1/recognize'

LANGUAGE_TRANSLATOR_APIKEY='QCqXxkcVZxzoKanUY7Y9K2BE3JyakCxQ8iKKvTmJr50n'
LANGUAGE_TRANSLATOR_URL='https://api.us-south.language-translator.watson.cloud.ibm.com/instances/5b5ad742-38cc-42f0-889f-9a9597073372/v3/translate'

TONE_ANALYZER_APIKEY='SsvqEQ_riAWRGCGp1yGq02gjtugD1ftos9k5u1ns62IB'
TONE_ANALYZER_URL='https://api.us-south.tone-analyzer.watson.cloud.ibm.com/instances/d332a067-bb24-4bab-a728-267d6e26ca24/v3/tone'


# 解析結果
OUTPUT_RESULT = "speechAnalyzer.json"

########################
class IBM_Serice:
    def __init__(self, jaText):
        self.inFile = INPUT_SPEECH
        self.jaText = jaText
        self.enText = "sample"
        self.result = ""
        #print(self.inFile)

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

        data = response.json()
        self.jaText = json.dumps(data["results"][0]["alternatives"][0]["transcript"], ensure_ascii=False)
        print(self.jaText)

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
        result = json.dumps(data["translations"][0]["translation"])
        self.enText = result
        self.result = "文書の翻訳結果 > " + result
        #print(result)

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

        try:
            result = json.dumps(data["document_tone"]["tones"][0], indent=2)
            print(result)
            #json_dict = json.loads(result)
            score = json.dumps(data["document_tone"]["tones"][0]["score"])
            score = str(float(score) * 100)
            tone = json.dumps(data["document_tone"]["tones"][0]["tone_name"])
        except:
            score = "100"
            tone = "謎"
        self.result = "あなたの感情分析結果 > " + tone + " は " + score + "点"

        #f = open(OUTPUT_RESULT, "w")
        #json.dump(data, f, ensure_ascii=False)
        #print("* save json = ", OUTPUT_RESULT)

    def getResult(self):
        return self.result

    def getPoem(self, delight, anger, sorrow, pleasure):
        # emotional poem endpoint
        url = "https://rapidapi.p.rapidapi.com/app/api/getPoem"

        # convert emotion anger, fear, joy, and sadness
        querystring = {"delight":delight,"anger":anger,"sorrow":sorrow,"pleasure":pleasure,"type":"max","method":"cos"}

        headers = {
            'x-rapidapi-host': "emotional-poem.p.rapidapi.com",
            'x-rapidapi-key': os.environ['EMOTIONAL_POEM_RAPIDAPI_KEY']
            }

        response = requests.request("GET", url, headers=headers, params=querystring)

        # return result of poem JSON
        data = response.json()
        return data

