import sys
import os
import json
import argparse
from time import sleep
from collections import Counter
from config import AUTH_TOKEN, AUTH_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET
import twitter


def process_previous_file(target_file):
    already_download_users = {}
    if os.path.exists(target_file):
        for line in open(target_file).readlines():
            try:
                twitter_user, following_user, _ = line.split('\t')
                if not already_download_users.get(twitter_user):
                    already_download_users[twitter_user] = []
                already_download_users[twitter_user].append(following_user)
            except:
                continue
    return already_download_users

def get_detailed_information(target_file, users):
    detail_info = {}
    if os.path.exists(target_file):
        for line in open(target_file).readlines():
            try:
                _, following_user, user_data = line.split('\t')
                if following_user in users and detail_info.get(following_user) is None:
                    detail_info[following_user] = json.loads(user_data)
            except:
                continue
    return detail_info

def split_in_sublist(sublist_size, list_):
    return [
        list_[i:i+sublist_size]
        for i  in range(0, len(list_), sublist_size)
    ]

def get_user_following(twitter_client, twitter_user, max_followers=1000):
    friend_ids = twitter_client.GetFriendIDsPaged(
        screen_name=twitter_user,
        count=5000
    )[2][-max_followers:] # Get the first X (max_followers) results
    following_users = []
    for user_ids_row in split_in_sublist(100, friend_ids):
        for user_info in twitter_client.UsersLookup(user_id=user_ids_row):
            following_users.append(
                [
                    user_info.screen_name,
                    user_info.AsJsonString()
                ]
            )
        sleep(3)
    sleep(60)
    return following_users


def get_pending_not_download(already_download_users, pending_users):
    pending_not_download_users = []
    for user in pending_users:
        if user not in already_download_users:
            pending_not_download_users.append(user)
    return pending_not_download_users


def write_user_to_file(_file, twitter_user, following_user, data):
    _file.write(
        "%s\t%s\t%s\n" % (
            twitter_user.replace('\t', ''),
            following_user.replace('\t', ''),
            data.replace('\t', ''),
        )
    )

def get_top_following(all_users, already_download_users):
    top_following_counter = Counter()
    for user in all_users:
        if user:
            top_following_counter.update(already_download_users[user])
    return top_following_counter

def get_users_to_download(top_following, all_users, users_per_iter=10):
    selected_users = []
    for following_user, _ in top_following.most_common():
        if len(selected_users) > users_per_iter:
            break
        if following_user not in all_users:
            selected_users.append(following_user)
    return selected_users

def generate_final_result(
        all_users, already_download_users, top_x=500, detail=False, target_file=None
    ):
    top_users = Counter([
        following_user
        for user in all_users
        for following_user in already_download_users[user]
    ])
    print("\nFinal results:", file=sys.stderr)
    if top_x == -1:
        most_common = top_users.most_common()
    else:
        most_common = top_users.most_common(top_x)
    most_common_screen_names = [user_row[0] for user_row in most_common]
    if detail:
        detail_info = get_detailed_information(target_file, most_common_screen_names)
    for user, user_counter in most_common:
        print("%s\t@%s" % (user_counter, user))
        if detail:
            description = detail_info[user].get('description', '').replace('\n', ' ')
            last_tweet = detail_info[user].get('status', {}).get('text', '').replace('\n', ' ')
            print("\t%s" % description)
            print("\t%s" % last_tweet)
            print("")
    return most_common_screen_names


def retrieve_influencers(
        twitter_client, target_file, initial_users_file, users_per_iter=10,
        iterations=10, top_x=500, detail=False
    ):
    # TODO: split this method

    already_download_users = process_previous_file(target_file)
    initial_users = [
        user
        for user in open(initial_users_file).read().replace('@', '').replace(' ', '').split('\n')
        if user
    ]

    all_users = initial_users
    selected_users = initial_users

    with open(target_file, 'a') as _file:
        current_iteration = 1
        for current_iteration in range(1, iterations + 1):
            print("iteration %s" % current_iteration, file=sys.stderr)
            print("\tUsers:\n\t%s" % "\n\t".join(selected_users), file=sys.stderr)
            for twitter_user in selected_users:
                if twitter_user and already_download_users.get(twitter_user) is None:
                    print("downloading user: %s" % twitter_user, file=sys.stderr)
                    following_users = get_user_following(twitter_client, twitter_user)
                    total_following = len(following_users)
                    already_download_users[twitter_user] = []
                    if total_following > 0:
                        for following_user in following_users:
                            already_download_users[twitter_user].append(following_user[0])
                            write_user_to_file(
                                _file, twitter_user, following_user[0], following_user[1]
                            )
                    else:
                        write_user_to_file(_file, twitter_user, '', '{}')
            top_following = get_top_following(all_users, already_download_users)
            if current_iteration < iterations:
                selected_users = get_users_to_download(top_following, all_users, users_per_iter)
                all_users += selected_users
    influencers = generate_final_result(
        all_users, already_download_users, top_x, detail, target_file
    )
    return influencers

def follow_within_list(twitter_client, list_name, influencers):
    twitter_lists = twitter_client.GetListsList()
    list_id = None
    for list_ in twitter_lists:
        if list_.slug == list_name:
            list_id = list_.id
    if list_id:
        for influencers_batch in split_in_sublist(100, influencers):
            twitter_client.CreateListsMember(list_id=list_id, screen_name=influencers_batch)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "initial_users_file",
        help="Path to the file with a list of twitter screen_name to start the iterations",
        type=str
    )
    parser.add_argument(
        "-f", "--db_file",
        help="Location to store the tmp collected data. Default: /tmp/crypto_influencers.tsv",
        type=str, action='store', default="/tmp/crypto_influencers.tsv"
    )
    parser.add_argument(
        "-l", "--limit", help="Retrieve up to X results. Default: 200. Use -1 for no limit",
        type=int, action='store', default=200
    )
    parser.add_argument(
        "-n", "--users_per_iter", help="Number of users to retrieve information for each iteration",
        type=int, action='store', default=10
    )
    parser.add_argument(
        "-i", "--iterations", help="Number of iterations. Default: 10.",
        type=int, action='store', default=10
    )
    parser.add_argument(
        "-d", "--show_details", help="Show tweets details. Default: False.",
        action='store_true', default=False
    )
    parser.add_argument(
        "--follow_to_list",
        help="Name of the twitter list, to add all the users as members. Default: ''.",
        type=str, action='store'
    )
    args = parser.parse_args()

    twitter_client = twitter.Api(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token_key=AUTH_TOKEN,
        access_token_secret=AUTH_TOKEN_SECRET
    )

    influencers = retrieve_influencers(
        twitter_client, args.db_file, args.initial_users_file, args.users_per_iter,
        args.iterations, args.limit, detail=args.show_details
    )
    if args.follow_to_list:
        follow_within_list(twitter_client, args.follow_to_list, influencers)


if __name__ == '__main__':
    main()
