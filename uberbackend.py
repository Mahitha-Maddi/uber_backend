from flask import Flask, flash, request, jsonify, render_template, redirect, url_for, g, session, send_from_directory, abort
from flask_cors import CORS
#from flask import status
from datetime import date, datetime, timedelta
from calendar import monthrange
from dateutil.parser import parse
import pytz
import os
import sys
import time
import uuid
import json
import random
import string
import pathlib
import io
from uuid import UUID
from bson.objectid import ObjectId

# straight mongo access
from pymongo import MongoClient

# mongo
#mongo_client = MongoClient('mongodb://localhost:27017/')
mongo_client = MongoClient("mongodb+srv://Mahitha-Maddi:Mahitha%4042@cluster0.1z0g8.mongodb.net/test")

app = Flask(__name__)
#CORS(app)
CORS(app, resources={r"/*": {"origins": "*"}})
basedir = os.path.abspath(os.path.dirname(__file__))

# Here are my datasets
bookings = dict()      


################
# Apply to mongo
################

def atlas_connect():
    # Node
    # const MongoClient = require('mongodb').MongoClient;
    # const uri = "mongodb+srv://admin:<password>@tweets.8ugzv.mongodb.net/myFirstDatabase?retryWrites=true&w=majority";
    # const client = new MongoClient(uri, { useNewUrlParser: true, useUnifiedTopology: true });
    # client.connect(err => {
    # const collection = client.db("test").collection("devices");
    # // perform actions on the collection object
    # client.close();
    # });

    # Python
    client = pymongo.MongoClient("mongodb+srv://Mahitha-Maddi:Mahitha%4042@cluster0.1z0g8.mongodb.net/test")
    db = client.test


# database access layer
def insert_one(r):
    start_time = datetime.now()
    with mongo_client:
        #start_time_db = datetime.now()
        db = mongo_client['Uber']
        #microseconds_caching_db = (datetime.now() - start_time_db).microseconds
        #print("*** It took " + str(microseconds_caching_db) + " microseconds to cache mongo handle.")

        print("...insert_one() to mongo: ", r)
        try:
            mongo_collection = db['bookings']
            result = mongo_collection.insert_one(r)
            print("inserted _ids: ", result.inserted_id)
        except Exception as e:
            print(e)

    microseconds_doing_mongo_work = (datetime.now() - start_time).microseconds
    print("*** It took " + str(microseconds_doing_mongo_work) + " microseconds to insert_one.")


def update_one(r):
    start_time = datetime.now()
    with mongo_client:
        #start_time_db = datetime.now()
        db = mongo_client['tweets']
        #microseconds_caching_db = (datetime.now() - start_time_db).microseconds
        #print("*** It took " + str(microseconds_caching_db) + " microseconds to cache mongo handle.")

        print("...update_one() to mongo: ", r)
        try:
            mongo_collection = db['tweets']
            result = mongo_collection.update_one(
                {"_id" : r['_id']},
                {"$set": r},
                upsert=True)
            print ("...update_one() to mongo acknowledged:", result.modified_count)
        except Exception as e:
            print(e)

    microseconds_doing_mongo_work = (datetime.now() - start_time).microseconds
    print("*** It took " + str(microseconds_doing_mongo_work) + " microseconds to update_one.")


def insert_many(r):
    start_time = datetime.now()
    with mongo_client:
        #start_time_db = datetime.now()
        db = mongo_client['tweets']
        #microseconds_caching_db = (datetime.now() - start_time_db).microseconds
        #print("*** It took " + str(microseconds_caching_db) + " microseconds to cache mongo handle.")

        print("...insert_many() to mongo: ", r.values())
        try:
            mongo_collection = db['tweets']
            result = mongo_collection.insert_many(r.values())
            print("inserted _ids: ", result.inserted_ids)
        except Exception as e:
            print(e)

    microseconds_doing_mongo_work = (datetime.now() - start_time).microseconds
    print("*** It took " + str(microseconds_doing_mongo_work) + " microseconds to insert_many.")


def update_many(r):
    start_time = datetime.now()
    with mongo_client:
        #start_time_db = datetime.now()
        db = mongo_client['tweets']
        #microseconds_caching_db = (datetime.now() - start_time_db).microseconds
        #print("*** It took " + str(microseconds_caching_db) + " microseconds to cache mongo handle.")

        print("...insert_many() to mongo: ", r.values())
        # much more complicated: use bulkwrite()
        # https://docs.mongodb.com/manual/reference/method/db.collection.bulkWrite/#db.collection.bulkWrite
        ops = []
        records = r
        print("...bulkwrite() to mongo: ", records)
        for one_r in records.values():
            op = dict(
                    replaceOne=dict(
                        filter=dict(
                            _id=one_r['_id']
                            ),
                        replacement=one_r,
                        upsert=True
                    )
            )
            ops.append(op)
        try:
            mongo_collection = db['tweets']
            result = mongo_collection.bulkWrite(ops, ordered=True)
            print("matchedCount: ", result.matchedCount)
        except Exception as e:
            print(e)

    microseconds_doing_mongo_work = (datetime.now() - start_time).microseconds
    print("*** It took " + str(microseconds_doing_mongo_work) + " microseconds to update_many.")


