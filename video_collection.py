import googleapiclient.discovery
import json
from datetime import datetime

FILE_DIRECTORY = 'raw_data' # directory to store generated data
NUM_ITERATIONS = 100 # with 50 max results, generates maximum 50 * NUM_ITERATIONS total results per query
# API information
api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = 'na'
# API client
youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)
queries = ['페미', '안티페미', '여성주의', '반여성주의', '페미니즘', '안티페미니즘']
page_tokens = {query : None for query in queries}
for i in range(NUM_ITERATIONS):
        print("Processing iteration " + str(i) + " of " + str(NUM_ITERATIONS))
        query_num = 1
        for query in queries:
                with open("raw_data_test.json", "a") as f:
                        start_date = datetime.strptime("03/09/20 00:00:00", "%m/%d/%y %H:%M:%S")
                        end_date = datetime.strptime("03/09/24 00:00:00", "%m/%d/%y %H:%M:%S")
                        if not page_tokens[query] and i > 0:
                                continue
                        if not page_tokens[query]:
                                request = youtube.search().list(
                                        part='id,snippet',
                                        type='video',
                                        q=query,
                                        maxResults=50,
                                        relevanceLanguage='ko',
                                        regionCode='kr',
                                        publishedAfter=start_date.isoformat() + "Z",
                                        publishedBefore=end_date.isoformat() + "Z",
                                        order='viewCount',
                                        fields='nextPageToken,items(id(videoId),snippet(publishedAt,channelId,channelTitle,title,description))'
                                )
                        else:
                                request = youtube.search().list(
                                        part='id,snippet',
                                        type='video',
                                        q=query,
                                        maxResults=50,
                                        relevanceLanguage='ko',
                                        regionCode='kr',
                                        publishedAfter=start_date.isoformat() + "Z",
                                        publishedBefore=end_date.isoformat() + "Z",
                                        order='viewCount',
                                        pageToken=page_tokens[query],
                                        fields='nextPageToken,items(id(videoId),snippet(publishedAt,channelId,channelTitle,title,description))'
                                )
                        response = request.execute()
                        if 'nextPageToken' in response:
                                page_tokens[query] = response['nextPageToken']
                        else:
                                page_tokens[query] = None
                        for val in response['items']:
                                f.write(json.dumps({val['snippet']['title'] : {"video_id" : val['id']['videoId'], "channel_id" : val['snippet']['channelId'], \
                                                        "channel_title" : val['snippet']['channelTitle'], "date_published" : val['snippet']['publishedAt'].split("T")[0], \
                                                                "description" : val['snippet']['description'], "query" : query}}, ensure_ascii=False) + "\n")
                        query_num += 1
        print("Successfully processed iteration")
