import tkinter as tk
from tkinter import LabelFrame, Label, Scrollbar, Text, VERTICAL, RIGHT, Y
import os
import dotenv

from langchain import LLMChain
from langchain.llms import OpenAI
from langchain.text_splitter import TokenTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI

import getKiprisPatent as kipris
import papago

# load .env
dotenv.load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


# kipris data 받아오기 => 단위모듈화 작업
# langchain chatbot 형태로 변경하기

# 출원번호 : 1020230008327 , 등록번호 : 1025569250000
def init():
    bot_response = '특허번호 혹은 등록번호를 입력해주세요\n'
    chatDisplay.config(state=tk.NORMAL)
    chatDisplay.insert(tk.END, "챗봇:\n " + bot_response + "\n")
    chatDisplay.config(state=tk.DISABLED)


def sendMessage():  # 채팅 메시지 입력
    message = userInput.get("1.0", "end-1c")  # Get user input
    chatDisplay.config(state=tk.NORMAL)
    chatDisplay.insert(tk.END, "사용자: " + message + "\n\n\n")
    result = kipris.getKiprisData(message)
    publicStatus = kipris.getPublicationStatus(result)
    claimContent = kipris.getClaimContent(result)
    inventionTitle = kipris.getInventionTitle(result)
    astractContent = kipris.getAstroContent(result)

    chatDisplay.config(state=tk.DISABLED)
    userInput.delete("1.0", tk.END)  # Clear the user input field

    # 챗봇 응답 시뮬레이션 (실제 챗봇 로직으로 대체)
    # 특허정보 관련( 특허명, 특허개요, 공고전문/공개전문여부)
    bot_response = ''

    chatDisplay.config(state=tk.NORMAL)
    bot_response = f"현재 이 특허는 {publicStatus}입니다.\n\n"  # 특허관련 요약 내용 추가
    chatDisplay.insert(tk.END, f"챗봇:\n\n{bot_response}\n")
    bot_response = f"특허명 : {inventionTitle}\n"
    chatDisplay.insert(tk.END, f"챗봇:\n\n{bot_response}\n")
    bot_response = f"특허개요 : {astractContent}\n"
    chatDisplay.insert(tk.END, f"챗봇:\n\n{bot_response}\n\n")

    # 청구항 원문 / 번역문
    independentClaims = []
    for patent in claimContent:
        claim = patent['claim']
        if claim.find("항에 있어서", 0, 30) == -1 and claim.find("삭제") == -1 and claim.find('항의') == -1 and claim.find(
                '청구항') == -1:  # and claim.find('에 있어서', 0, 30) == -1:
            independentClaims.append(claim)

    print(independentClaims)
    print(type(independentClaims))

    # 청구항 번역문
    translatedClaims = papago.translate(independentClaims, 'ko', 'en')
    print(translatedClaims)
    forGPTContent = ''
    for claim in translatedClaims:
        forGPTContent += ' ' + claim

    # tokenizer
    text_splitter = TokenTextSplitter(chunk_size=1000, chunk_overlap=0, length_function=len)
    texts = text_splitter.split_text(forGPTContent)
    # for item in texts:
    #     inputDataArr = {
    #         'content': item,
    #     }

    template = """
                        [start of document]
                        Document = {content}
                        [end of document]

                        [start of task intruction]
                        - only follow the output format defiend
                        - don't delete a claim in Document
                        - Briefly and Easily explain each claim in Document
                        [end of task instruction]

                        [output format start]
                        claim claim's number : briefly explained document.
                        [output format end]
                       """
    # llm = OpenAI(openai_api_key=OPENAI_API_KEY, temperature=0, model_name='gpt-3.5-turbo')
    llm = OpenAI(openai_api_key=OPENAI_API_KEY, temperature=0, model_name='text-davinci-003')
    prompt = PromptTemplate.from_template(template=template)
    chain = LLMChain(llm=llm, prompt=prompt)
    answer = papago.translate(chain.predict(content=texts), 'en', 'ko')
    print(f'answer : {answer}')
    print(type(answer))

    AnswerList = []

    for item in answer.split('Claim'):
        AnswerList.append(item)

    for answered in AnswerList:
        chatDisplay.insert(tk.END, f"챗봇: \n\n청구항요약:\n\n{answered.replace('claim', '청구항')}\n\n\n")

    for independentClaim, translatedClaim in zip(independentClaims, translatedClaims):
        chatDisplay.insert(tk.END, f"챗봇: \n{independentClaim}\n\n\n")
        chatDisplay.insert(tk.END, f"챗봇: \n{translatedClaim}\n\n\n")

    chatDisplay.config(state=tk.DISABLED)
    chatDisplay.see(tk.END)  # Scroll to the latest message


