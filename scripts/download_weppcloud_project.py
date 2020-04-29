import sys
from urllib.request import urlopen
import zipfile
import argparse
import os
from os.path import exists
from os.path import join as _join

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('run_id', type=str,   
                        help='run_id of weppcloud project')
    parser.add_argument('destination', type=str,   
                        help='directory to download to')
    parser.add_argument('-n', '--no_extract',
                        help='do not extract', action='store_true', default=False)    
    parser.add_argument('-r', '--remove',
                        help='remove zipfile after extracting', action='store_true', default=False)    
    args = parser.parse_args()

    wd = args.run_id
    destination = args.destination
    assert exists(destination)
    
    no_extract = args.no_extract
    remove = args.remove
    
    url = 'https://wepp1.nkn.uidaho.edu/weppcloud/runs/{wd}/0/archive'

    fname = _join(destination, "{wd}.zip".format(wd=wd))
    print("attempting to download", wd)

    response = urlopen('https://wepp1.nkn.uidaho.edu/weppcloud/runs/{wd}/0/archive'.format(wd=wd))
    data = response.read()
    print('download complete')


    print('saving archive')
    if exists(fname):
        os.remove(fname)

    # Write data to file
    file_ = open(fname, 'wb')
    file_.write(data)
    file_.close()

    if not no_extract:
        print('extracting archive')
        zip_ref = zipfile.ZipFile(fname, 'r')
        zip_ref.extractall(_join(destination, wd))
        zip_ref.close()
        
    if remove:
        os.remove(fname)

