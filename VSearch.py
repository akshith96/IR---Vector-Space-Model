import nltk
from nltk.stem.porter import *
nltk.download('punkt')
import difflib
import math
import re
import os
from functools import reduce

files = []
directory = input('Path to the directory where your corpus is stored : ')
for file in os.listdir(directory):
	if file.endswith(".txt"):
		files.append(directory + "\\" + file)
		
tokenized = []
stemmer = PorterStemmer()
def tokenize_normalize():
	global files
	global stemmer
	global tokenized
	for i in range(0,len(files)):
		read_file = open(files[i],"r",encoding='utf-8', errors='ignore').read()
		temp_tokenized = nltk.word_tokenize(read_file)
		temp_normalized = [stemmer.stem(word.lower()) for word in temp_tokenized]
		tokenized.append(temp_normalized)

tokenize_normalize()

posting_lists = {}
def create_positional_index():
	global tokenized
	global posting_lists
	i = 1
	for each_file_tokens in tokenized:
		j = 0
		for token in each_file_tokens:
			if token in posting_lists:
				if i in posting_lists[token]:
					posting_lists[token][i].append(j)
				else:
					posting_lists[token][i] = [j]
			else:
				posting_lists[token] = {}
				posting_lists[token][i] = [j]
			j += 1
		i += 1
		
create_positional_index()

tfidf_docs = {}
def calc_tfidfdocs():
	global tfidf_docs
	global tokenized
	global posting_lists
	i = 1	
	for each_file_tokens in tokenized:
		for token in each_file_tokens:
			count = len(posting_lists[token][i])
			if count != 0:
				tf = 1 + math.log10(count)
				idf = math.log10(float(len(files))/len(posting_lists[token]))
				if i in tfidf_docs:
					tfidf_docs[i][token] = tf*idf
				else:
					tfidf_docs[i] = {}
					tfidf_docs[i][token] = tf*idf
		i += 1
		
calc_tfidfdocs()
	
query = ""
tokenized_query = []
normalized_query = []
spl_cor_query = []
weights = {}
def search():
	global query
	global tokenized_query
	global normalized_query
	global spl_cor_query
	global weights
	query = input('Phrase you want to search in the corpus : ')
	tokenized_query = nltk.word_tokenize(query)
	normalized_query = [stemmer.stem(word.lower()) for word in tokenized_query]
	spl_cor_query = []
	for i in range(0,len(normalized_query)):
		if normalized_query[i] not in posting_lists:
			temp = difflib.get_close_matches(normalized_query[i], posting_lists)
			if len(temp) != 0:
				spl_cor_query.append(temp[0])
		else:
			spl_cor_query.append(normalized_query[i])
			
	query_tfidf = {}
	for j in spl_cor_query:
		if j in posting_lists:
			idf  = math.log10(float(len(files))/len(set(posting_lists[j])))
			query_tfidf[j] = (1 + math.log10(spl_cor_query.count(j)))*idf
			
	weights = {}
	relavant = {}
	for i in range(0,len(files)):
		if query in open(files[i],"r",encoding='utf-8', errors='ignore').read().lower():
			relavant[i] = 1
			
		temp_weight = 0
		for j in spl_cor_query:
			if j in posting_lists:
				if (i+1) in posting_lists[j]:
					count = len(posting_lists[j][i+1])
					if count != 0:
						tf = 1 + math.log10(count)
						idf  = math.log10(float(len(files))/len(set(posting_lists[j])))
						temp_weight += query_tfidf[j]*(tf*idf)
						
		l = list(query_tfidf.values())
		sqrt_sum_squr_query = reduce(lambda x,y: x+y*y,[l[:1][0]**2]+l[1:])
		l = list(tfidf_docs[i+1].values())
		sqrt_sum_squr_doc = reduce(lambda x,y: x+y*y,[l[:1][0]**2]+l[1:])
		temp_weight = temp_weight/((sqrt_sum_squr_query**(1/2))*(sqrt_sum_squr_doc**(1/2)))
		if temp_weight != 0:
			weights[i] = temp_weight

	relavant_docs = len(relavant)
	retrieved_docs = min(len(weights), 20)
	relavant_retrieved_docs = min(len(set(relavant.keys()) & set(weights.keys())),retrieved_docs)
	presicion = relavant_retrieved_docs / float(retrieved_docs)
	recall = relavant_retrieved_docs / float(relavant_docs)
	
	print("Precision : " + str(presicion))
	print("Recall : " + str(recall))
	print("Harmonic Mean : " + str((2*presicion*recall)/(presicion + recall)))
	
search()

def wildsearch():
	global query
	global tokenized_query
	global normalized_query
	global spl_cor_query
	global weights
	query = input('Phrase with wild card you want to search in the corpus : ')
	tokenized_query = nltk.word_tokenize(query)
	normalized_query = [stemmer.stem(word.lower()) for word in tokenized_query]
	spl_cor_query = []
	for i in range(0,len(normalized_query)):
		if "*" in normalized_query[i]:
			r = re.compile(r'^' + normalized_query[i].replace("*",".*") + r'$', re.IGNORECASE)
			for l in posting_lists:
				if r.match(l):
					spl_cor_query.append(l)
		else:
			if normalized_query[i] not in posting_lists:
				temp = difflib.get_close_matches(normalized_query[i], posting_lists)
				if len(temp) != 0:
					spl_cor_query.append(temp[0])
			else:
				spl_cor_query.append(normalized_query[i])
				
	print(spl_cor_query)
	print("Printed values are the wildcard query results, choose from them and search.")
	search()

