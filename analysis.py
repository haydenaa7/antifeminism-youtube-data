import json
from matplotlib import pyplot as plt
from matplotlib.dates import date2num
import numpy as np
import seaborn as sns

BEFORE_ELECTION_NUM, AFTER_ELECTION_NUM = None, None

def get_videos():
    return json.loads(open("data/videos.json", "r").readline())

def partition_videos(videos):
    def get_date(video):
        raw = list(video.values())[0]['date_published']
        return raw[:raw.index('T')]
    before_election = list(filter(lambda x : get_date(x) <= '2022-03-09', videos))
    after_election = list(filter(lambda x : get_date(x) > '2022-03-09', videos))
    return before_election, after_election

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
        date = date2num(np.datetime64(video_values['date_published'][:video_values['date_published'].index('T')]))
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
    plt.gca().set_ylim([0, 0.6])
    plt.xlabel("9 March 2020 - 9 March 2023")


    ys = [toxicity, severe_toxicity, identity_attack, insult, profanity, threat]
    palette = sns.color_palette(None, len(ys))
    labels = ['Toxicity', 'Severe Toxicity', 'Identity Attack', 'Insult', 'Profanity', 'Threat']
    for i in range(len(ys)):
        color = palette[i]
        plt.scatter(dates, ys[i], color=color, edgecolors=None, s=8, alpha=0.3)
        # Polynomial regression
        z = np.polyfit(dates, ys[i], 3)
        p = np.poly1d(z)
        plt.plot(dates, p(dates), color=color, label=labels[i], linewidth=3)
    date = date2num(np.datetime64('2022-03-09'))
    plt.plot([date, date], [0, 1], color='black', linestyle='--')
    plt.legend()
    plt.grid(True)
    plt.title("Trends in Average Negative Sentiments in YouTube Video Titles (n=" + str(len(toxicity)) + ")")
    plt.show()

def analyze_video_views(videos):
    dates = []
    views = []

    for video in videos:
        video_values = video[list(video.keys())[0]]
        if 'views' not in video_values:
            continue
        view_count = int(video_values['views'])
        views.append(view_count)
        date = date2num(np.datetime64(video_values['date_published'][:video_values['date_published'].index('T')]))
        dates.append(date)

    plt.figure(figsize=(15, 7))
    plt.gca().axes.get_xaxis().set_ticks([])
    plt.gca().axes.set_yscale('log')
    plt.gca().set_ylim([0, 1e8])
    plt.xlabel("9 March 2020 - 9 March 2023")
    plt.ylabel("Views")
    plt.bar(dates, views)

    # Polynomial regression
    z = np.polyfit(dates, views, 3)
    p = np.poly1d(z)
    plt.plot(dates, p(dates), linewidth=2, color='orange')

    date = date2num(np.datetime64('2022-03-09'))
    plt.plot([date, date], [0, 1e8], color='black', linewidth=2, linestyle='--')
    plt.title("Log-scale Trends in Average YouTube Video View Count (n=" + str(len(views)) + ")")
    plt.show()

def analyze_comment_sentiments(videos, comment_sentiments):
    dates = []
    toxicity = []
    severe_toxicity = []
    identity_attack = []
    insult = []
    profanity = []
    threat = []

    for video_id in comment_sentiments:
        sentiment_values = comment_sentiments[video_id]
        if len(sentiment_values['toxicity']) < 5:
            continue
        raw_date = list(filter(lambda x : list(x.values())[0]['video_id'] == video_id, videos))[0]
        date = date2num(np.datetime64(list(raw_date.values())[0]['date_published'][:list(raw_date.values())[0]['date_published'].index('T')]))
        dates.append(date)
        toxicity.append(sum(sentiment_values['toxicity'])/len(sentiment_values['toxicity']))
        severe_toxicity.append(sum(sentiment_values['severe_toxicity'])/len(sentiment_values['severe_toxicity']))
        identity_attack.append(sum(sentiment_values['identity_attack'])/len(sentiment_values['identity_attack']))
        insult.append(sum(sentiment_values['insult'])/len(sentiment_values['insult']))
        profanity.append(sum(sentiment_values['profanity'])/len(sentiment_values['profanity']))
        threat.append(sum(sentiment_values['threat'])/len(sentiment_values['threat']))

    plt.figure(figsize=(15, 7))
    plt.gca().axes.get_xaxis().set_ticks([])
    plt.gca().set_ylim([0, 0.6])
    plt.xlabel("9 March 2020 - 9 March 2023")


    ys = [toxicity, severe_toxicity, identity_attack, insult, profanity, threat]
    palette = sns.color_palette(None, len(ys))
    labels = ['Toxicity', 'Severe Toxicity', 'Identity Attack', 'Insult', 'Profanity', 'Threat']
    for i in range(len(ys)):
        color = palette[i]
        plt.scatter(dates, ys[i], color=color, edgecolors=None, s=8, alpha=0.3)
        z = np.polyfit(dates, ys[i], 1)
        p = np.poly1d(z)
        plt.plot(dates, p(dates), color=color, label=labels[i], linewidth=3, linestyle='--')
    date = date2num(np.datetime64('2022-03-09'))
    plt.plot([date, date], [0, 1], color='black')
    plt.legend()
    plt.grid(True)
    plt.title("Trends in Average Negative Sentiments in YouTube Video Comments (n=" + str(len(toxicity)) + ")")
    plt.show()


def main():
    videos = get_videos()
    before, after = partition_videos(videos)
    BEFORE_ELECTION_NUM, AFTER_ELECTION_NUM = len(before), len(after)
    video_sentiments = get_video_sentiments()
    comments = get_comments()
    comment_sentiments = get_comment_sentiments()
    #get_sample_sizes(videos, video_sentiments, comments, comment_sentiments, visualize=False, save_file=True)
    analyze_video_sentiments(videos, video_sentiments)
    #analyze_comment_sentiments(videos, comment_sentiments)
    #analyze_video_views(videos)
main()