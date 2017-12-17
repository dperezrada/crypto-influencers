# Bitcoin and cryptoassets twitter influencers


## The idea

I wanted to know to whom to follow related to this space.

## The process

 - Get seed users
 - Get their following (users they are following)
 - From the total of users, search for the 10 most followed, not already download
 - With those 10 users, we make another iteration.
 - After all iterations are over, we count the most followed users.


## Requirements

 - Python3
 - Twitter credentials, checkout https://apps.twitter.com/

## Install

```
pip install -r requirements.txt
```

Copy config, and edit with your credentials

```
cp config.py.default config.py
```


## Running the script

```
python twitter_influencers.py seeds/influencers_seed.txt -l 250 -n 15 > results/influencers_250_10_15.tsv
```

## Results

Checkout the results folder, with some pre-computed results

## Limitation

Due twitter rate limit, the first time you run it, is really slow, be patient.
