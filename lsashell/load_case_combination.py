'''
Created on 13. 4. 2014

@author: Vancikv
'''

from traits.api import \
    HasTraits, Int, Instance, Property

from traitsui.api import \
    View, Item

from limit_state import \
    LSTable


class LCC(HasTraits):

    lcc_id = Int

    # lcc_table = WeakRef()

    ls_table = Instance(LSTable)

    assess_value = Property()

    def _get_assess_value(self):
        return self.ls_table.assess_value

    traits_view = View(Item('ls_table@', show_label=False),
                       resizable=True,
                       scrollable=True
                       )
