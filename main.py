# openai
import tkinter

from langchain import LLMChain
from langchain.llms import OpenAI
from langchain.text_splitter import TokenTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI

# .env
from dotenv import load_dotenv
import os
# api 관련 모듈
import requests
import xmltodict
import json
# 번역 모듈
import googletrans
import papago

# window
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# load .env
load_dotenv()

# 변수
displayContent = ''

# API 키
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
KIPRIS_API_KEY = os.environ.get("KIPRIS_API_KEY")

MAX_TOKEN = 3800


def getKiprisData():
    # applicationNumber = '1020210187520'
    # 키프리스 특허 데이터 API

    # 출원번호, 등록번호를 입력할 때, 출원번호를 얻는 함수
    def classifyInputNum(inputNumber):
        if inputNumber != '':
            try:
                registrationUrl = f'http://plus.kipris.or.kr/kipo-api/kipi/patUtiModInfoSearchSevice/getAdvancedSearch?registerNumber={inputNumber}&ServiceKey={KIPRIS_API_KEY}'
                response = requests.get(registrationUrl)
                content = response.text
                result = xmltodict.parse(content)
                applicationNum = result['response']['body']['items']['item']['applicationNumber']
                print("공고전문")
                statusLabel.config(text="공고전문")
                # print(result)
                return applicationNum
            except Exception as ex:
                return inputNumber
        else:
            statusLabel.config('제대로된 번호를 입력해주세요!')
            return 0

    try:
        statusLabel.config(text='')
        inputNumber = classifyInputNum(inputNumber=Entry.get())  # 출원번호 : 1020230008327 , 등록번호 : 1025569250000
        print(inputNumber)
        applicationUrl = f"http://plus.kipris.or.kr/kipo-api/kipi/patUtiModInfoSearchSevice/getBibliographyDetailInfoSearch?applicationNumber={inputNumber}&ServiceKey={KIPRIS_API_KEY}"
        # registrationUrl = f'http://plus.kipris.or.kr/kipo-api/kipi/patUtiModInfoSearchSevice/getAdvancedSearch?registerNumber={inputNumber}&ServiceKey={KIPRIS_API_KEY}'

        # applicationUrl, registrationUrl 선택해서 들어가기
        # resultCode = 00 -> 성공, 99 -> 실패
        response = requests.get(applicationUrl)
        contents = response.text
        print(contents)
        # xml -> dick 형대로 변경
        result = xmltodict.parse(contents)
        # JSON
        # body = json.dumps(result, ensure_ascii=False, indent=3)
        body = json.dumps(result)

        # 공고번호
        publicationDate = result['response']['body']['item']['biblioSummaryInfoArray']['biblioSummaryInfo'][
            'publicationDate']
        if publicationDate is None:
            statusLabel.config(text='공개전문')
        elif publicationDate is not None:
            statusLabel.config(text='공고전문')
        print(f'공고일자 : {publicationDate}')

        # 발명 제목
        inventionTitle = result['response']['body']['item']['biblioSummaryInfoArray']['biblioSummaryInfo'][
            'inventionTitle']

        # 발명 개요
        astrtContent = result['response']['body']['item']['abstractInfoArray']['abstractInfo']['astrtCont']

        # 청구항
        claimContent = result['response']['body']['item']['claimInfoArray']['claimInfo']
        claimTxt = ""
        # claimContent.append(f'특허명 : {inventionTitle}')

        # 청구항 정리
        # for item in claimContent:
        #     claim = item['claim']
        #     print(claim.find("청구항"))
        #     if claim.find("항에 있어서") == -1 and claim.find("삭제") == -1 and claim.find("항의") == -1:
        #         print(f'hello{claim}')
        #         claimTxt += claim + " "

        # 청구항 배열로 정리
        # txt = f'특허명 : {inventionTitle}, 개요 : {astrtContent}, 청구항 : {claimTxt}'
        # txt = f'청구항 : {claimTxt}'
        # print(claimContent)
        # 반환값을 청구항 배열 넣기
        return claimContent
    except Exception as ex:
        print(ex)
        statusLabel.config(text='잘못 입력 하셨습니다, 출원번호 혹은 등록번호를 입력 부탁 드립니다.')
        return ""


