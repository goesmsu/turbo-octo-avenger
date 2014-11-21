#!/usr/bin/python

"""
    allometric_volume_parse.py
    ---------------------------
    	Function: Extracts and parses volume equations from Annexure I of 'Carbon Stocks in India's Forests'
    			The output files from the program can be use with "python manage.py loaddata <filename>"
    			Make sure the output files are placed in allometric/fixtures
    	Output: india_volumetric.json, india_species_v.json
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

	#OPEN FILE
	file_in_name = "../csv/allometric_volume.csv"
	f = open(file_in_name, 'r')	


	#CREATE SPECIES LIST
	for line in f:
		#Split line into genus_species and equation
		l = line.split(',')
		genus_species = str(l[0])
		equation = l[1]

		#Region: DO NOT WRITE ANYTHING
		if equation == "region\r\n":
			nothing = None

		#Equation
		else:
			#print "%s,%s" % (genus_species, equation)
			match = re.search(r"(?P<genus>\w+) (?P<name>\w+)", genus_species)

			if match is None:
				nothing = None
				#print "No matches"

			else:
				#EXTRACT MATCHES
				genus = match.group('genus')
				name = match.group('name')
				species = '%s %s' % (genus, name)
				if species in CORRECTIONS:
					new = CORRECTIONS[species]
					species = new
				#ADD SPECIES TO LIST
				species_list.append(species)
				#print "Added species to list: %s" % (species)
	f.close()


	#CREATE SET FROM SPECIES_LIST AND EMPTY DICT
	species_set = Set(species_list)
	species_set = sorted(species_set)
	SPECIES_DICT = {}

	#LOAD EXISTING SPECIES PK INTO SPECIES_DICT
	g = open('../json/Old/india_species_old.json', 'r')
	for line in g:
		pk_search = re.search(r'"pk": (?P<pk>[0-9]+)', line)
		name_search = re.search(r'"name": "(?P<name>\w+)"',line)
		genus_search =  re.search(r'"genus": "(?P<genus>\w+)"',line)
		end_search = re.search(r'},', line)
		end_search2 = re.search(r']', line)
		if pk_search:
			sp_pk = int(pk_search.group('pk'))
		elif name_search:
			name = name_search.group('name')
		elif genus_search:
			genus = genus_search.group('genus')
		elif end_search or end_search2: #end of one entry
			species = "%s %s" % (genus, name.lower())
			if species in CORRECTIONS:
				new = CORRECTIONS[species]
				species = new
			#print "SPECIES_DICT[%s] = %d" % (species, sp_pk)
			SPECIES_DICT[species] = sp_pk
		else:
			nothing = None
	g.close()

	#LOAD WOOD DENSITY VALUES INTO WOODDENSITY_DICT
	WOODDENSITY_DICT = {}
	wd = open('../txt/table.txt', 'r')
	for line in wd:
		line = line.split(',')
		species = line[0]
		wood_density = line[1]
		WOODDENSITY_DICT[species] = wood_density
	wd.close()

	wd2 = open('../csv/india_wood_density_database.csv')
	for line in wd2:
		line = line.split(',')
		
	#ADD SPECIES ALONG WITH PK INTO DICTIONARY 

	write2 = "[\n"
	write3 = ""
	sid = 54

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
			SPECIES_DICT[species] = sid
			write3 += '%s, %d\n' % (species,SPECIES_DICT[species]) #,SPECIES_DICT[species]
			write2 += '{\n'
			write2 += '    "pk": %s,\n' % (sid)
			sid += 1
	
		else: #item in SPECIES_DICT
			#print "Already in SPECIES_DICT: %s %s" % (species, SPECIES_DICT[species])
			write3 += '%s, %d\n' % (species, SPECIES_DICT[species]) #,SPECIES_DICT[species]
			write2 += '{\n'
			write2 += '    "pk": %s,\n' % (SPECIES_DICT[species])

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
	write2 += ']'
	#print write3

	s = open('india_species_v.json', 'w')
	s.write(write2)
	s.close()

	c = open('species_id_v.csv', 'w+')
	c.write(write3)
	c.close()


"""
	i=13
	g=23
	v=0
	write = '[\n'
	f = open('../csv/allometric_volume.csv', 'r')	
	default_equations = {}

	for line in f:
		#Split line into genus_species and equation
		l = line.split(',')
		genus_species = str(l[0])
		equation = str(l[1])


		#Region: DO NOT WRITE ANYTHING
		if equation == "region\r\n":
			region = genus_species

		#Equation
		else:
			#print "Equation"
			match = re.search(r"(?P<genus>\w+) (?P<name>\w+)", genus_species)
			new_equation = None

			if match is None:
				pass

			else:

				#EXTRACT MATCHES
				genus = match.group('genus')
				name = match.group('name')
			 	species = '%s %s' % (genus, name.lower())
				

				#REFORMAT EQUATION

				equation = re.sub("\n", "", equation)
				equation = re.sub("\r", "", equation)
				equation = re.sub("sqrt\(V\)", "sqrtV", equation)
				#equation = re.sub("D", "(dbh/100)", equation)

				dia_in_cm = re.search("\(dia D is in cm\)", equation)

				if dia_in_cm:
					equation = re.sub("\(dia D is in cm\)", "", equation)
					#print equation

				star = re.search("\*", genus_species)
				if star:
					#print "star"
					equation = re.sub("\*", "", equation)


				#"Naming Convention: last word = <# of params>
				#sqrt_eqtn_three
				sqrtV_C_BD_AsqrtD = re.search(r"sqrtV\s*=\s*(?P<CS>[-+]*)(?P<C>[0-9.]+)\s*(?P<BS>[-+]{1})\s*(?P<B>[0-9.]+)\s*D\s*(?P<AS>[-+]{1})\s*(?P<A>[-+0-9.]+)\s*sqrtD\s*$", equation)
				#sqrt_eqtn_two
				sqrtV_C_BD = re.search(r"sqrtV\s*=\s*(?P<CS>[-+]*)(?P<C>[0-9.]+)\s*(?P<BS>[-+]{1})\s*(?P<B>[0-9.]+)\s*D", equation)
				#VD2_BD2_C
				VD2_BD2_C = re.search(r"V/D2\s*=\s*(?P<BS>[-+]*)(?P<B>[0-9.]+)/D2\s*(?P<CS>[+-]{1})\s*(?P<C>[0-9.]+)\s*$", equation)
				VD2_B_CD2 =  re.search(r"V/D2\s*=\s*(?P<BS>[-+]*)(?P<B>[0-9.]+)\s*(?P<CS>[+-]{1})\s*(?P<C>[0-9.]+)/D2\s*$", equation)
				#v_over_D2_three
				VD2_CD2_BD_A = re.search(r"V/D2\s*=\s*(?P<CS>[-+]*)\s*(?P<C>[0-9.]+)/D2\s*(?P<BS>[+-]{1})\s*(?P<B>[0-9.]+)/D\s*(?P<AS>[+-]{1})\s*(?P<A>[0-9.]+)\s*$", equation)
				#v_over_D2_three_r
				VD2_CD2_A_BD = re.search(r"V/D2\s*=\s*(?P<CS>[-+]*)\s*(?P<C>[0-9.]+)/D2\s*(?P<AS>[+-]{1})\s*(?P<A>[0-9.]+)\s*(?P<BS>[+-]{1})\s*(?P<B>[0-9.]+)\D\s*$", equation)
	                 	#v_over_D2_four
				VD2_CD2_BD_A_ED = re.search(r"V/D2\s*=\s*(?P<CS>[-+]*)\s*(?P<C>[0-9.]+)/D2\s*(?P<BS>[+-]{1})\s*(?P<B>[0-9.]+)/D\s*(?P<AS>[+-]{1})\s*(?P<A>[0-9.]+)\s*(?P<ES>[+-]{1})\s*(?P<E>[0-9.]+)\s*D$", equation)
				#v_over_D_thre
				VD_CD_B_AD = re.search(r"V/D\s*=\s*(?P<CS>[+-]*)\s*(?P<C>[0-9.]+)/D\s*(?P<BS>[+-]{1})\s*(?P<B>[0-9.]+)\s*(?P<AS>[+-]{1})\s*(?P<A>[0-9.]+)\s*D$", equation)
				#log_e_
				logeV_C_BlogeD = re.search(r"logeV\s*=\s*(?P<CS>[+-]*)\s*(?P<C>[0-9.]+)\s*(?P<BS>[+-]{1})\s*(?P<B>[0-9.]+)\s*logeD", equation)
				#V_tw
				V_C_BD2 = re.search(r"V\s*=\s*(?P<CS>[+-]*)\s*(?P<C>[0-9.]+)\s*(?P<BS>[+-]{1})\s*(?P<B>[0-9.]+)\s*D2\s", equation)
				#V_thre
				V_C_BD_AD2 =  re.search(r"[Vv]\s*=\s*(?P<CS>[+-]*)\s*(?P<C>[0-9.]+)\s*(?P<BS>[+-]{1})\s*(?P<B>[0-9.]+)\s*D\s*(?P<AS>[+-]{1})\s*(?P<A>[0-9.]+)\s*D2", equation)
				V_C_BsqrtD_AD2 = re.search(r"[Vv]+\s*=\s*(?P<CS>[+-]*)\s*(?P<C>[0-9.]+)\s*(?P<BS>[+-]{1})\s*(?P<B>[0-9.]+)\s*sqrtD\s*(?P<AS>[+-]{1})\s*(?P<A>[0-9.]+)\s*D2", equation)
				V_C_AD2 = re.search(r"[vV]\s*=\s*(?P<CS>[+-]*)\s*(?P<C>[0-9.]+)\s*(?P<AS>[+-]*)\s*(?P<A>[0-9.]+)\s*D2", equation)
				V_C_AD3 = re.search(r"[vV]\s*=\s*(?P<CS>[+-]*)\s*(?P<C>[0-9.]+)\s*(?P<AS>[+-]*)\s*(?P<A>[0-9.]+)\s*D3", equation)
				V_BD_AD2 = re.search(r"[Vv]\s*=\s*(?P<BS>[+-]{1})\s*(?P<B>[0-9.]+)\s*D\s*(?P<AS>[+-]{1})\s*(?P<A>[0-9.]+)\s*D2", equation)

				V_ADB = re.search(r"[vV]\s*=\s*(?P<AS>[+-]*)\s*(?P<A>[0-9.]+)\s*D\s*\^\((?P<BS>[+-]*)(?P<B>[0-9.]+)", equation)
                                if sqrtV_C_BD_AsqrtD:
                                	#print "Match! sqrtV_C_BD_AsqrtD %s" % (equation)
					#sqrtV = C + B x + A sqrtx
					#V = (C + B x + A sqrtx)2
					#Expanded: V = A^2 x + 2 AB x^(3/2) + 2 AC sqrt(x) + B^2 x^2 + 2 BC x + C^2
					#Final format: V = 2 AB x^(3/2) + B^2 x^2 + (A^2 + 2 BC)x + 2 AC sqrt(x) + C^2
					#EXTRACT MATCHES
					C = float(sqrtV_C_BD_AsqrtD.group('C'))
					CS = sqrtV_C_BD_AsqrtD.group('CS')
					if CS == "-":
						C *= -1

					B = float(sqrtV_C_BD_AsqrtD.group('B'))
					BS = sqrtV_C_BD_AsqrtD.group('BS')
					if BS == "-":
						B *= -1

					A = float(sqrtV_C_BD_AsqrtD.group('A'))
					AS = sqrtV_C_BD_AsqrtD.group('AS')
					if AS == "-":
						A *= -1
					
					#BUILD NEW EQUATION
					A2 = A**2
					twoAB = 2*A*B
					twoAC = 2*A*C
					B2 = B**2
					twoBC = 2*B*C
					C2 = C**2
					A2twoBC= A2 + twoBC

					new_equation = "%f (dbh/100)^(3/2) + %f (dbh/100)^2 _%+f (dbh/100) _%+f sqrt(dbh/100) +  %f" % (twoAB, B2, A2twoBC, twoAC, C2)
					#print new_equation
				elif V_C_BD2:
					#V=C + B D2
					#V = B D2 + C

					#EXTRACT MATCHES
					C = float(V_C_BD2.group('C'))
					CS = V_C_BD2.group('CS')
					if CS == "-":
						C *= -1

					B = float(V_C_BD2.group('B'))
					BS = V_C_BD2.group('BS')
					if BS == "-":
						B *= -1
					
					new_equation = "%f (dbh/100)^2 _%+f" % (B,C)
				elif V_ADB:
					#TO DO: CREATE NEW EQUATION IN EACH OF THESE
					B = float(V_ADB.group('B'))
					BS = V_ADB.group('BS')
					if BS == "-":
						B *= -1

					A = float(V_ADB.group('A'))
					AS = V_ADB.group('AS')
					if AS == "-":
						A *= -1
					
					new_equation = "%f (dbh/100)^(%f)" % (A, B) 

				elif V_C_AD2:
					C = float(V_C_AD2.group('C'))
					CS = V_C_AD2.group('CS')
					if CS == "-":
						C *= -1

					A = float(V_C_AD2.group('A'))
					AS = V_C_AD2.group('AS')
					if AS == "-":
						A *= -1
					new_equation = "%f (dbh/100)^2 _%+f" % (A, C)	

				elif V_C_AD3:
					C = float(V_C_AD3.group('C'))
					CS = V_C_AD3.group('CS')
					if CS == "-":
						C *= -1

					A = float(V_C_AD3.group('A'))
					AS = V_C_AD3.group('AS')
					if AS == "-":
						A *= -1
					new_equation = "%f (dbh/100)^3 _%+f" % (A, C)	

				elif V_BD_AD2:
					B = float(V_BD_AD2.group('B'))
					BS = V_BD_AD2.group('BS')
					if BS == "-":
						B *= -1

					A = float(V_BD_AD2.group('A'))
					AS = V_BD_AD2.group('AS')
					if AS == "-":
						A *= -1
					new_equation = "%f (dbh/100)^2 _%+f (dbh/100)" % (A,B)	

				elif V_C_BD_AD2:
					#EXTRACT MATCHES
					C = float(V_C_BD_AD2.group('C'))
					CS = V_C_BD_AD2.group('CS')
					if CS == "-":
						C *= -1

					B = float(V_C_BD_AD2.group('B'))
					BS = V_C_BD_AD2.group('BS')
					if BS == "-":
						B *= -1

					A = float(V_C_BD_AD2.group('A'))
					AS = V_C_BD_AD2.group('AS')
					if AS == "-":
						A *= -1
					new_equation = "%f (dbh/100)^2 _%+f (dbh/100) _%+f" % (A,B,C)			
				elif V_C_BsqrtD_AD2:
					#EXTRACT MATCHES
					C = float(V_C_BsqrtD_AD2.group('C'))
					CS = V_C_BsqrtD_AD2.group('CS')
					if CS == "-":
						C *= -1

					B = float(V_C_BsqrtD_AD2.group('B'))
					BS = V_C_BsqrtD_AD2.group('BS')
					if BS == "-":
						B *= -1

					A = float(V_C_BsqrtD_AD2.group('A'))
					AS = V_C_BsqrtD_AD2.group('AS')
					if AS == "-":
						A *= -1
					
					new_equation = "%f (dbh/100)^2 _%+f sqrt(dbh/100) _%+f" % (A,B,C) 
				elif sqrtV_C_BD:
					#print "Match! sqrtV_C_BD %s" % (equation)
					#sqrtV = C+ Bx
					#V = (C+Bx)^2
					#Final Format: V = B^2 X^2 + 2 BC x + C^2

					#EXTRACT MATCHES
					C = float(sqrtV_C_BD.group('C'))
					CS = sqrtV_C_BD.group('CS')
					if CS == "-":
						C *= -1

					B = float(sqrtV_C_BD.group('B'))
					BS = sqrtV_C_BD.group('BS')
					if BS == "-":
						B *= -1

					#BUILD NEW EQUATION
					B2 = B**2
					twoBC = 2*B*C
					C2 = C**2

					new_equation = "%f (dbh/100)^2 _%+f (dbh/100) + %f" % (B2, twoBC, C2)
					#print new_equation
				
				elif VD2_BD2_C:
					#print "Match! VD2_BD2_C %s" % equation
					#V/D2 = B/D^2 + C
					#V = C D^2 + B

					#EXTRACT MATCHES
					C = float(VD2_BD2_C.group('C'))
					CS = VD2_BD2_C.group('CS')
					if CS == "-":
						C *= -1

					B = float(VD2_BD2_C.group('B'))
					BS = VD2_BD2_C.group('BS')
					if BS == "-":
						B *= -1

					#BUILD NEW EQUATION
					new_equation = "%f (dbh/100)^2 _%+f" % (C, B)

				elif VD2_B_CD2:
					#print "Match! VD2_BD2_C_r %s" % equation
					#V/D2 = B + C/D^2
					#V = B D^2 + C 

					#EXTRACT MATCHES
					C = float(VD2_B_CD2.group('C'))
					CS = VD2_B_CD2.group('CS')
					if CS == "-":
						C *= -1

					B = float(VD2_B_CD2.group('B'))
					BS = VD2_B_CD2.group('BS')
					if BS == "-":
						B *= -1

					#BUILD NEW EQUATION
					new_equation = "%f (dbh/100)^2 _%+f" % (B, C)

				elif VD2_CD2_BD_A:
					#print "Match! VD2_CD2_BD_A %s" % equation
					#V/D2 = C/D2 + B/D + A
					#V = A D2 + B D + C

					#EXTRACT MATCHES
					C = float(VD2_CD2_BD_A.group('C'))
					CS = VD2_CD2_BD_A.group('CS')
					if CS == "-":
						C *= -1

					B = float(VD2_CD2_BD_A.group('B'))
					BS = VD2_CD2_BD_A.group('BS')
					if BS == "-":
						B *= -1

					A = float(VD2_CD2_BD_A.group('A'))
					AS = VD2_CD2_BD_A.group('AS')
					if AS == "-":
						A *= -1
					
					new_equation = "%f (dbh/100)^2 _%+f (dbh/100) _%+f" % (A, B, C)

				elif VD2_CD2_A_BD:
					#V/D2 = C/D2 + A + B/D
					#V = A D2 + B D + C

					#EXTRACT MATCHES
                                        C = float(VD2_CD2_A_BD.group('C'))
                                        CS = VD2_CD2_A_BD.group('CS')
                                        if CS == "-":
                                                C *= -1

                                        B = float(VD2_CD2_A_BD.group('B'))
                                        BS = VD2_CD2_A_BD.group('BS')
                                        if BS == "-":
                                                B *= -1

                                        A = float(VD2_CD2_A_BD.group('A'))
                                        AS = VD2_CD2_A_BD.group('AS')
                                        if AS == "-":
                                                A *= -1
                                        
                                        new_equation = "%f (dbh/100)^2 _%+f (dbh/100) _%+f" % (A, B, C)

					
				elif VD2_CD2_BD_A_ED:
					#print "Match! VD2_CD2_BD_A_ED %s" % equation
					#V/D2 = C/D2 + B/D + A + E D
					#V = E D3 + A D2 + B D + C

					#EXTRACT MATCHES
					C = float(VD2_CD2_BD_A_ED.group('C'))
					CS = VD2_CD2_BD_A_ED.group('CS')
					if CS == "-":
						C *= -1

					B = float(VD2_CD2_BD_A_ED.group('B'))
					BS = VD2_CD2_BD_A_ED.group('BS')
					if BS == "-":
						B *= -1

					A = float(VD2_CD2_BD_A_ED.group('A'))
					AS = VD2_CD2_BD_A_ED.group('AS')
					if AS == "-":
						A *= -1

					E = float(VD2_CD2_BD_A_ED.group('E'))
					ES = VD2_CD2_BD_A_ED.group('ES')
					if ES == "-":
						E *= -1

					new_equation = "%f (dbh/100)^3 _%+f (dbh/100)^2 _%+f (dbh/100) _%+f" % (E, A, B, C)
					#print new_equation

				elif VD_CD_B_AD:
					#V/D = C/D + B + A D
					#V = A D^2 + B D + C
					C = float(VD_CD_B_AD.group('C'))
					CS = VD_CD_B_AD.group('CS')
					if CS == "-":
						C *= -1

					B = float(VD_CD_B_AD.group('B'))
					BS = VD_CD_B_AD.group('BS')
					if BS == "-":
						B *= -1

					A = float(VD_CD_B_AD.group('A'))
					AS = VD_CD_B_AD.group('AS')
					if AS == "-":
						A *= -1

					new_equation = "%f (dbh/100)^2 _%+f (dbh/100) _%+f" % (A, B, C)
					#print new_equation

				elif logeV_C_BlogeD:
					#print "Match! logeV_C_BlogeD"
					#log_e(V) = C + B log_e(D)
					#ln V = C + B ln D
					#e^(ln V) = e^(C+ B ln D)
					#V = e^C x^B

					C = float(logeV_C_BlogeD.group('C'))
					CS = logeV_C_BlogeD.group('CS')
					if CS == "-":
						C *= -1

					B = float(logeV_C_BlogeD.group('B'))
					BS = logeV_C_BlogeD.group('BS')
					if BS == "-":
						B *= -1

					new_equation = "e^%f (dbh/100)^%f" % (C,B)
					#print new_equation
				else:
					print "No match! %s" % (equation)
					print "Region: %s" % region
					print "Species: %s" % genus_species

					
				#reformat spaces properly
				if new_equation:
					new_equation = re.sub(r"_-", "- ", new_equation)
					new_equation = re.sub(r"_\+", "+ ", new_equation)

				else:
					#print "%s\t\t%s\t%s" % ( equation,genus_species, region)
					eqtn = equation.split('=')
					sub = re.sub(r"D2", "D^2", eqtn[1])
					sub2 = re.sub(r"D3", "D^3", sub)
					sub3 = re.sub(r"D", "(dbh/100)", sub2)
					sub4 = sub3.strip()
					new_equation = sub4

				if dia_in_cm:
					equation = re.sub("dbh/100", "dbh", equation)
					#Since parameters are scaled for centimeters to yield meters
				if star:
					default_equations[region] = new_equation

				#print new_equation

				if v%4 == 0:
					g+=1

				#CREATE JSON ENTRY
				write += '{\n'
				write += '    "pk": %s,\n' % (i)
				write += '    "model": "allometric.Equation",\n'
				write += '    "fields": {\n'
				write += '        "owner": 1,\n'
				write += '        "public": true,\n'
				write += '        "name": "%s %s",\n' % (genus, name)
				write += '        "string": "%s",\n' % (new_equation)
				write += '        "region": %s,\n' % (DICT[region])
				write += '        "species": %s,\n' % (SPECIES_DICT[species])
				write += '        "volumetric": true\n'
				#if v%4 <2:
				#	write += '        "less_than_ten": false\n'
				#else:
				#	write += '        "less_than_ten": true\n'
				write += '    }\n'
				write += '},\n'
				i += 1
				v += 1
	f.close()

	#TO DO: OUTPUT A LIST OF DEFAULT VOLUMETRIC EQUATIONS FOR REGIONS
	d_e = open("default_volumetric_equations.csv", 'w')
	writer = csv.writer(d_e)
	for key, value in default_equations.items():
		writer.writerow([key, value])
	d_e.close()

	write += "]"
	o = open('india_volumetric.json', 'w')
	o.write(write)
	o.close()
	return True
"""

start()
