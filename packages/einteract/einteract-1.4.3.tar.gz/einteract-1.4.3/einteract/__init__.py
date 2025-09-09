"""
This module is a wrapper around the `dashlab` and this should be considered deprecated in the future.
Use [dashlab](https://github.com/asaboor-gh/dashlab) instead.
"""

import sys
import dashlab

major, minor, *_ = [int(x) for x in dashlab.__version__.split(".")]
if major >= 0 and minor >= 2: # dashlab version >= 0.2 will remove support for einteract
    raise ImportError("einteract module is deprecated. Use dashlab module instead.")

sys.modules[__name__] = dashlab # Redirect to dashlab module
dashlab.InteractBase = dashlab.DashboardBase # For backward compatibility

print("Warning: einteract module will be deprecated. Use dashlab module instead.")    