def tryexcept(requesto, key, default):
    lhs = None
    try:
        lhs = requesto.json[key]
        # except Exception as e:
    except:
        lhs = default
    return lhs

## seconds since midnight
def ssm():
    now = datetime.now()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return str((now - midnight).seconds)


################################################
# Tweets 
################################################

# endpoint to create new tweet
@app.route("/tweet", methods=["POST"])
def add_tweet():
    user = request.json['user']
    description = request.json['description']
    private = request.json['private']
    pic = request.json['pic']
    tweet = dict(user=user, description=description, private=private,
                upvote=0, date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                pic=pic, _id=str(ObjectId()))
    tweets[tweet['_id']] = tweet

    insert_one(tweet)
    return jsonify(tweet)



# endpoint to show all of today's tweets
@app.route("/tweets-day2", methods=["GET"])
def get_tweets_day2():
    todaystweets = dict(
        filter(lambda elem: 
                elem[1]['date'].split(' ')[0] == datetime.now().strftime("%Y-%m-%d"), 
                tweets.items())
    )
    return jsonify(todaystweets)

# endpoint to show all tweets 
@app.route("/tweets", methods=["GET"])
def get_tweets2():
    return jsonify(tweets)

# endpoint to show all of this week's tweets (any user)
@app.route("/tweets-week", methods=["GET"])
def get_tweets_week2():
    weekstweets = dict(
        filter(lambda elem: 
                (datetime.now() - datetime.strptime(elem[1]['date'].split(' ')[0], '%Y-%m-%d')).days < 7, 
                tweets.items())
    )
    return jsonify(weekstweets)

# endpoint to create new tweet
@app.route("/checkAvailability", methods=["POST"])
def check_availability():
    source = request.json['source']
    destination = request.json['destination']
    date = request.json['date']
    with mongo_client:
        db = mongo_client['Uber']
        mongo_collection = db['available']
        print(source)

        myquery = {"source": { "$regex": str(source) },"destination": { "$regex": str(destination) },"date": {"$regex": str(date)}}
        cursor = dict()
        cursor = mongo_collection.find(myquery,{"_id": 0})
        records = list(cursor)
        howmany = len(records)
        print('found ' + str(howmany) + ' bookings!')
        sorted_records = sorted(records,key=lambda t: t['source'])
        print(type(sorted_records))
    return jsonify(sorted_records)

# endpoint to create new tweet
@app.route("/book", methods=["POST"])
def book_bus():
    source = request.json['source']
    destination = request.json['destination']
    date = request.json['date']
    startTime = request.json['startTime']
    endTime = request.json['endTime']
    user = request.json['user']
    busnumber = request.json['busnumber']
    booking = dict(user=user, source=source, destination=destination,busnumber=busnumber,
                date=date, startTime=startTime,endTime=endTime,bookeddate=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
               _id=str(ObjectId()))

    insert_one(booking)
    return jsonify(booking)
   

@app.route("/bookings-results", methods=["GET"])
def get_tweets_results():
    global bookings
    with mongo_client:
        db = mongo_client['Uber']
        mongo_collection = db['bookings']

        cursor = mongo_collection.find({})
        records = list(cursor)
        howmany = len(records)
        print('found ' + str(howmany) + ' bookings!')
        sorted_records = sorted(records,key=lambda t: t['source'])
    return jsonify(sorted_records)
        
@app.route("/tweets-week-results", methods=["GET"])
def get_tweets_week_results():
    weektweets = dict(
        filter(lambda elem: 
                (datetime.now() - datetime.strptime(elem[1]['date'].split(' ')[0], '%Y-%m-%d')).days < 7 and
                (
                    False == elem[1]['private']
                ), 
                tweets.items())
    )
    #return jsonify(todaystweets)
    return json.dumps({"results":
        sorted(
            [filter_tweet(k) for k in weektweets.keys()],
            key = lambda t: t['date']
        )
    })

# endpoint to show all of today's tweets (user-specific)
def filter_tweet(t):
    tweet = tweets[t]
    return dict(date=tweet['date'], description=tweet['description'], 
                private=tweet['private'], user=tweet['user'],
                upvote=tweet['upvote'] if 'upvote' in tweet else 0,
                pic=tweet['pic'])
@app.route("/tweets-user-day", methods=["POST"])
def get_tweets_user_day():
    user = request.json['user']
    todaystweets = dict(
        filter(lambda elem: 
                elem[1]['date'].split(' ')[0] == datetime.now().strftime("%Y-%m-%d") and
                (
                    False == elem[1]['private'] or
                    user == elem[1]['user']
                ), 
                tweets.items())
    )
    #return jsonify(todaystweets)
    return jsonify(
        sorted(
            [filter_tweet(k) for k in todaystweets.keys()],
            key = lambda t: t['date']
        )
    )

