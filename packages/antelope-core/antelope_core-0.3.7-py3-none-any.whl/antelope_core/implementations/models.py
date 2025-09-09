from antelope.models import ResponseModel, EntityRef
from typing import Optional, List, Dict

UNRESOLVED_ANCHOR_TYPE = 'term'  # this is used when an anchor node's origin cannot be resolved


class Anchor(ResponseModel):
    """
    An anchor is either: a terminal node designation (i.e. origin + ref) or a context, and a descent marker.
    and cached LCIA scores

    Use FlowTermination.to_anchor(term, ..) to produce
    """
    node: Optional[EntityRef] = None
    anchor_flow: Optional[EntityRef] = None
    context: Optional[List[str]] = None
    descend: bool
    score_cache: Optional[Dict[str, float]] = None

    def __str__(self):
        """
        Replicate FlowTermination

        :return:
          '---:' = fragment I/O
          '-O  ' = foreground node
          '-*  ' = process
          '-#  ' - sub-fragment (aggregate)
          '-#::' - sub-fragment (descend)
          '-B ' - terminated background
          '--C ' - cut-off background
          '--? ' - ungrounded catalog ref

        :return:
        """
        if self.node:
            if self.node.entity_type == 'process':
                return '-*  '
            elif self.node.entity_type == UNRESOLVED_ANCHOR_TYPE:
                return '--? '
            else:
                if self.descend:
                    return '-#::'
                else:
                    return '-#  '
        elif self.context:
            if self.context == ['None']:
                return '-)  '
            else:
                return '-== '
        else:
            return '---:'

    @property
    def type(self):
        if self.node:
            return 'node'
        elif self.context:
            return 'context'
        else:
            return 'cutoff'

    @property
    def unit(self):
        if self.is_null:
            return '--'
        if self.node:
            if self.node.entity_type == 'fragment':
                return '####'
            return '****'
        return '::::'

    @property
    def is_null(self):
        return not bool(self.node or self.context)

    @classmethod
    def null(cls):
        return cls(descend=True)

