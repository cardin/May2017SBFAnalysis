from typing import Any, Callable, List, Tuple


class ReplacePair(object):
    """
    Tuple to specify how and what to replace

    Attributes:
        name (str): Name of this ReplacePair
        prop_name (str): Name of the property. Object-oriented. Dot-delimited.
        prop_arr (List[str]): Name of the property split by nested layers
        matcher (callable): A lambda that takes in the current value. It returns an indication
                        if the value has changed, and if so, what the new value is.
    """
    name: str
    prop_name: str
    prop_arr: List[str]
    matcher: Any
    # Can't be Callable, 'cos MyPy has problems identifying methods vs lambdas,
    # of which the former cannot be re-assigned.
    # https://github.com/python/mypy/issues/708

    def __init__(self, prop_name: str, name: str,
                 matcher: Callable[[Any], Tuple[bool, Any]]) -> None:
        self.name = name
        self.prop_name = prop_name
        self.prop_arr = prop_name.split('.')
        self.matcher = matcher

    def clone(self) -> 'ReplacePair':
        """
        Returns:
            Shallow clone
        """
        # Note: we can't use self.prop_name - it doesn't have .pop() action
        return ReplacePair('.'.join(self.prop_arr), self.name,
                           self.matcher)
