import json
import googleapiclient.discovery

def get_video_ids():
    video_ids = []
    with open("videos.json", "r") as f:
        videos_list = json.loads(f.readlines()[0])
        for video in videos_list:
            video_ids.append(video[list(video.keys())[0]]['video_id'])
    return video_ids

def get_comments(ids):
    # API information
    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = 'AIzaSyBVZgLhciLiceJzE1mRIynS0Y_TpF-fZHo'
    # API client
    youtube = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey = DEVELOPER_KEY)
    comments = {val : [] for val in ids}
    for val in ids:
        request = youtube.commentThreads().list(
            part='id,snippet',
            videoId=val,
            maxResults=100,
            order='relevance',
            textFormat='plainText'
        )
        try:
            response = request.execute()
        except:
            continue
        if response['items'] == []:
            continue
        for item in response['items']:
            comments[val].append({'comment' : item['snippet']['topLevelComment']['snippet']['textDisplay'], \
                            'likes' : item['snippet']['topLevelComment']['snippet']['likeCount'], \
                                'reply_count' : item['snippet']['totalReplyCount']})
    return comments

def write_comments(comments):
    with open('comments.json', 'w') as f:
        f.write(json.dumps(comments, ensure_ascii=False))
def main():
    ids = get_video_ids()
    comments = get_comments(ids)
    write_comments(comments)
main()