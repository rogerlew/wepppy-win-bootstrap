import sys
from urllib.request import urlopen
import zipfile
import os
from os.path import exists

if __name__ == "__main__":

    wd = sys.argv[-1].strip()

    assert not wd.endswith('.py')

    url = 'https://wepp1.nkn.uidaho.edu/weppcloud/runs/{wd}/0/archive'

    fname = "{wd}.zip".format(wd=wd)
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


    print('extracting archive')
    zip_ref = zipfile.ZipFile(fname, 'r')
    zip_ref.extractall(wd)
    zip_ref.close()
