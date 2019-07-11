from flask import Flask,render_template,url_for,request
import pickle
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import itertools
import collections
import tweepy as tw
import nltk 
from nltk.corpus import stopwords
import re
import networkx
from textblob import TextBlob
 
import warnings
warnings.filterwarnings("ignore")
 
sns.set(font_scale=1.5)
sns.set_style("whitegrid")

consumer_key= 'j8QZnEO5jA3BBLD5mquFW9zqf'
consumer_secret= '2FKoIwyxS1aGXSZgxOXWOa3cJRPnp6tmuRmVRpJpYFk8u2c8G2'
access_token= '924361297478733829-TThjzyzUVcUS5KnGwB5VUxSqc86Qjic'
access_token_secret= 'G4iOQmT5nYTTIg0R9MYlYFoKE4Rx3KHOsv0Hjy7JDLJ2f'

app = Flask(__name__)

@app.route('/')
def home():
	return render_template('home.html')

@app.route('/predict',methods=['POST'])
def predict():
	keyword = request.form['hashtag']
	auth = tw.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	api = tw.API(auth, wait_on_rate_limit=True)

	search_term = '#' + keyword + " -filter:retweets"
	 
	tweets = tw.Cursor(api.search,
	                   q=search_term,
	                   lang="en",
	                   since='2018-11-01').items(100)
	 
	# Remove URLs
	tweets_no_urls = [" ".join(re.sub("([^0-9A-Za-z \t])|(\w+:\/\/\S+)", "", tweet.text).split()) for tweet in tweets]

	sentiment_objects = [TextBlob(tweet) for tweet in tweets_no_urls]
	sentiment_values = [[tweet.sentiment.polarity, str(tweet)] for tweet in sentiment_objects]
	sentiment_df = pd.DataFrame(sentiment_values, columns=["polarity", "tweet"])
	sentiment_df['review'] = ["Positive" if x > 0.2 else("Negative" if x < -0.2 else "Neutral") for x in sentiment_df['polarity']]
	sentiment_df2 = sentiment_df[sentiment_df.polarity != 0]
	fig, ax = plt.subplots(figsize=(8, 6))
	# Plot histogram with break at zero
	sentiment_df2.hist(bins=[-1, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1],
	             ax=ax,
	             color="blue")

	plt.title("Sentiments from Tweets on #"+ keyword)
	fig.savefig('static/images/my_plot2.png')

	return render_template('result.html',keyword = keyword,data=sentiment_df.to_html())



if __name__ == '__main__':
	app.run(debug=True)