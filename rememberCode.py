text = '청구항1에 기재된 전기자동차의 충전시스템을 집중제어하는 전자기기의 동작방법에 있어서, 상기 특정송신기로부터 상기 특정충전기의 준비통지메시지를 수신하여 충전정보를 생성하고, 상기 충전설정정보를 상기 특정충전기로 전송하는 것을 특징으로 하는 전기자동차의 충전시스템. 특정 충전기로부터 완료 알림 메시지가 수신되면 경고 메시지의 출력을 중지하도록 지정된 사용자 장치에도 경고 제어 명령을 전송합니다. 이 장치는 주차구역에 주차된 전기자동차의 전륜과 후륜 사이의 지면을 수직방향으로 상승시키거나, 주차장에 주차된 전기자동차의 전륜 또는 후륜 뒤의 지면에 수직방향으로 기립시킴으로써 제어되는 전기자동차의 이동을 제한하도록 되어 있다. 청구항7: 전기자동차 충전시스템을 집중제어하는 전자기기에서, 상기 장치는 적어도 하나의 충전기와 통신하는 통신부와, 상기 적어도 하나의 충전기에 배치된 전송커플러에 관한 정보를 저장하는 기억부와, 상기 특정 전송커플러 표준에 따라 충전방법을 결정하는 처리장치를 포함한다. 기억부는 전송 결합기의 각 규격에 대한 정보를 저장한다. 처리 장치가 병합된 것을 보냅니다.'
    text.replace('청구항', '1')
    print(text)
    splitedText = text.split('. ')
    print(splitedText)

    for text in splitedText:
        print(text.find('청구항'))
        if text.find('청구항') != -1:
            print(f'청구항 : {text}')
            print(text.find('청구항'))
            text.replace('청구항', '\n\n청구항', 1)
            text.replace('청구항', '[청구항]', 1)

        listbox1.insert(tk.END, text)

def chatTochatGPT():
    # llm = OpenAI(openai_api_key=OPENAI_API_KEY, temperature=0.9, model_name='text-davinci-003')

    # 프롬프트에 들어갈 내용
    prompt = promptTranslate(getKiprisData())

    # Token화
    # https://python.langchain.com/docs/modules/data_connection/document_transformers/text_splitters/character_text_splitter
    text_splitter = TokenTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_text(prompt)  # list

    # 메타데이터 삽입
    # metadatas = []
    # for i in range(0, len(texts)):
    #     metadatas.append({"document": i + 1})
    #     print(i)
    # document = text_splitter.create_documents(texts, metadatas=metadatas)
    # print(document)
    print(texts)
    print(len(texts))  # 1020190118445

    # OPEN EMBEDDING
    embeddings = OpenAIEmbeddings()
    # 크로마DB를 이용하여 텍스트를 벡터값으로 저장하는 과정
    docsearch = Chroma.from_texts(
        texts, embeddings, metadatas=[{"source": i} for i in range(1, len(texts) + 1)]
    )
    # 템플릿 구조
    query = "각 청구항 별로 순서대로 알기 쉽게 설명해줘!"
    docs = docsearch.similarity_search(query)

    template = """인간과 대화하는 챗봇입니다.

        아래의 긴 문서에서 추출된 일부 내용과 질문이 주어졌을 때, 최종 답변을 생성하세요.

        {context}

        {chat_history}
        사람: {human_input}
        챗봇:"""

    prompt = PromptTemplate(
        input_variables=["chat_history", "human_input", "context"], template=template
    )

    # 메모리 저장
    memory = ConversationBufferMemory(memory_key="chat_history", input_key="human_input")
    chain = load_qa_chain(
        OpenAI(temperature=0), chain_type="stuff", memory=memory, prompt=prompt
    )

    query = "각 청구항을 순서대로 알기 쉽게 설명해줘!"
    chain({"input_documents": docs, "human_input": query}, return_only_outputs=True)

    # 질문에 대한 답변 생성
    global displayContent
    displayContent = chain.memory.buffer
    print(displayContent)

    label.config(text=displayContent)

    # chain = load_summarize_chain(llm, chain_type="stuff", verbose=True)
    # innerContent1 = chain.run(document[0:3])

    # print(texts)
    # token = numTokensFromString(prompt, 'p50k_base')

    # 맥스토큰으로 배열 나누기
    def divideArrByNumToken(string: str, encoding_name: str, numToken: int, start: int, end: int):
        encoding = tik.get_encoding(encoding_name)
        txt_encoding = encoding.encode(string)
        divideArr = []
        if numToken > MAX_TOKEN:
            divideArr = txt_encoding[start:end]
            print(len(divideArr))
            print(encoding.decode(divideArr))
        return encoding.decode(divideArr)
        # text1 = divideArrByNumToken(prompt, 'p50k_base', token, 0, MAX_TOKEN)
        # text2 = divideArrByNumToken(prompt, 'p50k_base', token, MAX_TOKEN, MAX_TOKEN * 2)
        # text3 = divideArrByNumToken(prompt, 'p50k_base', token, MAX_TOKEN * 2, token)

    # 문자열 토큰으로 바꾸기
    def numTokensFromString(string: str, encoding_name: str) -> int:
        print('test')
        """Returns the number of tokens in a text string."""
        encoding = tik.get_encoding(encoding_name)
        # assert encoding.decode(encoding.encode(string)) == string, "에러임?"
        txt_encoding = encoding.encode(string)
        num_tokens = len(txt_encoding)
        print(num_tokens)
        return num_tokens

    def applicationNoChatGPT():
        try:
            llm = OpenAI(openai_api_key=OPENAI_API_KEY, temperature=0.1, model_name='text-davinci-003')
            ko_prompts = getKiprisData()
            # 프롬프트에 들어갈 특허관련 내용
            prompts = promptTranslate(ko_prompts, 'ko', 'en')
            print(prompts)
            # 토큰화 # 1020190118445
            text_splitter = TokenTextSplitter(chunk_size=1000, chunk_overlap=0, length_function=len)
            texts = text_splitter.split_text(prompts)
            print(len(texts))
            print(type(texts))

            # # 메타데이터 삽입
            # metadatas = []
            # for i in range(1, len(texts) + 1):
            #     metadatas.append({"document": i})
            # document = text_splitter.create_documents(texts, metadatas=metadatas)
            # print(len(document))
            # for i in document:
            #     print(f'document : {document}')

            # 프롬프트 템플릿
            template = """
                        you are a good patent consultant.
                        Briefly explain each claim,
                        you don't delete claim,
                       """
            prompt = PromptTemplate.from_template(template)

            chain = LLMChain(llm=llm, prompt=prompt)
            answer = promptTranslate(chain.run(texts), 'en', 'ko')
            # answer = chain.run(document)
            label3.config(text=answer, wraplength=1000)
        except Exception as ex:
            # label.config(text=f'{ex} : 에러가 발생했습니다.')
            label3.config(text='잘못 입력 하셨습니다, 출원번호를 입력 부탁 드립니다.')

            # 프롬프트 얻기
            def getPrompt():
                prompt = Entry.get()
                print(prompt)
                return str(prompt)
                # label.config(text=str(prompt))

            def promptTranslate(txt, src, dest):
                # 1020190118445
                translator = googletrans.Translator()
                result = translator.translate(txt, dest=dest, src=src)
                # print(txt)
                # print(result.text)
                return result.text