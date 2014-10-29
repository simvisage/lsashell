'''
Created on Oct 27, 2014

@author: rch
'''


from traits.api import \
    HasTraits, Float, Enum, on_trait_change, Event, Button

from traitsui.api import \
    View

class LoadCase(HasTraits):
    '''Specification of the load case results obtained from
    the numerical analysis of structural behavior.
    '''

    category = Enum('dead-load', 'additional dead-load', 'imposed-load')
    '''Category of the loading case
    '''
    def _category_default(self):
        return 'additional dead-load'

    change_event = Event

    change_button = Button

    @on_trait_change('change_event, change_button')
    def resolve_category_dependencies(self):
        print 'resolving'
        self.gamma_fav = self._get_gamma_fav()
        self.gamma_unf = self._get_gamma_unf()

    gamma_fav = Float(input=True)
    '''Safety factors ULS
    '''
    def _gamma_fav_default(self):
        return self._get_gamma_fav()

    def _get_gamma_fav(self):
        if self.category == 'dead-load':
            return 1.00
        if self.category == 'additional dead-load':
            return 0.00
        if self.category == 'imposed-load':
            return 0.00

    gamma_unf = Float(input=True)
    '''
    '''
    def _gamma_unf_default(self):
        return self._get_gamma_unf()

    def _get_gamma_unf(self):
        if self.category == 'dead-load':
            return 1.35
        if self.category == 'additional dead-load':
            return 1.35
        if self.category == 'imposed-load':
            return 1.50

    traits_view = View(['category',
                        'gamma_fav',
                        'gamma_unf',
                        'change_button'])

if __name__ == '__main__':
    ls = LoadCase()
    print'category:', ls.category
    print 'initial', ls.gamma_fav
    ls.category = 'imposed-load'
    print 'category:', ls.category
    print 'category changed', ls.gamma_fav
    ls.change_event = True
    print 'category:', ls.category
    print 'event fired', ls.gamma_fav

    ls.configure_traits()
