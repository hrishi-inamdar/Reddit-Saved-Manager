import praw
import json


def reverse_order(list):
    print('unsaving')
    for x in list:
        x.unsave()
    print('saving')
    for x in list:
        x.save()


def export_to_file(list):
    export_file = open('exported.txt', 'w+')
    export_obj = []
    for thing in list:
        if isinstance(thing, praw.models.Submission):
            export_obj += [{'type': 0, 'id': thing.id, 'title': thing.title, 'url': thing.url}]
        else:  # if it's a comment...
            export_obj += [{'type': 1, 'id': thing.id, 'body': thing.body}]
    export_file.write(json.dumps(export_obj))
    export_file.close()


def export_to_list(reddit, redditor, num):
    export_obj = []
    for thing in reddit.redditor(redditor).saved(limit=num):
        export_obj += [thing]
    return export_obj


def find_changed_extent(old_list, new_list):
    changed_extent = -1  # how much of the list has been changed from the top
    size = len(old_list)
    for i in range(size):
        x = size - i - 1
        if old_list[x] != new_list[x]:
            changed_extent = x
            break
    return changed_extent


def export_to_reddit(old_list, new_list):
    changed_extent = find_changed_extent(old_list, new_list)
    if changed_extent == -1:
        return
    changed_list = new_list[0:changed_extent+1]
    print('unsaving...')
    for sub in changed_list:
        sub.unsave()
    print('saving...')
    for sub in reversed(changed_list):
        sub.save()


def print_saved(list):
    for thing in list:
        print(thing.title)


# nonfunctional
def import_saved():
    file = open('exported.txt', 'r')


def get_list():
    redditor = 'manawan7'
    reddit = praw.Reddit(redditor)
    saved_list = export_to_list(reddit, redditor, None)
    return saved_list
