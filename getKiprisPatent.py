# api 관련 모듈
import requests
import xmltodict
import json

# .env
from dotenv import load_dotenv
import os

# load .env
load_dotenv()

# API KEY
KIPRIS_API_KEY = os.environ.get("KIPRIS_API_KEY")


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
            # print(result)
            return applicationNum
        except Exception as ex:
            return inputNumber
    else:
        return 0


# 특허 데이터 받는 함수
def getKiprisData(inputNumber):
    try:
        classifiedInputNumber = classifyInputNum(inputNumber)  # 출원번호 : 1020230008327 , 등록번호 : 1025569250000
        print(classifiedInputNumber)
        applicationUrl = f"http://plus.kipris.or.kr/kipo-api/kipi/patUtiModInfoSearchSevice/getBibliographyDetailInfoSearch?applicationNumber={classifiedInputNumber}&ServiceKey={KIPRIS_API_KEY}"

        # applicationUrl, registrationUrl 선택해서 들어가기
        # resultCode = 00 -> 성공, 99 -> 실패
        response = requests.get(applicationUrl)
        contents = response.text
        print(contents)
        # xml -> dick 형대로 변경
        result = xmltodict.parse(contents)
        return result
    except Exception as ex:
        print(ex)
        return ""


# 특허 공개전문/ 공고전문인지 확인하는 함수
def getPublicationStatus(result):
    # result = getKiprisData(inputNumber)
    # 공고번호
    publicationDate = result['response']['body']['item']['biblioSummaryInfoArray']['biblioSummaryInfo'][
        'publicationDate']
    print(f'공고일자 : {publicationDate}')
    publicationStatus = ''
    if publicationDate is None:
        publicationStatus = '공개전문'
    elif publicationDate is not None:
        publicationStatus = '공고전문'
    return publicationStatus


# 해당 특허의 청구항 얻는 함수
def getClaimContent(result):
    # result = getKiprisData(inputNumber)
    # 청구항
    claimContent = result['response']['body']['item']['claimInfoArray']['claimInfo']
    return claimContent


# 해당 특허의 명칭 얻는 함수
def getInventionTitle(result):
    # result = getKiprisData(inputNumber)
    # 발명 제목
    inventionTitle = result['response']['body']['item']['biblioSummaryInfoArray']['biblioSummaryInfo']['inventionTitle']
    return inventionTitle


# 해당 특허의 개요 얻는 함수
def getAstroContent(result):
    # result = getKiprisData(inputNumber)
    # 발명 개요
    astrtContent = result['response']['body']['item']['abstractInfoArray']['abstractInfo']['astrtCont']
    return astrtContent
