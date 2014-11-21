#!/usr/bin/python

"""
	india_species_validator.py
	---------------------------
	    Function: Checks a list of species on wikipedia.org and outputs a report 
	    		The report must be reviewed by a human for further processing
	    Output: species_report.txt

"""

import requests
import re 

__author__ = "Chelsea Bridson"
__copyright__ = "Copyright 2014, GOES MRV Development Team"


def start():

	file_in_name = '../allometric_biomass_parse/india_species_b.json'
	f = open(file_in_name, 'r')	
	write = ""
	for line in f:
		pk_search = re.search(r'"pk": (?P<pk>[0-9]+)', line)
		name_search = re.search(r'"name": "(?P<name>\w+)"',line)
		genus_search =  re.search(r'"genus": "(?P<genus>\w+)"',line)
		end_search = re.search(r'},', line)
		if pk_search:
			sp_pk = int(pk_search.group('pk'))
		elif name_search:
			name = name_search.group('name')
		elif genus_search:
			genus = genus_search.group('genus')
		elif end_search: #end of one entry
			species = "%s %s" % (genus, name.lower())
			url = "https://en.wikipedia.org/wiki/%s_%s" % (genus, name.lower())
			r = requests.get(url)
			print r.status_code
			if r.status_code == 200:
				nothing = None
			elif name == "species":
				nothing = None
			elif r.status_code == 404:
				write += "%s not found Wikipedia\n" % (species)
		else:
			nothing = None
	f.close()
	o = open('species_report.txt', "w")
	o.write(write)

start()