#	weights = {}
#	for i in range(0,len(files)):
#		temp_weight = 0
#		for j in spl_cor_query:
#			if j in posting_lists:
#				if (i+1) in posting_lists[j]:
#					count = len(posting_lists[j][i+1])
#					if count != 0:
#						tf = 1 + math.log10(count)
#						idf  = math.log10(float(len(files))/len(set(posting_lists[j])))
#						temp_weight += tf*idf
#		weights[i] = temp_weight
	
#wildsearch()

def proximitysearch():
	global query
	global tokenized_query
	global normalized_query
	global spl_cor_query
	global weights
	query = input('Positional query you want to search in the corpus (term1 no_of_words_between) term2) : ')
	tokenized_query = query.split(" ")
	number = int(tokenized_query[1]) + 1
	del tokenized_query[1]
	normalized_query = [stemmer.stem(word.lower()) for word in tokenized_query]
	spl_cor_query = []
	for i in range(0,len(normalized_query)):
		if normalized_query[i] not in posting_lists:
			temp = difflib.get_close_matches(normalized_query[i], posting_lists)
			if len(temp) != 0:
				spl_cor_query.append(temp[0])
		else:
			spl_cor_query.append(normalized_query[i])
			
	start = posting_lists[spl_cor_query[0]]
	end = posting_lists[spl_cor_query[1]]
	docs_intersect = set(list(start.keys()) + list(end.keys()))
	
	docs_result = []
	
	for i in range(0,number+1):
		for doc in docs_intersect:
			start_arr = start[doc]
			end_arr = end[doc]
			start_arr_to_end_arr = [x+i for x in start_arr]
			for j in start_arr_to_end_arr:
				if j in end_arr:
					docs_result.append(doc)
					break
				
	print(docs_result)
	search()
		
#positionalsearch()
	
while(1):
	print("Entering “1” will display the result of tokenization and normalization of the query.")
	print("Entering “2” will display the result of the spell correction of the query.")
	print("Entering “3” will fetch the documents for the query.")
	print("Entering “4” will prompt you to search new query")
	print("Entering “5” will prompt you to search new wildcard query")
	print("Entering “6” will prompt you to search new positional query")
	print("Entering “7” will prompt you to add a document to the corpus")
	print("Entering “8” will prompt you to delete a document from the corpus")
	print("Entering “9” will prompt you to enter a document that has been edited in the corpus")
	decision = int(input())
	if decision == 1:
		print(' '.join(normalized_query))
	elif decision == 2:
		print(' '.join(spl_cor_query))
	elif decision == 3:
		sorted_dict_keys_by_value = list(sorted(weights, key=weights.__getitem__, reverse=True))
		i = 0
		while(i < 20 and i < len(sorted_dict_keys_by_value)):
			print(files[sorted_dict_keys_by_value[i]] + " - " + str(weights[sorted_dict_keys_by_value[i]]))
			i += 1
	elif decision == 4:
		search()
	elif decision == 5:
		wildsearch()
	elif decision == 6:
		proximitysearch()
	elif desision == 7:
		addFile = input('Please enter the filename to be added with path and extension included : ')
		files.append(addFile)
		read_file = open(addFile,"r",encoding='utf-8', errors='ignore').read()
		addFile_tokenized = nltk.word_tokenize(read_file)
		addFile_normalized = [stemmer.stem(word.lower()) for word in addFile_tokenized]
		tokenized.append(addFile_normalized)
		
		i = len(files) + 1
		for token in addFile_normalized:
			if token in posting_lists:
				if i in posting_lists[token]:
					posting_lists[token][i].append(j)
				else:
					posting_lists[token][i] = [j]
			else:
				posting_lists[token] = {}
				posting_lists[token][i] = [j]
			j += 1
		calc_tfidfdocs()
	elif desision == 8:
		deleteFile = input('Please enter the filename to be deleted with path and extension included : ')
		if deleteFile in files:
			i = files.index(deleteFile) + 1
			files.remove(deleteFile)
			read_file = open(deleteFile,"r",encoding='utf-8', errors='ignore').read()
			deleteFile_tokenized = nltk.word_tokenize(read_file)
			deleteFile_normalized = [stemmer.stem(word.lower()) for word in deleteFile_tokenized]
			del tokenized[i-1]

			for token in deleteFile_normalized:
				if len(posting_lists[token]) > 1:
					posting_lists[token].pop(i, None)
				else:
					posting_lists.pop(token, None)
		calc_tfidfdocs()
	elif desision == 9:
		editFile = input('Please enter the filename that has been edited with path and extension included : ')
		if editFile in files:
			i = files.index(editFile) + 1
			read_file = open(editFile,"r",encoding='utf-8', errors='ignore').read()
			editFile_tokenized = nltk.word_tokenize(read_file)
			editFile_normalized = [stemmer.stem(word.lower()) for word in editFile_tokenized]
			tokenized[i-1] = editFile_normalized

			for token in editFile_normalized:
				if len(posting_lists[token]) > 1:
					posting_lists[token].pop(i, None)
				else:
					posting_lists.pop(token, None)
			
			for token in editFile_normalized:
				if token in posting_lists:
					if i in posting_lists[token]:
						posting_lists[token][i].append(j)
					else:
						posting_lists[token][i] = [j]
				else:
					posting_lists[token] = {}
					posting_lists[token][i] = [j]
				j += 1
		calc_tfidfdocs()
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		