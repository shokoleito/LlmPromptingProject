import copy
import json
import csv
import requests
import time
import pandas as pd

URL = open('URL.txt', 'r').read()

with open('HEADERS.json', 'r') as f:
    HEADERS = json.load(f)

with open('STRUCTURE.json', 'r') as f:
    STRUCTURE = json.load(f)

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

def test(test_file):
    test_cases = pd.read_csv(test_file, encoding='utf-8')
    test_cases[['pred_intent', 'time']] = test_cases['user_input'].apply(
        lambda x: send_request(URL, HEADERS, STRUCTURE, ROUTING_PROMPT, x) if isinstance(x, str) else (None, 0)).apply(
        pd.Series)
    test_cases['is_true'] = (test_cases['pred_intent'] == test_cases['expected_intent'])
    test_cases.to_csv(test_file+'_output.csv', index=False, header=False)
    return test_cases, test_cases.groupby('pred_intent')['is_true'].mean() * 100

def main():
    # prompt = open('TRANSLATION.txt', 'r', encoding='utf-8').read()
    _, res = test(test_file='film_qna_testcases.csv')
    print(res)
    # send_request(URL, HEADERS, STRUCTURE, ROUTING_PROMPT, 'gợi ý phim giống tây du ký')
    # send_request(URL, HEADERS, STRUCTURE, prompt, 'Deng Chan Yu')
    # send_request(URL, HEADERS, STRUCTURE, EXTRACT_WEATHER_QUERY_PROMPT, 'Thời tiết 5h chiều nay ở Hoàn Kiếm có nóng không?')

if __name__ == '__main__':
    main()
