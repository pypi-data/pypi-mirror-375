from mplabml.client import Client
from mplabml.client import Client as MPLABML
from mplabml.client import __version__

__all__ = ["MPLABML", "Client"]


try:
    from IPython.core.display import HTML

    display(HTML("<style>.container { width:90% !important; }</style>"))
except:
    pass

name = "mplabml"
