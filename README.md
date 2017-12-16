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
python -u twitter_influencers.py data/all_twitter_user.tsv  seeds/bitcoin-core_seed.txt 1000 10 15 > results/bitcoin-core_seed_1000_10_15.tsv
```

## Results

Checkout the results folder, with some pre-computed results

## Limitation

Due twitter rate limit, the first time you run it, is really slow, be patient.
