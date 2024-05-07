import json
from matplotlib import pyplot as plt
from matplotlib.dates import date2num
import numpy as np
import seaborn as sns
from scipy.stats import linregress

BEFORE_ELECTION_NUM, AFTER_ELECTION_NUM = None, None

def get_correlation(x, y):
    raw = linregress(x, y)
    return raw[2], raw[3]

def get_videos():
    return json.loads(open("data/videos.json", "r").readline())

def partition_videos(videos):
    def get_date(video):
        raw = list(video.values())[0]['date_published']
        return raw[:raw.index('T')]
    before_election = list(filter(lambda x : get_date(x) <= '2022-03-09', videos))
    after_election = list(filter(lambda x : get_date(x) > '2022-03-09', videos))
    return before_election, after_election

def add_comment_weighted_scores(comments, videos):
    total_views = sum(int(list(video.values())[0]['views']) for video in videos if 'views' in list(video.values())[0])
    def calculate_score(comment, views):
        likes = comment['likes']
        replies = comment['reply_count']
        return 0.5 * (likes*views/total_views) + 0.5 * (replies*views/total_views)
    for video in comments:
        raw = [list(x.values())[0]['views'] for x in videos if list(x.values())[0]['video_id'] == video and 'views' in list(x.values())[0]]
        if len(raw) == 0:
            continue
        views = int(raw[0])
        for comment in comments[video]:
            comment['score'] = calculate_score(comment, views)
    for video in videos:
        video_name = list(video.keys())[0]
        video_id = video[video_name]['video_id']
        video[video_name]['score'] = 0
        for comment in comments[video_id]:
            video[video_name]['score'] += comment['score']

def pretty_date(date1, date2):
    code = {'01' : 'January', '02' : 'February', '03' : 'March', '04' : 'April', '05' : 'May', '06' : 'June',\
            '07' : 'July', '08' : 'August', '09' : 'September', '10' : 'October', '11' : 'November', '12' : 'December'}
    date1y, date1m, date1d = date1.split('-')
    date2y, date2m, date2d = date2.split('-')
    return f'{date1d.lstrip("0")} {code[date1m]} {date1y} - {date2d.lstrip("0")} {code[date2m]} {date2y}'



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

def analyze_video_sentiments(videos, video_sentiments, limit=None):
    dates = []
    overall = []
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
        raw_date = video_values['date_published'][:video_values['date_published'].index('T')]
        if limit and (raw_date < limit[0] or raw_date > limit[1]):
            continue
        date = date2num(np.datetime64(raw_date))
        dates.append(date)
        sentiment_values = video_sentiments[video_id]
        toxicity.append(sentiment_values['toxicity'])
        severe_toxicity.append(sentiment_values['severe_toxicity'])
        identity_attack.append(sentiment_values['identity_attack'])
        insult.append(sentiment_values['insult'])
        profanity.append(sentiment_values['profanity'])
        threat.append(sentiment_values['threat'])
        overall.append(sentiment_values['toxicity'] * 1/6 + sentiment_values['severe_toxicity'] * 1/6 + sentiment_values['identity_attack'] * 1/6 + \
                       sentiment_values['insult'] * 1/6 + sentiment_values['profanity'] * 1/6 + sentiment_values['threat'] * 1/6)

    plt.figure(figsize=(15, 7))
    plt.gca().axes.get_xaxis().set_ticks([])
    plt.gca().set_ylim([0, 0.4])
    if not limit:
        plt.xlabel("9 March 2020 - 9 March 2023")
    else:
        plt.xlabel(pretty_date(limit[0], limit[1]))
    plt.ylabel("Sentiment")

    ys = [toxicity, severe_toxicity, identity_attack, insult, profanity, threat]
    palette = sns.color_palette(None, len(ys))
    labels = ['Toxicity', 'Severe Toxicity', 'Identity Attack', 'Insult', 'Profanity', 'Threat']
    for i in range(len(ys)):
        color = palette[i]
        plt.scatter(dates, ys[i], color=color, edgecolors=None, s=8, alpha=0.3)
        # Polynomial regression
        z = np.polyfit(dates, ys[i], 1)
        p = np.poly1d(z)
        rvalue, pvalue = get_correlation(dates, ys[i])
        plt.plot(dates, p(dates), color=color, label=labels[i] + ' (R2 = ' + str(round(rvalue**2, 3)) + ', p = ' + str(round(pvalue, 12)) + ')', linewidth=3)
        ci = 1.95 * np.std(ys[i]) / np.sqrt(len(dates))
        plt.fill_between(dates, (p(dates) - ci), (p(dates) + ci), color=color, alpha=0.1)
    
    z = np.polyfit(dates, overall, 1)
    p = np.poly1d(z)
    rvalue, pvalue = get_correlation(dates, overall)
    plt.plot(dates, p(dates), color='darkred', label='Overall (R2 = ' + str(round(rvalue**2, 3)) + ', p = ' + str(round(pvalue, 12)) + ')', linewidth=3, linestyle='-.')

    date = date2num(np.datetime64('2022-03-09'))
    plt.plot([date, date], [0, 1], color='black', linestyle='--')
    plt.legend()
    plt.grid(True)
    plt.title("Trends in Average Negative Sentiments in YouTube Video Titles (n=" + str(len(toxicity)) + ")")
    #plt.savefig('images/video_sentiments6monthsafter.png')
    plt.show()

