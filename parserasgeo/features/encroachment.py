"""
The encroachments are read from the profile file, not the geo file
This is to be read using ParseRASProfile
"""

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


class Encroachments(object):
    """
    Class encroachment
    """
    def __init__(self):
    	self.river = None
    	self.reach = None
    	# node id, method, left station, right station
        self.nodes = []

    def test(line):
        if line[:13] == 'Encroach River':
            return True
        else:
            return False

    def import_prof(self, line, prof_file):
        '''
        Imports the encroachment data from the profile file
        '''
        # river name
        line = line[15:]
        self.river = line
        line = next(prof_file)

        # reach name
        line = line[15:]
        self.reach = line
        line = next(prof_file)

        while line[:12] == 'Encroach Node':
        	node_id = line[14:]
        	next(line)
        	values = line.split()
        	method = values[0]
        	left_station = fl_int(values[1])
        	right_station = fl_int(values[2])
        	temp_node = EncroachmentNode(node_id, method, left_station, right_station)
        	self.nodes.append(EncroachmentNode)
        	line = next(prof_file)

        return next(prof_file)

    def __str__(self):
    	s = ''
    	s += 'Encroach River={}\n'.format(self.river)
    	s += 'Encroach Reach={}\n'.format(self.reach)

    	for node in self.nodes:
    		s += 'Encroach Node={}\n'.format(node[0])
    		s += str(node[1]).rjust(8)
    		s += str(node[2]).rjust(8)
    		s += str(node[3]).rjust(8)
    		s += '\n'

    	return s
	