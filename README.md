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

For more specific topic, for example Cardano, you should use less iterations. You can play around to find the right balance.

```
python -u twitter_influencers.py seeds/cardano.txt -l 30 -i 2 > results/cardano_30_10_02.tsv
```

## Following inside a list

You can create a list on twitter /lists. And you can allow the script to follow the results, to that specific list.

```
python -u twitter_influencers.py seeds/cardano.txt -l 30 -i 2 --follow_to_list=cardano
```

NOTE: you need to create the list in twitter first


## Results

Checkout the results folder, with some pre-computed results

## Limitation

Due twitter rate limit, the first time you run it, is really slow, be patient.
