from . import _version
__version__ = _version.get_versions()['version']

try:
    from AutoFeedback.plotchecks import check_plot
except ModuleNotFoundError:
    pass

from AutoFeedback.varchecks import check_vars
from AutoFeedback.answerchecks import check_answer
from AutoFeedback.funcchecks import check_func
from AutoFeedback.plotclass import line
from AutoFeedback.randomclass import randomvar

from . import _version
__version__ = _version.get_versions()['version']
