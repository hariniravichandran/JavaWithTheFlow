import pymysql.cursors
import datetime
import traceback
import json
import ConfigParser
import random
import string

config = ConfigParser.ConfigParser()
config.read('db.cfg')
connection = pymysql.connect(host=config.get('database','host'),
							 user=config.get('database','username'),
							 password=config.get('database','password'),
							 db = config.get('database','db'),
							 charset = 'utf8mb4',
							 cursorclass=pymysql.cursors.DictCursor)
userIdNameMap = {}
names = []
def getAllUsers():
	allUsers = []
	try:
		with connection.cursor() as cursor:
			sql = """select distinct `OwnerUserId` from `Posts`"""
			rowCount = cursor.execute(sql)
			if rowCount > 0:
				result = cursor.fetchall()
				for row in result:
					allUsers.append(str(row[u'OwnerUserId']))
			return allUsers
	except Exception, e:
		print traceback.print_exc()
		return -1


def genRandomString(size):
	return ''.join(random.choice(string.ascii_uppercase + 
		string.ascii_lowercase + string.digits) for _ in range(size))

def getNames():
	global names
	namesFile = "/Users/hariniravichandran/Downloads/names-all.txt"
	with open(namesFile, "r") as f:
		names = f.read().splitlines()
		names = [name.lower() for name in names]
		print names

def generateUserData():
	print "In generateUserData"
	allUsers = getAllUsers()
	allUsers.remove('None')
	#print allUsers
	count = 0
	try:
		with connection.cursor() as cursor:
			for userId in allUsers:
				count += 1
				print "Generating for: ", count
				flag = 1
				while(flag):
					userName = genRandomString(random.randint(0,16))
					if userName not in userIdNameMap.values():
						print userId, userName
						userIdNameMap[userId] = userName 
						flag = 0
						sql = """insert into `Users` (`Id`, `DisplayName`) values (%s, %s)"""
						cursor.execute(sql, [userId, userName])
		connection.commit()
		connection.close()
	except Exception, e:
		print traceback.print_exc()
		return -1

def updateUserData():
	getNames()
	allUsers = []
	count = 0
	try:
		with connection.cursor() as cursor:
			sql = "select `Id` from `Users`"
			rowCount = cursor.execute(sql)
			if rowCount > 0:
				results = cursor.fetchall()
				for row in results:
					allUsers.append(row[u'Id'])

			for userId in allUsers:
				count += 1
				print "Generating for: ", count
				flag = 1
				while(flag):
					#userName = genRandomString(random.randint(0,16))
					userName = names.pop()
					if userName not in userIdNameMap.values():
						print userId, userName
						userIdNameMap[userId] = userName 
						flag = 0
						sql = """update `Users` set `DisplayName` = %s where `Id` = %s"""
						cursor.execute(sql, [userName, userId])
						connection.commit()
		connection.close()
	except Exception, e:
		print traceback.print_exc()
		return -1
if __name__ == "__main__":
	#generateUserData()
	updateUserData()