def analyze_comment_sentiments(videos, comment_sentiments, limit=None):
    size = 0
    dates = []
    toxicity = []
    severe_toxicity = []
    identity_attack = []
    insult = []
    profanity = []
    threat = []
    overall = []

    for video_id in comment_sentiments:
        sentiment_values = comment_sentiments[video_id]
        if len(sentiment_values['toxicity']) < 5:
            continue
        raw_raw_date = list(filter(lambda x : list(x.values())[0]['video_id'] == video_id, videos))[0]
        raw_date = list(raw_raw_date.values())[0]['date_published'][:list(raw_raw_date.values())[0]['date_published'].index('T')]
        if limit and (raw_date < limit[0] or raw_date > limit[1]):
            continue
        date = date2num(np.datetime64(raw_date))
        dates.append(date)
        
        t = set(sentiment_values['toxicity'])
        toxicity.append(sum(t)/len(t))
        st = set(sentiment_values['severe_toxicity'])
        severe_toxicity.append(sum(st)/len(st))
        ia = set(sentiment_values['identity_attack'])
        identity_attack.append(sum(ia)/len(ia))
        i = set(sentiment_values['insult'])
        insult.append(sum(i)/len(i))
        p = set(sentiment_values['profanity'])
        profanity.append(sum(p)/len(p))
        th = set(sentiment_values['threat'])
        threat.append(sum(th)/len(th))

        overall.append(1/6 * sum(t)/len(t) + 1/6 * sum(st)/len(st) + 1/6 * sum(ia)/len(ia) + \
                       1/6 * sum(i)/len(i) + 1/6 * sum(p)/len(p) + 1/6 * sum(th)/len(th))

        size += len(t)

    plt.figure(figsize=(15, 7))
    plt.gca().axes.get_xaxis().set_ticks([])
    plt.gca().set_ylim([0, 0.4])
    if not limit:
        plt.xlabel("9 March 2020 - 9 March 2023")
    else:
        plt.xlabel(pretty_date(limit[0], limit[1]))


    ys = [toxicity, severe_toxicity, identity_attack, insult, profanity, threat]
    palette = sns.color_palette(None, len(ys))
    labels = ['Toxicity', 'Severe Toxicity', 'Identity Attack', 'Insult', 'Profanity', 'Threat']
    for i in range(len(ys)):
        color = palette[i]
        plt.scatter(dates, ys[i], color=color, edgecolors=None, s=8, alpha=0.3)
        z = np.polyfit(dates, ys[i], 1)
        p = np.poly1d(z)
        rvalue, pvalue = get_correlation(dates, ys[i])
        plt.plot(dates, p(dates), color=color, label=labels[i] + ' (R2 = ' + str(round(rvalue**2, 3)) + ', p = ' + str(round(pvalue, 12)) + ')', linewidth=3)
        ci = 1.95 * np.std(ys[i]) / np.sqrt(len(dates))
        plt.fill_between(dates, (p(dates) - ci), (p(dates) + ci), color=color, alpha=0.1)
    z = np.polyfit(dates, overall, 1)
    p = np.poly1d(z)
    rvalue, pvalue = get_correlation(dates, overall)
    plt.plot(dates, p(dates), color='darkred', label='Overall (R2 = ' + str(round(rvalue**2, 3)) + ', p = ' + str(round(pvalue, 12)) + ')', linewidth=3, linestyle='-.')
    

    date = date2num(np.datetime64('2022-03-09'))
    plt.plot([date, date], [0, 1], color='black', linestyle='--', linewidth=2)
    plt.legend()
    plt.grid(True)
    plt.title("Trends in Average Negative Sentiments in YouTube Video Comments (n=" + str(size) + ")")
    #plt.savefig('images/comment_sentiments6monthsafter.png')
    plt.show()

