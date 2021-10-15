from .tools import fl_int #  , split_by_n_str, pad_left, print_list_by_group, split_block_obs, split_by_n
from .description import Description

# START NON FEATURE CLASSES
class Width_Elev_Pair(object):
    '''
    This class is used to store width - elevation pairs for piers
    '''
    def __init__(self, width, elev):
        self.width = width
        self.elev = elev

class Sta_HighChord_LowChord(object):
    '''
    This class is used to store station - high chord - low chord triplets for decks
    '''
    def __init__(self, station, high_chord, low_chord):
        self.station = station
        self.high_chord = high_chord
        self.low_chord = low_chord

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
        self.distance = None
        self.width = None
        self.weir_coef = None
        self.deck_skew = None
        self.min_weir_flow_elev = None
        self.max_submergence = None
        self.us_embankment_ss = None
        self.ds_embankment_ss = None

        self.weir_crest_shape = None

        # only to be populated if weir_crest_shape == 'ogee'
        self.spill_approach_height = None
        self.design_energy_head = None

        self.us_sta_chords = []
        self.ds_sta_chords = []

        # unknown what these are for
        self.mystery_1 = None

    @staticmethod
    def test(line):
        if line.split()[0] == 'Deck':
            return True
        return False

    def import_geo(self, line, geo_file):
        # the parameters start after the test, unlike other objects such as Pier and Header
        line = next(geo_file)
        fields = line.split(',')

        self.distance = fl_int(fields[0])
        self.width = fl_int(fields[1])
        self.weir_coef = fl_int(fields[2])
        self.deck_skew = fl_int(fields[3])

        # these are to be used for internal record keeping. they are useful in parsing
        # the original geofile
        # they will be re-written to the geofile in __str__ and not stored as attributes
        # this is because the user may want to add upstream or downstream station/high coord/low coord
        # values, which would change the number of upstream or downstream coords
        num_us_chords = int(fields[4])
        num_ds_chords = int(fields[5])

        # could be blank
        try:
            self.min_weir_flow_elev = fl_int(fields[6])
        except ValueError:
            pass

        self.mystery_1 = fields[7]

        # could be blank
        try:
            self.max_submergence = fl_int(fields[8])
        except ValueError:
            pass

        if fl_int(fields[9]) == 0:
            self.weir_crest_shape = 'broad_crested'
        else:
            self.weir_crest_shape = 'ogee'

        # can be nothing. always has a preceding space
        if len(fields[9]) >1:
            self.us_embankment_ss = fl_int(fields[10])

        # can be nothing. does not have a preceding space
        if len(fields[10]) > 0:
            self.ds_embankment_ss = fl_int(fields[11])

        # only applicable for ogee shaped weirs
        if self.weir_crest_shape == 'ogee':
            print(self.weir_crest_shape)
            self.spill_approach_height = fl_int(fields[12])
            self.design_energy_head = fl_int(fields[13])

        line = next(geo_file)
        # collect the upstream and downstream deck station - high chord - low chord data
        # the collection will continue until the first character of the line is a letter
        temp_stations = []
        temp_high_chords = []
        temp_low_chords = []

        # flags for which list to populate
        populate_stations = True
        populate_high_chords = False
        populate_low_chords = False

        # flags for to populate upstream or downstream values
        # start with upstream flag
        upstream_flag = True
        downstream_flag = False

        count = 0

        while upstream_flag is True or downstream_flag is True:
            # the count is used to check against num_us_coords and num_ds_coords
            # first round collect all of the us stations, then the us high coords, then the us low coords
            # repeated for the ds stations, ds high coords, and ds low coords
            vals = [line[i:i+8] for i in range(0, len(line), 8)]

            # remove the newline character at the end of every line
            del(vals[-1])

          
            # convert values to a float or int
            # otherwise keep the spaces
            # this is important for record keeping and appropriate spacing in the geo file
            for i in range(len(vals)):
                try: 
                    vals[i] = fl_int(vals[i])
                except ValueError:
                    pass

            if populate_stations:
                temp_stations.extend(vals)
            elif populate_high_chords:
                temp_high_chords.extend(vals)
            elif populate_low_chords:
                temp_low_chords.extend(vals)

            count += len(vals)
            line = next(geo_file)


            # populate the upstream station chords
            if upstream_flag:
                if count == num_us_chords:
                    populate_stations = False
                    populate_high_chords = True
                elif count == num_us_chords * 2:
                    populate_high_chords = False
                    populate_low_chords = True
                elif count == num_us_chords * 3:
                    populate_low_chords = False
                    populate_stations = True
                    upstream_flag = False
                    downstream_flag = True


                    # populate stations chords
                    for j in range(len(temp_stations)):
                        temp_station = temp_stations[j]
                        temp_high_chord = temp_high_chords[j]
                        temp_low_chord = temp_low_chords[j]
                        self.us_sta_chords.append(Sta_HighChord_LowChord(temp_station, temp_high_chord, temp_low_chord))

                    # reset the counts and temporary lists
                    count = 0
                    temp_stations = []
                    temp_high_chords = []
                    temp_low_chords = []

            # populate the downstream station chords
            if downstream_flag:
                if count == num_ds_chords:
                    populate_stations = False
                    populate_high_chords = True
                elif count == num_ds_chords * 2:
                    populate_high_chords = False
                    populate_low_chords = True
                elif count == num_ds_chords * 3:
                    populate_low_chords = True
                    populate_stations = True
                    downstream_flag = False

                    # populate stations chords
                    for j in range(len(temp_stations)):
                        temp_station = temp_stations[j]
                        temp_high_chord = temp_high_chords[j]
                        temp_low_chord = temp_low_chords[j]
                        self.ds_sta_chords.append(Sta_HighChord_LowChord(temp_station, temp_high_chord, temp_low_chord))

        return line

    def __str__(self):
        s = 'Deck Dist Width WeirC Skew NumUp NumDn MinLoCord MaxHiCord MaxSubmerge Is_Ogee\n'
        s += str(self.distance) + ','
        s += str(self.width) + ','
        s += str(self.weir_coef) +','
        s += str(self.deck_skew) + ','
        s += ' ' + str(len(self.us_sta_chords)) + ','
        s += ' ' + str(len(self.ds_sta_chords)) + ','

        if self.min_weir_flow_elev is None:
            s += ' ,'
        else:
            s += ' ' + str(self.min_weir_flow_elev) + ','
    
        s += self.mystery_1 + ','

        if self.max_submergence is None:
            s += ' ,'
        else:
            s += ' ' + str(self.max_submergence) + ','

        if self.weir_crest_shape == 'broad_crested':
            s += ' 0,'
        else:
            s += ' -1,'

        if self.us_embankment_ss is None:
            s += ' ,'
        else:
            s += ' ' + str(self.us_embankment_ss) + ','

        if self.ds_embankment_ss is None:
            s += ','
        else:
            s += str(self.ds_embankment_ss) + ','

        if self.spill_approach_height is None:
            s += ','
        else:
            s += str(self.spill_approach_height)

        if self.design_energy_head is None:
            s += '\n'
        else:
            s += str(self.design_energy_head) + '\n'

        
        # upstream station - high chord - low chord
        station_s = ''
        high_chord_s = ''
        low_chord_s = ''
        for i, elem in enumerate(self.us_sta_chords, 1):
            if isinstance(elem.station, str):
                station_s += elem.station
            else:
                station_s += str(elem.station).rjust(8)

            if isinstance(elem.high_chord, str):
                high_chord_s += elem.high_chord
            else:
                high_chord_s += str(elem.high_chord).rjust(8)

            if isinstance(elem.low_chord, str):
                low_chord_s += elem.low_chord
            else:
                low_chord_s += str(elem.low_chord).rjust(8)


            if i % 10 == 0 and i != 0:
                station_s += '\n'
                high_chord_s += '\n'
                low_chord_s += '\n'

        # add a newline to the last line of the stations if there aren't 8 in the last line
        if i % 10 != 0:
                station_s += '\n'
                high_chord_s += '\n'
                low_chord_s += '\n'

        s += station_s + high_chord_s + low_chord_s

        # downstream station - high chord - low chord
        station_s = ''
        high_chord_s = ''
        low_chord_s = ''
        for i, elem in enumerate(self.ds_sta_chords, 1):
            if isinstance(elem.station, str):
                station_s += elem.station
            else:
                station_s += str(elem.station).rjust(8)

            if isinstance(elem.high_chord, str):
                high_chord_s += elem.high_chord
            else:
                high_chord_s += str(elem.high_chord).rjust(8)

            if isinstance(elem.low_chord, str):
                low_chord_s += elem.low_chord
            else:
                low_chord_s += str(elem.low_chord).rjust(8)


            if i % 10 == 0 and i != 0:
                station_s += '\n'
                high_chord_s += '\n'
                low_chord_s += '\n'

        # add a newline to the last line of the stations if there aren't 8 in the last line
        if i % 10 != 0:
                station_s += '\n'
                high_chord_s += '\n'
                low_chord_s += '\n'

        s += station_s + high_chord_s + low_chord_s

        return s


class Pier(object):
    def __init__(self):
        self.pier_skew = None
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
        elif line[:9] == 'Pier Skew':
            return True
        return False

    def import_geo(self, line, geo_file):
        # pier skew exists
        if line[:10] == 'Pier Skew=':
            fields = line.split('=')
            self.pier_skew = fields[1]
            line = next(geo_file)

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
        s = ''
        if self.pier_skew is not None:
            s = 'Pier Skew= {} \n'.format(str(self.pier_skew))

        s += 'Pier Skew, UpSta & Num, DnSta & Num=  ,'
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
        self.deck_roadway = Deck_Roadway()

        self.parts = [self.header, self.deck_roadway, self.pier]

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

    '''
    for g in test.geo_list:
        if type(g) == Pier:
            pier = g
            break

    pier.us_piers[0].width = 5
    print(str(test))
    '''