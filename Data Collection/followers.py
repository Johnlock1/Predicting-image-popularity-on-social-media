import sys
import json
import instaloader
from instaloader import NodeIterator

from datetime import datetime
from config import config

from tqdm import tqdm

import numpy as np
import pandas as pd

import logging
logging.basicConfig(filename='log.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)

# User credetials to login Instagram
USER = # add your username here
PASSWORD = # add your password here

# The profiles from which a list of followers will be downloded
profiles = ['archillect']

# Helper function from saving the csv with speficic column names
def save_csv(file, list):
    df = pd.DataFrame(list, columns=['username', 'mediacount', 'followees', 'followers'])
    df.to_csv(f'{file}.csv')

# Iteratame over all profiles
for profile in profiles:
    print(f'Start reading {profile} profile.')

    # Instantiate Instaloader with custom pattern for the output file
    L = instaloader.Instaloader(dirname_pattern=f"{config['DATA_FOLDER']}\{profile}", download_videos=False)
    L.login(USER, PASSWORD)        # (login)
    print(f'Logged in.')

    # Get profile
    _profile = instaloader.Profile.from_username(L.context, profile)

    # List to store the folloeints
    followers = []

    i = 0
    print(f'Start')

    # Iterate ocer the list of followers
    for follower in tqdm(_profile.get_followers()):
        try:
            # Create a row with speficic information about the follower
            row = []
            row.append(follower.username)
            row.append(follower.mediacount)
            row.append(follower.followees)
            row.append(follower.followers)
            followers.append(row)

        # Provides the ability to stop the execution via command line (Ctr + C)
        # Saves the progress to a csv file
        except KeyboardInterrupt:
            print('k')
            save_csv(f'followers_{profile}', followers)
            sys.exit()

        # Save the progress to a csv file in case on an expection
        except:
            save_csv(f'followers_{profile}', followers)

    # Save the progress to a csv file once all follower from the account have been extracted
    save_csv(f'followers_{profile}', followers)
