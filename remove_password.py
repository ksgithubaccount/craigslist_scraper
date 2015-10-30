'''
Created on Oct 29, 2015

@author: k
'''
import pickle
import os
import keyring

FILE_LOCATIONS = '/Users/abostroem/Desktop/craigslist_scraper'

if __name__ == '__main__':
    with open(os.path.join(FILE_LOCATIONS,'scraper.config')) as ofile:
        config_dict = pickle.load(ofile)
        config_dict['password'] = keyring.delete_password('CraigslistScraper',config_dict['username'])