def test():
    global inputDataArr
    try:
        # max token 확인하기
        llm = OpenAI(openai_api_key=OPENAI_API_KEY, temperature=0, model_name='gpt-3.5-turbo')
        # llm = OpenAI(openai_api_key=OPENAI_API_KEY, temperature=0, model_name='text-davinci-003')
        # chat = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model_name='gpt-3.5-turbo')
        patentDatas = getKiprisData()
        patentText = []
        for patent in patentDatas:
            claim = patent['claim']
            if claim.find("항에 있어서", 0, 30) == -1 and claim.find("삭제") == -1 and claim.find('항의') == -1 and claim.find(
                    '청구항') == -1:  # and claim.find('에 있어서', 0, 30) == -1:
                print(claim)
                patentText.append('청구항' + " " + claim)
        listbox2.delete(0, END)
        for patent in patentText:
            listbox2.insert(tk.END, patent)

        # translatedTexts = papago.translate(papago.translate(patentText, 'ko', 'ja'), 'ja', 'en')
        # translatedTexts = papago.translate(papago.translate(patentText, 'ko', 'zh-CN'), 'zh-CN', 'en')
        translatedTexts = papago.translate(patentText, 'ko', 'en')
        patentStr = ''
        listbox3.delete(0, 'end')
        for patent in translatedTexts:
            print(patent)
            patentStr += ' ' + patent
            listbox3.insert(tk.END, patent)
        # print(patentStr)

        # 토큰화
        text_splitter = TokenTextSplitter(chunk_size=1000, chunk_overlap=0, length_function=len)
        texts = text_splitter.split_text(patentStr)
        for item in texts:
            inputDataArr = {
                'content': item,
            }

        template = """
                    [start of document]
                    Document = {content}
                    [end of document]
                    
                    [start of task intruction]
                    - only follow the output format defiend
                    - don't delete a claim in Document
                    - Briefly and Easily explain each claim in Document
                    - output language is korean
                    [end of task instruction]
                    
                    [output format start]
                    claim claim's number : briefly explained document.
                    [output format end]
                   """
        # You are a good patent attorney.
        # you must not delete a claim.
        # you must briefly and easily explain each claim of patent.
        # answer format is claim claim'number : content
        # {content}.
        prompt = PromptTemplate.from_template(template=template)
        chain = LLMChain(llm=llm, prompt=prompt)
        # chain = LLMChain(llm=chat, prompt=prompt)
        answer = chain.predict(content=inputDataArr)
        print(f'answer : {answer}')
        print(type(answer))

        AnswerList = []

        for item in answer.split('Claim'):
            AnswerList.append(f'{item}')

        print(AnswerList)
        # translatedAnswer = papago.translate(papago.translate(AnswerList, 'en', 'ja'), 'ja', 'ko')
        # translatedAnswer = papago.translate(papago.translate(AnswerList, 'en', 'zh-CN'), 'zh-CN', 'ko')
        # translatedAnswer = papago.translate(AnswerList, 'en', 'ko')

        # print(f'trans : {translatedAnswer}')
        # print(type(translatedAnswer))
        # splitAnswer = translatedAnswer[0].split('\n\n')  # 이부분 체크
        # print(splitAnswer)
        # print(type(splitAnswer))
        splitAnswer = AnswerList[0].split('\n\n')  # 이부분 체크
        print(splitAnswer)
        print(type(splitAnswer))

        listbox1.delete(0, 'end')
        for item in splitAnswer:
            listbox1.insert(tk.END, item)

    except Exception as ex:
        print(ex)


# def translate():
#     patentData = getKiprisData()
#     patentTexts = []
#     for patent in patentData:
#         claim = patent['claim']
#         # print(claim)        print(claim.find("항에 있어서", 0, 30))
#         if claim.find("항에 있어서", 0, 30) == -1 and claim.find("삭제") == -1 and claim.find('항의') == -1:
#             patentTexts.append('청구항' + " " + claim)
#     print(f'독립항 원문 : {patentTexts}')
#
#     english = papago.translate(patentTexts, 'ko', 'en')
#     japanese = papago.translate(patentTexts, 'ko', 'ja')
#     chinese = papago.translate(patentTexts, 'ko', 'zh-CN')
#
#     def translatedJpToEn(text):
#         return papago.translate(text, 'ja', 'en')
#
#     def translatedCnToEn(text):
#         return papago.translate(text, 'zh-CN', 'en')
#
#     def translatedEnToKo(text):
#         return papago.translate(text, 'en', 'ko')
#
#     print(f'영어 : {english}')
#     print(f'일본어 -> 영어 : {translatedJpToEn(japanese)}')
#     print(f'중국어 -> 영어 : {translatedCnToEn(chinese)}')


# 윈도우 프레임
window = tk.Tk()
window.geometry("1920x1080+100+100")

# 윈도우 타이틀
window.title('OpenAI ChatGPT')

# 등록번호, 출원번호 입력창
Entry = ttk.Entry(window, bootstyle='dark', width=60)
Entry.pack()

# 특허데이터 검색 및 요약 버튼
searchApplicationNoBtn = ttk.Button(window, bootstyle='dark', width=59, text='특허 청구항 검색', command=test)
searchApplicationNoBtn.pack()

statusLabel = tk.Label(window, text='출원번호 혹은 등록번호를 입력해주세요')
statusLabel.pack()

# scrollbar = tk.Scrollbar(frame, relief='flat', orient='horizontal')
# scrollbar.pack(side="bottom", fill="x")

# 리스트 박스 생성
labelSummary = tk.Label(window, text='청구항 요약문', height=4)  # 리스트 박스 이름
labelSummary.place(x=50, y=50)
listbox1 = tk.Listbox(window, selectmode=tk.SINGLE, height=15)  # 청구항 요약문 리스트박스

# scrollbar["command"] = listbox1.xview

listbox1.place(x=50, y=100, width=1820)
# listbox1.pack()
#

labelKorean = tk.Label(window, text='청구항 원문', height=4)  # 리스트 박스 이름
labelKorean.place(x=50, y=350)
listbox2 = tk.Listbox(window, selectmode=tk.SINGLE, height=15)  # 청구항 원문 리스트박스
listbox2.place(x=50, y=400, width=1820)

labelTranslate = tk.Label(window, text='청구항 번역문', height=4)  # 리스트 박스 이름
labelTranslate.place(x=50, y=650)
listbox3 = tk.Listbox(window, selectmode=tk.SINGLE, height=15)  # 청구항 번역문 리스트박스
listbox3.place(x=50, y=700, width=1820)

# frame.pack(side="left", fill="both", expand=True)
window.mainloop()
