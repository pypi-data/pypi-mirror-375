from teradataml.analytics.meta_class import _AnalyticFunction
from teradataml.analytics.meta_class import _common_init, _common_dir
from teradataml.analytics.json_parser.utils import _get_associated_parent_classes

_uaf_functions = ['ACF',
                  'ArimaEstimate',
                  'ArimaValidate',
                  'DIFF',
                  'LinearRegr',
                  'MultivarRegr',
                  'PACF',
                  'PowerTransform',
                  'SeasonalNormalize',
                  'Smoothma',
                  'UNDIFF',
                  'Unnormalize',
                  'ArimaForecast',
                  'DTW',
                  'HoltWintersForecaster',
                  'MAMean',
                  'SimpleExp',
                  'BinaryMatrixOp',
                  'BinarySeriesOp',
                  'GenseriesFormula',
                  'MatrixMultiply',
                  'Resample',
                  'BreuschGodfrey',
                  'BreuschPaganGodfrey',
                  'CumulPeriodogram',
                  'DickeyFuller',
                  'DurbinWatson',
                  'FitMetrics',
                  'GoldfeldQuandt',
                  'Portman',
                  'SelectionCriteria',
                  'SignifPeriodicities',
                  'SignifResidmean',
                  'WhitesGeneral',
                  'Convolve',
                  'Convolve2',
                  'DFFT',
                  'DFFT2',
                  'DFFT2Conv',
                  'DFFTConv',
                  'GenseriesSinusoids',
                  'IDFFT',
                  'IDFFT2',
                  'LineSpec',
                  'PowerSpec',
                  'ExtractResults',
                  'InputValidator',
                  'MInfo',
                  'SInfo',
                  'TrackingOp',
                  'AutoArima',
                  'ArimaXEstimate',
                  'DWT',
                  'DWT2D',
                  'IDWT',
                  'IDWT2D',
                  'IQR',
                  'Matrix2Image',
                  'SAX',
                  'WindowDFFT']

for func in _uaf_functions:
    _c = (_AnalyticFunction,)
    for assoc_cl in _get_associated_parent_classes(func):
        _c = _c + (assoc_cl,)
    globals()[func] = type("{}".format(func), _c,
                           {"__init__": lambda self, **kwargs: _common_init(self,
                            'uaf', **kwargs),
                            "__doc__": _AnalyticFunction.__doc__,
                            "__dir__": _common_dir})

_stored_procedure = ['CopyArt', 'FilterFactory1d']

for func in _stored_procedure:
    globals()[func] = type("{}".format(func), (_AnalyticFunction,),
                           {"__init__": lambda self, **kwargs: _common_init(self,
                            'stored_procedure', **kwargs),
                            "__doc__": _AnalyticFunction.__doc__})
