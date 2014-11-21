#!/usr/bin/python

"""
    parser.py
    ---------
        Function: extracts and parses volume equations from Indonesia Unlocked
                  outputs a .json file which can be loaded into a django database
"""
# Wood Densities: http://db.worldagroforestry.org/wd

import re
import csv
import json
from pprint import pprint

DICT = {}

SPECIES = []

ENTRIES = []

LEGEND = {
    "PABAR" : "West Papua",
    "JABAR" : "West Java",
    "JATENG" : "Central Java",
    "JATIM" : "East Java",
    "KALTENG" : "Central Kalimantan",
    "KALBAR" : "West Kalimantan",
    "SUMSEL" : "South Sumatra",
    "NTT" : "East Nusa Tenggara"
}

with open('../mrv-env/mrv/allometric/fixtures/indonesia_species.json') as species_file:
    existingSpeciesjson = json.load(species_file)

with open('../mrv-env/mrv/allometric/fixtures/allometric.json') as data_file:
    data = json.load(data_file)
#pprint(data)

WOODDENSITY_DICT = {}
wd = open('parsing_tools/csv/indonesia_wood_density_database.csv', 'r')
for line in wd:
    line = line.split(',')
    species = line[2]
    wood_density = float(line[3])
    WOODDENSITY_DICT[species] = wood_density
wd.close()

sdfsdkfsjdfsl

for entry in data:
    if entry["model"] == "allometric.EquationRegion":
        name = entry["fields"]["name"].encode('ascii')
        pk = entry["pk"]
        DICT[name] = pk

existingSpecies = []
for entry in existingSpeciesjson:
    name = entry["fields"]["name"].encode('ascii')
    genus = entry["fields"]["genus"].encode('ascii')
    species = "%s %s" % (genus.title(), name.lower())
    existingSpecies.append(species)

#existingSpecies = set(existingSpecies)
existingSpecies_current = []

with open('Indonesia_Unlocked_new.csv') as csvfile:
    csvreader = csv.reader(csvfile)

    equationOutput = "[\n"
    #speciesOutput = "[\n"
    pk = 173
    pkk = 1409
    for row in csvreader:
        if len(row) == 0:
            break
        if(row[2] == ''):
            continue
        else:
            genus_species = row[2].split()
            name = "%s" % genus_species[1]
            genus = "%s" % genus_species[0]
            species = "%s %s" % (genus.title(), name.lower())
        if species not in existingSpecies_current:
            entry={}
            fields = {}
            entry['pk'] = pk
            entry['model'] = 'allometric.EquationSpecies'

            fields['genus'] = genus.title()
            fields['name'] = name.lower()
            if species in WOODDENSITY_DICT:
                fields['wood_density'] = WOODDENSITY_DICT[species]

            entry['fields'] = fields
            ENTRIES.append(entry)
            existingSpecies_current.append(species)


            #speciesOutput += '{\n'
            #speciesOutput += '    "pk": %s,\n' % (pk)
            #speciesOutput += '    "model": "allometric.EquationSpecies",\n'
            #speciesOutput += '    "fields": {\n'
            #speciesOutput += '        "genus": "%s",\n' % (genus.title())
            #if species in WOODDENSITY_DICT:
            #    speciesOutput += '        "name": "%s"\n,' % (name.lower())
            #    speciesOutput += '        "wood_density": %s\n' % (WOODDENSITY_DICT[species])
            #else:
            #    speciesOutput += '        "name": "%s"\n' % (name.lower())

            #speciesOutput += '    }\n'
            #speciesOutput += '},\n'
        #continue here, adding equations

        pkk += 1
        pk += 1

#speciesOutput += ']'
print ENTRIES
with open('indonesia_species.json', 'w') as fp:
    json.dump(ENTRIES, fp, indent = 4, separators=(',', ': ') )

