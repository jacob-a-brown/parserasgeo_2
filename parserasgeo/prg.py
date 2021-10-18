#! /usr/bin/python
"""
rasgeotool - tools for importing, modifying, and exporting HEC-RAS geometry files (myproject.g01 etc)

This has NOT been extensively tested.

Mike Bannister 2/24/2016
mike.bannister@respec.com

"""

from .features import CrossSection, RiverReach, Culvert, Bridge, LateralWeir, Junction
import os.path

# TODO - create geolist object


class CrossSectionNotFound(Exception):
    pass

class CulvertNotFound(Exception):
    pass

class BridgeNotFound(Exception):
    pass

class ParseRASGeo(object):
    def __init__(self, geo_filename, chatty=False, debug=False):
        self.geo_filename = geo_filename
        # add  test for file existence
        self.geo_list = []
        num_xs = 0
        num_river = 0
        num_bridge = 0
        num_culvert = 0
        num_lat_weir = 0
        num_junc = 0
        num_unknown = 0
        river = None
        reach = None

        if debug:
            print('Debugging is turned on')

        if geo_filename == '' or geo_filename is None:
            raise AttributeError('Filename passed to ParseRASGeo is blank.')

        if not os.path.isfile(geo_filename):
            raise AttributeError('File ' + str(geo_filename) + ' does not appear to exist.')

        # TODO - add 'debug' to all objects
        with open(geo_filename, 'rt') as geo_file:
            for line in geo_file:
                if RiverReach.test(line):
                    rr = RiverReach(debug)
                    rr.import_geo(line, geo_file)
                    river, reach = rr.header.river_name, rr.header.reach_name
                    num_river += 1
                    self.geo_list.append(rr)
                elif CrossSection.test(line):
                    xs = CrossSection(river, reach, debug)
                    xs.import_geo(line, geo_file)
                    num_xs += 1
                    self.geo_list.append(xs)
                elif Culvert.test(line):
                    culvert = Culvert(river, reach, debug)
                    culvert.import_geo(line, geo_file)
                    num_culvert += 1
                    self.geo_list.append(culvert)
                elif Bridge.test(line):
                    bridge = Bridge(river, reach)
                    bridge.import_geo(line, geo_file)
                    num_bridge += 1
                    self.geo_list.append(bridge)
                elif LateralWeir.test(line):
                    lat_weir = LateralWeir(river, reach)
                    lat_weir.import_geo(line, geo_file)
                    num_lat_weir += 1
                    self.geo_list.append(lat_weir)
                elif Junction.test(line):
                    junc = Junction()
                    junc.import_geo(line, geo_file)
                    num_junc += 1
                    self.geo_list.append(junc)
                else:
                    # Unknown line encountered. Store it as text.
                    self.geo_list.append(line)
                    num_unknown += 1
        if chatty:
            print(str(num_river)+' rivers/reaches imported')
            print(str(num_junc)+' junctions imported')
            print(str(num_xs)+' cross sections imported')
            print(str(num_bridge)+' bridge imported')
            print(str(num_culvert)+' culverts imported')
            print(str(num_lat_weir)+' lateral structures imported')
            print(str(num_unknown) + ' unknown lines imported')

    def write(self, out_geo_filename):
        with open(out_geo_filename, 'wt') as outfile:
            for line in self.geo_list:
                outfile.write(str(line))

    def return_xs_by_id(self, station, rnd=False, digits=0):
        """
        Returns XS with ID station. Rounds XS ids to digits decimal places if (rnd==True)
        :param station: id of cross section, assumed to be in ..... format
        :param rnd: rounds station to 'digits' if True
        :param digits: number of digits to round station to
        :return: CrossSection object
        """
        for item in self.geo_list:
            if isinstance(item, CrossSection):
                if rnd:
                    if round(item.header.station, digits) == round(station, digits):
                        return item
                else:
                    if item.header.station == station:
                        return item
        raise CrossSectionNotFound

    def return_xs(self, station, river, reach, strip=False, rnd=False, digits=0):
        """
        returns matching CrossSection if it is in self.geo_list. raises CrossSectionNotFound otherwise
        
        :param station: cross section id number
        :param river: name of river
        :param reach: name of reach
        :param strip: strips whitespace off river and reach if true
        :return: CrossSection object
        "raises CrossSectionNotFound: raises error if xs is not in the geometry file
        """
        return self._return_node(CrossSection, station, river, reach, strip, rnd, digits)
        
    def return_culvert(self, culvert_id, river, reach, strip=False, rnd=False, digits=0):
        """
        returns matching Culvert if it is in self.geo_list. raises CulvertNotFound otherwise
        
        :param culvert_id: culvert id number
        :param river: name of river
        :param reach: name of reach
        :param strip: strips whitespace off river and reach if true
        :return: Culvert object
        :raises CulvertNotFound: raises error if culvert is not in the geometry file
        """
        return self._return_node(Culvert, culvert_id, river, reach, strip, rnd, digits)

    def return_bridge_by_id(self, station, rnd = False, digits = 0):
        '''
        Returns bridge with ID station. Rounds bridge ids to digits decimal places if rnd == True

        --------
        Parameters
        --------
        station: int or float
            the station of the bdige

        rnd: boolean
            rounds station to digits if True

        digits: int
            number of digits to round station to

        --------
        Returns
        --------
        Bridge object
        '''

        for item in self.geo_list:
            if isinstance(item, Bridge):
                if rnd:
                    if round(item.header.station, digits) == round(station, digits):
                        return item
                else:
                    if item.header.station == station:
                        return item
        raise BridgeNotFound

    def return_bridge(self, bridge_id, river, reach, strip = False, rnd = False, digits = 0):
        '''
        Returns matching Bridge if it is self.geo list. raises BridgeNotFound otherwise
        
        --------
        Parameters
        -------
        bridge_id: int or float
            bridge id number
        river: str
            name of river
        reach: str
            name of reach
        strip: boolean
            strips whitespace off river and reach if true

        --------
        Returns
        --------
        bridge object

        --------
        Raises
        --------
        Raises BridgeNotFound error if bridge is not in the geometry file
        '''
        return self._return_node(Bridge, bridge_id, river, reach, strip, rnd, digits)



    def extract_all_xs(self):
        """
        Returns list of all cross sections in geometry
        """
        return self._extract_all_nodes(CrossSection)

    def extract_all_culverts(self):
        """
        Returns list of all culverts in geometry
        """
        return self._extract_all_nodes(Culvert)

    def extract_all_bridges(self):
        '''
        Returns list of all bridges in geometry
        '''
        return self._extract_all_nodes(Bridge)

    def number_xs(self):
        """
        Returns the number of cross sections in geo_list
        :param geo_list: list from import_ras_geo
        :return: number (int) of XS in geolist
        """
        xs_list = self.extract_all_xs()
        return len(xs_list)

    def is_xs_duplicate(self, station):
        """
        Checks for duplicate cross sections in geo_list
        rasises CrossSectionNotFound if station is not found
        :param geo_list: from import_ras_geo
        :return: True if duplicate
        """
        xs_list = self.extract_xs(self.geo_list)
        count = 0
        for xs in xs_list:
            if xs.station == station:
                count += 1
        if count > 1:
            return True
        elif count == 1:
            return False
        else:
            raise CrossSectionNotFound
    
    def _return_node(self, node_type, node_id, river, reach, strip=False, rnd=False, digits=0):
        """
        This semi-private method is written in a general format.
        It is meant to be called by more user friendly methods, such as
        return_xs or return_culvert
        
        returns matching node if it is in self.geo_list. raises <Node>NotFound otherwise where
        <Node> is a type of node
        
        :param node_type: the type of node to be returned
        :param culvert_id: culvert id number
        :param river: name of river
        :param reach: name of reach
        :param strip: strips whitespace off river and reach if true
        :return: Culvert object
        :raises NodeNotFound: raises error if the node is not found in the geometry file
        """
        wanted_river = river
        wanted_reach = reach
        wanted_node_id = node_id
        
        if node_type.__name__ == 'CrossSection':
            node_name = 'XS'
            NodeNotFound = CrossSectionNotFound
        if node_type.__name__ == 'Culvert':
            node_name = 'culvert'
            NodeNotFound = CulvertNotFound
        if node_type.__name__ == 'Bridge':
            node_name = 'bridge'
            NodeNotFound = BridgeNotFound
        
        if strip:
            if type(river) is not str and type(river) is not unicode:
                raise AttributeError('For {} "river" is not a string, got: {} instead.'.format(node_name, river))
            if type(reach) is not str and type(reach) is not unicode:
                raise AttributeError('For {} "reach" is not a string, got: {} instead.'.format(node_name, reach))
            wanted_river = river.strip()
            wanted_reach = reach.strip()
        if rnd:
            wanted_node_id = round(node_id, digits)

        for item in self.geo_list:
            if isinstance(item, node_type):
                test_river = item.river
                test_reach = item.reach
                
                test_node_id = item.header.station

                if strip:
                    test_river = test_river.strip()
                    test_reach = test_reach.strip()
                if rnd:
                    test_node_id = round(test_node_id, digits)

                # Rounding and strip is done, see if this is the right XS
                if test_node_id == wanted_node_id and test_river == wanted_river and test_reach == wanted_reach:
                    return item
        raise NodeNotFound 
            
    def _extract_all_nodes(self, node_type):
        """
        This semi-private method is written in a general format.
        It is meant to be called by more user friendly methods, such as
        extract_xs or extract_culvert
        
        :param node_type: the type of node to be returned
        :return: a list of all nodes of type <node_type> in geometry
        """
        new_geo_list = []
        for item in self.geo_list:
            if isinstance(item, node_type):
                new_geo_list.append(item)
        return new_geo_list


def main():
    from pathlib import Path
    geo_dir = Path('C:/C_PROJECTS/Python/parserasgeo/test')
    geo_file = 'Harvard_Gulch.g01'

    infile = geo_dir / geo_file
    geo = ParseRASGeo(infile)

    outfile = geo_dir / 'test_{}'.format(geo_file)
    geo.write(outfile)

if __name__ == '__main__':
    main()
