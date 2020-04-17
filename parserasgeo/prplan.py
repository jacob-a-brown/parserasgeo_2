"""
prplan.py - parse RAS plan file

Version 0.001

Parses very basic information from a RAS plan file.

"""

from .features import Encroachments

class ParseRASPlan(object):
    def __init__(self, plan_filename):
        self.plan_title = None   # Full plan name
        self.plan_id = None      # Short id
        self.geo_file = None     # geometry file extension: g01, g02, ..
        self.plan_file = None    # plan file extension: f01, f02, ..

        # list of the lines in the plan file
        # stored either as strings or custom classes
        self.plan_list = []

        with open(plan_filename, 'rt') as in_file:
            for line in in_file:
                if line.split('=')[0] == 'Plan Title':
                    self.plan_title = line.split('=')[1]
                    self.plan_list.append(line)
                
                elif line.split('=')[0] == 'Short Identifier':
                    self.plan_id = line.split('=')[1]
                    self.plan_list.append(line)
                
                elif line.split('=')[0] == 'Geom File':
                    self.geo_file = line.split('=')[1]
                    self.plan_list.append(line)

                elif line.split('=')[0] == 'Flow File':
                    self.flow_file = line.split('=')[1]
                    self.plan_list.append(line)

                elif Encroachments.test(line):
                    encroachment = Encroachments()

                    # import_plan returns the next line, which needs to be saved and
                    # added to the plan list so that it can be written to the 
                    # out file
                    line_after = encroachment.import_plan(line, in_file)
                    self.plan_list.append(encroachment)
                    self.plan_list.append(line_after)
                else:
                    self.plan_list.append(line)


    def __str__(self):
        s = 'Plan Title='+self.plan_title+'\n'
        s += 'Short Identifier='+self.plan_id+'\n'
        s += 'Geom File='+self.geo_file+'\n'
        s += 'Flow File='+self.flow_file+'\n'
        return s

    def write(self, out_plan_file_name):
        '''
        Write the plan file to an output file
        '''

        with open(out_plan_file_name, 'wt') as outfile:
            for line in self.plan_list:
                outfile.write(str(line))

    def return_encroachments(self):
        '''
        Returns the Encroachments found in the plan file
        '''
        for e in self.plan_list:
            if isinstance(e, Encroachments):
                return e

if __name__ == '__main__':
    in_plan_file = 'C:/C_PROJECTS/Python/EncroachmentAlterations/RAS_Models/EastPlumCreek/EPC_Reg_FW.p01'

    plan = ParseRASPlan(in_plan_file)
    encroachments = plan.return_encroachments()

    for node in encroachments.nodes:
        if node.node_id == '18323':
            print(node.node_id)
            print(node.river)
            print(node.reach)
        if node.node_id == '29076.44':
            print(node.node_id)
            print(node.river)
            print(node.reach)
            node.left_station = 10


    out_file = 'C:/C_PROJECTS/Python/EncroachmentAlterations/RAS_Models/EastPlumCreek/_test.p01'
    plan.write(out_file)
