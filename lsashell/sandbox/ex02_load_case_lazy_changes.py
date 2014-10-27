'''
Created on Oct 27, 2014

@author: rch
'''


from traits.api import \
    HasTraits, Property, Float, cached_property, Enum

class LoadCase(HasTraits):
    '''Specification of the load case results obtained from
    the numerical analysis of structural behavior.
    '''

    category = Enum('dead-load', 'additional dead-load', 'imposed-load', input=True)
    '''Category of the loading case
    '''

    gamma_fav = Property(Float, depends_on='category')
    '''Safety factors ULS
    '''
    @cached_property
    def _get_gamma_fav(self):
        print 'property change'
        if self.category == 'dead-load':
            return 1.00
        if self.category == 'additional dead-load':
            return 0.00
        if self.category == 'imposed-load':
            return 0.00

    gamma_unf = Property(Float, depends_on='category')
    '''
    '''
    @cached_property
    def _get_gamma_unf(self):
        if self.category == 'dead-load':
            return 1.35
        if self.category == 'additional dead-load':
            return 1.35
        if self.category == 'imposed-load':
            return 1.50

if __name__ == '__main__':
    ls = LoadCase()

    for i in range(5):
        print 'gamma_fav', ls.gamma_fav

    ls.configure_traits()
