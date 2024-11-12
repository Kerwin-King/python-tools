from __future__ import annotations
import typing as t
from ..error import TreeError, LoopError
from ..iterators import PreOrderIter

_T = t.TypeVar("_T", bound="NodeMixin")

class NodeMixin(object):
    separator = "/"
    strict_mode = True

    @property
    def parent(self) -> t.Optional[t.Self]:
        try:
            return self.__parent
        except AttributeError:
            return None

    @parent.setter
    def parent(self, value: t.Optional[t.Self]):
        if value is not None and not isinstance(value, type(self)):
            msg = f"Parent node {value !r} is not of type '{type(self)}'."
            raise TreeError(msg)
        try:
            parent = self.__parent
        except AttributeError:
            parent = None
        if parent is not value:
            self.__check_loop(value)
            self.__detach(parent)
            self.__attach(value)

    def __check_loop(self, node: t.Optional[t.Self]):
        if node is not None:
            if node is self:
                msg = "Cannot set parent. %r cannot be parent of itself."
                raise LoopError(msg % self)
            if any(child is self for child in node.iter_path_reverse()):
                msg = "Cannot set parent. %r is parent of %r."
                raise LoopError(msg % (self, node))

    def __detach(self, parent: t.Optional[t.Self]):
        if parent is not None:
            self._pre_detach(parent)
            parent_children = parent.__children_or_empty
            assert any(
                child is self for child in parent_children
            ), "Tree is corrupt."  # pragma: no cover
            # ATOMIC START
            parent.__children = [
                child for child in parent_children if child is not self
            ]
            self.__parent = None
            # ATOMIC END
            self._post_detach(parent)

    def __attach(self, parent: t.Optional[t.Self]):
        if parent is not None:
            self._pre_attach(parent)
            parent_children = parent.__children_or_empty
            if self.strict_mode:
                assert not any(
                    child is self for child in parent_children
                ), "Tree is corrupt."  # pragma: no cover
            # ATOMIC START
            parent_children.append(self)
            self.__parent = parent
            # ATOMIC END
            self._post_attach(parent)

    @property
    def __children_or_empty(self):
        try:
            return self.__children
        except AttributeError:
            self.__children = []
            return self.__children

    @property
    def children(self) -> tuple[t.Self, ...]:
        return tuple(self.__children_or_empty)

    @classmethod
    def __check_children(cls, children: t.Iterable[t.Self]):
        seen = set()
        for child in children:
            if not isinstance(child, cls):
                msg = (
                    "Cannot add non-node object %r. It is not a subclass of 'NodeMixin'."
                    % child
                )
                raise TreeError(msg)
            child_id = id(child)
            if child_id not in seen:
                seen.add(child_id)
            else:
                msg = "Cannot add node %r multiple times as child." % child
                raise TreeError(msg)

    @children.setter
    def children(self, children: t.Iterable[t.Self]):
        # convert iterable to tuple
        children = tuple(children)
        self.__check_children(children)
        # ATOMIC start
        old_children = self.children
        del self.children
        try:
            self._pre_attach_children(children)
            for child in children:
                child.parent = self
            self._post_attach_children(children)
            assert len(self.children) == len(children)
        except Exception:
            self.children = old_children
            raise
        # ATOMIC end

    @children.deleter
    def children(self):
        children = self.children
        self._pre_detach_children(children)
        for child in self.children:
            child.parent = None
        assert len(self.children) == 0
        self._post_detach_children(children)

    def _pre_detach_children(self, children):
        """Method call before detaching `children`."""
        pass

    def _post_detach_children(self, children):
        """Method call after detaching `children`."""
        pass

    def _pre_attach_children(self, children):
        """Method call before attaching `children`."""
        pass

    def _post_attach_children(self, children):
        """Method call after attaching `children`."""
        pass

    @property
    def path(self) -> tuple[t.Self, ...]:
        return self._path

    def iter_path_reverse(self) -> t.Iterable[t.Self]:
        node = self
        while node is not None:
            yield node
            node = node.parent

    @property
    def _path(self):
        return tuple(reversed(list(self.iter_path_reverse())))

    @property
    def ancestors(self) -> tuple[t.Self, ...]:
        if self.parent is None:
            return tuple()
        return self.parent.path

    @property
    def descendants(self) -> tuple[t.Self, ...]:
        return tuple(PreOrderIter(self))[1:]

    @property
    def root(self) -> t.Self:
        node = self
        while node.parent is not None:
            node = node.parent
        return node

    @property
    def siblings(self) -> tuple[t.Self, ...]:
        parent = self.parent
        if parent is None:
            return tuple()
        else:
            return tuple(node for node in parent.children if node is not self)

    @property
    def leaves(self) -> tuple[t.Self, ...]:
        return tuple(PreOrderIter(self, filter_=lambda node: node.is_leaf))

    @property
    def is_leaf(self) -> bool:
        return len(self.__children_or_empty) == 0

    @property
    def is_root(self) -> bool:
        return self.parent is None

    @property
    def height(self) -> int:
        children = self.__children_or_empty
        if children:
            return max(child.height for child in children) + 1
        else:
            return 0

    @property
    def depth(self):
        # count without storing the entire path
        i = -1
        for _ in enumerate(self.iter_path_reverse()):
            i += 1
        return i

    def _pre_detach(self, parent):
        """Method call before detaching from `parent`."""
        pass

    def _post_detach(self, parent):
        """Method call after detaching from `parent`."""
        pass

    def _pre_attach(self, parent):
        """Method call before attaching to `parent`."""
        pass

    def _post_attach(self, parent):
        """Method call after attaching to `parent`."""
        pass

    @classmethod
    def new_tree(cls, node:_T, copy_info:t.Callable[[_T], _T], strict_mode:bool = False) -> _T:
        """Copy a new tree starting at `node`."""
        new_node = copy_info(node)
        for c in node.children:
            new_c = cls.new_tree(c, copy_info)
            cls.strict_mode = strict_mode
            new_c.parent = new_node
            cls.strict_mode = True
        return new_node