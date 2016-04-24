import pymysql.cursors
import datetime
import traceback
import json


connection = pymysql.connect(host='localhost',
							 user='root',
							 password='admin123+',
							 db = 'ANS',
							 charset = 'utf8mb4',
							 cursorclass=pymysql.cursors.DictCursor)

#Method to save answer
def saveAnswer(data):
	#data = request.json
	postTypeId = 2
	parentId = data["QuestionId"]
	creationDate = datetime.datetime.now()
	score = 0
	viewcount = 1
	body = data["Body"]
	displayname = data["DisplayName"]
	#insert this into database in Posts table
	try:
		#Get user id for the diplayname
		with connection.cursor() as cursor:
			sql = "SELECT `Id` FROM `Users` WHERE `DisplayName` = %s"
			cursor.execute(sql, (displayname))
			userId = cursor.fetchone()
			
		#save the answer in database
		with connection.cursor() as cursor:
			sql = """INSERT INTO `posts` (
				`PostTypeId`,
				`AcceptedAnswerId`,
				`ParentId`,
				`CreationDate`,
				`DeletionDate`,
				`Score`,
				`ViewCount`,
				`Body`,
				`OwnerUserId`,
				`OwnerDisplayName`,
				`LastEditorUserId`,
				`LastedEditorDisplayName`,
				`LastEditDate`,
				`LastActivityDate`,
				`Title`,
				`Tags`,
				`AnswerCount`,
				`CommentCount`,
				`FavouriteCount`,
				`ClosedDate`) VALUES (%s, %s, %s, %s, %s,
				%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
				%s, %s, %s)"""
				
			cursor.execute(sql, (postTypeId, None, parentId, creationDate, None, 
			score, viewcount, body, userId["Id"], displayname, None, None, None, None, None, 
			None, None, 0, None, None))
			
			newRowId = cursor.lastrowid

		#Update the answer count in database for the question
		with connection.cursor() as cursor:
			sql = """UPDATE `Posts` SET 
				`AnswerCount` = `AnswerCount` + 1
				WHERE `Id` = %s"""
			cursor.execute(sql, (parentId))
		connection.commit()
		return newRowId
	except Exception, e:
		print traceback.print_exc()
		return -1

#Method to save comments
def saveComment(data):
	postId = data["PostId"]
	score = 0
	text = data["Text"]
	creationDate = datetime.datetime.now()
	displayname = data["DisplayName"]
	try:
		#Select the userid for the current user
		with connection.cursor() as cursor:
			sql = "SELECT `Id` FROM `Users` WHERE `DisplayName` = %s"
			cursor.execute(sql, (displayname))
			userId = cursor.fetchone()

		#Insert the new comment into database
		with connection.cursor() as cursor:
			sql = """INSERT INTO `Comments` (
				`PostId`,
				`Score`,
				`Text`,
				`CreationDate`,
				`UserDisplayName`,
				`UserId`) VALUES (%s, %s, %s, %s, %s, %s)"""
			cursor.execute(sql, (postId, score, text, creationDate, 
				displayname, userId["Id"]))
			#print("id="+str(cursor.lastrowid))
		#update comment count for the post
		with connection.cursor() as cursor:
			sql = """UPDATE `Posts` SET 
				`CommentCount` = `CommentCount` + 1
				WHERE `Id` = %s"""
			cursor.execute(sql, (postId))
		connection.commit()
		return 1
	except Exception, e:
		print traceback.print_exc()
		return -1
		
#Method to store the user rating for an answer
def saveUserRating(data):
	postId = data["PostId"]
	creationDate = datetime.datetime.now()
	userId = data["UserId"]
	ratingScore = data["RatingScore"]
	ret = -1
	try:
		with connection.cursor() as cursor:
			sql = "CALL `sp_UpdateUserRatingScore`(%s, %s, %s)"
			cursor.execute(sql, (postId, userId, ratingScore))
			ret = cursor.fetchone()
			ret = 1
		connection.commit()
		return ret
	except Exception, e:
		print traceback.print_exc()
		return -1

	

#Method for adding new question
def addQuestion(data):
	postTypeId = 1
	acceptedAnswerId = -1
	parentId = None
	creationDate = datetime.datetime.now()
	score = 0
	deletionDate = None
	viewcount = 1
	body = data["Body"]
	displayname = data["DisplayName"]
	title = data["Title"]
	tags = data["Tags"] #Do we need to update it automatically?
	answerCount = 0
	commentCount = 0
	favouriteCount = 0

	try:
		#Get user id for the diplayname
		with connection.cursor() as cursor:
			sql = "SELECT `Id` FROM `Users` WHERE `DisplayName` = %s"
			cursor.execute(sql, (displayname))
			userId = cursor.fetchone()
		#save the question in database
		with connection.cursor() as cursor:
			sql = """INSERT INTO `posts` (
				`PostTypeId`,
				`AcceptedAnswerId`,
				`ParentId`,
				`CreationDate`,
				`DeletionDate`,
				`Score`,
				`ViewCount`,
				`Body`,
				`OwnerUserId`,
				`OwnerDisplayName`,
				`LastEditorUserId`,
				`LastedEditorDisplayName`,
				`LastEditDate`,
				`LastActivityDate`,
				`Title`,
				`Tags`,
				`AnswerCount`,
				`CommentCount`,
				`FavouriteCount`,
				`ClosedDate`) VALUES (%s, %s, %s, %s, %s,
				%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
				%s, %s, %s)"""
				
			cursor.execute(sql, (postTypeId, acceptedAnswerId, 
				parentId, creationDate, None, 
				score, viewcount, body, userId["Id"], 
				displayname, None, None, None, None, title, 
				tags, answerCount, 0, 0, None))

		connection.commit()
		return 1
	except Exception, e:
		print traceback.print_exc()
		return -1

