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

modelName = 'text-davinci-003'


# TODO: 모델전환 기능 추가
def model_toggle():
    modelValue = 0
    global modelName
    if modelValue == 0:
        modelValue += 1
        modelName = 'gpt-turbo-3.5'
    elif modelValue == 1:
        modelValue -= 1
        modelName = 'text-davinci-003'
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

        # TODO: 기존 문장의 내용 초기화하기

        # TODO: 원문 모두 넣기
        origianlText.config(state=tk.NORMAL)
        # for item in independentClaims:
        #     origianlText.insert(tk.END, f'{item}\n\n')
        origianlText.insert(tk.END, f'{independentClaims[0]}\n\n')
        origianlText.config(state=tk.DISABLED)

        translatedClaims = papago.translate(independentClaims, 'ko', 'en')
        # translatedClaims = papago.translatedTexts = papago.translate(papago.translate(independentClaims, 'ko', 'ja'), 'ja', 'en')
        # translatedClaims = papago.translate(papago.translate(independentClaims, 'ko', 'zh-CN'), 'zh-CN', 'en')

        # TODO: 세번째 번역된 내용 모두 집어넣기
        translatedText.config(state=tk.NORMAL)
        # for item in translatedClaims:
        #     translatedText.insert(tk.END, f'{item}\n\n')
        translatedText.insert(tk.END, f'{translatedClaims[0]}\n\n')
        translatedText.config(state=tk.DISABLED)

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
        answer = chain.predict(content=texts)

        AnswerList = []

        for item in answer.split('claim'):
            AnswerList.append(item)

        AnswerList.pop(0)

        print(answer)
        print(AnswerList)
        print(len(AnswerList))

        # TODO:요약본 모두 넣기
        summaryText.config(state=tk.NORMAL)
        # for item in AnswerList:
        #     summaryText.insert(tk.END, f'{item}\n\n')
        summaryText.insert(tk.END, f'{AnswerList[0]}\n\n')
        summaryText.config(state=tk.DISABLED)

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
searchFrame.pack()  # 라인 제거 unfinished

# 검색 및 모델전환버튼
searchApplicationNoBtn = ttk.Button(searchFrame, bootstyle='dark', width=29, text='특허 청구항 검색', command=test)
searchApplicationNoBtn.pack(side=LEFT)
toggleBtn = ttk.Button(searchFrame, bootstyle='dark', width=29, text='모델전환', command='')
toggleBtn.pack(side=LEFT)

# 상태정보 표시
statusLabel = tk.Label(window, text='출원번호 혹은 등록번호를 입력해주세요')
statusLabel.pack()

# 요약문 구역
summaryFrame = tk.LabelFrame(window, text="청구항 요약문", width=1870, height=250, padx=2, pady=2, relief='solid')
summaryFrame.pack(fill=tk.X, padx=25, pady=15)
summaryText = tk.Text(summaryFrame, wrap=tk.WORD, spacing2=15, height=12, font=('Pretendard', 12), padx=10, pady=5,
                      state=tk.DISABLED)
summaryText.pack(fill=tk.BOTH, padx=2, pady=2)

# 본문 구역
origianlFrame = tk.LabelFrame(window, text="청구항 원문", width=1870, height=250, padx=2, pady=2, relief='solid')
origianlFrame.pack(fill=tk.X, padx=25, pady=15)
origianlText = tk.Text(origianlFrame, wrap=tk.WORD, spacing2=15, height=12, font=('Pretendard', 12), padx=5,
                       pady=10, state=tk.DISABLED)
origianlText.pack(fill=tk.BOTH, padx=2, pady=2)

# 번역문 구역
translatedFrame = tk.LabelFrame(window, text="청구항 번역문", width=1870, height=250, padx=2, pady=2, relief='solid')
translatedFrame.pack(fill=tk.X, padx=25, pady=15)
translatedText = tk.Text(translatedFrame, wrap=tk.WORD, spacing2=15, height=12, font=('Pretendard', 12), padx=5,
                         pady=10, state=tk.DISABLED)
translatedText.pack(fill=tk.BOTH, padx=2, pady=2)

# 스크롤바 세팅
scrollbar = tk.Scrollbar(summaryText, relief='flat', orient=VERTICAL)
# TODO: 스크롤바 세팅
# scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)

# frame.pack(side="left", fill="both", expand=True)
window.mainloop()
