from collections import defaultdict

import sys
import os
import sqlite3
import json
import pprint
sys.path.append("../")
import controllers
from controllers.methods import *

"""
config.json
{
	"last_dictionary_file": "<file_name>",
	"last_dictionary_file_word": "<word>"
}
"""

class DictionaryExtractor ():
	class DirectoryNotFoundError (Exception):
		pass

	configFile = "config.json"

	def __init__ (self, dictionaryFilesPath, databaseFilePath = "database.db"):
		if (not os.path.isdir(dictionaryFilesPath)):
			raise DirectoryNotFoundError("Please supply the path to a valid directory")
		self.dictionaryFilesPath = dictionaryFilesPath
		self.conn = sqlite3.Connection(databaseFilePath)
		self.cursor = self.conn.cursor()
		self.__loadConfig()
		self.generator = controllers.PrivateKeyGenerator()

	def __loadConfig (self):
		print("[+] Loading config...")
		if (os.path.isfile(self.configFile)):
			with open(self.configFile, "r") as file:
				self.config = json.loads(file.read())
		else:
			self.config = {}
		print("[+] Finished loading config")

	def __saveConfig (self):
		print("[+] Saving config...")
		with open(self.configFile, "w") as file:
			file.write(json.dumps(self.config))
		print("[+] Finished saving config")

	def loadDictionary (self):
		self.checkTables()

		print("[+] Loading dictionaries...")
		filesToLoad = os.listdir(self.dictionaryFilesPath)
		if (self.config.get("last_dictionary_file")):
			print("[+] Retrieving index...")
			filesToLoad = filesToLoad[filesToLoad.index(self.config["last_dictionary_file"]):]
		
		for _ in filesToLoad:
			print("[+] Loading dictionary file...")
			with open(os.path.join(self.dictionaryFilesPath, _), "r") as file:
				print("[+] Finished loading dictionary file...")
				self.parseDictionary(file.read(), _)
			self.config["last_dictionary_file"] = _
			self.__saveConfig()
			self.conn.commit()

	def parseDictionary(self, fileData, fileName):
		print("[+] Parsing dictionary data...")
		dictionaryData = json.loads(fileData)
		wordsToLoad = dictionaryData.keys()

		if (self.config.get("last_dictionary_file") == fileName) and (
		    self.config.get("last_dictionary_file_word")):
			wordsToLoad = list(dictionaryData.keys())[list(dictionaryData.keys()).index(self.config["last_dictionary_file_word"]):]

		for wordToLoad in wordsToLoad:
			self.parseDictionaryWord(dictionaryData[wordToLoad])
			self.config["last_dictionary_file_word"] = dictionaryData[wordToLoad]["word"]

	def parseDictionaryWord (self, wordData):
		print(f"[+] Parsing dictionary word {wordData['word']}...")
		definitionIds = []
		wordId = self.generateId(10, "word")
		wordData = defaultdict(lambda *args, **kwargs: [], wordData)
		print(jsonize(wordData, indent = 4))
		for definition in wordData["meanings"]:
			print(f"[+] Going through: {wordData['word']}")

			definition = defaultdict(lambda *args, **kwargs: "", definition)
			definitionId = self.generateId(10, "definition")
			thesaurusId = self.generateId(10, "thesaurus")

			definitionIds.append(definitionId)

			query = f"""
			INSERT INTO `definition`
			(ID, DEFINITION, EXAMPLE, SOUND, PART_OF_SPEECH, THESAURUS)
			VALUES (?, ?, ?, ?, ?, ?)
			"""
			self.cursor.execute(query, (definitionId, definition["def"], definition["example"], "", definition["speech_part"], thesaurusId))

			query = f"""
			INSERT INTO `thesaurus`
			(ID, DEFINITION)
			VALUES (?, ?)
			"""
			self.cursor.execute(query, (thesaurusId, definitionId))

		query = f"""
		INSERT INTO `word`
		(ID, WORD, DEFINITIONS)
		VALUES (?, ?, ?)
		"""
		self.cursor.execute(query, (wordId, wordData["word"], json.dumps(definitionIds)))

	def checkTables (self):
		query = """
		CREATE TABLE IF NOT EXISTS `definition` (
			ID VARCHAR (50) PRIMARY KEY,
			DEFINITION TEXT DEFAULT '',
			EXAMPLE TEXT DEFAULT '',
			SOUND TEXT DEFAULT '',
			PART_OF_SPEECH TEXT DEFAULT '',
			THESAURUS TEXT DEFAULT ''
		);
		"""
		self.cursor.execute(query)

		query = """
		CREATE TABLE IF NOT EXISTS `glossary` (
			ID VARCHAR (50) PRIMARY KEY,
			DEFINITION TEXT DEFAULT ''
		);
		"""
		self.cursor.execute(query)

		query = """
		CREATE TABLE IF NOT EXISTS `word` (
			ID VARCHAR (50) PRIMARY KEY,
			WORD TEXT,
			DEFINITIONS TEXT DEFAULT '[]'
		);
		"""
		self.cursor.execute(query)

		query = """
		CREATE TABLE IF NOT EXISTS `thesaurus` (
			ID VARCHAR (50) PRIMARY KEY,
			DEFINITION TEXT DEFAULT '',
			ANTONYMS TEXT DEFAULT '',
			SYNONYMS TEXT DEFAULT '',
			HOMOPHONES TEXT DEFAULT ''
		);
		"""
		self.cursor.execute(query)

	def generateId (self, idLength, tableName):
		print(f"[+] Generating ID for {tableName}")
		while (True):
			id = self.generator.generate(level = 10)
			query = f"SELECT * FROM `{tableName}` WHERE ID='{id}'"
			res = self.cursor.execute(query)
			result = res.fetchone()
			if (not result):
				break

		print(f"[+] Generated ID ({tableName}): {id}")
		return id

def displayHelpMenu ():
	print(f"Usage: {sys.argv[0]} <dictionary file path> [<database file path>]")
	print("Where:")
	print("\t<dictionary file path> = path to the folder (data) containing dictionary JSON files -- resource: https://github.com/wordset/wordset-dictionary")
	print("\t[<database file path>] (optional) = arbitrary path to a sqlite database file")

if __name__ == "__main__":
	dictionaryFilesPath = ""
	if (len(sys.argv) >= 2):
		dictionaryFilesPath = sys.argv[1]
		if (dictionaryFilesPath.lower() == "--help" or dictionaryFilesPath.lower() == "-h" or dictionaryFilesPath.lower() == "/h" or dictionaryFilesPath.lower() == "/help" or dictionaryFilesPath == "/?"):
			displayHelpMenu()
			exit()
	databaseFilePath = sys.argv[2] if (len(sys.argv) >= 3) else "database.db"
	if (dictionaryFilesPath):
		app = DictionaryExtractor(dictionaryFilesPath, databaseFilePath = databaseFilePath)
		app.loadDictionary()
	else:
		displayHelpMenu()
