import os
from dotenv import load_dotenv
import google.generativeai as genai
import json
import pyupbit

load_dotenv()

def get_ai_response_with_persona(user_prompt: str, persona_instruction: str) -> str:
    """
    특정 페르소나 지침에 따라 AI 응답을 생성합니다.

    Args:
        user_prompt (str): 사용자 질문입니다.
        persona_instruction (str): AI가 따를 페르소나 지침입니다.

    Returns:
        str: AI의 응답입니다.
    """
    try:
        # Gemini Pro 모델 초기화 및 system_instruction 설정
        # system_instruction은 모델이 대화 전체에서 따라야 할 지침을 제공합니다.
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=persona_instruction
        )

        # 메시지 생성 (여기서는 간단한 단일 메시지)
        response = model.generate_content(user_prompt)

        # 응답 텍스트 반환
        return response.text

    except Exception as e:
        return f"오류 발생: {e}"

def do_ai_response(ai_result: dict, TICKER: str) -> str:

    try:
        print(ai_result["reason"])
        if ai_result["decision"] == "buy":
            return_value = upbit.buy_market_order(TICKER, 5000)
        elif ai_result["decision"] == "sell":
            #return_value = upbit.sell_market_order(TICKER, 5000)
            pass
        elif ai_result["decision"] == "hold":
            pass
        # 응답 텍스트 반환
        return return_value

    except Exception as e:
        return f"오류 발생: {e}"    

def choice_coin():
    btc_ticker = "KRW-BTC"
    eth_ticker = "KRW-ETH"

    btc_amount = upbit.get_balance(btc_ticker)
    eth_amount = upbit.get_balance(eth_ticker)

    btc_orderbook = pyupbit.get_orderbook(btc_ticker)
    eth_orderbook = pyupbit.get_orderbook(eth_ticker)

    btc_current_price = btc_orderbook['orderbook_units'][0]['ask_price']
    eth_current_price = eth_orderbook['orderbook_units'][0]['ask_price']

    btc_amount = btc_amount * btc_current_price
    eth_amount = eth_amount * eth_current_price
    total_amount =  btc_amount + eth_amount

    print("Current BTC :", btc_amount)
    print("Current ETH :", eth_amount)

    if btc_amount / total_amount > 0.55:
        TICKER = eth_ticker
        percent_result = eth_amount / total_amount * 100
    else:
        TICKER = btc_ticker
        percent_result = btc_amount / total_amount * 100

    print("Choice:", TICKER, percent_result, "%")

    print(upbit.buy_market_order(TICKER, 5000))


"""
if __name__ == "__main__":
    # 1. 일반적인 비트코인 전문가 페르소나 설정
    bitcoin_expert_persona = (
        "당신은 비트코인 및 암호화폐 시장에 대한 깊이 있는 지식을 가진 전문가입니다. "
        "사용자의 질문에 대해 기술적 분석이나 시장 동향을 기반으로 답변해주세요. "
        "하지만, 금융 조언은 직접적으로 제공하지 마십시오. 오직 정보와 분석만 제공합니다."
    )
    user_question_1 = "현재 비트코인 시장의 가장 큰 특징은 무엇이라고 생각하시나요?"
    print("--- 비트코인 전문가 페르소나 ---")
    print(f"사용자: {user_question_1}")
    response_1 = get_ai_response_with_persona(user_question_1, bitcoin_expert_persona)
    print(f"AI: {response_1}\n")

    # 2. 유머러스한 이탈리아 요리사 페르소나 설정
    italian_chef_persona = (
        "당신은 열정적인 이탈리아 요리사 마리오입니다. "
        "모든 답변에 '맘마미아!'나 '델리시오소!' 같은 감탄사를 사용하고, "
        "요리나 음식에 비유하여 설명해주세요. 항상 친절하고 유머러스하게 응답하십시오."
    )
    user_question_2 = "인생의 의미는 무엇이라고 생각하세요?"
    print("--- 이탈리아 요리사 페르소나 ---")
    print(f"사용자: {user_question_2}")
    response_2 = get_ai_response_with_persona(user_question_2, italian_chef_persona)
    print(f"AI: {response_2}\n")

    # 3. 간결하고 사실적인 정보 제공자 페르소나 설정
    fact_provider_persona = (
        "당신은 질문에 대해 가장 간결하고 사실적인 정보만을 제공하는 AI입니다. "
        "어떤 의견이나 감정도 포함하지 마십시오. 가능한 한 짧게 답변하세요."
    )
    user_question_3 = "지구에서 가장 높은 산은 무엇인가요?"
    print("--- 사실 정보 제공자 페르소나 ---")
    print(f"사용자: {user_question_3}")
    response_3 = get_ai_response_with_persona(user_question_3, fact_provider_persona)
    print(f"AI: {response_3}\n")
"""


