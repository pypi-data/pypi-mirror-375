# coding=utf-8
# Copyright (c) 2025 Jifeng Wu
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
import sys
from typing import Iterable, Iterator, List, TypeVar

DEFAULT_PLACEHOLDER = object()
T = TypeVar('T')


class PutBackIterator(Iterator[T]):
    """A drop-in replacement for built-in iterators that supports putting items back.

    This iterator wraps any iterable and provides additional functionality to
    push consumed items back into the iterator for later consumption. Ideal for
    parsing, lexing, and other scenarios requiring lookahead or backtracking.

    Args:
        iterable: Any iterable object (list, string, generator, etc.) to wrap.

    Example:
        >>> it = PutBackIterator([1, 2, 3])
        >>> next(it)
        1
        >>> it.put_back(1)
        >>> list(it)
        [1, 2, 3]

    Attributes:
        iterator (Iterator[T]): The underlying iterator
        put_back_stack (List[T]): Stack for items that have been put back
    """
    __slots__ = (
        'iterator',
        'put_back_stack'
    )

    def __init__(self, iterable):
        # type: (Iterable[T]) -> None
        """Initialize the PutBackIterator with an iterable.

        Args:
            iterable: Any object that can be iterated over
        """
        self.iterator = iter(iterable)  # type: Iterator[T]
        self.put_back_stack = []  # type: List[T]

    def __iter__(self):
        # type: () -> PutBackIterator[T]
        """
        Return the iterator object itself.

        Returns:
            PutBackIterator[T]: The current iterator instance.

        This makes PutBackIterator compatible with the iterator protocol,
        so it can be used directly in for-loops and other iterable contexts.
        """
        return self

    def next_implementation(self, default=DEFAULT_PLACEHOLDER):
        """
        Return the next item from the iterator, considering any put-back items.

        Args:
            default: Optional; a value to return if the iterator is exhausted.
                     If not provided and no items remain, raises StopIteration.

        Returns:
            T: The next item from the put-back stack (if not empty), or the underlying iterator.

        Raises:
            StopIteration: If there are no more items and no default is provided.

        Notes:
            This method underlies both the Python 2 and 3 iterator protocol methods.
        """
        if self.put_back_stack:
            return self.put_back_stack.pop()
        else:
            end_sentinel = object()
            element_or_sentinel = next(self.iterator, end_sentinel)
            if element_or_sentinel is end_sentinel:
                if default is DEFAULT_PLACEHOLDER:
                    raise StopIteration
                else:
                    return default
            else:
                return element_or_sentinel

    if sys.version_info < (3,):
        next = next_implementation
    else:
        __next__ = next_implementation

    def put_back(self, element):
        # type: (T) -> None
        """
        Put an item back into the iterator to be returned on the next call to `next()`.

        Args:
            element (T): The item to put back onto the iterator.

        Notes:
            Items are put back in a last-in, first-out (LIFO) order. Calling `put_back()` multiple times will return those items in reverse order of addition.
        """
        self.put_back_stack.append(element)

    def has_next(self):
        # type: () -> bool
        """
        Check whether the iterator has at least one more item to yield, without consuming it.

        Returns:
            bool: True if there is another item available, False otherwise.

        Notes:
            If there is no item in the put-back stack, this method advances
            the underlying iterator once for lookahead, puts the value back if found, and then returns the result.
        """
        if self.put_back_stack:
            return True
        else:
            end_sentinel = object()
            element_or_sentinel = next(self, end_sentinel)
            if element_or_sentinel is end_sentinel:
                return False
            else:
                self.put_back_stack.append(element_or_sentinel)
                return True
