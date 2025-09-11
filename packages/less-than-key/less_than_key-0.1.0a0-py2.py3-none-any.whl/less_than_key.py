# coding=utf-8
# Copyright (c) 2025 Jifeng Wu
# Licensed under the <license> License. See LICENSE file in the project root for full license information.
from abc import ABCMeta

from rawattr import raw_getattr
from six import with_metaclass


class LessThanKeyMeta(ABCMeta):
    """
    Metaclass for LessThanKey.

    This enables the syntax `LessThanKey[my_less_than_func]` to generate (and cache)
    specialized subclasses of LessThanKey that compare using the given less-than function.

    Attributes:
        LESS_THAN (callable): Placeholder for the less-than function.
        type_and_less_than_to_subtype_instantiation (dict): Cache for dynamically generated classes.

    Example:
        MyKey = LessThanKey[lambda a, b: a > b]
        obj = MyKey(3)
    """
    LESS_THAN = None
    type_and_less_than_to_subtype_instantiation = {}

    def __getitem__(self, less_than):
        """
        Return (and cache) a dynamically created subclass with a specific LESS_THAN function.

        Args:
            less_than (callable): A function of two arguments that implements "less than" between values.

        Returns:
            type: A subclass of LessThanKey with the LESS_THAN attribute set to less_than.
        """
        if (self, less_than) in self.type_and_less_than_to_subtype_instantiation:
            return self.type_and_less_than_to_subtype_instantiation[(self, less_than)]
        else:
            # Instantiate a subtype
            instantiation = type(
                '%s[%s]' % (self.__name__, less_than),
                (self,),
                dict(
                    __module__=self.__module__,
                    LESS_THAN=less_than
                )
            )

            self.type_and_less_than_to_subtype_instantiation[(self, less_than)] = instantiation

            return instantiation


class LessThanKey(with_metaclass(LessThanKeyMeta, object)):
    """
    Key wrapper class with customizable less-than logic for sorting and comparison.

    This class, when specialized by supplying a less-than function via
    `LessThanKey[less_than_function]`, produces instances that compare their `.value`
    attributes using the provided logic. This is useful for custom sorting,
    especially with the `key` parameter in Python's `sorted()` or other sorting APIs.

    Attributes:
        value: The wrapped value.
        LESS_THAN (callable): Class-level less-than function.

    Example:
        # Reverse order by absolute value
        rev_abs_key = LessThanKey[lambda a, b: abs(a) > abs(b)]
        keys = [rev_abs_key(-5), rev_abs_key(2)]
        assert sorted(keys) == [rev_abs_key(-5), rev_abs_key(2)]
    """
    __slots__ = ('value',)

    def __new__(cls, value):
        """
        Create a new LessThanKey instance wrapping value.

        Args:
            value: Any value to be compared using the class's less-than function.
        """
        self = super(LessThanKey, cls).__new__(cls)
        self.value = value
        return self

    def __repr__(self):
        """
        Return a string representation of the LessThanKey instance.

        Returns:
            str: e.g. "LessThanKey[<function>](value)"
        """
        return '%s(%r)' % (type(self).__name__, self.value)

    @classmethod
    def __subclasshook__(cls, subclass):
        """
        Allow issubclass checks for dynamically specialized LessThanKey classes.

        Returns:
            bool: True if subclass is compatible, otherwise NotImplemented.
        """
        # Forced no method resolution
        cls_less_than = raw_getattr(cls, 'LESS_THAN')

        if cls in subclass.__mro__ and (
                cls_less_than is None  # Any instantiated class is a subclass of a non-instantiated class
                or raw_getattr(subclass, 'LESS_THAN') is cls_less_than
        ):
            return True
        else:
            return NotImplemented

    def __lt__(self, other):
        """
        Compare self < other using the class's LESS_THAN function.

        Args:
            other (LessThanKey): Another instance of the same LessThanKey subclass.

        Returns:
            bool: True if self < other, else False.
        """
        cls = type(self)
        if isinstance(other, cls):
            lt = raw_getattr(cls, 'LESS_THAN')
            self_value = self.value
            other_value = other.value

            return lt(self_value, other_value)
        else:
            return NotImplemented

    def __gt__(self, other):
        """
        Compare self > other using the class's LESS_THAN function.

        Args:
            other (LessThanKey): Another instance of the same LessThanKey subclass.

        Returns:
            bool: True if self > other, else False.
        """
        cls = type(self)
        if isinstance(other, cls):
            lt = raw_getattr(cls, 'LESS_THAN')
            self_value = self.value
            other_value = other.value

            return lt(other_value, self_value)
        else:
            return NotImplemented

    def __ge__(self, other):
        """
        Compare self >= other using the class's LESS_THAN function.

        Args:
            other (LessThanKey): Another instance of the same LessThanKey subclass.

        Returns:
            bool: True if self >= other, else False.
        """
        cls = type(self)
        if isinstance(other, cls):
            lt = raw_getattr(cls, 'LESS_THAN')
            self_value = self.value
            other_value = other.value

            return not lt(self_value, other_value)
        else:
            return NotImplemented

    def __le__(self, other):
        """
        Compare self <= other using the class's LESS_THAN function.

        Args:
            other (LessThanKey): Another instance of the same LessThanKey subclass.

        Returns:
            bool: True if self <= other, else False.
        """
        cls = type(self)
        if isinstance(other, cls):
            lt = raw_getattr(cls, 'LESS_THAN')
            self_value = self.value
            other_value = other.value

            return not lt(other_value, self_value)
        else:
            return NotImplemented

    def __ne__(self, other):
        """
        Compare self != other using the class's LESS_THAN function.

        Args:
            other (LessThanKey): Another instance of the same LessThanKey subclass.

        Returns:
            bool: True if values are not equal per LESS_THAN, else False.
        """
        cls = type(self)
        if isinstance(other, cls):
            lt = raw_getattr(cls, 'LESS_THAN')
            self_value = self.value
            other_value = other.value

            return lt(self_value, other_value) or lt(other_value, self_value)
        else:
            return NotImplemented

    def __eq__(self, other):
        """
        Compare self == other using the class's LESS_THAN function.

        Args:
            other (LessThanKey): Another instance of the same LessThanKey subclass.

        Returns:
            bool: True if values are equal per LESS_THAN, else False.
        """
        cls = type(self)
        if isinstance(other, cls):
            lt = raw_getattr(cls, 'LESS_THAN')
            self_value = self.value
            other_value = other.value

            return (not lt(self_value, other_value)) and (not lt(other_value, self_value))
        else:
            return NotImplemented


def less_than_to_key(less_than):
    """
    Create a key function for sorting, based on a less-than function.

    Args:
        less_than (callable): A two-argument function implementing a 'less than' logic.

    Returns:
        function: A function f(value) that returns a specialized LessThanKey instance
                  wrapping value for use as a key in sorting or data structures.

    Example:
        sorted(items, key=less_than_to_key(lambda a, b: abs(a) > abs(b)))
    """
    InstantiatedLessThanKey = LessThanKey[less_than]

    def key(value):
        return InstantiatedLessThanKey(value)

    return key
