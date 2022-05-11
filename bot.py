import tweepy
import logging
import pickle
import time
import numpy as np
from secrets import API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, TWITTER_ID

logger = logging.getLogger("Tweepy")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="tweepy.log")
logger.addHandler(handler)

def getAPI(api_key, api_secret, access_token, access_token_secret):
    auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
    api = tweepy.API(auth)
    return api

def classifyTweet(tweet):
    with open('finalPipeline.pickle' , 'rb') as f:
        clf = pickle.load(f)
    tweet = [tweet]
    prediction = clf.predict(tweet)
    proba = np.max(clf.predict_proba(tweet))
    return prediction, proba

def generateResponse(funny, proba):
    if funny:
        return f'beep boop... I am {proba*100:.2f}% sure this is funny.'
    else:
        return f'beep boop... I am {proba*100:.2f}% sure this is not funny.'

def extractText(tweet):
    tweet = tweet.full_text
    tweet = tweet.split('@HumourDetector', 1)
    return tweet[-1]

def readLastSeen(filename):
    with open(filename, 'r') as f:
        lastSeenID = int(f.read().strip())
        return lastSeenID

def storeLastSeen(filename, lastSeenID):
    with open(filename, 'w') as f:
        f.write(str(lastSeenID))

def getLastReceived(messages):
    received = []
    for message in messages:
        if message.message_create['target']['recipient_id'] == TWITTER_ID:
            received.append(message)
    return received

def getParent(tweet):
    parentID = tweet.in_reply_to_status_id
    parentTweet = api.get_status(id=parentID, tweet_mode='extended')
    return parentTweet

api = getAPI(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

def reply():
    mentions = api.mentions_timeline(count=10, since_id=readLastSeen('tweetHistory.txt'), tweet_mode='extended')
    messages = api.get_direct_messages(count=10)
    receivedMessages = getLastReceived(messages)
    for tweet in mentions:
        clfInput = extractText(tweet)
        if clfInput:
            clfOutput, clfProba = classifyTweet(clfInput)
            clfResponse = generateResponse(clfOutput, clfProba)
            api.update_status("@" + tweet.user.screen_name + " " + clfResponse, in_reply_to_status_id=tweet.id)
            api.create_favorite(tweet.id)
            api.create_friendship(user_id=tweet.user.id)
            storeLastSeen('tweetHistory.txt', tweet.id)
            print(f"stored {tweet.id}")
        else:
            parent = getParent(tweet)
            clfInput = extractText(parent)
            print(clfInput)
            clfOutput, clfProba = classifyTweet(clfInput)
            clfResponse = generateResponse(clfOutput, clfProba)
            api.update_status("@" + parent.user.screen_name + " @" + tweet.user.screen_name + " " + clfResponse, in_reply_to_status_id=parent.id)
            api.create_favorite(parent.id)
            api.create_favorite(tweet.id)
            api.create_friendship(user_id=parent.user.id)
            api.create_friendship(user_id=tweet.user.id)
            storeLastSeen('tweetHistory.txt', tweet.id)
            print(f"stored {tweet.id}")
    if receivedMessages:
        for message in receivedMessages:
            messageID = int(message.id)
            if messageID > readLastSeen('messageHistory.txt'):
                clfInput = message.message_create["message_data"]["text"]
                clfOutput, clfProba = classifyTweet(clfInput)
                clfResponse = generateResponse(clfOutput, clfProba)
                api.send_direct_message(recipient_id=message.message_create["sender_id"], text=clfResponse)
                storeLastSeen('messageHistory.txt', messageID)
                print(f"stored dm {messageID}")

while True:
    reply()
    time.sleep(60)
