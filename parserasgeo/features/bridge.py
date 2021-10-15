from .tools import fl_int #  , split_by_n_str, pad_left, print_list_by_group, split_block_obs, split_by_n
from .description import Description

# START NON FEATURE CLASSES
class Width_Elev_Pair(object):
    '''
    This class is used to store width elevation pairs for piers
    '''
    def __init__(self, width, elev):
        self.width = width
        self.elev = elev

# START FEATURE CLASSES

class Feature(object):
    """
    This is a template for other features.
    """
    def __init__(self):
        pass

    @staticmethod
    def test(line):
        if line.split('=')[0] == 'XS GIS Cut Line':
            return True
        return False

    def import_geo(self, line, geo_file):
        return line

    def __str__(self):
        pass

class Deck_Roadway(object):
    def __init__(self):
        pass
        

class Pier(object):
    def __init__(self):
        self.center_sta_us = None
        self.center_sta_ds = None
        self.floating_debris = None
        self.debris_width = None
        self.debris_height = None

        self.us_piers = []
        self.ds_piers = []

        # it's not currently known what these values are
        # but they change from one bridge pier to the next
        # so they need to be recorded to correctly be written
        self.mystery_1 = None
        self.mystery_2 = None
        self.mystery_3 = None
        self.mystery_4 = None

    @staticmethod
    def test(line):
        # there are lines in bridges that are just spaces. skip those if that is the case
        if len(line.split()) == 0:
            return False
        elif line.split()[0] == 'Pier':
            return True
        return False

    def import_geo(self, line, geo_file):
        fields = line[39:].split(',')
        self.center_sta_us = fl_int(fields[0])
        self.mystery_1 = fields[1]
        self.center_sta_ds = fl_int(fields[2])
        self.mystery_2 = fields[3]
        self.mystery_3 = fields[4]
        self.mystery_4 = fields[5]
        if fl_int(fields[6]) == 0:
            self.floating_debris = False
        else:
            self.floating_debris = True

        if len(fields[7]) == 0:
            self.debris_width = 0
        else:
            self.debris_width = fl_int(fields[7])

        if fields[8] == '\n':
            self.debris_height = 0
        else:
            self.debris_height = fl_int(fields[8])

        # upstream piers
        line = next(geo_file)
        fields = line.split()
        us_pier_widths = [fl_int(width) for width in fields]

        line = next(geo_file)
        fields = line.split()
        us_pier_elevs = [fl_int(elev) for elev in fields]

        for i in range(len(us_pier_widths)):
            temp_width = us_pier_widths[i]
            temp_elev = us_pier_elevs[i]
            temp_width_elev = Width_Elev_Pair(temp_width, temp_elev)
            self.us_piers.append(temp_width_elev)

        # downstream peirs
        line = next(geo_file)
        fields = line.split()
        ds_pier_widths = [fl_int(width) for width in fields]

        line = next(geo_file)
        fields = line.split()
        ds_pier_elevs = [fl_int(elev) for elev in fields]

        for i in range(len(ds_pier_widths)):
            temp_width = ds_pier_widths[i]
            temp_elev = ds_pier_elevs[i]
            temp_width_elev = Width_Elev_Pair(temp_width, temp_elev)
            self.ds_piers.append(temp_width_elev)

        return next(geo_file)


    def __str__(self):
        s = 'Pier Skew, UpSta & Num, DnSta & Num=  ,'
        s += str(self.center_sta_us)
        s += ',{},'.format(self.mystery_1)
        s += str(self.center_sta_ds)
        s += ',{},{},{},'.format(self.mystery_2, self.mystery_3, self.mystery_4)
        if self.floating_debris is True:
            s += ' 1 ,'
        else:
            s += ' 0 ,'

        if self.debris_width == 0:
            s += ','
        else:
            s += str(self.debris_width) + ','

        if self.debris_height == 0:
            pass
        else:
            s += str(self.debris_height)

        s += '\n'

        # upstream piers
        for pier in self.us_piers:
            width = pier.width
            s += str(width).rjust(8)
        s += '\n'

        for pier in self.us_piers:
            elev = pier.elev
            s += str(elev).rjust(8)
        s += '\n'

        # downstream piers
        for pier in self.ds_piers:
            width = pier.width
            s += str(width).rjust(8)
        s += '\n'

        for pier in self.ds_piers:
            elev = pier.elev
            s += str(elev).rjust(8)
        s += '\n'

        return s

# TODO: possibly move header into Bridge
class Header(object):
    def __init__(self):

        self.station = None
        self.node_type = None
        self.value1 = None
        self.value2 = None
        self.value3 = None

    @staticmethod
    def test(line):
        if line[:23] == 'Type RM Length L Ch R =':
            if line[24:25] == '3':
                return True
        return False

    def import_geo(self, line, geo_file):
        fields = line[23:].split(',')
        # print line, fields
        assert len(fields) == 5
        # vals = [fl_int(x) for x in fields]
        # Node type and cross section id
        self.node_type = fl_int(fields[0])
        self.station = fl_int(fields[1])
        # TODO: Not sure what these are yet
        self.value1 = fields[2]
        self.value2 = fields[3]
        self.value3 = fields[4]
        return next(geo_file)

    def __str__(self):
        s = 'Type RM Length L Ch R = '
        s += str(self.node_type) + ' ,'
        s += '{:<8}'.format(str(self.station)) + ','
        s += str(self.value1) + ',' + str(self.value2) + ',' + str(self.value3)  # + '\n' TODO: Add this back it later once the remainder of the
                                                                                                    # header if figured out
        return s


class Bridge(object):
    def __init__(self, river, reach):
        self.river = river
        self.reach = reach

        # Load all bridge parts
        self.header = Header()
        self.pier = Pier()

        self.parts = [self.header, self.pier]

        self.geo_list = []  # holds all parts and unknown lines (as strings)

    def import_geo(self, line, geo_file):
        while line != '\n':
            for part in self.parts:
                if part.test(line):
                    # print str(type(part))+' found!'
                    line = part.import_geo(line, geo_file)
                    self.parts.remove(part)
                    self.geo_list.append(part)
                    break
            else:  # Unknown line, add as text
                self.geo_list.append(line)
                line = next(geo_file)
        return line

    def __str__(self):
        s = ''
        for line in self.geo_list:
            s += str(line)
        return s + '\n'

    @staticmethod
    def test(line):
        return Header.test(line)

if __name__ == '__main__':
    from pathlib import Path
    test_dir = Path('C:/C_Projects/Python/parserasgeo/test')
    file_path = test_dir / 'HG_bridge_test.g01'

    river = 'test river'
    reach = 'test_reach'

    test = Bridge(river, reach)
    with open(file_path, 'rt') as geo_file:
        for line in geo_file:
            if test.test(line):
                test.import_geo(line, geo_file)
                break

    print(str(test))

    for g in test.geo_list:
        if type(g) == Pier:
            pier = g
            break

    pier.us_piers[0].width = 5
    print(str(test))