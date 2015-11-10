__title__ = 'pysdn'
__version__ = '1.3.4'
__author__ = 'Sergei Garbuzov'
__license__ = 'BSD'
__copyright__ = 'Brocade Communications'

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
