# Fast Searches for Anagrams 

**Question Prompt** 

The project is to build an API that allows fast searches for anagrams.`dictionary.txt` is a text file containing every word in the English dictionary. Ingesting the file doesn’t need to be fast, and you can store as much data in memory as you like.

## Implementation Details

- I used python's Flask framework to construct my server. Flask, being a micro-framework  is easy to use, and can be utilized for minimalistic web applications. Flask is also easy to set up because there is very little boilerplate code for getting a simple application running. Since the anagram application is a small scale application , I felt that flask would be good way to approach the problem.

- I used the Redis key-value store to store the words of the dictionaries as keys in Redis. Redis is simple to set up and it stores data as key-values pairs as large as 512 MB. Being an in-memory database, data retrieval is much faster than an relational database. Additionally, the problem statement permitted the usage of large amounts of memory and Redis was the perfect choice for this project. Moreover, Redis doesn’t require a schema to be set up. Redis works well for this project but could be too big of a tradeoff for large applications. 

- Used the NLTK's Parts of a speech tagger to detect whether or not a word is a proper noun. A proper noun doesn't nescessarily have to start with a capital letter. NLTK's POS tagger tags proper nouns as NNP. This is an efficient method to filter out proper nouns from the list of redis keys.


## Installations and Running the server

1. Flask Installation

```{bash}
pip install flask
```

2. Redis Installation 

```{bash}
pip install redis 
```
If the above command doesn't import redis, then use the following:

```{bash}
Download from [http://download.redis.io/redis-stable.tar.gz](http://download.redis.io/redis-stable.tar.gz)
Open a terminal and write the following:
1. tar xvzf redis-stable.tar.gz
2. cd redis-stable
3. make
4. Add export PATH=$PATH:$HOME/Downloads/redis-stable/src to zshrc on Mac
5. source ~/.zshrc
6. restart redis server
```
To start and stop Redis:

- Start : 
```{bash} 
redis-server 
```
- Check if Redis is running : 
```{bash} 
redis-cli ping
``` 
will provide an output 'PONG'

- Stop : 
```{bash}
redis-cli shutdown
```

3. NLTK Installation

```{bash}
 pip install nltk 
    (or)
 sudo pip install -U nltk
```
4. To run the app:

```{bash}
python3 server.py
```
5. To check in browser:

```{bash}
http://localhost:3000/<endpoint>
```

6. To run the tests:

```{bash}
ruby anagram_test.rb
```

## Endpoints and testing:

- `POST /words.json`: Takes a JSON array of English-language words and adds them to the corpus (data store).
- `GET /anagrams/:word.json`: Returns a JSON array of English-language words that are anagrams of the word passed in the URL.This endpoint should support an optional query param that indicates the maximum number of results to return.
- `DELETE /words/:word.json`: Deletes a single word from the data store.
- `DELETE /words.json`: Deletes all contents of the data store.
- `GET /calculatemetrics`: returns a count of words in the corpus and min/max/median/average word length
- `GET /getmaxanagrams` : Endpoint that identifies words with the most anagrams
- `DELETE /delwordanagrams` : Endpoint to delete a word *and all of its anagrams*
- `GET /checkanagrams/words.json` : Endpoint that takes a set of words and returns whether or not they are all anagrams of each other
- `GET /groupsize` : Endpoint to return all anagram groups of size >= *x*
- `GET /propernoun/:word.json` : Respect a query param for whether or not to include proper nouns in the list of anagrams




## Additional features that can be added to the API:

1. An API that returns anagrams of a word that start with a particular letter. For instance, return anagrams of 'read' that start with 'd' => {'dear','dare'}

2. An API that returns the position of a particular letter in a group of anagrams.

3. An API that generates the tenses of words and check if they are are anagrams of a particular word. For instance, the word 'education' is in the dictionary but its anagrams
'auctioned' and 'cautioned' are the past tense of words 'auction' and 'caution' in the dictionary. Tenses can be generated using the Natural Processing language toolkit in python.

4. An API that generates anagrams of phrases instead of words.

## Edge Cases:

1. Edge cases included whether or not to convert the word to lowercase while storing in Redis. To make operations uniform I stored all words in Redis in their lowercase. However I encountered a problem while dealing with the proper noun endpoint where I had to obtain the proper nouns which were anagrams of the current word. For this purpose I created another redis database that stored words in the form as that of dictionary.txt and compared the current word with those words.

2. Handled the edge case when the 'delete a word' endpoint was called again on a word that was non-existant in the database


## Design Overview and trade-offs










