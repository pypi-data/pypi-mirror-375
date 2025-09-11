from teradataml.analytics.byom.H2OPredict import H2OPredict
from teradataml.analytics.byom.PMMLPredict import PMMLPredict

from teradataml.analytics.meta_class import _AnalyticFunction
from teradataml.analytics.meta_class import _common_init, _common_dir

_byom_functions = ['H2OPredict', 'PMMLPredict', 'ONNXPredict', 'DataikuPredict', 'DataRobotPredict', 'ONNXEmbeddings', 'ONNXSeq2Seq']

for func in _byom_functions:
    globals()[func] = type("{}".format(func), (_AnalyticFunction,),
                           {"__init__": lambda self,
                                               **kwargs: _common_init(self,
                                                                      'byom',
                                                                      **kwargs),
                            "__doc__": _AnalyticFunction.__doc__,
                            "__dir__": _common_dir})