def analyze_video_views(videos, limit=None):
    dates = []
    views = []

    for video in videos:
        video_values = video[list(video.keys())[0]]
        if 'views' not in video_values:
            continue
        raw_date = video_values['date_published'][:video_values['date_published'].index('T')]
        if limit and (raw_date < limit[0] or raw_date > limit[1]):
            continue
        date = date2num(np.datetime64(raw_date))
        dates.append(date)
        view_count = int(video_values['views'])
        views.append(view_count)

    plt.figure(figsize=(15, 7))
    plt.gca().axes.get_xaxis().set_ticks([])
    plt.gca().axes.set_yscale('log')
    plt.gca().set_ylim([0, 1e8])
    if not limit:
        plt.xlabel("9 March 2020 - 9 March 2023")
    else:
        plt.xlabel(pretty_date(limit[0], limit[1]))
    plt.ylabel("Views")
    plt.bar(dates, views)

    # Polynomial regression
    z = np.polyfit(dates, views, 3)
    p = np.poly1d(z)
    rvalue, pvalue = get_correlation(dates, views)
    plt.plot(dates, p(dates), linewidth=2, color='orange', label='R2 = ' + str(round(rvalue**2, 3)) + ', p = ' + str(round(pvalue, 12)))
    ci = 1.95 * np.std(views) / np.sqrt(len(dates))
    plt.fill_between(dates, (p(dates) - ci), (p(dates) + ci), color='orange', alpha=0.1)

    date = date2num(np.datetime64('2022-03-09'))
    plt.plot([date, date], [0, 1e8], color='black', linewidth=2, linestyle='--')
    plt.title("Log-scale Trends in Average YouTube Video View Count (n=" + str(len(views)) + ")")
    plt.legend()
    plt.grid(True)
    #plt.savefig('images/views6months.png')
    plt.show()

