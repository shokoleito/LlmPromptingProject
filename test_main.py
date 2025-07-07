import copy
import json
import csv
import requests
import time
import pandas as pd

URL = 'https://aihub.vietteltelecom.vn:8443/api/llm/test-prompt'

HEADERS = {
    'Content-Type': 'application/json',
    'x-api-key': 'CjuiGkZSLSyxWspiQaRfiA',
    'Cookie': 'JSESSIONID=1482DC461E653ED54CE029D985F5B8B2'
}

STRUCTURE = {
    'max_tokens': 100,
    'temperature': 0.0,
    'stream': False,
    'model': 'Qwen2.5-14B-Instruct',
    'messages': [
        {
            'role': 'system',
            'content': ''
        },
        {
            'role': 'user',
            'content': ''
        }
    ]
}

ROUTING_PROMPT = open('ROUTING_PROMPT_AIBOX.txt', 'r', encoding='utf-8').read()
COMMON_EXTRACT_PROMPT = open('COMMON_EXTRACT_PROMPT.txt', 'r', encoding='utf-8').read()
CHANNEL_EXTRACT_PROMPT = open('CHANNEL_EXTRACT_PROMPT.txt', 'r', encoding='utf-8').read()
GOLD_PRICE_EXTRACT_PROMPT = open('EXTRACT_GOLD_PRICE_PROMPT.txt', 'r', encoding='utf-8').read()
EXTRACT_WEATHER_QUERY_PROMPT = open('EXTRACT_WEATHER_QUERY_PROMPT.txt', 'r', encoding='utf-8').read()

def send_request(url_route, header, data, prompt_type, query):
    tmp = copy.deepcopy(data)
    tmp['messages'][0]['content'] = prompt_type
    tmp['messages'][1]['content'] = query
    # print(tmp)

    try:
        start = time.time()
        response = requests.post(url=url_route, headers=header, json=tmp)
        duration = time.time() - start
        response.raise_for_status()

        if response.status_code == 200:
            res_json = response.json()
            print(f"Status Code: 200")
            print(f"Response JSON: {res_json}")
            print(f"Time: {duration:.3f}s")
            return res_json.get('intent'), duration
        else:
            print(f"Unexpected Status Code: {response.status_code}")
            print(f"Response Text: {response.text}")
            return None, 0
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None, 0

def test():
    test_cases = pd.read_csv('full_intent_20each.csv', encoding='utf-8')
    test_cases[['pred_intent', 'time']] = test_cases['user_input'].apply(
        lambda x: send_request(URL, HEADERS, STRUCTURE, ROUTING_PROMPT, x) if isinstance(x, str) else (None, 0)).apply(
        pd.Series)
    test_cases['is_true'] = (test_cases['pred_intent'] == test_cases['expected_intent'])
    test_cases.to_csv('test_output.txt', index=False, header=False)

def main():
    prompt = open('TRANSLATION.txt', 'r', encoding='utf-8').read()
    # test()
    # test_cases = pd.read_csv('full_intent_20each.csv', encoding='utf-8')
    # test_case['pred_intent'] = test_cases['user_input'].apply(lambda x: send_request(URL, HEADERS, STRUCTURE, ROUTING_PROMPT, x)[0] if isinstance(x, str) else 0)
    # test_case['time'] = test_cases['user_input'].apply(lambda x: send_request(URL, HEADERS, STRUCTURE, ROUTING_PROMPT, x)[1])
    # test_cases[['pred_intent', 'time']] = test_cases['user_input'].apply(lambda x: send_request(URL, HEADERS, STRUCTURE, ROUTING_PROMPT, x) if isinstance(x, str) else (None, 0)).apply(pd.Series)
    # test_cases['is_true'] = (test_cases['pred_intent'] == test_cases['expected_intent'])
    # test_cases.to_csv('test_output.txt', index=False, header=False)
    send_request(URL, HEADERS, STRUCTURE, ROUTING_PROMPT, 'gợi ý phim giống tây du ký')

    # send_request(URL, HEADERS, STRUCTURE, prompt, 'Deng Chan Yu')
    # send_request(URL, HEADERS, STRUCTURE, EXTRACT_WEATHER_QUERY_PROMPT, 'Thời tiết 5h chiều nay ở Hoàn Kiếm có nóng không?')
if __name__ == '__main__':
    main()
