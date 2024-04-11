import json
from matplotlib import pyplot as plt
import numpy as np
import seaborn as sns

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

def analyze_video_sentiments(videos, video_sentiments):
    dates = []
    toxicity = []
    severe_toxicity = []
    identity_attack = []
    insult = []
    profanity = []
    threat = []

    for video in videos:
        video_values = video[list(video.keys())[0]]
        video_id = video_values['video_id']
        if video_id not in video_sentiments:
            continue
        date = int(video_values['date_published'][:video_values['date_published'].index('T')].replace('-', ''))
        dates.append(date)
        sentiment_values = video_sentiments[video_id]
        toxicity.append(sentiment_values['toxicity'])
        severe_toxicity.append(sentiment_values['severe_toxicity'])
        identity_attack.append(sentiment_values['identity_attack'])
        insult.append(sentiment_values['insult'])
        profanity.append(sentiment_values['profanity'])
        threat.append(sentiment_values['threat'])

    plt.figure(figsize=(15, 7))
    plt.gca().axes.get_xaxis().set_ticks([])
    plt.xlabel("9 March 2020 - 9 March 2023")


    ys = [toxicity, severe_toxicity, identity_attack, insult, profanity, threat]
    palette = sns.color_palette(None, len(ys))
    labels = ['Toxicity', 'Severe Toxicity', 'Identity Attack', 'Insult', 'Profanity', 'Threat']
    for i in range(len(ys)):
        color = palette[i]
        plt.scatter(dates, ys[i], color=color, label=labels[i], edgecolors=None)
        z = np.polyfit(dates, ys[i], 1)
        p = np.poly1d(z)
        plt.plot(dates, p(dates), color=color)
    plt.plot([20220309, 20220309], [0, 1], color='black')
    plt.legend()
    plt.grid(True)
    plt.title("Trends in Average Negative Sentiments (n=" + str(len(toxicity)) + ")")
    plt.show()

def main():
    videos = get_videos()
    video_sentiments = get_video_sentiments()
    comments = get_comments()
    comment_sentiments = get_comment_sentiments()
    #get_sample_sizes(videos, video_sentiments, comments, comment_sentiments, visualize=False, save_file=True)
    analyze_video_sentiments(videos, video_sentiments)
main()