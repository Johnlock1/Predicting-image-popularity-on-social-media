import json
import lzma

from datetime import datetime

def update_dict(dict, element):
    if element in dict:
        dict[element] += 1
    else:
        dict[element] = 1

def get_created_datetime(file):
    unix_ts = os.path.getmtime(file)
    date_ts = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    return (unix_ts, date_ts)

'''
Functions for figuring the type of a file
'''
def is_filetype(extension, name):
    return extension in name

def is_json_xz(name):
    return is_filetype('.json.xz', name)

def is_jpg(name):
    return is_filetype('.jpg', name)

'''
Functions for handing the json with metadata
'''
def read_compessed_json(path, filename):
    with lzma.open(f'{path}{filename}', mode='rt') as file:
        return json.load(file)

def write_json(path, filename):
    with open(f'{path}{filename}', 'w') as f:
        json.dump(json_data, f)

'''
Functions for retrieving certain properties from the metadata json file
'''
def get_post_type(json_data):
    return json_data['node']['__typename']

def get_shortcode(json_data):
    return json_data['node']['shortcode']

def get_post_timestamp(json_data):
    unix_timestamp = json_data['node']['taken_at_timestamp']
    date_timstamp = datetime.utcfromtimestamp(unix_timestamp).strftime('%Y-%m-%d %H:%M:%S')
    return (unix_timestamp, date_timstamp)

def get_likes(json_data):
    return json_data['node']['edge_media_preview_like']['count']

def get_comments(json_data):
    return json_data['node']['edge_media_to_comment']['count']

def get_number_of_images_on_post(json_data):
    try:
        return len(json_data['node']['edge_sidecar_to_children']['edges'])
    except KeyError:
        return 1

def is_video(json_data):
    return json_data['node']['is_video']

def get_profile_followers(json_data):
    return json_data['node']['owner']['edge_followed_by']['count']
