import os
import numpy as np

from tqdm import tqdm

from utils import *
from config import config

DATA = config['DATA_FOLDER']

# Save stats into a dictionary
stats = {}
stats['Profiles'] = 0
stats['Posts'] = 0
stats['Image Posts'] = 0
stats['Images'] = 0
stats['Image per post'] = {}
stats['Post Types'] = {}
stats['Is video'] = {}
stats['Comments'] = []
stats['Likes'] = []
stats['Post timestamp'] = []

# Get all folders inside DATA. Each folder corresponds to a profile
for subdir in tqdm(os.listdir(DATA)):

    # Check that path is a direcory
    if os.path.isdir(f'{DATA}\{subdir}'):
        stats['Profiles'] += 1

        # Iterate over all files
        for file in os.listdir(f'{DATA}\{subdir}'):
            # Count images
            if is_jpg(file):
                stats['Images'] += 1

            # Count json files
            elif is_json_xz(file):

                # Get metadata from the json file
                stats['Posts'] += 1
                json_data = read_compessed_json(f'{DATA}\{subdir}\\', file)
                update_dict(stats['Post Types'], get_post_type(json_data))
                update_dict(stats['Is video'], is_video(json_data))

                if not is_video(json_data):
                    stats['Image Posts'] += 1
                    update_dict(stats['Image per post'], get_number_of_images_on_post(json_data))
                    get_number_of_images_on_post
                    stats['Likes'].append(get_likes(json_data))
                    stats['Comments'].append(get_comments(json_data))
                    stats['Post timestamp'].append(get_post_timestamp(json_data))


# Calculated metrics
stats['Post per profile'] = stats['Posts'] / stats['Profiles']
stats['Image Post per profile'] = stats['Image Posts'] / stats['Profiles']
stats['Avg Image per post'] = stats['Images'] / stats['Posts']
stats['Avg Image per image post'] = stats['Images'] / stats['Image Posts']

# Save json file
try:
    with open('.\\eda\\stats.json', 'w') as f:
        json.dump(stats, f)
        f.close()
except:
    print('Error while saving the file')
