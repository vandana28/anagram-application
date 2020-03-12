## Fast Searches for Anagrams - Flask

import requests
from flask import Flask, request,Response
import jsonpickle
import pickle
import redis
import os
import nltk

app = Flask(__name__)

# database  connection to Redis
# redis_db - redis db object that corresponds to lowercase words.
# redis_db2 - redis db object that corresponds to the `dictioanry.txt` format
redis_db = redis.Redis(host="localhost",port = "6379", db=0)
redis_db2 = redis.Redis(host="localhost",port = "6379",db=1)


basedir = os.path.abspath(os.path.dirname(__file__))
data_file = os.path.join(basedir, 'static/dictionary.txt')

# removed the last character of the word which was `\n` while storing in redis db.
with open(data_file, "r") as file:
    for line in file.readlines():
        redis_db.set(line[:-1].lower(), "")
        redis_db2.set(line[:-1], "")


## Abstracted functions
def generate_anagrams(word):  
    word = word.lower()
    if len(word) <=1:
        return word
    else:
        anagrams = []
        for perm in generate_anagrams(word[1:]):
            for i in range(len(word)):
                curr = perm[:i] + word[0:1] + perm[i:]
                anagrams.append(curr)
                
        return anagrams

def groupAnagrams():
    max_anagrams = {}
    for key in redis_db.scan_iter("*"):
        key = key.decode("utf-8")
        sortedword = "".join(sorted(key))
        if sortedword in max_anagrams:
            max_anagrams[sortedword].append(key)
        else:
            max_anagrams[sortedword] = [key]
    return max_anagrams


# this scans the second redis db, that has all uppercases and lowercases, 
# returns the list of proper nouns
def listProperNouns():
    all_words = []
    properNoun_words = []
    for key in redis_db2.scan_iter("*"):
        key = key.decode("utf-8")
        all_words.append(key)
    for word in all_words:
        tagged_word = nltk.tag.pos_tag([word])
        if tagged_word[0][1] == 'NNP':
            properNoun_words.append(tagged_word[0][0])
    return (all_words,properNoun_words)
   
# 1. Adding words to redis corpus.
@app.route('/words.json',methods=['POST'])
def addwords():
    data = request.get_json(force = True)
    for word in data["words"]:
        word = word.lower()
        if redis_db.get(word) == None:
            redis_db.set(word,"")   
    message = "Words have been added to the corpus"

    return Response(response=message, status=201, mimetype="text/html")

# 2. Endpoint to find anagrams of a current word. Limit parameter included
@app.route('/anagrams/<X>',methods=['GET'])
def findAnagrams(X):
    new_word = X.split(".")[0] 
    limit_value = request.args.get('limit')
    anagrams_returned = []
    final_anagrams = []
    anagrams_returned = generate_anagrams(new_word)
    for words in anagrams_returned:
        if redis_db.exists(words) and words != new_word:
            final_anagrams.append(words)
    if limit_value:
        response = {

            "anagrams": final_anagrams[:int(limit_value)]
        }
    else:
        response = {

            "anagrams": final_anagrams
        }

    # reponse is pickled through jsonpickle library in python and sent as a response
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled,status=200, mimetype="application/json")

#  3. Endpoint to delete a particular word in redis
@app.route('/words/<X>',methods=['DELETE'])
def deleteword(X):
    new_word = X.split(".")[0] 
    if redis_db.exists(new_word):
        redis_db.delete(new_word)
        return Response(status=204,mimetype="text/html")

    else:
        message = "Word not found"
        return Response(response=message,status=404,mimetype="text/html")

# 4. Endpoint to delete all words 
@app.route('/words.json',methods=['DELETE'])
def deleteDataStore():
    redis_db.flushall()
    return Response(status=204,mimetype="text/html")


### optional endpoints

### 1. Endpoint that returns a count of words in the corpus and min/max/median/average word length
@app.route('/calculatemetrics',methods = ['GET'])
def calculateMetrics():
    all_words = []
    number_ofwords = redis_db.dbsize()
    for key in redis_db.scan_iter("*"):
        all_words.append(key.decode("utf-8"))
    minimum_length = len(min(all_words,key=len))
    maximum_length = len(max(all_words,key=len))
    average_length = round(sum(len(word) for word in all_words)/number_ofwords)
    sorted_array = sorted(all_words,key=len)
    median_length = round((len(sorted_array[0])+len(sorted_array[-1]))/2)
    response = {
        "corpus word count " : number_ofwords,
        "minimum word length" : minimum_length,
        "maximum word length" : maximum_length,
        "average word length" : average_length,
        "Median word length" : median_length

    }
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled,status=200, mimetype="application/json")

