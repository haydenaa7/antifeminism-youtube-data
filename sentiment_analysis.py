import json
from googleapiclient import discovery
import time

API_KEYS = ['AIzaSyBVZgLhciLiceJzE1mRIynS0Y_TpF-fZHo', 'AIzaSyATYZXMLy5gE6-VedIAjhjKsxuhHNpHcVE', \
            'AIzaSyBCB08Ov42yWxaY9O_wu_idSLPZIE9PB3E', 'AIzaSyCyM8jTZfF-rMEwD72KWz8IRuR7s5bLiKw']

def analyze_comments(comments, perspectives):
    original_pos = int(open('data/comment_loc.txt', 'r').readline())
    i = original_pos
    with open('data/comment_sentiments.json', 'a') as f:
        for j in range(original_pos, len(comments)):
            video_id = list(comments.keys())[j]
            output = {video_id : {'toxicity' : [], 'severe_toxicity' : [], 'identity_attack' : [], 'insult' : [], 'profanity' : [], 'threat' : []}}
            for k in range(len(comments[video_id])):
                for api in perspectives:
                    if k > len(comments[video_id])-1:
                        continue
                    request = {
                        'comment': {'text': comments[video_id][k]['comment']},
                        'requestedAttributes': {'TOXICITY' : {}, 'SEVERE_TOXICITY': {}, 'IDENTITY_ATTACK': {}, 'INSULT': {}, 'PROFANITY': {}, 'THREAT': {}}
                    }
                    try:
                        response = api.comments().analyze(body=request).execute()
                    except:
                        continue
                    output[video_id]['toxicity'].append(response['attributeScores']['TOXICITY']['spanScores'][0]['score']['value'])
                    output[video_id]['severe_toxicity'].append(response['attributeScores']['SEVERE_TOXICITY']['spanScores'][0]['score']['value'])
                    output[video_id]['identity_attack'].append(response['attributeScores']['IDENTITY_ATTACK']['spanScores'][0]['score']['value'])
                    output[video_id]['insult'].append(response['attributeScores']['INSULT']['spanScores'][0]['score']['value'])
                    output[video_id]['profanity'].append(response['attributeScores']['PROFANITY']['spanScores'][0]['score']['value'])
                    output[video_id]['threat'].append(response['attributeScores']['THREAT']['spanScores'][0]['score']['value'])
                    k += 1
                    open('data/comment_loc.txt', 'w').write(str(i))
                time.sleep(1.05)
            f.write(json.dumps(output) + "\n")
            i += 1
            if output[list(output.keys())[0]]['toxicity'] != []:
                print("Successfully outputted sentiment information for video id " + str(video_id))
            else:
                print("Outputted video id " + video_id + ", but there was no sentiment to analyze")

def analyze_videos(videos, perspective):
    i = 0
    original_pos = int(open('data/video_loc.txt', 'r').readline())
    with open('data/video_sentiments.json', 'a') as f:
        f.write("\n")
        for video in videos:
            video_name = list(video.keys())[0]
            if i < original_pos:
                i += 1
                continue
            request = {
                'comment': {'text': video_name},
                'requestedAttributes': {'TOXICITY' : {}, 'SEVERE_TOXICITY': {}, 'IDENTITY_ATTACK': {}, 'INSULT': {}, 'PROFANITY': {}, 'THREAT': {}}
            }
            try:
                response = perspective.comments().analyze(body=request).execute()
            except:
                continue
            video_id = video[video_name]['video_id']
            output = {video_id : {}}
            output[video_id]['toxicity'] = response['attributeScores']['TOXICITY']['spanScores'][0]['score']['value']
            output[video_id]['severe_toxicity'] = response['attributeScores']['SEVERE_TOXICITY']['spanScores'][0]['score']['value']
            output[video_id]['identity_attack'] = response['attributeScores']['IDENTITY_ATTACK']['spanScores'][0]['score']['value']
            output[video_id]['insult'] = response['attributeScores']['INSULT']['spanScores'][0]['score']['value']
            output[video_id]['profanity'] = response['attributeScores']['PROFANITY']['spanScores'][0]['score']['value']
            output[video_id]['threat'] = response['attributeScores']['THREAT']['spanScores'][0]['score']['value']
            f.write(json.dumps(output) + "\n")
            i += 1
            open('data/video_loc.txt', 'w').write(str(i))
            time.sleep(1.1)

def main():
    comments = json.loads(open("data/comments.json", "r").readline())
    videos = json.loads(open("data/videos.json", "r").readline())
    apis = []
    for key in API_KEYS:
        api = discovery.build(
            serviceName='commentanalyzer',
            version='v1alpha1',
            developerKey=key,
            discoveryServiceUrl='https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1',
            static_discovery=False
        )
        apis.append(api)
    analyze_comments(comments, apis)
    
    

main()