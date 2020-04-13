"""
The encroachments are read from the project file, not the geo file
This is to be read using ParseRASProject
"""

from .tools import fl_int

class EncroachmentNode(object):
    """
    An encroachment node that houses the node id, method, left station, and 
    right station
    """

    def __init__(self, node_id, method, left_station, right_station):
        self.node_id = node_id
        self.method = method
        self.left_station = left_station
        self.right_station = right_station

    def __str__(self):
        s = ''
        s += 'Encroach Node={}\n'.format(self.node_id.ljust(8))
        s += str(self.method).rjust(8)
        s += str(self.left_station).rjust(8)
        s += str(self.right_station).rjust(8)

        return s



class Encroachments(object):
    """
    Class encroachment
    """
    def __init__(self):
        self.river = None
        self.reach = None
        # node id, method, left station, right station
        self.nodes = []

    @staticmethod
    def test(line):
        if line[:14] == 'Encroach River':
            return True
        else:
            return False

    def import_proj(self, line, proj_file):
        '''
        Imports the encroachment data from the project file
        '''
        # river name
        line = line[15:]
        self.river = line.strip()
        line = next(proj_file)

        # reach name
        line = line[15:]
        self.reach = line.strip()
        line = next(proj_file)
        
        while line[:13] == 'Encroach Node':
            node_id = line[14:].strip()
            line = next(proj_file)
            values = line.split()
            method = values[0]
            left_station = fl_int(values[1])
            right_station = fl_int(values[2])
            temp_node = EncroachmentNode(node_id, method, left_station, right_station)
            self.nodes.append(temp_node)
            line = next(proj_file)

        return line

    def __str__(self):
        s = ''
        s += 'Encroach River={}\n'.format(self.river.ljust(16))
        s += 'Encroach Reach={}\n'.format(self.reach.ljust(16))

        for node in self.nodes:
            s += str(node)
            s += '\n'

        return s

if __name__ == '__main__':
    in_prof_file = 'C:/C_PROJECTS/Misc/20200413_Encroachments/RAS/SecondCreekFHAD-.p01'

    test = Encroachments()
    with open(in_prof_file, 'rt') as in_file:
        for line in in_file:
            if test.test(line):
                test.import_proj(line, in_file)
                print(test)
                break

