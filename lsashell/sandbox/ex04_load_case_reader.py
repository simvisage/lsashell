'''
Created on Oct 28, 2014

@author: rch
'''

from load_case_reader import \
    LCReaderInfoCAD

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

    state_data = lc_reader.read_state_data('LC6.txt')
    geo_data = lc_reader.read_geo_data('LC6.txt')

    import mayavi.mlab as mlab

    lc_reader.plot_sd(mlab, geo_data, 'nx', state_data, 10.0)

    mlab.show()