# endpoint to show all of this week's tweets (user-specific)
@app.route("/tweets-user-week", methods=["POST"])
def get_tweets_user_week():
    user = request.json['user']
    weekstweets = dict(
        filter(lambda elem: 
                (datetime.now() - datetime.strptime(elem[1]['date'].split(' ')[0], '%Y-%m-%d')).days < 7 and
                (
                    False == elem[1]['private'] or
                    user == elem[1]['user']
                ), 
                tweets.items())
    )
    #return jsonify(weekstweets)
    return jsonify(
        sorted(
            [filter_tweet(k) for k in weekstweets.keys()],
            key = lambda t: t['date']
        )
    )


@app.route("/tweets-user-week-results", methods=["GET"])
def get_tweets_user_week_results():
    user = request.json['user']
    weektweets = dict(
        filter(lambda elem: 
                (datetime.now() - datetime.strptime(elem[1]['date'].split(' ')[0], '%Y-%m-%d')).days < 7 and
                (
                    False == elem[1]['private'] or
                    user == elem[1]['user']
                ), 
                tweets.items())
    )
    #return jsonify(todaystweets)
    return json.dumps({"results":
        sorted(
            [filter_tweet(k) for k in weektweets.keys()],
            key = lambda t: t['date']
        )
    })


# endpoint to get tweet detail by id
@app.route("/tweet/<id>", methods=["GET"])
def tweet_detail(id):
    return jsonify(tweets[id])


##################
# Apply from mongo
##################
def applyRecordLevelUpdates():
    return None

def applyCollectionLevelUpdates():
    global bookings
    with mongo_client:
        db = mongo_client['Uber']
        mongo_collection = db['available']

        cursor = mongo_collection.find({})
        records = list(cursor)
        #bookings[0] = records[0]
        
        howmany = len(records)
        print('found ' + str(howmany) + ' bookings!')
        sorted_records = sorted(records,key=lambda t: t['source'])
        #return json.dumps({"results": sorted_records })

        for booking in sorted_records:
            bookings[booking['_id']] = booking


################################################
# Mock
################################################
@app.route("/")
def home(): 
    return """Welcome to online mongo/twitter testing ground!<br />
        <br />
        Run the following endpoints:<br />
        From collection:<br/>
        http://localhost:5000/tweets<br />
        http://localhost:5000/tweets-week<br />
        http://localhost:5000/tweets-week-results<br />
        Create new data:<br />
        http://localhost:5000/mock-tweets<br />
        Optionally, to purge database: http://localhost:5000/purge-db"""


# add new tweet, for testing
@app.route("/dbg-tweet", methods=["GET"])
def dbg_tweet():
    with app.test_client() as c:
        json_data = []
        name = ''.join(random.choices(string.ascii_lowercase, k=7))
        description = ''.join(random.choices(string.ascii_lowercase, k=50))
        print("posting..")
        rv = c.post('/tweet', json={
            'user': name, 'description': description,
            'private': False, 'pic': None
        })
    return rv.get_json()


# endpoint to mock tweets
@app.route("/mock-tweets", methods=["GET"])
def mock_tweets():

    # first, clear all collections
    global tweets
    tweets.clear()

    # create new data
    json_data_all = []
    with app.test_client() as c:
        
        # tweets: 30
        print("@@@ mock-tweets(): tweets..")
        json_data_all.append("@@@ tweets")            
        for i in range(30):
            description = []
            private = random.choice([True, False])
            for j in range(20):
                w = ''.join(random.choices(string.ascii_lowercase, k=random.randint(0,7)))
                description.append(w)
            description = ' '.join(description)
            u = ''.join(random.choices(string.ascii_lowercase, k=7))
            img_gender = random.choice(['women', 'men'])
            img_index = random.choice(range(100))
            img_url = 'https://randomuser.me/api/portraits/' + img_gender + '/' + str(img_index) + '.jpg'
            rv = c.post('/tweet', json={
                'user': u, 'private': private,
                'description': description, 'pic': img_url
            })
            #json_data.append(rv.get_json())
        json_data_all.append(tweets)

    # done!
    print("@@@ mock-tweets(): done!")
    return jsonify(json_data_all)


##################
# ADMINISTRATION #
##################

# This runs once before the first single request
# Used to bootstrap our collections
@app.before_first_request
def before_first_request_func():
    applyCollectionLevelUpdates()

# This runs once before any request
@app.before_request
def before_request_func():
    applyRecordLevelUpdates()


############################
# INFO on containerization #
############################

# To containerize a flask app:
# https://pythonise.com/series/learning-flask/building-a-flask-app-with-docker-compose

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')