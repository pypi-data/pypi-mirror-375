"""
# morethon
Interpreter for morethon language.

## See Also
### Github repository
* https://github.com/Chitaoji/morethon/

### PyPI project
* https://pypi.org/project/morethon/

## License
This project falls under the BSD 3-Clause License.

"""

from typing import List

from . import core
from .__version__ import __version__
from .core import *

__all__: List[str] = []
__all__.extend(core.__all__)