def analyze_video_comments(videos, limit=None):
    dates = []
    comments = []

    for video in videos:
        video_values = video[list(video.keys())[0]]
        if 'comments' not in video_values:
            continue
        raw_date = video_values['date_published'][:video_values['date_published'].index('T')]
        if limit and (raw_date < limit[0] or raw_date > limit[1]):
            continue
        date = date2num(np.datetime64(raw_date))
        dates.append(date)
        comment_count = int(video_values['comments'])/int(video_values['views'])
        comments.append(comment_count)

    plt.figure(figsize=(15, 7))
    plt.gca().axes.get_xaxis().set_ticks([])
    #plt.gca().axes.set_yscale('log')
    plt.gca().set_ylim([0, 0.1])
    if not limit:
        plt.xlabel("9 March 2020 - 9 March 2023")
    else:
        plt.xlabel(pretty_date(limit[0], limit[1]))
    plt.ylabel("Comment/View Ratio")
    plt.bar(dates, comments)

    # Polynomial regression
    z = np.polyfit(dates, comments, 3)
    p = np.poly1d(z)
    rvalue, pvalue = get_correlation(dates, comments)
    plt.plot(dates, p(dates), linewidth=2, color='orange', label='R2 = ' + str(round(rvalue**2, 3)) + ', p = ' + str(round(pvalue, 12)))
    ci = 1.95 * np.std(comments) / np.sqrt(len(dates))
    plt.fill_between(dates, (p(dates) - ci), (p(dates) + ci), color='orange', alpha=0.1)

    date = date2num(np.datetime64('2022-03-09'))
    plt.plot([date, date], [0, 0.1], color='black', linewidth=2, linestyle='--')
    plt.title("Trends in Average YouTube Video Comment/View Ratio (n=" + str(len(comments)) + ")")
    plt.legend()
    plt.grid(True)
    #plt.savefig('images/comments6months.png')
    plt.show()

def analyze_video_likes(videos, limit=None):
    dates = []
    likes = []

    for video in videos:
        video_values = video[list(video.keys())[0]]
        if 'likes' not in video_values:
            continue
        raw_date = video_values['date_published'][:video_values['date_published'].index('T')]
        if limit and (raw_date < limit[0] or raw_date > limit[1]):
            continue
        date = date2num(np.datetime64(raw_date))
        dates.append(date)
        like_count = int(video_values['likes'])/int(video_values['views'])
        likes.append(like_count)


    plt.figure(figsize=(15, 7))
    plt.gca().axes.get_xaxis().set_ticks([])
    #plt.gca().axes.set_yscale('log')
    plt.gca().set_ylim([0, 0.2])
    if not limit:
        plt.xlabel("9 March 2020 - 9 March 2023")
    else:
        plt.xlabel(pretty_date(limit[0], limit[1]))
    plt.ylabel("Like/View Ratio")
    plt.bar(dates, likes)

    # Polynomial regression
    z = np.polyfit(dates, likes, 3)
    p = np.poly1d(z)
    rvalue, pvalue = get_correlation(dates, likes)
    plt.plot(dates, p(dates), linewidth=2, color='orange', label='R2 = ' + str(round(rvalue**2, 3)) + ', p = ' + str(round(pvalue, 12)))
    ci = 1.95 * np.std(likes) / np.sqrt(len(dates))
    plt.fill_between(dates, (p(dates) - ci), (p(dates) + ci), color='orange', alpha=0.1)

    date = date2num(np.datetime64('2022-03-09'))
    plt.plot([date, date], [0, 0.4], color='black', linewidth=2, linestyle='--')
    plt.title("Trends in Average YouTube Video Like/View Ratio (n=" + str(len(likes)) + ")")
    plt.legend()
    plt.grid(True)
    #plt.savefig('images/likes.png')
    plt.show()

def analyze_video_scores(videos, limit=None):
    dates = []
    scores = []

    for video in videos:
        video_values = video[list(video.keys())[0]]
        if 'score' not in video_values:
            continue
        raw_date = video_values['date_published'][:video_values['date_published'].index('T')]
        if limit and (raw_date < limit[0] or raw_date > limit[1]):
            continue
        date = date2num(np.datetime64(raw_date))
        dates.append(date)
        score = int(video_values['score'])
        scores.append(score)

    plt.figure(figsize=(15, 7))
    plt.gca().axes.get_xaxis().set_ticks([])
    plt.gca().set_ylim([0, 60])
    if not limit:
        plt.xlabel("9 March 2020 - 9 March 2023")
    else:
        plt.xlabel(pretty_date(limit[0], limit[1]))
    plt.ylabel("Score")
    plt.bar(dates, scores)

    # Polynomial regression
    z = np.polyfit(dates, scores, 3)
    p = np.poly1d(z)
    rvalue, pvalue = get_correlation(dates, scores)
    plt.plot(dates, p(dates), linewidth=2, color='orange', label='R2 = ' + str(round(rvalue**2, 3)) + ', p = ' + str(round(pvalue, 12)))
    ci = 1.95 * np.std(scores) / np.sqrt(len(dates))
    plt.fill_between(dates, (p(dates) - ci), (p(dates) + ci), color='orange', alpha=0.1)

    date = date2num(np.datetime64('2022-03-09'))
    plt.plot([date, date], [0, 1e5], color='black', linewidth=2, linestyle='--')
    plt.title("Trends in Average YouTube Video Importance Score (n=" + str(len(scores)) + ")")
    plt.legend()
    plt.grid(True)
    #plt.savefig('images/scores6months.png')
    plt.show()

