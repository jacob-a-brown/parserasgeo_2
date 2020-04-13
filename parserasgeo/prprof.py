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
			if isinstance(e, Encroachments):
				to_return.append(e)
		return to_return

	def write(self, out_profile_file_name):
		'''
		Write the profile file to an output file
		'''

		with open(out_profile_file_name, 'wt') as outfile:
			for line in self.prof_list:
				outfile.write(line)

if __name__ == '__main__':
	in_prof_file = 'C:/C_PROJECTS/Misc/20200413_Encroachments/RAS/SecondCreekFHAD-.p01'

	prof = ParseRASProfile(in_prof_file)
	encroachments = prof.return_encroachments()

	print(len(encroachments))
	for l in encroachments:
		print(l)
