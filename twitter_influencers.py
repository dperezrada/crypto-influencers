import sys
import os
from time import sleep
from collections import Counter
from config import AUTH_TOKEN, AUTH_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET
import twitter


def process_previous_file(target_file):
    already_download_users = {}
    if os.path.exists(target_file):
        for line in open(sys.argv[1]).readlines():
            try:
                twitter_user, following_user, _ = line.split('\t')
                if not already_download_users.get(twitter_user):
                    already_download_users[twitter_user] = []
                already_download_users[twitter_user].append(following_user)
            except:
                continue
    return already_download_users

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

def generate_final_result(all_users, already_download_users, top_x=500):
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
    for user, user_counter in most_common:
        print("%s\t%s" % (user_counter, user))

def retrieve_influencers(
        target_file, initial_users_file,
        users_per_iter=10, iterations=10, top_x=500
    ):
    twitter_client = twitter.Api(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token_key=AUTH_TOKEN,
        access_token_secret=AUTH_TOKEN_SECRET
    )

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
            print("selected users:\n\t%s" % "\n\t".join(selected_users), file=sys.stderr)
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
    generate_final_result(all_users, already_download_users, top_x)


def main():
    if len(sys.argv) < 3:
        print(
            'Usage:\n\n' + os.path.basename(sys.argv[0]) +
            ' <db_file> <initial_users_file> [top_x] [users_per_it] [iterations]'
        )
    target_file = sys.argv[1]
    initial_users_file = sys.argv[2]
    if len(sys.argv) > 3:
        top_x = int(sys.argv[3])
    else:
        top_x = 500
    if len(sys.argv) > 4:
        users_per_iter = int(sys.argv[4])
    else:
        users_per_iter = 10
    if len(sys.argv) > 5:
        iterations = int(sys.argv[5])
    else:
        iterations = 10
    retrieve_influencers(target_file, initial_users_file, users_per_iter, iterations, top_x)

if __name__ == '__main__':
    main()
