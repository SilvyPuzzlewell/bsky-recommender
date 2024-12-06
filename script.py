import requests
import pickle

def get_batch(handle, cursor=""):
    if not cursor:
        batch_jsn = requests.get(f"https://public.api.bsky.app/xrpc/app.bsky.graph.getFollows?actor={handle}").json()
    else:
        batch_jsn = requests.get(f"https://public.api.bsky.app/xrpc/app.bsky.graph.getFollows?actor={handle}&cursor={cursor}").json()
    cursor = batch_jsn["cursor"] if "cursor" in batch_jsn else None
    cur_handles = {follow["handle"] for follow in batch_jsn["follows"]} if "follows" in batch_jsn else set()
    return cursor, cur_handles

def get_follows_for_handle(handle, limit=10000):
    handles = set()
    cursor, new_handles = get_batch(handle)
    handles |= new_handles
    while cursor and len(handles) <= limit:
        cursor, new_handles = get_batch(handle, cursor)
        handles |= new_handles
    return handles

def count_shared_follows(follows_follow_handles: list[set[str]]):
    counter = {}
    for handle_set in follows_follow_handles:
        for handle in handle_set:
            if handle not in counter:
                counter[handle] = 1
            else:
                counter[handle] += 1
    return counter

def get_shared_followers(q_handle):
    q_follows = get_follows_for_handle(q_handle)
    follows_follow_handles = []
    print(f"number of followers for {q_handle}: {len(q_follows)}")
    for i, follow in enumerate(q_follows):
        print(f"processing {i}/{len(q_follows)}, follower {follow}")
        follows_follow_handles.append(get_follows_for_handle(follow))
    counter = count_shared_follows(follows_follow_handles)
    return counter, q_follows

def shared_followers_for_handle(handle):
    result, queried_follows = get_shared_followers(handle)
    if handle in result:
        del result[handle]
    for follow in queried_follows:
        if follow in result:
            del result[follow]
    data = sorted(result.items(), key=lambda x: x[1], reverse=True)
    return data

