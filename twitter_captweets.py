import csv
import time, dateutil 
from dateutil import parser
import requests

counts_url = "https://api.twitter.com/2/tweets/counts/all"

start_time = '2022-01-01T00:00:00.000Z'
end_time = '2022-03-25T23:00:00.000Z'
counts_query_params = {'query': '(@FashionNova -is:retweet) lang:en', 'start_time': start_time, 
                'end_time': end_time, 'granularity': 'day'}

#Inputs for tweets
def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers

def create_url(keyword, start_date, end_date, max_results = 10):
    
    search_url = "https://api.twitter.com/2/tweets/search/all" #Change to the endpoint you want to collect data from

    #change params based on the endpoint you are using
    query_params = {'query': keyword,
                    'start_time': start_date,
                    'end_time': end_date,
                    'max_results': max_results,
                    'expansions': 'author_id,in_reply_to_user_id,geo.place_id',
                    'tweet.fields': 'id,text,author_id,in_reply_to_user_id,geo,conversation_id,created_at,lang,public_metrics,referenced_tweets,reply_settings,source',
                    'user.fields': 'id,name,username,created_at,description,public_metrics,verified',
                    'place.fields': 'full_name,id,country,country_code,geo,name,place_type',
                    'next_token': {}}
    return (search_url, query_params)

def connect_to_endpoint(url, headers, params, next_token = None):
    params['next_token'] = next_token   #params object received from create_url function
    response = requests.request("GET", url, headers = headers, params = params)
    print("Endpoint Response Code: " + str(response.status_code))
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

def append_to_csv(json_response, fileName):

    #A counter variable
    counter = 0

    #Open OR create the target CSV file
    csvFile = open(fileName, "a", newline="", encoding='utf-8')
    csvWriter = csv.writer(csvFile)

    #Loop through each tweet
    for tweet in json_response['data']:
        
        # We will create a variable for each since some of the keys might not exist for some tweets
        # So we will account for that

        # 1. Author ID
        author_id = tweet['author_id']

        # 2. Time created
        created_at = dateutil.parser.parse(tweet['created_at'])

        # 3. Geolocation
        if ('geo' in tweet):   
            geo = tweet['geo']['place_id']
        else:
            geo = " "

        # 4. Tweet ID
        tweet_id = tweet['id']

        # 5. Language
        lang = tweet['lang']

        # 6. Tweet metrics
        retweet_count = tweet['public_metrics']['retweet_count']
        reply_count = tweet['public_metrics']['reply_count']
        like_count = tweet['public_metrics']['like_count']
        quote_count = tweet['public_metrics']['quote_count']

        # 7. source
        source = tweet['source']

        # 8. Tweet text
        text = tweet['text']
        
        # Assemble all data in a list
        res = [author_id, created_at, geo, tweet_id, lang, like_count, quote_count, reply_count, retweet_count, source, text]
        
        # Append the result to the CSV file
        csvWriter.writerow(res)
        counter += 1

    # When done, close the CSV file
    csvFile.close()

    # Print the number of tweets for this iteration
    print("# of Tweets added from this response: ", counter) 

bearer_token = 'AAAAAAAAAAAAAAAAAAAAAMINawEAAAAAUhv%2BPsLsgvECBOlGK4MbOTcD4Xc%3DQ6tJRmkOfRxzA5aL4tZkYFewvcs2LIb1IbsoEZXhoaxhSchgpK'
headers = create_headers(bearer_token)
keyword = "(@FashionNova -is:retweet) lang:en"
start_list =    ['2022-01-01T00:00:00.000Z']

end_list =      ['2022-01-31T00:00:00.000Z']
max_results = 20

def count_tweets():
    total_count = 0
    flag = True
    next_token = None
    # Check if flag is true
    while flag:
        print("-----------------------------")
        json_response = connect_to_endpoint(counts_url, headers, counts_query_params, next_token)
        result_count = json_response['meta']['total_tweet_count']
        print("Count from " + json_response['data'][0]['start'] + " to " 
                + json_response['data'][len(json_response['data']) - 1]['end'] 
                + " is: " + str(result_count))
        # print("--------------------------------")
        # print(json_response)
        if 'next_token' in json_response['meta']:
            # Save the token to use for next call
            next_token = json_response['meta']['next_token']
            if result_count is not None and result_count > 0 and next_token is not None:
                total_count += result_count
                time.sleep(5)                
        # If no next token exists
        else:
            if result_count is not None and result_count > 0:
                total_count += result_count
                time.sleep(5)
            
            #Since this is the final request, turn flag to false to move to the next time period.
            flag = False
            next_token = None
        time.sleep(5)
    print("The total tweets from " + start_time + " to " + end_time + " is: " + str(total_count))


def search_tweets():
    #Total number of tweets we collected from the loop
    total_tweets = 0

    # Create file
    csvFile = open("data.csv", "a", newline="", encoding='utf-8')
    csvWriter = csv.writer(csvFile)

    #Create headers for the data you want to save, in this example, we only want save these columns in our dataset
    csvWriter.writerow(['author id', 'created_at', 'geo', 'id','lang', 'like_count', 'quote_count', 'reply_count','retweet_count','source','tweet'])
    csvFile.close()

    for i in range(0,len(start_list)):

        # Inputs
        count = 0 # Counting tweets per time period
        max_count = 100 # Max tweets per time period
        flag = True
        next_token = None
        
        # Check if flag is true
        while flag:
            # Check if max_count reached
            if count >= max_count:
                break
            print("-------------------")
            print("Token: ", next_token)
            url = create_url(keyword, start_list[i],end_list[i], max_results)
            json_response = connect_to_endpoint(url[0], headers, url[1], next_token)
            result_count = json_response['meta']['result_count']

            if 'next_token' in json_response['meta']:
                # Save the token to use for next call
                next_token = json_response['meta']['next_token']
                print("Next Token: ", next_token)
                if result_count is not None and result_count > 0 and next_token is not None:
                    print("Start Date: ", start_list[i])
                    append_to_csv(json_response, "data.csv")
                    count += result_count
                    total_tweets += result_count
                    print("Total # of Tweets added: ", total_tweets)
                    print("-------------------")
                    time.sleep(5)                
            # If no next token exists
            else:
                if result_count is not None and result_count > 0:
                    print("-------------------")
                    print("Start Date: ", start_list[i])
                    append_to_csv(json_response, "data.csv")
                    count += result_count
                    total_tweets += result_count
                    print("Total # of Tweets added: ", total_tweets)
                    print("-------------------")
                    time.sleep(5)
                
                #Since this is the final request, turn flag to false to move to the next time period.
                flag = False
                next_token = None
            time.sleep(5)
    print("Total number of results: ", total_tweets)

count_tweets()