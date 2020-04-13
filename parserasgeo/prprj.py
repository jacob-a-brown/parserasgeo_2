"""
prprj.py - parse RAS project file

Version 0.001

Parses very basic information from a RAS project file.

"""

from features import Encroachments

class ParseRASProject(object):
    def __init__(self, project_filename):
        # full project name
        self.plan_title = None 

        # list of the lines in the project file
        # stored either as strings or custom classes
        self.proj_list = []

        with open(project_filename, 'rt') as pr_file:
            for line in pr_file:
                if line.split('=')[0] == 'Plan Title':
                    self.plan_title = line.split('=')[1]
                elif Encroachments.test(line):
                    encroachment = Encroachments()
                    
                    # import_proj returns the next line, which needs to be saved and
                    # added to the project list so that it can be written to the 
                    # out file
                    line_after = encroachment.import_proj(line, pr_file)
                    self.proj_list.append(encroachment)
                    self.proj_list.append(line_after)
                else:
                    self.proj_list.append(line)

    def __str__(self):
        s = 'Proj Title='+self.plan_title
        return s

    def return_encroachments(self):
        '''
        Returns the Encroachments found in the project file
        '''
        to_return = []
        for e in self.proj_list:
            if isinstance(e, Encroachments):
                to_return.append(e)
        return to_return

    def write(self, out_project_file_name):
        '''
        Write the project file to an output file
        '''

        with open(out_project_file_name, 'wt') as outfile:
            outfile.write('Plan Title={}'.format(self.plan_title))
            for line in self.proj_list:
                outfile.write(str(line))


if __name__ == '__main__':
    in_proj_file = 'C:/C_PROJECTS/Misc/20200413_Encroachments/RAS/SecondCreekFHAD-.p01'

    proj = ParseRASProject(in_proj_file)
    encroachments = proj.return_encroachments()

    for l in encroachments:
    	print(len(l.nodes))
    	print(l)

    out_file = 'C:/C_PROJECTS/Misc/20200413_Encroachments/RAS/test_out/test.p01'

    proj.write(out_file)
