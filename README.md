# Fast Searches for Anagrams 

**Question Prompt** 

The project is to build an API that allows fast searches for anagrams.`dictionary.txt` is a text file containing every word in the English dictionary. Ingesting the file doesn’t need to be fast, and you can store as much data in memory as you like.

## Implementation Details

- I used python's Flask framework to construct my server. Flask, being a micro-framework  is easy to use, and can be utilized for minimalistic web applications. Flask is also easy to set up because there is very little boilerplate code for getting a simple application running. Since the anagram application is a small scale application , I felt that flask would be good way to approach the problem.

- I used the Redis key-value store to store the words of the dictionaries as keys in Redis. Redis is simple to set up and it stores data as key-values pairs as large as 512 MB. Being an in-memory database, data retrieval is much faster than an relational database. Additionally, the problem statement permitted the usage of large amounts of memory and Redis was the perfect choice for this project. Moreover, Redis doesn’t require a schema to be set up. Redis works well for this project but could be too big of a tradeoff for large applications. 

- I additionally used the NLTK's Parts of a speech tagger to detect whether or not a word is a proper noun. The package tags a word with 'NNP' if it is a proper noun. This is essential because non-proper nouns can be stored with a capital letter in the file. Additionally, words such as 'Alphonsine' and 'Canberra' weren't detected as proper nouns by NLTK's POS tagger. POS tagger works well with sentences and phrases since it takes into consideration the word that are located before and after the current word. Moreover, it apply rules to eliminate certain tags for a word based on its context.Even though the keys in 
Redis aren't sentences, the POS tagger is an efficient method to filter out proper nouns from the list of redis keys.


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
6. restart redis server - redis-server
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

## Endpoints:

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

## Testing:

I tested all endpoints using POSTMAN API client by providing appropriate sample inputs.
Additionally I ran the `anagram_test.rb` script to test the mandatory endpoints.


1. adding words to the corpus:

```{bash}
curl -i -X POST -d '{ "words": ["read", "dear", "dare"] }' http://localhost:3000/words.json
HTTP/1.0 201 CREATED
...
Words have been added to the corpus% 
```

2. Fetching anagrams:
```{bash}
curl -i http://localhost:3000/anagrams/read.json
HTTP/1.0 200 OK
...
{"anagrams": ["ared", "dear", "dare", "daer"]}% 
```

3. Specifying maximum number of anagrams
```{bash}
curl -i http://localhost:3000/anagrams/read.json?limit=1
HTTP/1.0 200 OK
...
{"anagrams": ["ared"]}% 
```

4. Delete single word
```{bash}
curl -i -X DELETE http://localhost:3000/words/read.json
HTTP/1.0 204 NO CONTENT
...
```
5. Delete all words
```{bash}
curl -i -X DELETE http://localhost:3000/words.json
HTTP/1.0 204 NO CONTENT
...
```

6. Calculate Metrics
```{bash}
curl -i -X GET http://localhost:3000/calculatemetrics
HTTP/1.0 200 OK
...
{"Median word length": 12, "average word length": 10, "corpus word count ": 234371, "maximum word length": 24, "minimum word length": 1}%  
```

7. Maximum anagram groups

- (**Note:** Some words in the dictionary maybe be proper nouns but they are stored in their lower case and they happen be anagrams of common words. For instance: words such as 'organ' and 'groan' have anagrams such as 'orang' which is short for Orangutan)
```{bash}
curl -i -X GET http://localhost:3000/getmaxanagrams
HTTP/1.0 200 OK
...
{"max_angrams": 
{"aelps": ["sepal", "lapse", "salep", "pales", "saple", "speal", "elaps", "spale", "lepas", "slape"], 
"agnor": ["grano", "rogan", "organ", "argon", "nagor", "ronga", "groan", "angor", "goran", "orang"]}}% 
```

8. Delete a word and all of its anagrams
```{bash}
curl -i -X DELETE 'http://localhost:3000/delwordanagrams/read.json'
HTTP/1.0 204 NO CONTENT
...
```

