from teradataml.analytics.meta_class import _AnalyticFunction
from teradataml.analytics.meta_class import _common_init, _common_dir

_nos_functions = ['ReadNOS', 'WriteNOS', 'Image2Matrix']

for func in _nos_functions:
    globals()[func] = type("{}".format(func), (_AnalyticFunction,),
                           {"__init__": lambda self, **kwargs: _common_init(self,
                            'nos', **kwargs),
                            "__doc__": _AnalyticFunction.__doc__,
                            "__dir__": _common_dir})
