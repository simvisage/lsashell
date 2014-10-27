'''
Created on Oct 27, 2014

@author: rch
'''


from traits.api import \
    HasTraits, Float, Enum, on_trait_change

class LoadCase(HasTraits):
    '''Specification of the load case results obtained from
    the numerical analysis of structural behavior.
    '''

    category = Enum('dead-load', 'additional dead-load', 'imposed-load', input=True)
    '''Category of the loading case
    '''
    def _category_default(self):
        return 'additional dead-load'

    @on_trait_change('category')
    def resolve_category_dependencies(self):
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

if __name__ == '__main__':
    ls = LoadCase()
    print ls.__doc__
    print ls.gamma_fav
    ls.configure_traits()
