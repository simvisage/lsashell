'''
Created on Oct 28, 2014

@author: rch
'''

from load_case_reader import \
    LCReaderInfoCAD

from load_case import \
    LC

import os

if __name__ == '__main__':

    from matresdev.db.simdb import \
        SimDB

    simdb = SimDB()

    dd = os.path.join(simdb.simdb_dir,
                      'simdata',
                      'input_data_barrelshell',
                      '2cm-feines-Netz',
                      )
    lc_reader = LCReaderInfoCAD(data_dir=dd)

    lc = LC(reader=lc_reader, file_name='LC6.txt')

    lc.configure_traits()
