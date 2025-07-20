import copy
import json
import csv
import requests
import time
import pandas as pd

URL = open('./config/URL.txt', 'r').read()

with open('./config/HEADERS.json', 'r') as f:
    HEADERS = json.load(f)

with open('./config/STRUCTURE.json', 'r') as f:
    STRUCTURE = json.load(f)

ROUTING_PROMPT = open('./prompts/ROUTING_PROMPT_AIBOX.txt', 'r', encoding='utf-8').read()
COMMON_EXTRACT_PROMPT = open('./prompts/COMMON_EXTRACT_PROMPT.txt', 'r', encoding='utf-8').read()
PROGRAM_EXTRACT_PROMPT = open('./prompts/PROGRAM_EXTRACT_PROMPT.txt', 'r', encoding='utf-8').read()
GOLD_PRICE_EXTRACT_PROMPT = open('./prompts/EXTRACT_GOLD_PRICE_PROMPT.txt', 'r', encoding='utf-8').read()
EXTRACT_WEATHER_QUERY_PROMPT = open('./prompts/EXTRACT_WEATHER_QUERY_PROMPT.txt', 'r', encoding='utf-8').read()
EXTRACT_VOLUME_REDUCE = open('./prompts/EXTRACT_VOLUME.txt', 'r', encoding='utf-8').read()
EXTRACT_FORWARD = open('./prompts/EXTRACT_FORWARD_PROMPT.txt', 'r', encoding='utf-8').read()

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
    test_cases = pd.read_csv('./tests/'+test_file+'.csv', encoding='utf-8')
    test_cases[['pred_intent', 'time']] = test_cases['user_input'].apply(
        lambda x: send_request(URL, HEADERS, STRUCTURE, ROUTING_PROMPT, x) if isinstance(x, str) else (None, 0)).apply(
        pd.Series)
    test_cases['is_true'] = (test_cases['pred_intent'] == test_cases['expected_intent'])
    test_cases.to_csv('./tests/'+test_file+'_output.csv', index=False, header=False)
    accuracy = test_cases.groupby('expected_intent')['is_true'].mean().reset_index()
    accuracy.columns = ['expected_intent', 'accuracy']
    accuracy.to_csv('./tests/'+test_file+'_accuracy.csv', index=False)

def main():
    # prompt = open('TRANSLATION.txt', 'r', encoding='utf-8').read()
    send_request(URL, HEADERS, STRUCTURE, ROUTING_PROMPT, 'hôm nay tôi buồn quá, bạn giúp tôi vui lên được không')
    # send_request(URL, HEADERS, STRUCTURE, EXTRACT_VOLUME_REDUCE, 'tiếng to quá tôi muốn giảm xuống mức 10%')
    # test(test_file='full_test_intent')

    # send_request(URL, HEADERS, STRUCTURE, ROUTING_PROMPT, 'Bật kênh chiếu phim Thương ngày nắng về')
    # send_request(URL, HEADERS, STRUCTURE, prompt, 'Deng Chan Yu')
    # send_request(URL, HEADERS, STRUCTURE, EXTRACT_WEATHER_QUERY_PROMPT, 'Thời tiết 5h chiều nay ở Hoàn Kiếm có nóng không?')
    # send_request(URL, HEADERS, STRUCTURE, ROUTING_PROMPT, 'diễn viên phương anh đào đóng phim nào?')

if __name__ == '__main__':
    main()