def sendMessageGPT():  # 채팅 메시지 입력
    message = userInput.get("1.0", "end-1c")  # Get user input
    chatDisplay.config(state=tk.NORMAL)
    chatDisplay.insert(tk.END, "사용자: " + message + "\n\n\n")
    result = kipris.getKiprisData(message)
    publicStatus = kipris.getPublicationStatus(result)
    claimContent = kipris.getClaimContent(result)
    inventionTitle = kipris.getInventionTitle(result)
    astractContent = kipris.getAstroContent(result)

    chatDisplay.config(state=tk.DISABLED)
    userInput.delete("1.0", tk.END)  # Clear the user input field

    # 챗봇 응답 시뮬레이션 (실제 챗봇 로직으로 대체)
    # 특허정보 관련( 특허명, 특허개요, 공고전문/공개전문여부)
    bot_response = ''

    chatDisplay.config(state=tk.NORMAL)
    bot_response = f"현재 이 특허는 {publicStatus}입니다.\n\n"  # 특허관련 요약 내용 추가
    chatDisplay.insert(tk.END, f"챗봇:\n\n{bot_response}\n")
    bot_response = f"특허명 : {inventionTitle}\n"
    chatDisplay.insert(tk.END, f"챗봇:\n\n{bot_response}\n")
    bot_response = f"특허개요 : {astractContent}\n"
    chatDisplay.insert(tk.END, f"챗봇:\n\n{bot_response}\n\n")

    # 청구항 원문 / 번역문
    independentClaims = []
    for patent in claimContent:
        claim = patent['claim']
        if claim.find("항에 있어서", 0, 30) == -1 and claim.find("삭제") == -1 and claim.find('항의') == -1 and claim.find(
                '청구항') == -1:  # and claim.find('에 있어서', 0, 30) == -1:
            independentClaims.append(claim)

    print(independentClaims)
    print(type(independentClaims))

    # 청구항 번역문
    translatedClaims = papago.translate(independentClaims, 'ko', 'en')
    print(translatedClaims)
    forGPTContent = ''
    for claim in translatedClaims:
        forGPTContent += ' ' + claim

    # tokenizer
    text_splitter = TokenTextSplitter(chunk_size=1000, chunk_overlap=0, length_function=len)
    texts = text_splitter.split_text(forGPTContent)
    # for item in texts:
    #     inputDataArr = {
    #         'content': item,
    #     }

    template = """
                        [start of document]
                        Document = {content}
                        [end of document]

                        [start of task intruction]
                        - only follow the output format defiend
                        - don't delete a claim in Document
                        - Briefly and Easily explain each claim in Document
                        [end of task instruction]

                        [output format start]
                        claim claim's number : briefly explained document.
                        [output format end]
                       """
    llm = OpenAI(openai_api_key=OPENAI_API_KEY, temperature=0, model_name='gpt-3.5-turbo')
    # llm = OpenAI(openai_api_key=OPENAI_API_KEY, temperature=0, model_name='text-davinci-003')
    prompt = PromptTemplate.from_template(template=template)
    chain = LLMChain(llm=llm, prompt=prompt)
    answer = papago.translate(chain.predict(content=texts), 'en', 'ko')
    print(f'answer : {answer}')
    print(type(answer))

    AnswerList = []

    for item in answer.split('Claim'):
        AnswerList.append(item)

    for answered in AnswerList:
        chatDisplay.insert(tk.END, f"챗봇: \n\n청구항요약:\n\n{answered.replace('claim', '청구항')}\n\n\n")

    for independentClaim, translatedClaim in zip(independentClaims, translatedClaims):
        chatDisplay.insert(tk.END, f"챗봇: \n{independentClaim}\n\n\n")
        chatDisplay.insert(tk.END, f"챗봇: \n{translatedClaim}\n\n\n")

    chatDisplay.config(state=tk.DISABLED)
    chatDisplay.see(tk.END)  # Scroll to the latest message


