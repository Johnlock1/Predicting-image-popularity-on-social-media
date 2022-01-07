import os
import sys
import json
import logging
import instaloader

import pandas as pd

from tqdm import tqdm
from freeze import Freezer

def checkpoint():
    def read_checkpoint(checkpoint_file):
        with open(checkpoint_file, 'r') as file:
            return json.loads(file.read())

    def create_checkpoint(checkpoint_file):
        checkpoint = {}
        checkpoint['frozen'] = []
        checkpoint['completed'] = []
        checkpoint['in_progress'] = []

        with open(checkpoint_file, 'w') as outfile:
            json.dump(checkpoint, outfile)

        return read_checkpoint(checkpoint_file)

    checkpoint_file = f'{CHECKPOINTS}checkpoint.json'

    if os.path.exists(checkpoint_file):
        print(f'Checkpoint file was loaded')
        return read_checkpoint(checkpoint_file)
    else:
        print(f'Checkpoint file was created')
        return create_checkpoint(checkpoint_file)

def update_checkpoint(checkpoint):
    with open(f'{CHECKPOINTS}checkpoint.json', 'w') as outfile:
        json.dump(checkpoint, outfile)

def in_progress(username, checkpoint):
        checkpoint['in_progress'].append(username)
        update_checkpoint(checkpoint)

def frozen(username, checkpoint):
    if username in checkpoint['in_progress']:
        checkpoint['in_progress'].remove(username)
    checkpoint['frozen'].append(username)
    update_checkpoint(checkpoint)

def completed(username, checkpoint):
    if username in checkpoint['frozen']:
        checkpoint['frozen'].remove(username)
    checkpoint['completed'].append(username)
    update_checkpoint(checkpoint)

def error(username, checkpoint):
    checkpoint['error'].append(username)
    update_checkpoint(checkpoint)

def is_in_list(username, list):
    return username in list

def read_txt(file):
    if os.path.exists(file):
        with open(file, 'r') as f:
             return f.read().split('\n')
    else:
        return []

def save_txt(file, mode, list):
    if mode == 'a':
        existing = read_txt(file)
        with open(file, mode) as f:
            for s in list:
                if s not in existing:
                    f.write(s)
                    f.write('\n')

    else:
        with open(file, mode) as f:
            for s in list:
                f.write(s)
                f.write('\n')

def save_iteration(profile, post_iterator):
    # Freeze iterator to a json file
    with open(f'{FROZEN_ITERATORS}resume_information_{profile}.json', 'w') as j:
        json.dump(post_iterator.freeze(), j)

def save_shortcodes(profile, post_shortcode):
    # Save shortcodes list into a file
    with open(f'{SHORTCODES}shortcodes_{profile}.txt', 'a') as f:
        for s in post_shortcode:
            f.write(s)
            f.write('\n')

def shortcode_list_empty(list):
    return len(list)==1 and list[0] == ""




# Folders
CHECKPOINTS = '.\\checkpoints\\'
OUTPUT = '.\\data\\'
SHORTCODES = '.\\shortcodes\\'
FROZEN_ITERATORS = '.\\frozenIterators\\'
LOGS = '.\\logs\\'

logging.basicConfig(filename=f'{LOGS}log 11-Oct.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)

# Use one the credetials of the two users, by uncommented the respective rows
# # User 1
# USER = 'username'
# PASSWORD = 'password'
# # User 1
# USER = 'username'
# PASSWORD = 'password'

L = instaloader.Instaloader(download_videos=False)
L.login(USER, PASSWORD)        # (login)

checkpoint = checkpoint()

# Read the list of followers extracted from the 'archillect' profile
parent_node = 'archillect'
followers = pd.read_csv(f'followers_{parent_node}.csv')

# Iterate over all usernames of th elist
for username in list(followers['username']):

    # If post for the user are already downloaded, Continue
    if is_in_list(username, checkpoint['completed']):
        # print(f' Data for {username} are already downloaded')
        continue

    # Don't bother if downloing posts from this username those some error
    if is_in_list(username, checkpoint['error']):
        pass

    elif is_in_list(username, checkpoint['in_progress']):
        pass

    # If shortcodes are already frozen, load them from disk
    elif is_in_list(username, checkpoint['frozen']):
        with open(f'{SHORTCODES}shortcodes_{username}.txt') as file:
            shortcode_list = file.read().split('\n')

    # Else, freeeze the shortcodes
    else:
        print(f'Freezing posts from {username}.')
        try:
            freezer = Freezer(L, username, SHORTCODES, FROZEN_ITERATORS, logger)
            freezer.get_posts()
            freezer.freeze_shortcodes()
            frozen(username, checkpoint)
            print(f' End reading {username} profile.')
        except:
            pass

    # Download post
    if not shortcode_list_empty(shortcode_list):
        print(f'Start downling post for {username} profile.')
        logger.info(f'Start downling post for {username} profile.')

        # Set output file and pass it as parameter to the Instaloder instance
        output_folder = f'{OUTPUT}{username}\\'
        L2 = instaloader.Instaloader(dirname_pattern=output_folder, download_videos=False)

        L2.login(USER, PASSWORD)        # (login)

        # Create a few helper lists
        # First, load the list of shortcodes that were downloaded before
        # This will be used to skip codes that were downloded beroe
        downloaded_before = read_txt(f'{SHORTCODES}shortcodes_{username}_downloaded.txt')
        cannot_download = [] # To append codes that throwed error
        downloaded_now = [] # To append codes that were successfully downloaded

        logger.info('-Downloaded_before:')
        logger.info(downloaded_before)

        # Iterate over all shortcodes
        for shortcode in shortcode_list:
            logger.info(f'-Shortcode: {shortcode}')
            logger.info(f'-Should downloaded (only if not downloaded before) : {shortcode not in downloaded_before}')
            try:
                # Attept to download the  post, only if it wasn't downloded before
                if shortcode not in downloaded_before:
                    logger.info(f'-Downloading: {shortcode}')
                    post = instaloader.Post.from_shortcode(L2.context, shortcode)
                    L2.download_post(post, shortcode)
                    downloaded_now.append(shortcode)

            # Provides the ability to stop the execution via command line (Ctr + C)
            # Saves the progress, by appending the erronous and successfully \
            # downloded posts in the respective file
            except KeyboardInterrupt:
                print('Keyboard Interrupt')
                save_txt(f'{SHORTCODES}shortcodes_{username}_cannot_download.txt', 'a', cannot_download)
                save_txt(f'{SHORTCODES}shortcodes_{username}_downloaded.txt', 'a', downloaded_now)
                sys.exit()

            except Exception as e:
                print('Exception:')
                print(e)
                cannot_download.append(shortcode)

        # Saves progress once all codes in the list were parsed
        save_txt(f'{SHORTCODES}shortcodes_{username}_cannot_download.txt', 'a', cannot_download)
        save_txt(f'{SHORTCODES}shortcodes_{username}_downloaded.txt', 'a', downloaded_now)

    # Moves the profile to 'completed', so no future attemps to download posts from it will be made
    completed(username, checkpoint)
    print(f'Complete {username}')
