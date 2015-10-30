#!/usr/bin/env python

from datetime import datetime
import pdb
import pickle
import urllib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import keyring

FILE_LOCATIONS = '/Users/abostroem/Desktop/craigslist_scraper'
SAVED_RESULTS_FILENAME = "last_run_davis.pkl"

def get_login_credentials():
	with open(os.path.join(FILE_LOCATIONS,'scraper.config')) as ofile:
		config_dict = pickle.load(ofile)
        config_dict['password'] = keyring.get_password('CraigslistScraper',config_dict['username'])
	return config_dict['username'], config_dict['password']

def send_email(message):
    msg = MIMEMultipart()
    msg["Subject"] = "New Craigslist Results"
    msg["From"] = "abostorem@gmail.com"
    msg["To"] = "abostroem@gmail.com"
    msg.attach(MIMEText(message))
    s = smtplib.SMTP("smtp.gmail.com:587")
    s.starttls()
    username, password = get_login_credentials()
    s.login(username, password)
    s.sendmail("abostroem@gmail.com",["abostroem@gmail.com"], msg.as_string())
    s.quit()

def read_in_files(filename):
	'''
	Read html file
	'''
	sock = urllib.urlopen("http://sacramento.craigslist.org/search/apa?query=Davis&sale_date=-")
	htmlSource = sock.read()
	sock.close()
	return htmlSource.split('\n')

def split_text_by_ad(all_lines):
	'''
	Split single row into a list where each element corresponds to an ad
	'''
	for iline in all_lines:
		#Find beginning of content
		if 'class="row"' in iline:
			indiv_ads = iline.split('class="row"')
			return indiv_ads[1:]


def find_davis_ads(indiv_ads):
	'''
	Loop over each add and pull out the location, price, title, date posted, and url

	Check:
		if the location isn't listed but davis is in the title or davis is the location
		The price is less than 950
		The word share is not in the title
		The word room is not in the title
	If ad meets all of these conditions, then create a dictionary to hold title, location,
		price, date, and url
	Return this dictionary
	'''
	davis_ads_dict = {}
	ad_num = 0
	for i, ad in enumerate(indiv_ads):

		title = ad.split('class="hdrlnk">')[1].split('</a>')[0]
		try:
			location = ad.split('class="pnr"> <small> ')[1].split('</small>')[0]
		except IndexError: #If no location listed
			location = ''
		try:
			price = float(ad.split('class="price">&#x0024;')[1].split('</span>')[0])
		except IndexError: #If no price listed
			price = 0
		url = ad.split('<a href="')[1].split('" class="i"')[0]
		try:
			num_bedrooms = ad.split('class="housing">/')[1].split()[0]
		except:
			num_bedrooms = ''
		date = ad.split('datetime="')[1].split()[0]
		year,month, day = date.split('-')
		today = datetime.today()
		this_morning = datetime.strptime('{} {} {}'.format(today.month, today.day, today.year), '%m %d %Y')
		computer_date = datetime.strptime('{} {} {}'.format(month, day, year), '%m %d %Y')
		if (((location == '') and ('davis' in title.lower())) or
					('davis' in location.lower())) and \
				(price < 950) and \
				('room' not in title.lower()) and \
				('share' not in title.lower()): #and (computer_date > this_morning):
			ad_num += 1
			davis_ads_dict[title.replace(' ', '_')] = {'title':title,
										'location':location,
										'price':price,
										'date':date,
										'bedrooms':num_bedrooms,
										'url':'"http://sacramento.craigslist.org'+,url}
	return davis_ads_dict


def pickle_dictionary(davis_ads_dict):
	with open(os.path.join(FILE_LOCATIONS,SAVED_RESULTS_FILENAME), 'w') as ofile:
		pickle.dump(davis_ads_dict, ofile)

def find_new_entries(davis_ads_dict):
	last_run_file = os.path.join(FILE_LOCATIONS,SAVED_RESULTS_FILENAME)

	if os.path.exists(last_run_file):
		ofile = open(last_run_file)
		old_davis_ads_dict = pickle.load(ofile)
		old_ad_titles = old_davis_ads_dict.keys()
		email_txt = ''
		for ad in davis_ads_dict.keys():
			if ad not in old_ad_titles:
				email_txt += '{} \n\tPrice: {}, \n\tLocation: {}, \n\tDate posted: {}, \
						\n\tBedrooms: {},\n\tlink: {}\n\n'.format(
					davis_ads_dict[ad]['title'], davis_ads_dict[ad]['price'],
					davis_ads_dict[ad]['location'], davis_ads_dict[ad]['date'],
					davis_ads_dict[ad]['bedrooms'], davis_ads_dict[ad]['url'])
	else:
		email_txt = ''
		for ad in davis_ads_dict.keys():
			email_txt += '{} \n\tPrice: {}, \n\tLocation: {}, \n\tDate posted: {}, \
					\n\tBedrooms: {},\n\tlink: {}\n\n'.format(
				davis_ads_dict[ad]['title'], davis_ads_dict[ad]['price'],
				davis_ads_dict[ad]['location'], davis_ads_dict[ad]['date'],
				davis_ads_dict[ad]['bedrooms'], davis_ads_dict[ad]['url'])
	return email_txt


def find_new_ads(davis_ads_dict):
	with open(os.path.join(FILE_LOCATIONS,SAVED_RESULTS_FILENAME), 'r') as ofile:
		last_davis_ads_dict = pickle.load(ofile)

def write_log(email_txt):
	if os.path.exists(os.path.join(FILE_LOCATIONS, 'log.txt')):
		mode = 'a'
	else:
		mode = 'w'

	with open(os.path.join(FILE_LOCATIONS, 'log.txt'), mode) as ofile:
		today = datetime.today()
		if len(email_txt) > 1:
			ofile.write('{} email sent \n'.format(datetime.ctime(today)))
		else:
			ofile.write('{} Nothing to report \n'.format(datetime.ctime(today)))


if __name__ == "__main__":
	all_lines = read_in_files('craigslist.html')
	indiv_ads = split_text_by_ad(all_lines)
	davis_ads_dict = find_davis_ads(indiv_ads)
	email_txt = find_new_entries(davis_ads_dict)
	if len(email_txt) > 1:
		send_email(email_txt)
	pickle_dictionary(davis_ads_dict)
	write_log(email_txt)

