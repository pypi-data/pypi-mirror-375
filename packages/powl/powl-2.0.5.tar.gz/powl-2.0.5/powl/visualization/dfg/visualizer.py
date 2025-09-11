from pm4py.visualization.common import gview
from pm4py.visualization.common import save as gsave
from powl.visualization.dfg.variants import base
from enum import Enum
from pm4py.util import exec_utils
from copy import deepcopy
from typing import Optional, Dict, Any, Tuple
import graphviz
from pm4py.objects.log.obj import EventLog


class Variants(Enum):
    BASE = base


DEFAULT_VARIANT = Variants.BASE


def apply(dfg0: Dict[Tuple[str, str], float], log: EventLog = None, activities_count : Dict[str, int] = None, serv_time: Dict[str, float] = None, parameters: Optional[Dict[Any, Any]] = None, variant=DEFAULT_VARIANT) -> graphviz.Digraph:
    """
    Visualize a frequency/performance directly-follows graph

    Parameters
    -----------------
    dfg0
        Directly-follows graph
    log
        (if provided) Event log for the calculation of statistics
    activities_count
        (if provided) Dictionary associating to each activity the number of occurrences in the log.
    serv_time
        (if provided) Dictionary associating to each activity the average service time
    parameters
        Variant-specific parameters
    variant
        Variant:
        - Frequency DFG representation
        - Performance DFG representation

    Returns
    -----------------
    gviz
        Graphviz digraph
    """
    dfg = deepcopy(dfg0)
    return exec_utils.get_variant(variant).apply(dfg, log=log, activities_count=activities_count, serv_time=serv_time, parameters=parameters)


def save(gviz, output_file_path, parameters=None):
    """
    Save the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    output_file_path
        Path where the GraphViz output should be saved
    """
    gsave.save(gviz, output_file_path, parameters=parameters)
    return ""


def view(gviz, parameters=None):
    """
    View the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    """
    return gview.view(gviz, parameters=parameters)


def matplotlib_view(gviz, parameters=None):
    """
    Views the diagram using Matplotlib

    Parameters
    ---------------
    gviz
        Graphviz
    """

    return gview.matplotlib_view(gviz, parameters=parameters)
