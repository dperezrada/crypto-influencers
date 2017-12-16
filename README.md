# Bitcoin and cryptoassets twitter influencers


## The idea

I wanted to know to whom to follow related to this space.

## The process

 - Get seed users
 - Get their following (users they are following)
 - From the total of users, search for the 10 most followed, not already download
 - With those 10 users, we make another iteration.
 - After all iterations are over, we count the most followed users.

## Example

with parameters: data/all_twitter_user.tsv seeds/influencers_seed.txt 25 10 10
```
85	NickSzabo4
85	aantonop
84	adam3us
80	petertoddbtc
79	SatoshiLite
79	orionwl
78	pwuille
75	barrysilbert
75	balajis
75	TheBlueMatt
75	ErikVoorhees
74	morcosa
73	TuurDemeester
73	bendavenport
71	jgarzik
71	gavinandresen
70	lopp
69	Blockstream
69	VitalikButerin
66	bitcoincoreorg
66	wences
66	naval
66	zooko
66	jerrybrito
65	FEhrsam
65	pmarca
65	virtuallylaw
65	brian_armstrong
64	starkness
63	Melt_Dem
62	jimmysong
62	Excellion
62	roasbeef
61	eric_lombrozo
61	coindesk
60	msantoriESQ
60	rogerkver
59	fredwilson
59	blockchain
59	coinbase
```


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

 - Due twitter rate limit, the first time you run it, is really slow, be patient.
 - We are not checking if the user is related with crypto, Obama, E. Musk, could be between the results.
