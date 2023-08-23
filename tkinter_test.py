import tkinter as tk
from tkinter import LabelFrame, Label, Scrollbar, Text, VERTICAL, RIGHT, Y

# kipris data 받아오기 => 단위모듈화 작업
# langchain chatbot 형태로 변경하기
#

def send_message():
    message = user_input.get("1.0", "end-1c")  # Get user input
    chat_display.config(state=tk.NORMAL)
    chat_display.insert(tk.END, "사용자: " + message + "\n")
    chat_display.config(state=tk.DISABLED)
    user_input.delete("1.0", tk.END)  # Clear the user input field

    # 챗봇 응답 시뮬레이션 (실제 챗봇 로직으로 대체)
    bot_response = "안녕하세요! 무엇을 도와드릴까요?\n" # 특허관련 요약 내용 추가

    chat_display.config(state=tk.NORMAL)
    chat_display.insert(tk.END, "챗봇: " + bot_response + "\n")
    chat_display.config(state=tk.DISABLED)
    chat_display.see(tk.END)  # Scroll to the latest message


window = tk.Tk()
window.title("챗봇 GUI")
window.geometry("640x600+100+100")
chat_frame = LabelFrame(window, text="채팅 내역", padx=10, pady=10)
chat_frame.pack(fill=tk.BOTH, expand=True)

chat_display = Text(chat_frame, wrap=tk.WORD, state=tk.DISABLED)
chat_display.pack(fill=tk.BOTH, expand=True)

scrollbar = Scrollbar(chat_frame, command=chat_display.yview, orient=VERTICAL)
scrollbar.pack(side=RIGHT, fill=Y)
chat_display.config(yscrollcommand=scrollbar.set, relief='flat')

input_frame = LabelFrame(window, text="메시지 입력", padx=10, pady=10)
input_frame.pack(fill=tk.BOTH, expand=True)

user_input = Text(input_frame, wrap=tk.WORD)
user_input.pack(fill=tk.X, expand=True)

send_button = tk.Button(input_frame, text="전송", command=send_message)
send_button.pack()

window.mainloop()