def sendMessageJp():  # 채팅 메시지 입력
    message = userInput.get("1.0", "end-1c")  # Get user input
    chatDisplay.config(state=tk.NORMAL)
    chatDisplay.insert(tk.END, "사용자: " + message + "\n\n\n")
    result = kipris.getKiprisData(message)
    publicStatus = kipris.getPublicationStatus(result)
    claimContent = kipris.getClaimContent(result)
    inventionTitle = kipris.getInventionTitle(result)
    astractContent = kipris.getAstroContent(result)

    chatDisplay.config(state=tk.DISABLED)
    userInput.delete("1.0", tk.END)  # Clear the user input field

    # 챗봇 응답 시뮬레이션 (실제 챗봇 로직으로 대체)
    # 특허정보 관련( 특허명, 특허개요, 공고전문/공개전문여부)
    bot_response = ''

    chatDisplay.config(state=tk.NORMAL)
    bot_response = f"현재 이 특허는 {publicStatus}입니다.\n\n"  # 특허관련 요약 내용 추가
    chatDisplay.insert(tk.END, f"챗봇:\n\n{bot_response}\n")
    bot_response = f"특허명 : {inventionTitle}\n"
    chatDisplay.insert(tk.END, f"챗봇:\n\n{bot_response}\n")
    bot_response = f"특허개요 : {astractContent}\n"
    chatDisplay.insert(tk.END, f"챗봇:\n\n{bot_response}\n\n")

    # 청구항 원문 / 번역문
    independentClaims = []
    for patent in claimContent:
        claim = patent['claim']
        if claim.find("항에 있어서", 0, 30) == -1 and claim.find("삭제") == -1 and claim.find('항의') == -1 and claim.find(
                '청구항') == -1:  # and claim.find('에 있어서', 0, 30) == -1:
            independentClaims.append(claim)

    print(independentClaims)
    print(type(independentClaims))

    # 청구항 번역문
    translatedClaims = papago.translate(papago.translate(independentClaims, 'ko', 'ja'), 'ja', 'en')
    print(translatedClaims)
    forGPTContent = ''
    for claim in translatedClaims:
        forGPTContent += ' ' + claim

    # tokenizer
    text_splitter = TokenTextSplitter(chunk_size=1000, chunk_overlap=0, length_function=len)
    texts = text_splitter.split_text(forGPTContent)
    # for item in texts:
    #     inputDataArr = {
    #         'content': item,
    #     }

    template = """
                        [start of document]
                        Document = {content}
                        [end of document]

                        [start of task intruction]
                        - only follow the output format defiend
                        - don't delete a claim in Document
                        - Briefly and Easily explain each claim in Document
                        [end of task instruction]

                        [output format start]
                        claim claim's number : briefly explained document.
                        [output format end]
                       """
    # llm = OpenAI(openai_api_key=OPENAI_API_KEY, temperature=0, model_name='gpt-3.5-turbo')
    llm = OpenAI(openai_api_key=OPENAI_API_KEY, temperature=0, model_name='text-davinci-003')
    prompt = PromptTemplate.from_template(template=template)
    chain = LLMChain(llm=llm, prompt=prompt)
    answer = papago.translate(chain.predict(content=texts), 'en', 'ko')
    print(f'answer : {answer}')
    print(type(answer))

    AnswerList = []

    for item in answer.split('Claim'):
        AnswerList.append(item)

    for answered in AnswerList:
        chatDisplay.insert(tk.END, f"챗봇: \n\n청구항요약:\n\n{answered.replace('claim', '청구항')}\n\n\n")

    for independentClaim, translatedClaim in zip(independentClaims, translatedClaims):
        chatDisplay.insert(tk.END, f"챗봇: \n{independentClaim}\n\n\n")
        chatDisplay.insert(tk.END, f"챗봇: \n{translatedClaim}\n\n\n")

    chatDisplay.config(state=tk.DISABLED)
    chatDisplay.see(tk.END)  # Scroll to the latest message


