'''
Created on 13. 4. 2014

@author: Vancikv
'''

from traits.api import \
    HasTraits, Directory, \
    Property, WeakRef

class LCReader(HasTraits):
    '''Base class for LCC Readers.'''

    _dd = Directory

    data_dir = Property
    def _get_data_dir(self):
        if self._dd:
            return self._dd
        else:
            return self.lcc_table.data_dir
    def _set_data_dir(self, data_dir):
        self._dd = data_dir

    def check_for_consistency(self, lc_list, geo_data_dict):
        return True

    lcc_table = WeakRef
