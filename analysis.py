import json
from matplotlib import pyplot as plt

def get_videos():
    return json.loads(open("data/videos.json", "r").readline())

def get_video_sentiments():
    video_sentiments = {}
    with open("data/video_sentiments.json", "r") as f:
        for line in f:
            line = json.loads(f.readline())
            key = list(line.keys())[0]
            if key not in video_sentiments and len(line[key]) > 0:
                video_sentiments[key] = line[key]
    return video_sentiments

def get_comments():
    return json.loads(open("data/comments.json", "r").readline())

def get_comment_sentiments():
    comment_sentiments = {}
    with open("data/comment_sentiments.json", "r") as f:
        for line in f:
            line = json.loads(f.readline())
            key = list(line.keys())[0]
            if key not in comment_sentiments and len(line[key]) > 0:
                comment_sentiments[key] = line[key]
    return comment_sentiments

def get_sample_sizes(videos, video_sentiments, comments, comment_sentiments, visualize=False, save_file=False):
    videos_size = len(videos)
    video_sentiments_size = len(video_sentiments)
    comment_size = sum([0 if len(comments[key]) == 0 else len(comments[key]) for key in comments])
    comment_sentiment_size = sum(len(comment_sentiments[key]['toxicity']) for key in comment_sentiments)
    
    if visualize or save_file:
        names = ['Videos', 'Analyzed Videos', 'Comments', 'Analyzed Comments']
        values = [videos_size, video_sentiments_size, comment_size, comment_sentiment_size]
        _, ax = plt.subplots()
        bar_container = ax.bar(names, values, color=['darkred', 'blue', 'darkred', 'blue'])
        ax.set_title('Sample Sizes')
        ax.set(ylabel='Number')
        ax.bar_label(bar_container, fmt='{:,.0f}')
        if visualize:
            plt.show()
        if save_file:
            plt.savefig("images/sample_sizes.png")

def main():
    videos = get_videos()
    video_sentiments = get_video_sentiments()
    comments = get_comments()
    comment_sentiments = get_comment_sentiments()
    get_sample_sizes(videos, video_sentiments, comments, comment_sentiments, visualize=False, save_file=True)
main()