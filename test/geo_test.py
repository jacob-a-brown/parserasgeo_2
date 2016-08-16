import glob
import sys
import filecmp
import subprocess
sys.path.insert(0, '..')

import prg


def main():
    outfile = 'prg_test.g00'
    test_files = glob.glob('../geos/*.g??')
    print test_files

    for test_file in test_files:
        print '*' * 100,
        print 'Processing ', test_file
        geo_list = prg.import_ras_geo(test_file)
        prg.export_ras_geo(outfile, geo_list)

        if filecmp.cmp(test_file, outfile, shallow=False):
            print 'Geometry file', test_file, 'exported correctly.'
        else:
            print 'WARNING: file', test_file, 'did not export properly'
            subprocess.Popen(["diff", test_file, outfile])
            sys.exit('WARNING: file' + test_file + 'did not export properly')

if __name__ == '__main__':
    main()