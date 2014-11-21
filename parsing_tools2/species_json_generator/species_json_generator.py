"""
    species_json_parse.py
    ---------------------------
    	Function: Reformats india_species.json
    			The output file from the program can be used with "python manage.py loaddata <filename>"
    			Make sure the output file is placed in allometric/fixtures
    	Output: india_species.json
"""

import re
import math
import csv

__author__ = "Chelsea Bridson"
__copyright__ = "Copyright 2014, GOES MRV Development Team"



from sets import Set

DICT = { 
        "East Coast": 1,
        "West Coast": 2,
        "Eastern Ghats": 3,
        "Western Ghats": 4,
        "Central Highlands": 5,
        "East Deccan": 6,
        "North Deccan": 7,
        "South Deccan": 8,
        "Eastern Plain": 9,
        "Northern Plain": 10,
        "Western Plain": 11,
        "North-Eastern Ranges": 12,
        "Eastern Himalayas": 13,
        "Western Himalayas": 14,
        "Calculate By Species (Indonesia)": 15,
}

CORRECTIONS = {
	'Acacia leucophlaea':'Acacia leucophloea',
	'Pinus petula':'Pinus patula', 
	'Acacia mearnsu':'Acacia mearnsii',
	'Xylia xylocarpus':'Xylia xylocarpa',
	'Prosopis guliflora':'Prosopis juliflora',
	'Prosopis ceneraria':'Prosopis cineraria',
	'Palaquim ellipticum':'Palaquium ellipticum',
	'Mallotus philippinensis':'Mallotus philippensis',
	'Lagerstroemia spaciosa':'Lagerstroemia speciosa',
	'Lagerstroemia inicrocarpa':'Lagerstroemia microcarpa',
	'Amoora wallichi':'Amoora wallichii',
	'Eucalyptus globules':'Eucalyptus globulus'
}

def start():
    region = None
    species_list = []
    write = "[\n"

    WOODDENSITY_DICT = {}
    wd = open('../csv/india_wood_density_database.csv', 'r')
    for line in wd:
        line = line.split(',')
        species = line[2]
        wood_density = line[3]
        WOODDENSITY_DICT[species] = wood_density
    wd.close()

    f = open("../json/Old/india_species.json", 'r')
    count = 0
    i = 0
    wood_density = None
    WOODDENSITY = {}
    for line in f:
    	wood_search = None
    	genus_search = None
    	name_search = None
    	pk_search = None

    	left_search = re.search("{",line)
    	right_search = re.search("}",line)

    	if left_search:
    		count += 1
    	if right_search:
    		count -= 1

    	genus_search = re.search('"genus"',line)
    	name_search = re.search('"name"', line)
    	wood_search = re.search('"wood_density"', line)
    	pk_search = re.search('"pk"', line)
    	if genus_search:
    		line = line.split(':')
    		genus = line[1].strip('\n\r" ,')
    		genus = re.sub('"','',genus)
    	elif name_search:
    		line = line.split(':')
    		name = line[1].strip('\n\r" ,')
    		name = re.sub('"','',name)
    	elif wood_search:
    		line = line.split(':')
    		wood_density = line[1].strip('\n\r" ,')
    		WOODDENSITY[name] = wood_density
    	elif pk_search:
    		line = line.split(':')
    		pk = line[1].strip('\n\r" ,')

    	if count == 0 and i>1:
    		species = "%s %s" % (genus, name)
    		if species in CORRECTIONS:
        		new = CORRECTIONS[species]
        		species = new
        	write += '{\n'
        	write += '    "pk": %s,\n' % (pk)
        	write += '    "model": "allometric.EquationSpecies",\n'
        	write += '    "fields": {\n'
        	write += '        "genus": "%s",\n' % (genus.title())
        	if name in WOODDENSITY:
        		write += '        "name": "%s",\n' % (name.lower())
        		write += '        "wood_density": %s\n' % (WOODDENSITY[name])
        	elif species in WOODDENSITY_DICT:
        		write += '        "name": "%s",\n' % (name.lower())
        		write += '        "wood_density": %s\n' % (WOODDENSITY_DICT[species])
        	else:
        		write += '        "name": "%s"\n' % (name.lower())
        	write += '    }\n'
        	write += '},\n'
        i += 1

    write += ']'
    s = open('india_species_new.json', 'w')
    s.write(write)
    s.close()

start()