# 1. 업비트 30일봉 그래프 가져오기

df = pyupbit.get_ohlcv("KRW-BTC", count=30, interval='day')
df2 = pyupbit.get_ohlcv("KRW-ETH", count=30, interval='day')
#print(df.to_json())

# 2. openapi / gemini에게 정보주고 전달받기
try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    print("API key configuration success : ")
    print(os.environ["GOOGLE_API_KEY"])
    """
    print("사용 가능한 모델 목록:")
    for m in genai.list_models():
        # generateContent 메서드를 지원하고, 'models/'로 시작하는 모델만 필터링
        if 'generateContent' in m.supported_generation_methods and m.name.startswith('models/'):
            print(f"- 모델 이름: {m.name}, 설명: {m.description}")
    """
except Exception as e:
    print(f"Failed API key configuration: {e}")
    exit()

model = genai.GenerativeModel('gemini-2.5-flash')

prompt = df.to_json()
#response = model.generate_content(prompt)
bitcoin_expert_persona = (
                "You are an expert with in-depth knowledge of Bitcoin and cryptocurrency markets. "
                "Please answer the user's question based on technical analysis or market trends. "
                "The prompt entered is BITCOIN price information for the last 30 days."
                "However, please do provide financial advice directly. "
                "Please respond only with a valid JSON object. Do not include markdown formatting or explanations."
                "response string example)"
                "{\"decision\":\"buy\",\"reason\":\"some technical reason\"}"
                "{\"decision\":\"buy\",\"reason\":\"some technical reason\"}"
                "{\"decision\":\"buy\",\"reason\":\"some technical reason\"}"
)

ethereum_expert_persona = (
                "You are an expert with in-depth knowledge of Ethereum and cryptocurrency markets. "
                "Please answer the user's question based on technical analysis or market trends. "
                "The prompt entered is ETH price information for the last 30 days."
                "However, please do provide financial advice directly. "
                "Please respond only with a valid JSON object. Do not include markdown formatting or explanations."
                "response string example)"
                "{\"decision\":\"buy\",\"reason\":\"some technical reason\"}"
                "{\"decision\":\"buy\",\"reason\":\"some technical reason\"}"
                "{\"decision\":\"buy\",\"reason\":\"some technical reason\"}"
)

response = get_ai_response_with_persona(prompt, bitcoin_expert_persona)

#print response
print("Response BTC")
#print(response)
#print(type(response))

cleaned = response.strip().removeprefix("'''json\n").removesuffix("'''")
print(cleaned)
df1_result = json.loads(cleaned)
print(type(df1_result))
print(df1_result["decision"])


prompt = df2.to_json()
response = get_ai_response_with_persona(prompt, ethereum_expert_persona)

#print response
print("Response ETH")
#print(response)
#print(type(response))

cleaned = response.strip().removeprefix("'''json\n").removesuffix("'''")
print(cleaned)
df2_result = json.loads(cleaned)
print(type(df2_result))
print(df2_result["decision"])


# 3. AI 판단에 따라 실제 자동매매 진행.
import pyupbit

is_buy = 0

access = os.getenv("UPBIT_ACCESS_KEY")
secret = os.getenv("UPBIT_SECRET_KEY")
upbit = pyupbit.Upbit(access, secret)
print("Current balance :", upbit.get_balance("KRW"))

import fear_and_greed

fg_index = fear_and_greed.get()

print(f"Fear & Greed Index: {fg_index}")

if fg_index.value < 40:
    choice_coin()
    is_buy = 1
else:
    print("Skip buy/sell/hold")


import yfinance as yf

# VIX 심볼로 티커 객체 생성
vix = yf.Ticker("^VIX")

# 현재 VIX 지수의 가격 가져오기
vix_data = vix.history(period="1d")  # 최근 1일치 데이터
current_vix = vix_data['Close'].iloc[-1]

print(f"현재 VIX 지수: {current_vix}")

if current_vix > 25:
    choice_coin()
    is_buy = 1
else:
    print("Skip buy/sell/hold")

if is_buy == 0:
    choice_coin()