def analyze_video_scores_sentiment(videos, video_sentiments):
    scores = []
    toxicity = []
    severe_toxicity = []
    identity_attack = []
    insult = []
    profanity = []
    threat = []

    for video in videos:
        video_values = video[list(video.keys())[0]]
        video_id = video_values['video_id']
        if video_id not in video_sentiments or 'score' not in video_values:
            continue
        scores.append(int(video_values['score']))
        sentiment_values = video_sentiments[video_id]
        toxicity.append(sentiment_values['toxicity'])
        severe_toxicity.append(sentiment_values['severe_toxicity'])
        identity_attack.append(sentiment_values['identity_attack'])
        insult.append(sentiment_values['insult'])
        profanity.append(sentiment_values['profanity'])
        threat.append(sentiment_values['threat'])

    plt.figure(figsize=(15, 7))
    plt.gca().set_ylim([0, 0.6])
    plt.gca().axes.set_xscale('log')
    plt.xlabel("Score")
    plt.ylabel("Sentiment")

    ys = [toxicity, severe_toxicity, identity_attack, insult, profanity, threat]
    palette = sns.color_palette(None, len(ys))
    labels = ['Toxicity', 'Severe Toxicity', 'Identity Attack', 'Insult', 'Profanity', 'Threat']
    for i in range(len(ys)):
        color = palette[i]
        plt.scatter(scores, ys[i], color=color, s=8, alpha=0.3)
        # Polynomial regression
        z = np.polyfit(scores, ys[i], 1)
        p = np.poly1d(z)
        rvalue, pvalue = get_correlation(scores, ys[i])
        plt.plot(scores, p(scores), color=color, label=labels[i] + ' (R2 = ' + str(round(rvalue**2, 3)) + ', p = ' + str(round(pvalue, 12)) + ')', linewidth=3)
        ci = 1.95 * np.std(ys[i]) / np.sqrt(len(scores))
        plt.fill_between(scores, (p(scores) - ci), (p(scores) + ci), color=color, alpha=0.1)
        
    plt.legend()
    plt.grid(True)
    plt.title("Log-scale Correlation in Negative Sentiment and Video Score (n=" + str(len(toxicity)) + ")")
    #plt.savefig('images/video_sentiments.png')
    plt.show()

def main():
    videos = get_videos()
    before, after = partition_videos(videos)
    BEFORE_ELECTION_NUM, AFTER_ELECTION_NUM = len(before), len(after)
    video_sentiments = get_video_sentiments()
    comments = get_comments()
    comment_sentiments = get_comment_sentiments()

    #get_sample_sizes(videos, video_sentiments, comments, comment_sentiments, visualize=True, save_file=False)

    #analyze_video_sentiments(videos, video_sentiments, limit=('2021-09-09', '2023-03-09'))
    analyze_comment_sentiments(videos, comment_sentiments, limit=('2021-09-09', '2023-03-09'))
    #analyze_video_views(videos, limit=('2021-09-09', '2022-03-09'))
    #analyze_video_comments(videos, limit=('2021-09-09', '2022-03-09'))
    #analyze_video_likes(videos)

    #add_comment_weighted_scores(comments, videos)
    #analyze_video_scores(videos, limit=('2022-09-09', '2023-03-09'))
    #analyze_video_scores_sentiment(videos, video_sentiments)
main()