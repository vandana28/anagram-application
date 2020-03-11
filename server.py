import requests
from flask import Flask, request,Response
import jsonpickle
import pickle
import redis
import os
import nltk

app = Flask(__name__)

redis_db = redis.Redis(host="localhost",port = "6379", db=0)
redis_db2 = redis.Redis(host="localhost",port = "6379",db=1)


basedir = os.path.abspath(os.path.dirname(__file__))
data_file = os.path.join(basedir, 'static/dictionary.txt')

with open(data_file, "r") as file:
    for line in file.readlines():
        redis_db.set(line[:-1].lower(), "")
        redis_db2.set(line[:-1], "")



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
   
@app.route('/words.json',methods=['POST'])
def addwords():
    data = request.get_json(force = True)
    for word in data["words"]:
        word = word.lower()
        if redis_db.get(word) == None:
            redis_db.set(word,"")   
        # redis_db.set(word, pickle.dumps(anagrams))
        # print(pickle.loads(redis_db.get(word)))
    message = "Words have been added to the corpus"

    return Response(response=message, status=201, mimetype="text/html")

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

    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled,status=200, mimetype="application/json")

@app.route('/words/<X>',methods=['DELETE'])
def deleteword(X):
    new_word = X.split(".")[0] 
    if redis_db.exists(new_word):
        redis_db.delete(new_word)
        return Response(status=204,mimetype="text/html")

    else:
        message = "Word not found"
        return Response(response=message,status=404,mimetype="text/html")

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
    print([{key:value} for key,value in max_anagrams.items() if len(value)== max_value])  
    return Response(response='Groups with maximum anagrams returned',status = 200,mimetype="text/html")


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
    anagrams = groupAnagrams()
    if len(anagrams.items()) == 1:
        return Response(response = "True, they are anagrams of each other",status=200,mimetype="text/html")
    else:
        return Response(response = "False, Not anagrams of each other",status=200,mimetype="text/html")


## 5. Endpoint to return all anagram groups of size >= *x*
@app.route('/groupsize',methods= ['GET'])
def anagramGroupSize():
    size = request.args.get('size')
    groups = groupAnagrams()
    for key,value in groups.items():
        if len(value) >=int(size):
            print(key,value)
 
    return Response(response='Anagrams of required group size returned',status = 200,mimetype="text/html")


## 6. Respect a query param for whether or not to include proper nouns in the list of anagrams

''' for proper nouns, the redis db needs to be filled with common nouns and proper nouns
 if proper nouns can be included, then anagrams can be found and should be equated 
to lower case of the redis word. '''
''' if proper nouns can be included as anagarms, all words are treated as normal and it
    it doesn't matter if their upper case or lower case.'''
    # generate anagrams will convert the word into lower case before checking
''' If proper nouns cannot be included as anagrams, we need to discard them from 
the all words list in redis, convert the remaining all_words to lower case and then
compute the anagrams
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