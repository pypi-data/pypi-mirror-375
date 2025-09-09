from .bm_static import TarjanBackground
from ..engine.live_background import LiveBackground
from ..background.foreground import TarjanForegroundImplementation


class DynamicBackground(TarjanBackground):

    def _fetch(self, entity, **kwargs):
        return self._flat.index.get(entity, **kwargs)

    def __init__(self, source, engine=None, prefer=None, **kwargs):
        super(DynamicBackground, self).__init__(source, save_after=False, **kwargs)

        if prefer:
            self._make_prefer_dict(prefer, update=True)

        if engine:
            self._flat = LiveBackground(engine)

    def make_interface(self, iface, privacy=None):
        if iface == 'foreground':
            return TarjanForegroundImplementation(self)
        return super(DynamicBackground, self).make_interface(iface, privacy=privacy)

    def create_flat_background(self, index, save_after=None, prefer=None, **kwargs):
        if self._flat is None:
            prefer_dict = self._make_prefer_dict(prefer)
            print('Creating live background')
            self._flat = LiveBackground.from_index(index, preferred=prefer_dict, **kwargs)

        return self._flat
