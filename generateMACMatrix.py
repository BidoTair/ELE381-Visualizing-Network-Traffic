import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import numpy as np
import random
import itertools
import os
import sys
import copy


buildings = ["Dillon-Gym-0067", "Wu-Wilcox-0160", "Frist-Campus-Center-0605", "Forbes-College-Main-0148", "Firestone-0069", "Madison-Hall-0036",
"Lewis-Library-0630", "Friend-Center-0616", "Whitman-College-0668"]

def diff(first, second):
    second = set(second)
    return [item for item in first if item not in second]

def findMacAdresses(d, adresses, ran):
	l = [0,0,0,0,0,0,0,0,0]
	
	if not adresses:
		return l

	for key in d.keys():
		for mac in adresses:
			if mac in d[key]:
				adresses.remove(mac)
				l[buildings.index(key)] += 1

	if ran:
		return random.sample(range(15), 9)
	return l





d = np.load('buildingToRouterDic.npy')
buildingToRouter = d.item()




upDirectory = '.'
if os.name == 'nt':
	upDirectory = '..'
certDirectory = os.path.join(upDirectory, 'ele-381-course-project-firebase-adminsdk-n1b3y-2c948ee2ce.json')
cred = credentials.Certificate(certDirectory)
firebase_admin.initialize_app(cred)

db = firestore.client()

collectionName = '2019-05-13_MAC'
docs = db.collection(collectionName).get()

prevBuildingToMAC = {}
currBuildingToMAC = {}
listOfDifferences = []

k = 0
for doc in docs:
	if k >= 86:
		print("Index: " + str(k))
		d = doc.to_dict()
		for i in range(len(buildings)):
			macAdresses = []
			for router in buildingToRouter[buildings[i]]:
				macList = d.get(router)
				if macList != None:
					for mac in macList:
						macAdresses.append(list(mac.values()))
			currBuildingToMAC[buildings[i]] = list(itertools.chain.from_iterable(macAdresses))
			

		# K is step size for timestamps
		if k % 3 == 0:
			if prevBuildingToMAC:
				diffMatrix = []
				for building in buildings:
					

					#print(building)
					# Get MAC adresses that are in prev building but not in curr building
					travelledMac_prev = diff(prevBuildingToMAC[building], currBuildingToMAC[building])
					p1 = findMacAdresses(currBuildingToMAC, travelledMac_prev, False)

					diffMatrix.append(p1)

				# Find buildings that new devices were prev in
				for j, building in enumerate(buildings):
					#print(building)
					# Get MAC adresses that are in curr building but not in prev building
					travelledMac_curr = diff(currBuildingToMAC[building], prevBuildingToMAC[building])
					p2 = findMacAdresses(prevBuildingToMAC, travelledMac_curr, False)
					# Indices in this array are prev buildings
					for i in range(len(p2)):
						if p2[i]:
							diffMatrix[i][j] += p2[i]

				listOfDifferences.append(diffMatrix)
			prevBuildingToMAC = copy.deepcopy(currBuildingToMAC)
	k += 1

print(listOfDifferences)
count = 0
	
for m in listOfDifferences:
	count += np.sum(m)
print(count)
listOfDifferences = np.array(listOfDifferences)
#print(listOfDifferences)
np.save('listOfMACDifferences_5_13_19.npy', listOfDifferences)




	