def sendMessageZh():  # 채팅 메시지 입력
    message = userInput.get("1.0", "end-1c")  # Get user input
    chatDisplay.config(state=tk.NORMAL)
    chatDisplay.insert(tk.END, "사용자: " + message + "\n\n\n")
    result = kipris.getKiprisData(message)
    publicStatus = kipris.getPublicationStatus(result)
    claimContent = kipris.getClaimContent(result)
    inventionTitle = kipris.getInventionTitle(result)
    astractContent = kipris.getAstroContent(result)

    chatDisplay.config(state=tk.DISABLED)
    userInput.delete("1.0", tk.END)  # Clear the user input field

    # 챗봇 응답 시뮬레이션 (실제 챗봇 로직으로 대체)
    # 특허정보 관련( 특허명, 특허개요, 공고전문/공개전문여부)
    bot_response = ''

    chatDisplay.config(state=tk.NORMAL)
    bot_response = f"현재 이 특허는 {publicStatus}입니다.\n\n"  # 특허관련 요약 내용 추가
    chatDisplay.insert(tk.END, f"챗봇:\n\n{bot_response}\n")
    bot_response = f"특허명 : {inventionTitle}\n"
    chatDisplay.insert(tk.END, f"챗봇:\n\n{bot_response}\n")
    bot_response = f"특허개요 : {astractContent}\n"
    chatDisplay.insert(tk.END, f"챗봇:\n\n{bot_response}\n\n")

    # 청구항 원문 / 번역문
    independentClaims = []
    for patent in claimContent:
        claim = patent['claim']
        if claim.find("항에 있어서", 0, 30) == -1 and claim.find("삭제") == -1 and claim.find('항의') == -1 and claim.find(
                '청구항') == -1:  # and claim.find('에 있어서', 0, 30) == -1:
            independentClaims.append(claim)

    print(independentClaims)
    print(type(independentClaims))

    # 청구항 번역문
    translatedClaims = papago.translate(papago.translate(independentClaims, 'ko', 'zh-CN'), 'zh-CN', 'en')
    print(translatedClaims)
    forGPTContent = ''
    for claim in translatedClaims:
        forGPTContent += ' ' + claim

    # tokenizer
    text_splitter = TokenTextSplitter(chunk_size=1000, chunk_overlap=0, length_function=len)
    texts = text_splitter.split_text(forGPTContent)
    # for item in texts:
    #     inputDataArr = {
    #         'content': item,
    #     }

    template = """
                        [start of document]
                        Document = {content}
                        [end of document]

                        [start of task intruction]
                        - only follow the output format defiend
                        - don't delete a claim in Document
                        - Briefly and Easily explain each claim in Document
                        [end of task instruction]

                        [output format start]
                        claim claim's number : briefly explained document.
                        [output format end]
                       """
    # llm = OpenAI(openai_api_key=OPENAI_API_KEY, temperature=0, model_name='gpt-3.5-turbo')
    llm = OpenAI(openai_api_key=OPENAI_API_KEY, temperature=0, model_name='text-davinci-003')
    prompt = PromptTemplate.from_template(template=template)
    chain = LLMChain(llm=llm, prompt=prompt)
    answer = papago.translate(chain.predict(content=texts), 'en', 'ko')
    print(f'answer : {answer}')
    print(type(answer))

    AnswerList = []

    for item in answer.split('Claim'):
        AnswerList.append(item)

    for answered in AnswerList:
        chatDisplay.insert(tk.END, f"챗봇: \n\n청구항요약:\n\n{answered.replace('claim', '청구항')}\n\n\n")

    for independentClaim, translatedClaim in zip(independentClaims, translatedClaims):
        chatDisplay.insert(tk.END, f"챗봇: \n{independentClaim}\n\n\n")
        chatDisplay.insert(tk.END, f"챗봇: \n{translatedClaim}\n\n\n")

    chatDisplay.config(state=tk.DISABLED)
    chatDisplay.see(tk.END)  # Scroll to the latest message

