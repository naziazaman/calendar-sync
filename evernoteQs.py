from configure import ConfigHandler
from evernote.api.client import EvernoteClient
from datetime import datetime
import evernote.edam.notestore.ttypes as NoteStoreTypes
import time

class EvernoteAPI:
	def __init__(self):
		config = ConfigHandler('evernote.config')
		token = config.get('one-calendar', 'token')
		self.client = EvernoteClient(token=token)

	def user_store(self):
		return self.client.get_user_store()

	def note_store(self):
		return self.client.get_note_store()


def parse_note_description(xml_desc):
	from lxml import etree
	from StringIO import StringIO

	root = etree.fromstring(xml_desc)
	context = etree.iterparse(StringIO(xml_desc))

	span = False
	text = []
	subtext = []
	for action, elem in context:
		if elem.tag == 'div' and elem.text:
			text.append(elem.text)
			if len(subtext) > 0:
				text.append(' '.join(subtext))
				subtext = []
		elif elem.text:
			subtext.append(elem.text)
		if elem.tail:
			subtext.append(elem.tail)
		
	if len(subtext) > 0:
		text.append(' '.join(subtext))

	return '\n'.join(text)

def get_reminders():
	note_api = EvernoteAPI()
	note_store = note_api.note_store()

	nFilter = NoteStoreTypes.NoteFilter()
	nFilter.words = "reminderOrder:*"
	rSpec = NoteStoreTypes.NotesMetadataResultSpec()
	
	notesMetadataList = note_store.findNotesMetadata(nFilter, 0, 50, rSpec)

	reminder_list = []
	for note in notesMetadataList.notes:
		note_details = note_store.getNote(note.guid, False, False, False, False)
		note_attributes = note_details.attributes
		
		note_description = parse_note_description(note_store.getNoteContent(note.guid))
		
		reminder_list.append({'title': note_details.title,
			'time': time.localtime(note_attributes.reminderTime/1000.),
			'description': note_description,
			'location': note_attributes.placeName if note_attributes.placeName else ''})

	return reminder_list