#Method to retrieve comments
def getComments(parentId):
	comments = []
	comment = {}
	try:
		with connection.cursor() as cursor:
			sql = "SELECT * FROM `Comments` WHERE `PostId` = %s"
			rowCount = cursor.execute(sql, (parentId))
			if rowCount > 0:
				results = cursor.fetchall()
				for row  in results:					
					commentId = row[u'Id']
					commentedUser = row[u'UserDisplayName']
					commentedTime = str(row[u'CreationDate'])
					commentText = row[u'Text']
					userUrl = "#"
					comment = {
						"commentId": commentId,
						"commentedUser": commentedUser,
						"commentedTime": commentedTime,
						"commentText": commentText,
						"userUrl": userUrl 
					}
					comments.append(comment)

				
        
		connection.commit()
		return comments
	except Exception, e:
		print traceback.print_exc()
		return -1
	

#Method to retrieve answers along with comments
def getAnswers(parentId):
	answers = []
	comments = []
	temp = {}
	try:
		#Select the answer with the particular id
		with connection.cursor() as cursor:
			sql = "SELECT * FROM `Posts` WHERE `ParentId` = %s"
			rowCount = cursor.execute(sql, (parentId))
			if rowCount > 0:
				results = cursor.fetchall()
				for row in results:					
					postId = row[u'Id']				
					postTypeId = row[u'PostTypeId']
					postText =  row[u'Body']
					answeredByUserName = row[u'OwnerDisplayName']
					answeredByUserId = row[u'OwnerUserId']
					answeredUserProfile = "#"
					answeredDate = str(row[u'CreationDate'])
					isAcceptedAnswer = "#"
					usefulness = "#"
					score = row[u'Score']
					upvotes = "#"
					downvotes = "#"

					answer = {
						"postId": postId,
						"postTypeId": postTypeId,
						"postText": postText,
						"answeredbyUserName": answeredByUserName,
						"answeredbyUserId": answeredByUserId,
						"answeredUserProfile": answeredUserProfile,
						"answeredDate": answeredDate,
						"isAcceptedAnswer": isAcceptedAnswer,
						"usefulness": usefulness,
						"score": score,
						"upvotes": "#",
						"downvotes": "#"
					}

					comments = getComments(postId)
					temp = {"answer" : answer, "comments" : comments}
					answers.append(temp)
					

		return answers
	except Exception, e:
		print traceback.print_exc()
		return -1
	
#Method to retrieve post details 
def getQuestion(data):
	qId = data
	question = {}
	print(connection.open)
	try:
		#Select the question with the particular postId
		with connection.cursor() as cursor:
			sql = "SELECT * FROM `Posts` WHERE `Id` = %s"
			rowCount = cursor.execute(sql, (qId))
			if rowCount > 0:
				results = cursor.fetchall()
				for row in results:																
					postId = row[u'Id']
					postTypeId = row[u'PostTypeId']
					postTitle = row[u'Title']
					postText = row[u'Body']
					usefulness = "#"
					traffic = "#"
					upvotes = "#"
					downvotes = "#"
					score = row[u'Score']
					isFavorite = "#"
					tags = row[u'Tags']
					askedDate = str(row[u'CreationDate'])
					status = "#"
					askedByUserName = row[u'OwnerDisplayName']
					askedByUserId = row[u'OwnerUserId']
					askedUserProfile = "#"
					noOfAnswers = row[u'AnswerCount']

					question =  {
						"postId": postId,
						"postTypeId": postTypeId,
						"postTitle": postTitle,
						"postText": postText,
						"usefulness": usefulness,
						"traffic": traffic,
						"upvotes": upvotes,
						"downvotes": downvotes,
						"score": score,
						"isFavorite": isFavorite,
						"tags": tags,
						"askedDate": askedDate,
						"status": status,
						"askedbyUserName": askedByUserName,
						"askedbyUserId": askedByUserId,
						"askedUserProfile": "#",
						"noOfAnswers": noOfAnswers
	  				}

		comments = getComments(qId)
		answers = getAnswers(qId)
		final = {"question" : question, "comments" : comments, "answers" : answers}

		connection.commit()
		return final
	except Exception, e:
		print traceback.print_exc()
		return -1

#Method to return view counts for each topic
def getViewCount():
	data = {}
	try:
		# Get all topics
		with connection.cursor() as cursor:
			sql = "SELECT * FROM `Topics`"
			rowCount = cursor.execute(sql)
			if rowCount > 0:
				results = cursor.fetchall()
				for row in results:
					# Get list of question ids under each topic
					topicSql = "SELECT `PostId` from `PostTopicMap` where `TopicId` = %s"
					topicRowCount = cursor.execute(topicSql, (row[u'Id']))					
					if(topicRowCount > 0):
						topicResults = cursor.fetchall()
						postIds = []
						for topicRow in topicResults:
							postIds.append(topicRow[u'PostId'])
						# Calculate sum of view counts
						viewCountSql = "SELECT sum(`ViewCount`) from `Posts` where `Id` in (%s)"
						# Some high tech execution #YOLO 
						in_p=', '.join(list(map(lambda x: '%s', postIds)))
						viewCountSql = viewCountSql % in_p
						viewCountRowCount = cursor.execute(viewCountSql, postIds)
						temp = {}
						temp["topicName"] = str(row[u'Name'])
						if(viewCountRowCount > 0):
							viewCountResults = cursor.fetchone()	
							temp["viewCount"] = str(viewCountResults[u'sum(`ViewCount`)'])
						else:
							temp["viewCount"] = '0'	
						data[row[u'Id']] = temp			
		return data
	except Exception, e:
		print traceback.print_exc()
		return -1	