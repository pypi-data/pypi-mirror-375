"""
Tachyon Web Framework - Parameter Definition Module

This module provides parameter marker classes for defining how endpoint function
parameters should be resolved from HTTP requests (query strings, path variables,
and request bodies).
"""

from typing import Any, Optional


class Query:
    """
    Marker class for query string parameters.

    Use this to define parameters that should be extracted from the URL query string
    with optional default values and automatic type conversion.

    Args:
        default: Default value if parameter is not provided. Use ... for required parameters.
        description: Optional description for OpenAPI documentation.

    Example:
        @app.get("/search")
        def search(
            q: str = Query(...),        # Required query parameter
            limit: int = Query(10),     # Optional with default value
            active: bool = Query(False) # Optional boolean parameter
        ):
            return {"query": q, "limit": limit, "active": active}

    Note:
        - Boolean parameters accept: "true", "1", "t", "yes" (case-insensitive) as True
        - Type conversion is automatic based on parameter annotation
        - Missing required parameters return 422 Unprocessable Entity
        - Invalid type conversions return 422 Unprocessable Entity
    """

    def __init__(self, default: Any = ..., description: Optional[str] = None):
        """
        Initialize a Query parameter marker.

        Args:
            default: Default value for the parameter. Use ... (Ellipsis) for required parameters.
            description: Optional description for API documentation.
        """
        self.default = default
        self.description = description


class Path:
    """
    Marker class for path parameters.

    Use this to define parameters that should be extracted from the URL path.
    Path parameters are always required.

    Args:
        description: Optional description for OpenAPI documentation.
    """

    def __init__(self, description: Optional[str] = None):
        """
        Initialize a Path parameter marker.

        Args:
            description: Optional description for API documentation.
        """
        self.description = description


class Body:
    """
    Marker class for request body parameters.

    Use this to define parameters that should be extracted and validated from
    the JSON request body. The parameter type should be a Struct subclass.

    Args:
        description: Optional description for OpenAPI documentation.
    """

    def __init__(self, description: Optional[str] = None):
        """
        Initialize a Body parameter marker.

        Args:
            description: Optional description for API documentation.
        """
        self.description = description
