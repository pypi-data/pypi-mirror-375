"""Filter builder for DataScribe API.

This module provides the Filter class, which enables Pythonic and expressive construction of filter objects
for use with the DataScribe API. It supports operator overloading and named methods for all common SQL-like
filter operations, including equality, comparison, IN, LIKE, IS NULL, and more.
"""

from typing import Any, Union


class Filter:
    """A Filter builder for DataScribe API.

    Supports operator overloading and named methods for intuitive filter creation.

    Example usage:
        Filter("age") > 30
        Filter("name") == "Alice"
        Filter("status").in_(["active", "pending"])
        Filter("name").like("%John%")
        Filter("deleted_at").is_null()
    """

    __hash__ = None

    def __init__(self, column: str) -> None:
        """Initialize a filter for a specific column.

        Args:
            column (str): The column name to filter on.
        """
        self.column: str = column
        self.operator: str | None = None
        self.value: Any = None

    def _build(self, operator: str, value: Any) -> "Filter":
        """Internal helper to set the operator and value for the filter.

        Args:
            operator (str): The filter operator (e.g., '=', 'in', 'like').
            value (Any): The value for the filter.

        Returns:
            Filter: The filter instance (self).
        """
        self.operator = operator
        self.value = value
        return self

    def __eq__(self, other: Any) -> "Filter":
        """Equals operator (==)."""
        return self._build("=", other)

    def __ne__(self, other: Any) -> "Filter":
        """Not equals operator (!=)."""
        return self._build("!=", other)

    def __gt__(self, other: Any) -> "Filter":
        """Greater than operator (>)."""
        return self._build(">", other)

    def __ge__(self, other: Any) -> "Filter":
        """Greater than or equal operator (>=)."""
        return self._build(">=", other)

    def __lt__(self, other: Any) -> "Filter":
        """Less than operator (<)."""
        return self._build("<", other)

    def __le__(self, other: Any) -> "Filter":
        """Less than or equal operator (<=)."""
        return self._build("<=", other)

    def in_(self, values: list[Any]) -> "Filter":
        """IN operator.

        Args:
            values (list[Any]): List of values for the IN operator.

        Returns:
            Filter: The filter instance.
        """
        return self._build("in", values)

    def not_in(self, values: list[Any]) -> "Filter":
        """NOT IN operator.

        Args:
            values (list[Any]): List of values for the NOT IN operator.

        Returns:
            Filter: The filter instance.
        """
        return self._build("not in", values)

    def like(self, value: str) -> "Filter":
        """LIKE operator.

        Args:
            value (str): The pattern for LIKE.

        Returns:
            Filter: The filter instance.
        """
        return self._build("like", value)

    def ilike(self, value: str) -> "Filter":
        """ILIKE operator (case-insensitive LIKE).

        Args:
            value (str): The pattern for ILIKE.

        Returns:
            Filter: The filter instance.
        """
        return self._build("ilike", value)

    def is_null(self) -> "Filter":
        """IS NULL operator.

        Returns:
            Filter: The filter instance.
        """
        return self._build("is null", None)

    def is_not_null(self) -> "Filter":
        """IS NOT NULL operator.

        Returns:
            Filter: The filter instance.
        """
        return self._build("is not null", None)

    def to_dict(self) -> dict[str, Any]:
        """Convert the filter to a dictionary suitable for the API.

        Returns:
            dict: The filter as a dictionary.
        """
        return {"column": self.column, "operator": self.operator, "value": self.value}

    @staticmethod
    def serialize(filters: Union[dict[str, Any], "Filter", list["Filter"], None]) -> Any:
        """Serialize filters to a format suitable for the API.

        Args:
            filters (dict, Filter, list[Filter], or None): The filters to serialize.

        Returns:
            Any: The serialized filters.

        Raises:
            TypeError: If the input is not a supported type.
        """
        if filters is None:
            return None
        if isinstance(filters, dict):
            return filters
        if isinstance(filters, Filter):
            return filters.to_dict()
        if isinstance(filters, list):
            return [f.to_dict() if isinstance(f, Filter) else f for f in filters]
        raise TypeError("filters must be a dict, Filter, list of Filters, or None")