#### 2. Endpoint that identifies words with the most anagrams
@app.route('/getmaxanagrams',methods = ['GET'])
def maxAnagrams():
    max_anagrams = groupAnagrams()
    max_length = (max(max_anagrams.items(), key = lambda k : len(k[1])))
    max_value = len(max_length[1])
    final = {}
    for key,value in max_anagrams.items():
        if len(value) == max_value:
            final[key] = value
    response ={
        "max_angrams" : final
    }

    # print([{key:value} for key,value in max_anagrams.items() if len(value)== max_value])  

    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled,status=200, mimetype="application/json")


## 3. Endpoint to delete a word *and all of its anagrams*
@app.route('/delwordanagrams/<X>',methods = ['DELETE'])
def delWordAnagrams(X):
    new_word = X.split(".")[0]  
    anagram_list = []
    anagram_list = generate_anagrams(new_word)
    redis_db.delete(new_word)
    for word in anagram_list:
        redis_db.delete(word)

    return Response(status=204,mimetype="text/html")


## 4. Endpoint that takes a set of words and returns whether or not they are all anagrams of each other
@app.route('/checkanagrams/words.json',methods = ['GET'])
def checkanagrams():
    data = request.get_json(force = True)
    max_anagrams ={}
    for word in data["words"]:
        sortedword = "".join(sorted(word))
        if sortedword in max_anagrams:
            max_anagrams[sortedword].append(word)
        else:
            max_anagrams[sortedword] = [word]

    # the logic here is that, if all the words are anagrams of each other, there should exist only 1 key in the dictionary.
    # if there are two keys, then there are two groups of anagrams which refer to different letters.
    if len(max_anagrams.items()) == 1:
        return Response(response = "True, they are anagrams of each other",status=200,mimetype="text/html")
    else:
        return Response(response = "False, Not anagrams of each other",status=200,mimetype="text/html")


## 5. Endpoint to return all anagram groups of size >= *x*
@app.route('/groupsize',methods= ['GET'])
def anagramGroupSize():
    size = request.args.get('size')
    groups = groupAnagrams()
    final = {}
    for key,value in groups.items():
        if len(value) >=int(size):
            final[key] = value
    response ={
        "groups" : final
    }    

    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled,status=200, mimetype="application/json")


## 6. Respect a query param for whether or not to include proper nouns in the list of anagrams


''' 1. if proper nouns can be included as anagarms(TRUE), all words are treated as normal and it
    it doesn't matter if their upper case or lower case. So the general anagram function can be utilized.

    2. the generate anagrams function converts the word into lower case before checking the redis database

    3.If proper nouns cannot be included as anagrams(FALSE), we need to discard them from the list of all words 
    . Once the proper nouns are removed, the  remaining words are converted to lower case and the 
        anagrams are then computed. Redis db 2 is scanned to obtain proper nouns. 
'''
@app.route('/propernoun/<X>',methods = ['GET'])
def propernoun(X):
    properNounFlag = request.args.get('flag')
    new_word = X.split(".")[0] 
    anagram_list = []
    final_anagrams = []
    response = {}

    if properNounFlag == 'true':
            anagram_list = generate_anagrams(str(new_word))
            for word in anagram_list:
                if redis_db.exists(word) and word!=new_word:
                    final_anagrams.append(word)
            response ={
                'anagrams':final_anagrams
            }

    elif properNounFlag == "false":
        all_list,propernoun_list = listProperNouns()
        for word in propernoun_list:
            all_list.remove(word)
        lower_case = [word.lower() for word in all_list]
        anagram_list = generate_anagrams(str(new_word))
        for word in anagram_list:
                if word in lower_case and word != new_word:
                    final_anagrams.append(word)
        response ={
                'anagrams':final_anagrams
            }

    else:
        response = {
            "Error" : "Invalid Input"
        }

    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled,status=200, mimetype="application/json")


app.run(host="localhost", port=3000)
