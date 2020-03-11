# Fast Searches for Anagrams - Ibotta 

**Question Prompt** 

The project is to build an API that allows fast searches for anagrams.`dictionary.txt` is a text file containing every word in the English dictionary. Ingesting the file doesn’t need to be fast, and you can store as much data in memory as you like.

## Implementation Details

- I used python's Flask framework to construct my server. Flask, being a micro-framework  is easy to use, and can be utilized for minimalistic web applications. Flask is also easy to set up because there is very little boilerplate code for getting a simple application running. Since the anagram application is a small scale application , I felt that flask would be good way to approach the problem.

- I used the Redis key-value store to store the words of the dictionaries as keys in Redis. Redis is simple to set up and it stores data as key-values pairs as large as 512 MB. Being an in-memory database, data retrieval is much faster than an relational database. Additionally, the problem statement permitted the usage of large amounts of memory and Redis was the perfect choice for this project. Moreover, Redis doesn’t require a schema to be set up. Redis works well for this project but could be too big of a tradeoff for large applications. 


## Installations and Running the server

1. Flask Installation

```{bash}
pip install flask
```




