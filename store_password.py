'''
Created on Oct 22, 2015

@author: k
'''

import pickle
import os
import keyring

FILE_LOCATIONS = '/Users/abostroem/Desktop/craigslist_scraper'

if __name__ == '__main__':
    with open(os.path.join(FILE_LOCATIONS,'scraper.config'),'w') as ifile:
        config_dict = {}
        config_dict['username']=raw_input('Please enter your email username:\n')
        keyring.set_password('CraigslistScraper',config_dict['username'],raw_input('Please enter your email password:\n'))
        pickle.dump(config_dict,ifile)
