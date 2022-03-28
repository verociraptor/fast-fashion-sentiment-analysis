import requests, os, json, time, pandas as pd
from datetime import datetime as dt
from config import TOKEN

bearer_token = TOKEN

search_url = "https://api.twitter.com/2/tweets/search/all"
counts_url = "https://api.twitter.com/2/tweets/counts/all"

start_time = '2022-01-01T00:00:00.000Z'
end_time = '2022-03-25T23:00:00.000Z'
# Optional params: start_time,end_time,since_id,until_id,max_results,next_token,
# expansions,tweet.fields,media.fields,poll.fields,place.fields,user.fields
search_query_params = {'query': '(@FashionNova -is:retweet) lang:en', 'start_time': start_time, 
                'end_time': end_time, 'expansions': 'author_id', 
                'user.fields': 'created_at', 'tweet.fields':'created_at', 
                'max_results':'100'}

counts_query_params = {'query': '(@FashionNova -is:retweet) lang:en', 'start_time': start_time, 
                'end_time': end_time, 'granularity': 'day'}


#https://api.twitter.com/2/tweets/search/recent?query=from:nfl&expansions=author_id&user.fields=created_at&tweet.fields=created_at

def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

def connect_to_endpoint(url, params):
    response = requests.get(url, auth=bearer_oauth, params=params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

def count_tweets():
    json_response = connect_to_endpoint(counts_url, counts_query_params)
    print(json.dumps(json_response, indent=4, sort_keys=True))
    print("Total count from " + start_time + " to " + end_time + " is:" + str(json_response['meta']['total_tweet_count']))

def search_tweets():
    all_tweets = []
    api_calls, total_api_calls = 0, 0
    earliest_timestamp = "2023-11-09T15:24:27.000Z" #some arbitrary timestamp a year in the future to satify the initial condition of line 43
    end_time = '2022-03-18T00:00:00.000Z'
    
    while earliest_timestamp > end_time:
        json_response = connect_to_endpoint(search_url, query_params)
        all_tweets += json_response['data']
        
        earliest_timestamp = json_response['data'][0]['created_at']
        print(earliest_timestamp)
        query_params['end_time'] = earliest_timestamp
        api_calls += 1
        total_api_calls += 1
        print(api_calls, total_api_calls)

        if api_calls == 180:
            print("API Limit Hit Time to Sleep for 15 seconds")
            print(dt.now().strftime("%H:%M:%S"))
            time.sleep(900)
            print("------DONE------")
            print(dt.now().strftime("%H:%M:%S"))
            api_calls = 0
            
            
    df = pd.DataFrame(all_tweets)
    df.to_csv("fashionnova_jan1_to_mar25_2022.csv")


count_tweets()