from langchain import LLMChain
from langchain.llms import OpenAI
from langchain.text_splitter import TokenTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

# .env
from dotenv import load_dotenv
import os

# 번역 모듈
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

modelName = 'gpt-3.5-turbo'
modelValue = 0


def model_toggle():
    global modelValue
    global modelName
    if modelValue == 0:
        modelValue += 1
        modelName = 'text-davinci-003'
    elif modelValue == 1:
        modelValue -= 1
        modelName = 'gpt-3.5-turbo'
    print(modelName)
    toggleBtn.config(text=f'모델 변환({modelName})')


def test():
    global modelName
    inputNumber = Entry.get()  # 출원번호 : 1020230008327 , 등록번호 : 1025569250000
    # kipris data 가져오기
    result = kipris.getKiprisData(inputNumber)

    # 특허명
    inventionTitle = kipris.getInventionTitle(result)

    # 공고전문 / 공개전문 여부 확인하기
    publicationStatus = kipris.getPublicationStatus(result)

    # 특허번호 / 등록번호
    applicationNum = kipris.getPatentNumber(result).get('applicationNum')
    registerNum = kipris.getPatentNumber(result).get('registerNum')

    # 해당 특허에 대한 정보 입력
    statusText = f'특허명 : {inventionTitle},    출원번호 : {applicationNum},    등록번호 : {registerNum},    공고상태 : {publicationStatus}'

    print(statusText)
    statusLabel.config(text=statusText)

    claimContents = kipris.getClaimContent(result)

    independentClaims = []
    for claimContent in claimContents:
        claim = claimContent['claim']
        if claim.find("항에 있어서", 0, 30) == -1 and claim.find("삭제") == -1 and claim.find('항의') == -1 and claim.find(
                '청구항') == -1:  # and claim.find('에 있어서', 0, 30) == -1:
            print(claim)
            independentClaims.append(claim)
    # TODO: independentClaims 를 split(;)
    easyReadList = []
    for item in independentClaims:
        easyReadList.append(';\n\n'.join(item.split(';')))
    print(f'easyReadList : {easyReadList}')

    # 원문 초기화 및 입력
    origianlText.config(state=tk.NORMAL)
    origianlText.delete('1.0', tk.END)
    origianlText.insert(tk.END, f'{easyReadList[0]}\n\n')
    origianlText.config(state=tk.DISABLED)

    # 번역된 내용 초기화 및 입력
    translatedClaims = papago.translate(independentClaims, 'ko', 'en')
    translatedText.config(state=tk.NORMAL)
    translatedText.delete('1.0', tk.END)
    translatedText.insert(tk.END, f'{translatedClaims[0]}\n\n')
    translatedText.config(state=tk.DISABLED)

    # llm model에 들어갈 컨텐츠

    chat = ChatOpenAI(openai_api_key=OPENAI_API_KEY, temperature=0, model_name=modelName)

    forGPTContent = ''
    for claim in translatedClaims:
        forGPTContent += f'{claim}, '
    forGPTContent += f'{len(translatedClaims)} of claim'
    # 토큰화
    text_splitter = TokenTextSplitter(chunk_size=1000, chunk_overlap=0, length_function=len)
    texts = text_splitter.split_text(forGPTContent)

    template = """
                [start of document]
                Document = {content}
                [end of document]
    
                [start of task intruction]
                - only follow the output format defiend
                - don't remove a claim in Document
                - don't add and divide a claim in Document
                - summarize each claim without omitting details in Document
                - output language is korean
                [end of task instruction]
    
                [output format start]
                claim claim's number : briefly explained Document.
                [output format end]
            """

    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    human_template = "{content}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

    answer = chat(chat_prompt.format_prompt(content=texts).to_messages())
    print(type(answer.content))
    answerContent = answer.content
    print(answerContent)
    print(type(answerContent))
    AnswerList = []

    print(answerContent.find('클레임'))
    # print(answerContent.split('클레임'))

    if answerContent.find('클레임') == -1:
        for item in answerContent.split('claim'):
            AnswerList.append(item)
    # else:
    #     for item in answerContent.split('클레임'):
    #         AnswerList.append(item)

    print(AnswerList)

    # for item in AnswerList:
    #     if item.find(':') == -1:
    #         print(item.find(':'))
    #         AnswerList.remove(item)
    print(AnswerList)
    print('-------------------------------------------------------------------------')
    enumList = enumerate(AnswerList)
    for index, item in enumList:
        print(index)
        print(item)


    # 요약본 초기화 및 입력
    summaryText.config(state=tk.NORMAL)
    summaryText.delete('1.0', tk.END)
    summaryText.insert(tk.END, f'{AnswerList[0]}\n\n')
    summaryText.config(state=tk.DISABLED)

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
searchFrame = tk.LabelFrame(window, padx=0, pady=0)
searchFrame.pack()

# 검색 및 모델전환버튼
searchApplicationNoBtn = ttk.Button(searchFrame, bootstyle='dark-outline', width=28, text='특허 청구항 검색', command=test)
searchApplicationNoBtn.pack(side=LEFT)
toggleBtn = ttk.Button(searchFrame, bootstyle='dark-outline', width=27, text=f'모델 변환({modelName})',
                       command=model_toggle)
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

window.mainloop()
