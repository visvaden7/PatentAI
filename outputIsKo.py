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

import getKiprisPatent as kipris

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


def model_toggle():
    modelValue = 0
    modelName = 'gpt-turbo-3.5'
    if modelValue == 0:
        modelValue += 1
        modelName = 'text-davinci-003'
    elif modelValue == 1:
        modelValue -= 1
        modelName = 'gpt-turbo-3.5'
    return modelName


def test():
    inputNumber = Entry.get()  # 출원번호 : 1020230008327 , 등록번호 : 1025569250000
    statusLabel.config(text="출원번호 혹은 등록번호 입력해주세요!")
    try:
        # kipris data 가져오기
        result = kipris.getKiprisData(inputNumber)

        # 공고전문 / 공개전문 여부 확인하기
        publicationStatus = kipris.getPublicationStatus(result)
        statusLabel.config(text=publicationStatus)

        inventionTitle = kipris.getInventionTitle(result)
        claimContents = kipris.getClaimContent(result)

        independentClaims = []
        for claimContent in claimContents:
            claim = claimContent['claim']
            if claim.find("항에 있어서", 0, 30) == -1 and claim.find("삭제") == -1 and claim.find('항의') == -1 and claim.find(
                    '청구항') == -1:  # and claim.find('에 있어서', 0, 30) == -1:
                print(claim)
                independentClaims.append(claim)

        # 원문 넣기

        translatedClaims = papago.translate(independentClaims, 'ko', 'en')
        # translatedClaims = papago.translatedTexts = papago.translate(papago.translate(independentClaims, 'ko', 'ja'), 'ja', 'en')
        # translatedClaims = papago.translate(papago.translate(independentClaims, 'ko', 'zh-CN'), 'zh-CN', 'en')

        # 세번째 번역된 내용 집어넣기 unfinished

        # llm model에 들어갈 컨텐츠
        forGPTContent = ''
        for claim in translatedClaims:
            forGPTContent += ' ' + claim

        # 토큰화
        text_splitter = TokenTextSplitter(chunk_size=1000, chunk_overlap=0, length_function=len)
        texts = text_splitter.split_text(forGPTContent)

        # 템플릿
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

        # llm 모델 세팅하기
        llm = OpenAI(openai_api_key=OPENAI_API_KEY, temperature=0, model_name='gpt-3.5-turbo')
        # llm = OpenAI(openai_api_key=OPENAI_API_KEY, temperature=0, model_name='text-davinci-003')
        prompt = PromptTemplate.from_template(template=template)
        chain = LLMChain(llm=llm, prompt=prompt)

        # GPT 값 출력하기
        answer = chain.predict(content=forGPTContent)

        AnswerList = []

        for item in answer.split('Claim'):
            AnswerList.append(item)

        # 요약본 추가하기 unfinished

    except:
        statusLabel.config(text='정확한 번호를 입력 해주세요')


# 윈도우 프레임
window = tk.Tk()
window.geometry("1920x1080+100+100")

# 윈도우 타이틀
window.title('OpenAI ChatGPT')

# 등록번호, 출원번호 입력창
Entry = ttk.Entry(window, bootstyle='dark', width=60)
Entry.pack()

# 특허데이터 검색 및 요약 버튼
# 검색창 및 버튼구역
searchFrame = tk.LabelFrame(window, padx=0, pady=5)
searchFrame.pack() # 라인 제거 unfinished

# 검색 및 모델전환버튼
searchApplicationNoBtn = ttk.Button(searchFrame, bootstyle='dark', width=29, text='특허 청구항 검색', command=test)
searchApplicationNoBtn.pack(side=LEFT)
toggleBtn = ttk.Button(searchFrame, bootstyle='dark', width=29, text='모델전환', command='')
toggleBtn.pack(side=LEFT)

# 상태정보 표시
statusLabel = tk.Label(window, text='출원번호 혹은 등록번호를 입력해주세요')
statusLabel.pack()

# 요약문 구역
summaryFrame = tk.LabelFrame(window, text="청구항 요약문", width=1870, height=300, padx=2, pady=2)
summaryFrame.pack()

# 본문 구역
origianlFrame = tk.LabelFrame(window, text="청구항 원문", width=1870, height=300, padx=2, pady=2)
origianlFrame.pack()

# 번역문 구역
translatedFrame = tk.LabelFrame(window, text="청구항 번역문", width=1870, height=300, padx=2, pady=2)
translatedFrame.pack()

#스크롤바 세팅
scrollbar = tk.Scrollbar(summaryFrame, relief='flat', orient=VERTICAL)
# scrollbar.pack(side=tk.RIGHT) unfinished


# frame.pack(side="left", fill="both", expand=True)
window.mainloop()
