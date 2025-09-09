"""
Tools for retrieving information about impact-generating nodes in a traversal

collect_stages_by_group(): collect values of stage_property from subfragments of nodes having group_property
"""


from collections import defaultdict, deque


def _is_spec(value):
    if isinstance(value, str):
        if len(value) == 0:
            return False
        return True
    return bool(value)


def _generate_descriptors(_sub_ffs, property):
    for ff in _sub_ffs:
        v = ff.fragment.get(property)
        if _is_spec(v):
            yield v
        else:
            if ff.term.is_process:
                # we reached a terminal node with no matching key
                yield ff.term.term_node.external_ref
            elif ff.term.is_context:
                yield '/'.join(ff.term.term_node.as_list())
            elif ff.term.is_subfrag:
                for v in _generate_descriptors(ff.subfragments, property):
                    yield v
            # nothing to do for cutoffs or foreground fragments


def collect_stages_by_group(_ffs, group_property, stage_property):
    """
    A utility function to report
    :param _ffs:
    :param group_property:
    :param stage_property:
    :return:
    """
    stages = defaultdict(list)
    dq = deque(_ffs)
    while dq:
        ff = dq.popleft()
        g = ff.fragment.get(group_property)
        if _is_spec(g):
            for p in _generate_descriptors([ff], stage_property):
                stages[g].append(p)
        else:
            if ff.term.is_process:
                # we reached a terminal node with no group
                stages[None].append(ff.term.term_node.external_ref)
            elif ff.term.is_context:
                stages[None].append('/'.join(ff.term.term_node.as_list()))
            elif ff.term.is_subfrag:
                dq.extend(ff.subfragments)
            # nothing to do for cutoffs or foreground fragments
    # order-preserving remove duplicates
    return {k: list(dict.fromkeys(v)) for k, v in stages.items()}
