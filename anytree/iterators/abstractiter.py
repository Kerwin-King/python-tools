import typing as t
from abc import abstractmethod

_T = t.TypeVar("_T")


class AbstractIter(t.Generic[_T]):

    def __init__(
        self,
        node: _T,
        filter_: t.Callable[[_T], bool] | None = None,
        stop: t.Callable[[_T], bool] | None = None,
        maxlevel: int | None = None,
    ):
        """
        Iterate over tree starting at `node`.

        Base class for all iterators.

        Keyword Args:
            filter_: function called with every `node` as argument, `node` is returned if `True`.
            stop: stop iteration at `node` if `stop` function returns `True` for `node`.
            maxlevel (int): maximum descending in the node hierarchy.
        """
        self.node = node
        self.filter_ = filter_
        self.stop = stop
        self.maxlevel = maxlevel
        self.__iter = None

    @staticmethod
    def __default_filter(node: _T):
        return True

    @staticmethod
    def __default_stop(node: _T):
        return False

    @staticmethod
    def _abort_at_level(level: int, maxlevel: int | None):
        return maxlevel is not None and level > maxlevel

    @staticmethod
    def _get_children(children, stop: t.Callable[[_T], bool]) -> list[_T]:
        return [child for child in children if not stop(child)]

    def __init(self):
        node = self.node
        maxlevel = self.maxlevel
        filter_: t.Callable[[_T], bool] = self.filter_ or AbstractIter.__default_filter
        stop: t.Callable[[_T], bool] = self.stop or AbstractIter.__default_stop
        children = t.cast(
            list[_T],
            (
                []
                if AbstractIter._abort_at_level(1, maxlevel)
                else AbstractIter._get_children([node], stop)
            ),
        )
        return self._iter(children, filter_, stop, maxlevel)

    def __iter__(self):
        return self

    def __next__(self):
        if self.__iter is None:
            self.__iter = self.__init()
        return next(self.__iter)  # type: ignore

    @abstractmethod
    def _iter(
        self,
        children,
        filter_: t.Callable[[_T], bool],
        stop: t.Callable[[_T], bool],
        maxlevel: int | None,
    ): ...
