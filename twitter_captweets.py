import csv, time, dateutil, requests, pandas as pd
from config import TOKEN
from dateutil import parser

counts_url = "https://api.twitter.com/2/tweets/counts/all"

start_time = '2021-09-01T00:00:00.000Z'
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
                    'tweet.fields': 'id,text,author_id,created_at',
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

        # 4. Tweet ID
        tweet_id = tweet['id']
        # 8. Tweet text
        text = tweet['text']

        
        # Assemble all data in a list
        res = [tweet_id,  created_at, text, author_id]
        
        # Append the result to the CSV file
        csvWriter.writerow(res)
        counter += 1

    # When done, close the CSV file
    csvFile.close()

    # Print the number of tweets for this iteration
    print("# of Tweets added from this response: ", counter) 

bearer_token = TOKEN
headers = create_headers(bearer_token)
keyword = "(@FashionNova -is:retweet) lang:en"
start_list =    ['2022-03-23T00:00:00.000Z']

end_list =      ['2022-03-25T23:00:00.000Z']
max_results = 100

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
    # #Total number of tweets we collected from the loop
    total_tweets = 0

    # Create file
    csvFile = open("data.csv", "a", newline="", encoding='utf-8')
    csvWriter = csv.writer(csvFile)

    #Create headers for the data you want to save, in this example, we only want save these columns in our dataset
    csvWriter.writerow(['tweet_id', 'created_at', 'text','author_id'])
    csvFile.close()

    for i in range(0,len(start_list)):

        # Inputs
        count = 0 # Counting tweets per time period
        flag = True
        next_token = None
        
        # Check if flag is true
        while flag:
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

search_tweets()