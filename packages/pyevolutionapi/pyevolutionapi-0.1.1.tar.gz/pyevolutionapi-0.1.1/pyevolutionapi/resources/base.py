"""
Base resource class for API resources.
"""

from typing import TYPE_CHECKING, Any, Dict, Optional, Type, TypeVar, Union

from pydantic import BaseModel

if TYPE_CHECKING:
    from ..client import EvolutionClient

T = TypeVar("T", bound=BaseModel)


class BaseResource:
    """Base class for all API resources."""

    def __init__(self, client: "EvolutionClient"):
        """
        Initialize resource with client.

        Args:
            client: The Evolution API client instance
        """
        self.client = client

    def _handle_response(self, response) -> Any:
        """
        Handle response, whether it's a Response object, dict, or list.

        Args:
            response: Response object, dict, or list

        Returns:
            Response data (dict, list, or other type)
        """
        if hasattr(response, "json"):
            return response.json()
        elif isinstance(response, (dict, list)):
            return response
        else:
            raise ValueError(f"Unexpected response type: {type(response)}")

    def _get(
        self,
        endpoint: str,
        instance: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Union[Dict[str, Any], list]:
        """Make a GET request."""
        response = self.client.request("GET", endpoint, instance=instance, params=params, **kwargs)
        return self._handle_response(response)

    def _post(
        self,
        endpoint: str,
        instance: Optional[str] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Union[Dict[str, Any], list]:
        """Make a POST request."""
        response = self.client.request(
            "POST", endpoint, instance=instance, json=json, data=data, files=files, **kwargs
        )
        return self._handle_response(response)

    def _put(
        self,
        endpoint: str,
        instance: Optional[str] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Union[Dict[str, Any], list]:
        """Make a PUT request."""
        response = self.client.request("PUT", endpoint, instance=instance, json=json, **kwargs)
        return self._handle_response(response)

    def _delete(
        self,
        endpoint: str,
        instance: Optional[str] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Union[Dict[str, Any], list]:
        """Make a DELETE request."""
        response = self.client.request("DELETE", endpoint, instance=instance, json=json, **kwargs)

        # Handle empty responses for DELETE
        if hasattr(response, "text") and not response.text:
            return {"status": "success"}
        elif isinstance(response, dict) and not response:
            return {"status": "success"}

        return self._handle_response(response)

    def _parse_response(self, response_data: Dict[str, Any], model: Type[T]) -> T:
        """
        Parse response data into a Pydantic model.

        Args:
            response_data: The response data dictionary
            model: The Pydantic model class to parse into

        Returns:
            Instance of the model
        """
        return model.model_validate(response_data)

    async def _aget(
        self,
        endpoint: str,
        instance: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Union[Dict[str, Any], list]:
        """Make an async GET request."""
        response = await self.client.arequest(
            "GET", endpoint, instance=instance, params=params, **kwargs
        )
        return self._handle_response(response)

    async def _apost(
        self,
        endpoint: str,
        instance: Optional[str] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Union[Dict[str, Any], list]:
        """Make an async POST request."""
        response = await self.client.arequest(
            "POST", endpoint, instance=instance, json=json, data=data, files=files, **kwargs
        )
        return self._handle_response(response)

    async def _aput(
        self,
        endpoint: str,
        instance: Optional[str] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Union[Dict[str, Any], list]:
        """Make an async PUT request."""
        response = await self.client.arequest(
            "PUT", endpoint, instance=instance, json=json, **kwargs
        )
        return self._handle_response(response)

    async def _adelete(
        self,
        endpoint: str,
        instance: Optional[str] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Union[Dict[str, Any], list]:
        """Make an async DELETE request."""
        response = await self.client.arequest(
            "DELETE", endpoint, instance=instance, json=json, **kwargs
        )

        # Handle empty responses for DELETE
        if hasattr(response, "text") and not response.text:
            return {"status": "success"}
        elif isinstance(response, dict) and not response:
            return {"status": "success"}

        return self._handle_response(response)
