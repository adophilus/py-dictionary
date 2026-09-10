from flask import globals

from app import db
from app.controllers.methods import unjsonize
from app.models.definition import Definition

class Word (db.Model):
	ID = db.Column(db.String(50), primary_key = True)
	WORD = db.Column(db.Text)
	DEFINITIONS = db.Column(db.Text)

	def __str__ (self):
		return self.WORD

	def getDefinitions(self):
		definitions = []
		for definition_id in unjsonize(self.DEFINITIONS):
			if definition := Definition.query.filter_by(ID=definition_id).first():
				definitions.append(definition)
		return definitions

	@classmethod
	def getById (cls, word_id):
		return cls.query.filter_by(ID = word_id).first()

	@classmethod
	def getByMatch (cls, word):
		word = word.replace('_', '__').replace('*', '%').replace('?', '_')
		return cls.query.filter(cls.WORD.contains(f"%{word}%")).all()
