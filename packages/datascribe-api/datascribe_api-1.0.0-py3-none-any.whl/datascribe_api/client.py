"""DataScribe API Client.

This module provides a client for interacting with the DataScribe API, allowing users to search for data tables and their metadata.
"""

import json
import os
from typing import Any

import requests
from requests import HTTPError

from datascribe_api.filter import Filter
from datascribe_api.routes import ROUTES


class DataScribeClient:
    """This client provides methods to interact with the DataScribe API, allowing users to search for data tables and their metadata.

    Attriesbutes:
        api_key (str): The API key for authentication.
        base (str): The base URL for the DataScribe API.
        session (Session): The session used for making HTTP requests with retry logic.
    """

    def __init__(self, api_key: str | None = None, base: str = "https://datascribe.cloud/data/") -> None:
        """Initialize the DataScribe API client.

        Args:
            api_key (str | None): The API key for authentication. If not provided, it will be read from the environment variable `DATASCRIBE_API_TOKEN`.
            base (str): The base URL for the DataScribe API. Defaults to "https://datascribe.cloud/data".

        Raises:
            ValueError: If the API key is not provided and not found in the environment variables.
        """
        self._api_key = api_key or os.getenv("DATASCRIBE_API_TOKEN")
        if not self._api_key:
            raise ValueError(
                "A DataScribe API key is required. Check https://datascribe.cloud/profile to generate an API key.",
            )
        self._base = base.rstrip("/")
        self._session = requests.session()
        self._session.headers.update(
            {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._api_key}",
            },
        )

    def __enter__(self) -> "DataScribeClient":
        """Context manager entry method for the DataScribeClient."""
        return self

    def __exit__(self, *args) -> None:
        """Context manager exit method for the DataScribeClient. Closes the session."""
        self.close()

    def _get(self, path: str, params: dict[str, Any]) -> Any:
        """Make a GET request to the DataScribe API.

        Args:
            path (str): The API endpoint path to which the request is made.
            params (Dict[str, Any]): The query parameters for the request.

        Returns:
            dict: The JSON response from the API.

        Raises:
            HTTPError: If the request fails with a status code indicating an error.
        """
        url = f"{self._base}{path}"
        filters = params.get("filters")
        if filters is not None:
            try:
                serialized = Filter.serialize(filters)
            except Exception as e:
                raise TypeError(f"Invalid filters: {e}") from e
            params["filters"] = json.dumps(serialized)
        try:
            resp = self._session.get(url=url, params=params, timeout=30)
            resp.raise_for_status()
        except HTTPError as e:
            error_json = e.response.json()
            message = error_json.get("message") or error_json.get("data") or str(e)
            raise HTTPError(f"HTTP Error {e.response.status_code} - {message}") from e
        return resp.json()

    def search(self, endpoint: str, **kwargs: Any) -> Any:
        """Search for data tables or metadata in the DataScribe API.

        Args:
            endpoint (str): The endpoint to search, e.g., "get_data_tables", "get_data_table", etc.
            **kwargs: Additional parameters to pass to the API. For endpoints supporting filtering, pass 'filters' as a dict, Filter, or list of Filters.

        Example:
                    filters = Filter("age") > 30
                    filters = [Filter("age") > 30, Filter("name") == "Alice"]
                    filters = {"column": "age", "operator": ">", "value": 30}
                    client.get_data_table_rows(tableName="users", columns=["id", "name", "age"], filters=filters)

        Returns:
            Any: A list of data models corresponding to the search results.

        Raises:
            ValueError: If required parameters are missing.
        """
        path, model, required_params = ROUTES[endpoint]
        missing = [p for p in required_params if p not in kwargs]
        if missing:
            raise ValueError(f"Missing required parameters for '{endpoint}': {', '.join(missing)}")
        resp = self._get(path, {**kwargs})
        if resp.get("success") is False:
            raise ValueError(f"API request failed: {resp.get('message', 'Unknown error')}")
        resp = resp.get("data", resp)
        docs = model(resp) if isinstance(resp, list) else model(**resp)
        return docs

    def close(self) -> None:
        """Close the session used by the DataScribeClient."""
        self._session.close()

    def __getattr__(self, name: str) -> Any:
        """Dynamic attribute access for searching data tables or metadata.

        This method allows access to search methods based on the endpoint names defined in ROUTES.

        Args:
            name (str): The name of the endpoint to search, e.g., "data-table", "data-tables", etc.

        Returns:
            Callable: A function that performs the search for the specified endpoint.
        """
        if name in ROUTES:
            return lambda **kwargs: self.search(name, **kwargs)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def __dir__(self) -> list[str]:
        """List all available attributes and methods of the DataScribeClient, including the API endpoints.

        Returns:
            list[str]: A list of attribute names, including API endpoints defined in ROUTES.
        """
        return list(ROUTES.keys()) + super().__dir__()
