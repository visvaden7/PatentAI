import os
import urllib.request
import urllib.parse
import json

from dotenv import load_dotenv


# NEED URLLIB, JSON MODULE
def translate(texts: str and list, src: str, det: str):
    # 파파고 API
    # dotenv 를 통한 파파고 API CLIENT_ID AND SECRET
    load_dotenv()
    PAPAGO_CLIENT_ID = os.environ.get("PAPAGO_CLIENT_ID")
    PAPAGO_CLIENT_SECRET = os.environ.get("PAPAGO_CLIENT_SECRET")

    def papagoTranslate(txt):
        # 파파고 API CLIENT_ID AND SECRET
        client_id = PAPAGO_CLIENT_ID
        client_secret = PAPAGO_CLIENT_SECRET

        encText = urllib.parse.quote(txt)
        data = f"source={src}&target={det}&text=" + encText
        url = "https://naveropenapi.apigw.ntruss.com/nmt/v1/translation"
        request = urllib.request.Request(url)
        request.add_header("X-NCP-APIGW-API-KEY-ID", client_id)
        request.add_header("X-NCP-APIGW-API-KEY", client_secret)
        response = urllib.request.urlopen(request, data=data.encode("utf-8"))
        resCode = response.getcode()
        if resCode == 200:
            response_body = response.read()
            response = json.loads(response_body.decode('utf-8'))
            result = response['message']['result']['translatedText']
            # print(result)
            return result
        else:
            print("Error Code:" + resCode)

    # STR AND LIST 두 자료타입을 받더라도 처리할 수 있도록 작동
    try:
        if type(texts) == str:
            print('번역완료 str')
            return papagoTranslate(texts)
        elif type(texts) == list:
            list_result = []
            for text in texts:
                list_result.append(papagoTranslate(str(text)))
            print(list_result)
            print('번역완료 List')
            return list_result
    except Exception as ex:
        print(ex)
