import json
import os
import matplotlib.pyplot as plt
import numpy as np
import googleapiclient.discovery

queries = ['페미', '안티페미', '여성주의', '반여성주의', '페미니즘', '안티페미니즘']
transliterated = {'페미' : 'Pheymi', '안티페미' : 'Anthipheymi', '여성주의' : 'Yesengcwuuy', '반여성주의' : 'Panyesengcwuuy', '페미니즘' : 'Pheyminicum', '안티페미니즘' : 'Anthipheyminicum'}

def parse_data():
    data = {'페미' : [], '안티페미' : [], '여성주의' : [], '반여성주의' : [], '페미니즘' : [], '안티페미니즘' : []}
    for i, filename in enumerate(os.listdir('raw_data')):
        with open('raw_data/' + filename, "r") as f:
            for line in f:
                parsed = json.loads(line)
                if parsed not in data[queries[i]]:
                    parsed['query'] = queries[i]
                    data[queries[i]].append(parsed)
    return data

def combine_data(data):
    added_ids = []
    combined = []
    for query in data:
        for result in data[query]:
            values = result[list(result.keys())[0]]
            if values['video_id'] not in added_ids:
                added_ids.append(values['video_id'])
                combined.append(result)
    return sorted(combined, key=lambda x : x[list(x.keys())[0]]['date_published'])

def plot_query_sizes(data):
    plt.figure(figsize=(12, 6))
    plt.title("Sample Sizes of Query Results")
    plt.ylabel("Number")
    plt.bar(np.array(list(transliterated.values())), np.array([len(data[val]) for val in data]), color='orange')
    
    #plt.show()
    #plt.savefig('images/queries.png')

def add_statistics(data):
    video_ids = [val[list(val.keys())[0]]['video_id'] for val in data]
    # API information
    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = 'AIzaSyBVZgLhciLiceJzE1mRIynS0Y_TpF-fZHo'
    # API client
    youtube = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey = DEVELOPER_KEY)
    for i, val in enumerate(video_ids):
        request = youtube.videos().list(
            part='id,statistics,contentDetails',
            id=str(val),
        )
        response = request.execute()
        current_video = data[i][list(data[i].keys())[0]]
        if response['items'] == []:
            continue
        assert current_video['video_id'] == response['items'][0]['id']
        current_video['duration'] = response['items'][0]['contentDetails']['duration'].replace('PT', '')
        current_video['views'] = response['items'][0]['statistics']['viewCount']
        if 'likeCount' in response['items'][0]['statistics']:
            current_video['likes'] = response['items'][0]['statistics']['likeCount']
        if 'favoriteCount' in response['items'][0]['statistics']:
            current_video['favorites'] = response['items'][0]['statistics']['favoriteCount']
        if 'commentCount' in response['items'][0]['statistics']:
            current_video['comments'] = response['items'][0]['statistics']['commentCount']

def main():
    data_by_query = parse_data()
    plot_query_sizes(data_by_query)
    #combined_data = combine_data(data_by_query)
    #add_statistics(combined_data)
    # with open('videos.json', 'w') as f:
    #     f.write(json.dumps(combined_data, ensure_ascii=False))

main()


    