def sendMessageGPT_KO():  # 채팅 메시지 입력
    message = userInput.get("1.0", "end-1c")  # Get user input
    chatDisplay.config(state=tk.NORMAL)
    chatDisplay.insert(tk.END, "사용자: " + message + "\n\n\n")
    result = kipris.getKiprisData(message)
    publicStatus = kipris.getPublicationStatus(result)
    claimContent = kipris.getClaimContent(result)
    inventionTitle = kipris.getInventionTitle(result)
    astractContent = kipris.getAstroContent(result)

    chatDisplay.config(state=tk.DISABLED)
    userInput.delete("1.0", tk.END)  # Clear the user input field

    # 챗봇 응답 시뮬레이션 (실제 챗봇 로직으로 대체)
    # 특허정보 관련( 특허명, 특허개요, 공고전문/공개전문여부)
    bot_response = ''

    chatDisplay.config(state=tk.NORMAL)
    bot_response = f"현재 이 특허는 {publicStatus}입니다.\n\n"  # 특허관련 요약 내용 추가
    chatDisplay.insert(tk.END, f"챗봇:\n\n{bot_response}\n")
    bot_response = f"특허명 : {inventionTitle}\n"
    chatDisplay.insert(tk.END, f"챗봇:\n\n{bot_response}\n")
    bot_response = f"특허개요 : {astractContent}\n"
    chatDisplay.insert(tk.END, f"챗봇:\n\n{bot_response}\n\n")

    # 청구항 원문 / 번역문
    independentClaims = []
    for patent in claimContent:
        claim = patent['claim']
        if claim.find("항에 있어서", 0, 30) == -1 and claim.find("삭제") == -1 and claim.find('항의') == -1 and claim.find(
                '청구항') == -1:  # and claim.find('에 있어서', 0, 30) == -1:
            independentClaims.append(claim)

    print(independentClaims)
    print(type(independentClaims))

    # 청구항 번역문
    translatedClaims = papago.translate(independentClaims, 'ko', 'en')
    print(translatedClaims)
    forGPTContent = ''
    for claim in translatedClaims:
        forGPTContent += ' ' + claim

    # tokenizer
    text_splitter = TokenTextSplitter(chunk_size=1000, chunk_overlap=0, length_function=len)
    texts = text_splitter.split_text(forGPTContent)
    # for item in texts:
    #     inputDataArr = {
    #         'content': item,
    #     }

    template = """
                        [start of document]
                        Document = {content}
                        [end of document]

                        [start of task intruction]
                        - only follow the output format defiend
                        - don't delete a claim in Document
                        - Briefly and Easily explain each claim in Document
                        - Output language is Korean
                        [end of task instruction]

                        [output format start]
                        claim claim's number : briefly explained document.
                        [output format end]
                       """
    llm = OpenAI(openai_api_key=OPENAI_API_KEY, temperature=0, model_name='gpt-3.5-turbo')
    # llm = OpenAI(openai_api_key=OPENAI_API_KEY, temperature=0, model_name='text-davinci-003')
    prompt = PromptTemplate.from_template(template=template)
    chain = LLMChain(llm=llm, prompt=prompt)
    answer = chain.predict(content=texts)
    print(f'answer : {answer}')
    print(type(answer))

    AnswerList = []

    for item in answer.split('Claim'):
        AnswerList.append(item)

    for answered in AnswerList:
        chatDisplay.insert(tk.END, f"챗봇: \n\n청구항요약:\n\n{answered.replace('claim', '청구항')}\n\n\n")

    for independentClaim, translatedClaim in zip(independentClaims, translatedClaims):
        chatDisplay.insert(tk.END, f"챗봇: \n{independentClaim}\n\n\n")
        chatDisplay.insert(tk.END, f"챗봇: \n{translatedClaim}\n\n\n")

    chatDisplay.config(state=tk.DISABLED)
    chatDisplay.see(tk.END)  # Scroll to the latest message


def clearMessage():  # 채팅메시지 클리어
    chatDisplay.config(state=tk.NORMAL)
    chatDisplay.delete("1.0", tk.END)
    chatDisplay.config(state=tk.DISABLED)
    chatDisplay.see(tk.END)


# winodw
window = tk.Tk()
window.title("챗봇 GUI")
window.geometry("640x900+100+100")
chatFrame = LabelFrame(window, text="정보 내역", padx=0, pady=5)
chatFrame.pack(fill=tk.BOTH, expand=True)

chatDisplay = Text(chatFrame, wrap=tk.WORD, width=640, height=700, spacing2=15, font=('Pretendard', 12), padx=10,
                   pady=10, state=tk.DISABLED)
chatDisplay.pack(fill=tk.BOTH, expand=True)

scrollbar = Scrollbar(chatDisplay, command=chatDisplay.yview, orient=VERTICAL, highlightbackground='red')
scrollbar.pack(side=RIGHT, fill=tk.BOTH)
chatDisplay.config(yscrollcommand=scrollbar.set, relief='groove')

inputFrame = LabelFrame(window, text="특허번호 입력", font=('Pretendard', 12), width=640, height=20, padx=3, pady=3)
inputFrame.pack(fill=tk.BOTH)

userInput = Text(inputFrame, wrap=tk.WORD, width=640, height=1)
userInput.pack(fill=tk.X, expand=True)

init()  # 처음 인사말 세팅

send_button = tk.Button(inputFrame, text="TEXT-DAVINCI-003", command=sendMessage)
send_button.pack(side=tk.LEFT, padx=5)

send_button2 = tk.Button(inputFrame, text="GPT-TURBO-3.5", command=sendMessageGPT)
send_button2.pack(side=tk.LEFT, padx=5)

send_button2 = tk.Button(inputFrame, text="OUTPUT IS KO", command=sendMessageGPT_KO)
send_button2.pack(side=tk.LEFT, padx=5)

clear_button = tk.Button(inputFrame, text="초기화", command=clearMessage)
clear_button.pack(side=tk.LEFT, padx=5)

Jp_button = tk.Button(inputFrame, text="일본어 번역", command=sendMessageJp)
Jp_button.pack(side=tk.LEFT, padx=5)
Zh_button = tk.Button(inputFrame, text="중국어 번역", command=sendMessageZh)
Zh_button.pack(side=tk.LEFT, padx=5)

window.mainloop()
