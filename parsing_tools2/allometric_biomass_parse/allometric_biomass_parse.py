#!/usr/bin/python

"""
    allometric_biomass_parse.py
    ---------------------------
    	Function: Extracts and parses biomass equations from Annexure II of 'Carbon Stocks in India's Forests'
    			The output files from the program can be use with "python manage.py loaddata <filename>"
    			Make sure the output files are placed in allometric/fixtures
    	Output: india_biomass.json, india_species_b.json
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
	'Amoora wallichi':'Amoora wallichii'
}

def start():
    region = None
    species_list = []
    eqtn_list = []

    #OPEN FILE
    f = open("../csv/india_biomass.csv", 'r')

    #CREATE SPECIES LIST
    for line in f:
        #Split line into genus_species and equation
        l = line.split(',')
        genus_species = str(l[0])
        equation = l[1]

        #Region: DO NOT WRITE ANYTHING
        if equation == "region\r\n":
        	region = genus_species
            nothing = None

        #Equation
        else:
            #print "%s,%s" % (genus_species, equation)
            match = re.search(r"(?P<genus>\w{4,15}) (?P<name>\w{4,15})", genus_species)

            if match is None:
                nothing = None
                #print "No matches"

            else:
                #EXTRACT MATCHES
                genus = match.group('genus')
                name = match.group('name')
                species = '%s %s' % (genus, name)

                #REFORMAT EQUATION  HERE
                if species in CORRECTIONS:
            		new = CORRECTIONS[species]
            		species = new


                #ADD EQUATION TO LIST
                tupl = (species, equation)
                eqtn_list.append(tupl)

                #ADD SPECIES TO LIST
                species_list.append(species)

                #print "Added species to list: %s" % (species)
    f.close()


    #CREATE SET FROM SPECIES_LIST AND EMPTY DICT
    species_set = Set(species_list)
    species_set = sorted(species_set)
    SPECIES_DICT = {}

    q = open("../allometric_volume_parse/species_id_b.csv","r")
    for line in q:
        l = line.split(',')
        genus_species = str(l[0])
        sp_id = int(l[1])
        if genus_species in CORRECTIONS:
            new = CORRECTIONS[genus_species]
            genus_species = new
        SPECIES_DICT[genus_species]=sp_id
    q.close()

    #LOAD WOOD DENSITY VALUES INTO WOODDENSITY_DICT
    WOODDENSITY_DICT = {}
    wd = open('../txt/table.txt', 'r')
    for line in wd:
        line = line.split(',')
        species = line[0]
        wood_density = line[1]
        WOODDENSITY_DICT[species] = wood_density
    wd.close()

    #ADD SPECIES ALONG WITH PK INTO DICTIONARY

    write2 = "[\n"
    write3 = ""
    sid = 151

    for item in species_set:
        #SPLIT NAME
        split = item.split()
        genus = split[0]
        name = split[1]
        
        species = "%s %s" % (genus,name.lower())
        if species in CORRECTIONS:
            new = CORRECTIONS[species]
            species = new
        #print species

        if species not in SPECIES_DICT:
            #New species sourced from india_biomass.csv
            SPECIES_DICT[species] = sid
            write3 += '%s, ' % (species)#, SPECIES_DICT[species])
            write2 += '{\n'
            write2 += '    "pk": %s,\n' % (sid)
            sid += 1
            write2 += '    "model": "allometric.EquationSpecies",\n'
            write2 += '    "fields": {\n'
            write2 += '        "genus": "%s",\n' % (genus)
            if species in WOODDENSITY_DICT:
                write2 += '        "name": "%s",\n' % (name.lower())
                write2 += '        "wood_density": %s\n' % (WOODDENSITY_DICT[species])
            else:
                write2 += '        "name": "%s"\n' % (name.lower())
            write2 += '    }\n'
            write2 += '},\n'
        else: 
            pass
            #item in SPECIES_DICT\
            #Species object already in database
            #print "Already in SPECIES_DICT: %s %s" % (species, SPECIES_DICT[species])
            #write3 += '%s, %d\n' % (species, SPECIES_DICT[species]) #,SPECIES_DICT[species]
            #write2 += '{\n'
            #write2 += '    "pk": %s,\n' % (SPECIES_DICT[species])
    #print write3
    write2 += ']'
    s = open('india_species_b.json', 'w')
    s.write(write2)
    s.close()

    c = open('species_list_b.csv', 'w')
    c.write(write3)
    c.close()
        
    i=356
    g=23
    v=0
    default_equations = {}
    write = '[\n'

    s = open('../csv/india_biomass.csv', 'r')

    for line in s:
        #Split line into genus_species and equation
        l = line.split(',')
        genus_species = str(l[0])
        equation = str(l[1])

        #Region: DO NOT WRITE ANYTHING
        region_search = re.search("region", equation)
        if region_search:
        	print "REGION"
        	region = genus_species

        #Equation
        else:
            #print "Equation"
            match = re.search(r"(?P<genus>\w{4,15}) (?P<name>\w{4,15})", genus_species)
            new_equation = None

            if match:
                #EXTRACT MATCHES
                genus = match.group('genus')
                name = match.group('name')
                species = '%s %s' % (genus, name.lower())
                if species in CORRECTIONS:
            		new = CORRECTIONS[species]
            		species = new
            		print species

                equation = equation.split('=')
                #print equation
                equation = equation[1]
                #REFORMAT EQUATION
                new_equation = re.sub("\n", "", equation)
                new_equation = re.sub("\r", "", new_equation)
                new_equation = re.sub("D,", "(dbh)", new_equation)
                new_equation = re.sub("Di", "(dbh)", new_equation)
                new_equation = re.sub("D12", "(dbh)^2", new_equation)
                new_equation = re.sub("D13", "(dbh)^3", new_equation)
                new_equation = re.sub("D1", "(dbh)", new_equation)
                new_equation = re.sub("D2", "(dbh/100)^2", new_equation)
                new_equation = re.sub("D3", "(dbh/100)^3", new_equation)
                new_equation = re.sub("D", "(dbh/100)", new_equation)

                if v%4 == 0:
                    g+=1
                write += '{\n'
                write += '    "pk": %s,\n' % (i)
                write += '    "model": "allometric.Equation",\n'
                write += '    "fields": {\n'
                write += '        "owner": 1,\n'
                write += '        "public": true,\n'
                write += '        "name": "%s",\n' % (species)
                write += '        "string": "%s",\n' % (new_equation)
                write += '        "region": %s,\n' % (DICT[region])
                write += '        "species": %s,\n' % (SPECIES_DICT[species])
                write += '        "volumetric": false,\n'
                if v%4 < 2: #  first two less_than_ten: false
                    write += '        "less_than_ten": false,\n'
                else:        # last two less_than_then: true
                    write += '        "less_than_ten": true,\n'
                if v%2 == 0:
                    write += '        "anatomy": "SW"\n'
                else:#1%2, 3%2
                    write += '        "anatomy": "FL"\n'
                write += '    }\n'
                write += '},\n'
                i += 1
                v += 1
            else:
            	pass
        pass
	pass

	
    s.close()

    o = open('india_biomass.json', 'w')
    write += "]"
    o.write(write)
    o.close()
    return True

start()
