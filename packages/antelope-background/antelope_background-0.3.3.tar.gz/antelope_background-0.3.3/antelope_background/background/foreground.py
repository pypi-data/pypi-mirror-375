from antelope.interfaces.iforeground import ForegroundInterface
from antelope_core.implementations import BasicImplementation

# we do NOT want to do this

class TarjanForegroundImplementation(BasicImplementation, ForegroundInterface):
    def traverse(self, fragment, scenario=None, **kwargs):
        """
        IN the background implementation of the foreground interface, a traversal is generative.
        :param fragment:
        :param scenario:
        :param kwargs:
        :return:
        """
        pass
