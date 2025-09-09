"""
Analogous to flat_background, except containing a live Tarjan engine instead of a flattened (static) bg.

The way this works is:

 - a data resource is created with bm_dynamic as the ds_type

"""

from .background_engine import BackgroundEngine
from .background_layer import BackgroundLayer, ExchDef, TermRef


class LiveBackground(BackgroundLayer):
    """
    This is used to store an operable Tarjan engine to dynamically construct partially-ordered backgrounds from
    traversals and retain a Tarjan stack.
    """
    @classmethod
    def from_index(cls, index, preferred=None, **kwargs):
        engine = BackgroundEngine(index, preferred=preferred, **kwargs)
        return cls(engine)

    @property
    def index(self):
        return self._engine.fg

    def __init__(self, engine):
        """
        so... how do we now add traversals to this engine? ans: we use the foreground interface

        """
        self._engine = engine

