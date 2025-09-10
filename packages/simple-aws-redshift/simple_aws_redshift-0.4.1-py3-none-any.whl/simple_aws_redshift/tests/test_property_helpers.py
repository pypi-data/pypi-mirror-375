# -*- coding: utf-8 -*-

import inspect
import typing as T
from functools import cached_property

from ..model import BaseModel


def verify_all_properties(
    klass: T.Type[BaseModel],
    instance: BaseModel,
):
    """
    Test all property and cached_property methods of a class by accessing them.

    This utility function automatically discovers all properties and cached properties
    defined on a class and accesses them on the provided instance to ensure
    they don't raise exceptions during basic access (happy path testing).

    :param cls: The class to inspect for properties
    :param instance: An instance of the class to test properties on
    """
    # Get all members of the class
    for name, member in inspect.getmembers(klass):
        # Skip private/protected attributes
        if name.startswith("_"):
            continue

        # Check if it's a property or cached_property
        if isinstance(member, property) or isinstance(member, cached_property):
            try:
                # Access the property to test it
                value = getattr(instance, name)
                print(f"{klass.__name__}.{name} = {value}")  # Print the property name and value
            except Exception as e:
                # Re-raise with more context about which property failed
                raise RuntimeError(
                    f"Property '{name}' failed during access: {e}"
                ) from e
