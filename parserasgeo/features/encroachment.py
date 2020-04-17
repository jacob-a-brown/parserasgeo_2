"""
The encroachments are read from the plan file, not the geo file
This is to be read using ParseRASPlan
"""

from .tools import fl_int

class EncroachmentNode(object):
    """
    An encroachment node that houses the node id, method, left station, and 
    right station
    """

    def __init__(self):
        self.node_id = None
        self.river = None
        self.reach = None
        self.method = None
        self.left_station = None
        self.right_station = None

    @staticmethod
    def test(line):
        '''
        Returns True if an encroachment node is reached
        '''
        if line.split('=')[0] == 'Encroach Node':
            return True
        else:
            return False

    def import_plan(self, line, plan_file):
        values = line.split('=')
        self.node_id = values[1].strip()
        line = next(plan_file)
        values = line.split()
        self.method = fl_int(values[0])
        self.left_station = fl_int(values[1])
        self.right_station = fl_int(values[2])

        return line

    def __str__(self):
        s = ''
        s += 'Encroach Node={}\n'.format(self.node_id.ljust(8))
        s += str(self.method).rjust(8)
        s += str(self.left_station).rjust(8)
        s += str(self.right_station).rjust(8)

        return s


class EncroachmentReach(object):
    '''
    This class contains all of the encroachment nodes in a given reach
    '''
    def __init__(self):
        self.name = None

    @staticmethod
    def test(line):
        '''
        Returns True if an encroachment reach is reached
        '''
        if line.split('=')[0] == 'Encroach Reach':
            return True
        else:
            return False

    def import_plan(self, line):
        values = line.split('=')
        self.name = values[1].strip()

    def __str__(self):
        return 'Encroach Reach={}'.format(self.name)

class EncroachmentRiver(object):
    '''
    This class contains all of the encroachment reaches in a given river
    '''

    def __init__(self):
        self.name = None

    @staticmethod
    def test(line):
        '''
        Returns True if an encroachment reach is reached
        '''
        if line.split('=')[0] == 'Encroach River':
            return True
        else:
            return False

    def import_plan(self, line):
        values = line.split('=')
        self.name = values[1].strip()

    def __str__(self):
        return 'Encroach River={}'.format(self.name)

class Encroachments(object):
    """
    Class encroachment
    """
    def __init__(self):
        self.nodes = []

    @staticmethod
    def test(line):
        if line[:14] == 'Encroach River':
            return True
        else:
            return False

    def import_plan(self, line, plan_file):
        '''
        Imports the encroachment data from the plan file
        '''
        while line[:8] == 'Encroach':
            if EncroachmentRiver.test(line):
                current_river = EncroachmentRiver()
                current_river.import_plan(line)
                line = next(plan_file)

            elif EncroachmentReach.test(line):
                current_reach = EncroachmentReach()
                current_reach.import_plan(line)
                line = next(plan_file)

            elif EncroachmentNode.test(line):
                current_node = EncroachmentNode()
                current_node.import_plan(line, plan_file)
                current_node.river = current_river.name
                current_node.reach = current_reach.name
                self.nodes.append(current_node)
                line = next(plan_file)

        return line
    

    def __str__(self):
        s = ''
        print_river = self.nodes[0].river
        print_reach = self.nodes[0].reach
        s += 'Encroach River={}\n'.format(print_river.ljust(16))
        s += 'Encroach Reach={}\n'.format(print_reach.ljust(16))

        for node in self.nodes:
            current_river = node.river
            current_reach = node.reach
            if current_river != print_river:
                print_river = current_river
                s += 'Encroach River={}\n'.format(print_river.ljust(16))
            if current_reach != print_reach:
                print_reach = current_reach
                s += 'Encroach Reach={}\n'.format(print_reach.ljust(16))

            s += str(node)
            s += '\n'        

        return s

if __name__ == '__main__':
    in_plan_file = 'C:/C_PROJECTS/Python/EncroachmentAlterations/RAS_Models/SecondCreek/SecondCreekFHAD-.p01'

    test = Encroachments()
    with open(in_plan_file, 'rt') as in_file:
        for l in in_file:
            if test.test(l):
                test.import_plan(l, in_file)
                print(test)
                break

