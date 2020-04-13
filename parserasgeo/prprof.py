'''
Parse HEC-RAS' profile file

Current elements parsed:

- Encroachments
'''

from features.tools import fl_int
from features import Encroachments


class ParseRASProfile(object):
	def __init__(self, profile_filename):
		self.profile_filename = profile_filename

		# store every line of the profile file. used to write the file back out
		self.prof_list = []

		with open(profile_filename, 'rt') as pr_file:
			for line in pr_file:
				if Encroachments.test(line):
					encroachment = Encroachments()
					encroachment.import_prof(line, pr_file)
					self.prof_list.append(encroachment)
				else:
					self.prof_list.append(line)

	def return_encroachments(self):
		to_return = []
		for e in self.prof_list:
			if e.__name__ == 'Encroachments':
				to_return.append(e)
		return to_return