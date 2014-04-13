'''
Created on 13. 4. 2014

@author: Vancikv
'''

from traits.api import \
    Property, Color, Float
    
from traitsui.tabular_adapter \
    import TabularAdapter

class LSArrayAdapter (TabularAdapter):

    columns = Property
    def _get_columns(self):
#        print 'GETTING COLUMNS', self.object.columns, self.object, self.object.__class__
        columns = self.object.columns
        return [ (name, idx) for idx, name in enumerate(columns) ]

    font = 'Courier 10'
    alignment = 'right'
    format = '%5.2f'  # '%g'
    even_bg_color = Color(0xE0E0FF)
    width = Float(80)
