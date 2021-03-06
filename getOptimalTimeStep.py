import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import numpy as np
import random
import itertools
import os
import sys
import copy


def diff(first, second):
    second = set(second)
    return [item for item in first if item not in second]

def findMacAdresses(d, adresses, ran):
	l = [0,0,0,0,0,0,0,0,0]
	
	if not adresses:
		return l

	for i, key in enumerate(d.keys()):
		for mac in adresses:
			if mac in d[key]:
				adresses.remove(mac)
				l[i] += 1

	if ran:
		return random.sample(range(15), 9)
	return l



timestep = [1, 2, 3, 4, 5, 8, 10, 12, 14, 16, 18, 20]
allCounts = []

d = np.load('buildingToRouterDic.npy')
buildingToRouter = d.item()
buildings = list(buildingToRouter.keys())



upDirectory = '.'
if os.name == 'nt':
	upDirectory = '..'
certDirectory = os.path.join(upDirectory, 'ele-381-course-project-firebase-adminsdk-n1b3y-2c948ee2ce.json')
cred = credentials.Certificate(certDirectory)
firebase_admin.initialize_app(cred)

db = firestore.client()

collectionName = '2019-05-13_MAC'
docs = db.collection(collectionName).get()





for t in timestep:
	print(t)
	k = 0
	prevBuildingToMAC = {}
	currBuildingToMAC = {}
	listOfDifferences = []
	docs = db.collection(collectionName).get()
	for doc in docs:
		if k >= 86:
			print("Index: " + str(k))
			d = doc.to_dict()
			#prevBuildingToMAC = copy.deepcopy(currBuildingToMAC)
			for i in range(len(buildings)):
				macAdresses = []
				for r in buildingToRouter[buildings[i]]:
					a = d.get(r)
					if a != None:
						for pair in a:
							macAdresses.append(list(pair.values()))
				currBuildingToMAC[buildings[i]] = list(itertools.chain.from_iterable(macAdresses))
				

			# K is step size for timestamps
			if k % t == 0:
				if prevBuildingToMAC:
					diffMatrix = []
					for building in prevBuildingToMAC.keys():
						
						# Get MAC adresses that are in prev building but not in curr building
						travelledMac_prev = diff(prevBuildingToMAC[building], currBuildingToMAC[building])
						p1 = findMacAdresses(currBuildingToMAC, travelledMac_prev, False)

						diffMatrix.append(p1)

					# Find buildings that new devices were prev in
					for j, building in enumerate(currBuildingToMAC.keys()):
						
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
	count = 0
	print(len(listOfDifferences))
	for m in listOfDifferences:
		count += np.sum(m)
	allCounts.append(count)

# print(listOfDifferences)
# listOfDifferences = np.array(listOfDifferences)
#print(listOfDifferences)
#np.save('listOfMACDifferences_5_10_19.npy', listOfDifferences)
print(allCounts)




	