9. Check if a set of words are anagrams of each other
```{bash}
curl -i -X GET -d '{ "words": ["read", "dear", "dare"] }' http://localhost:3000/checkanagrams/words.json
HTTP/1.0 200 OK
...
True, they are anagrams of each other%

curl -i -X GET -d '{ "words": ["read", "dear", "darr"] }' http://localhost:3000/checkanagrams/words.json
HTTP/1.0 200 OK
...
False, Not anagrams of each other%     
```
10. Return anagrams of a certain group size
```{bash}
curl -i -X GET 'http://localhost:3000/groupsize?size=7'
HTTP/1.0 200 OK
...
sample output : {"groups": 
{"aacinr": ["crania", "acinar", "carina", "carian", "canari", "arnica", "narica"],
"abeilt": ["albeit", "albite", "baltei", "bletia", "belait", "libate", "betail"] }
```
11. Include proper nouns
```{bash}
curl -i -X GET 'http://localhost:3000/propernoun/sail.json?flag=false'
HTTP/1.0 200 OK
...

{"anagrams": ["sial", "lasi", "lias"]}% 
```
- **Note** : Here when the proper noun flag is false ( meaning I can't include proper nouns), the word 'Lisa' from dictionary.txt is not included
```{bash}
 curl -i -X GET 'http://localhost:3000/propernoun/sail.json?flag=true' 
HTTP/1.0 200 OK
...

{"anagrams": ["sial", "lasi", "lisa", "lias"]}% -> When proper nouns can be included, they are converted to lowercase for convenience sake. Here the word 'Lisa' is included in the list of anagrams
```


## Additional features that can be added to the API:

1. An API that returns anagrams of a word that start with a particular letter. For instance, return anagrams of 'read' that start with 'd' => {'dear','dare'}

2. An API that returns the position of a particular letter in a group of anagrams. Eg: the letter 'e' is at position 2 for 'dear' and position 4 for 'dare'

3. An API that generates the tenses of words and check if they are are anagrams of a particular word. For instance, the word 'education' is in the dictionary but its anagrams 'auctioned' and 'cautioned' are the past tense of words 'auction' and 'caution' in the dictionary. Tenses can be generated using [nodeBox - Linguistics](https://www.nodebox.net/code/index.php/Linguistics#verb_conjugation)

4. An API that generates anagrams of phrases instead of words.

## Edge Cases:

1. Edge cases included whether or not to convert the word to lowercase while storing in Redis. To make operations uniform I stored all words in Redis in their lowercases. Additionally when the user provides an input word that is in its uppercase, I've converted the word to lowercase before processing it.
- However I encountered a problem while dealing with the proper noun endpoint where I had to include proper nouns which were anagrams of the current word to the list. For this purpose I created another redis database that stored words similar to dictionary.txt and compared the current word with words in the second database.

2. Handled the edge case when 'delete a word' endpoint was called again on a word that was non-existant in the database.


## Design Overview and trade-offs

- The entire dictionary is ingested once into Redis. I'm maintaining two redis databases, one that works with words in their lower cases and the other database mimics the words of the dictionary text file. I created two databases to avoid conficts when the proper noun end point is triggered. I used the NLTK library to identify proper nouns in the second database and created a separate list L1 that excluded proper nouns. Finally, the anagrams obtained in L1 don't contain proper nouns. 

- Since, the focus was on fast retrieval of words, I decided to have additional memory to aid my process. Here the trade-off was to give time more priority than space. 

-Throughout my program, I abstracted similar functionality into separate functions to make the code less coupled and cleaner.

- Another trade-off arose when deciding to use Flask or Django. Flask being a minimalistic framework lacks some functionality when compared to a full-fledged framework such as Django. For instance Flask lacks authetication, input validation etc and it requires third-party plugins to help faciliate these functions. However Flask is very easy to use and extensible. Since Flask keeps the core simple and lightweight, it was the perfect framework to use for this application.













