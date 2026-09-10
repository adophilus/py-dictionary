from flask import Blueprint

from app import models

definitionsBlueprint = Blueprint("definitions", __name__)
definitionsUrlPrefix = "/definitions"

@definitionsBlueprint.route("/<word>")
def getWordDefinitions(word):
	if word_record := models.Word(WORD=word):
		return word_record.DEFINITIONS
	return ""
