import os
import sys
import json
import logging
import instaloader

from datetime import datetime
from instaloader import NodeIterator
from tqdm import tqdm


class Freezer():

    def __init__(self, Instaloader, username, shortcodes_folder, iterators_folder, logger):
        self.L = Instaloader
        self.username = username
        self.profile  = None
        self.shortcodes_folder = shortcodes_folder
        self.iterators_folder = iterators_folder
        self.logger = logger

    def read_shortcodes(self, file):
        if os.path.exists(file):
            with open(file, 'r') as f:
                 return f.read().split('\n')
        else:
            return []

    def save_iteration(self, post_iterator, username):
        # Freeze iterator to a json file
        with open(f'{self.iterators_folder}resume_information_{username}.json', 'w') as j:
            json.dump(post_iterator.freeze(), j)

    def save_shortcodes(self, shortcode_list, username):
        file = f'{self.shortcodes_folder}shortcodes_{username}.txt'
        existing = self.read_shortcodes(file)
        # Save shortcodes list into a file
        with open(file, 'a') as f:
            for s in shortcode_list:
                if s not in existing:
                    f.write(s)
                    f.write('\n')

    def save_status(self, username, post_iterator, shortcode_list):
        self.save_iteration(post_iterator, username)
        self.save_shortcodes(shortcode_list, username)


    def get_profile(self):
        self.profile = instaloader.Profile.from_username(self.L.context, self.username)
        print(f' Got Insta profile.')

    def get_posts(self):
        if self.profile is None:
            self.get_profile()
        self.post_iterator = self.profile.get_posts()

        try:
             self.post_iterator.thaw(instaloader.FrozenNodeIterator(*json.load(open(f'{self.iterators_folder}resume_information_{self.username}.json', encoding="utf8"))))
             print(' Read info from json and resuming operations.')
        except Exception as e:
            print(f' Cannot read \'resume_information_{self.username}.json\' file')
            self.logger.error(e)

    # Store (of "Freeze") all the shortcodes in a file
    def freeze_shortcodes(self):
        self.post_shortcode = []

        try:
            self.logger.info(' Start iterating posts.')

            for post in tqdm(self.post_iterator):
                # Append shortcode to a list
                self.post_shortcode.append(post._node['shortcode'])

        except Exception as e:

            self.save_status(self.username, self.post_iterator, self.post_shortcode)
            self.logger.error(e)
            print(' There was an exception. Please check log.')


        except KeyboardInterrupt as e:
            self.save_status(self.username, self.post_iterator, self.post_shortcode)
            self.logger.error(e)
            print('KeyboardInterrupt')
            sys.exit()

        # Save shortcodes after end of profile
        self.save_status(self.username, self.post_iterator, self.post_shortcode)
