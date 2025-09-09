from typing import Type, Union

from fastapi import HTTPException, Request
from fastapi.security.base import SecurityBase

from .user import BaseUser


class AuthenticationBackend(SecurityBase):
    def authenticate(self, request: Request) -> Union[Type[BaseUser], None]:
        """Authenticate."""
        return None

    def __call__(self, request: Request) -> None:
        """Callable method."""
        # As this method is supposed to be "Provider Agnostic",
        # it only calls the authenticate method, which returns either an user or None.
        # It then modifies the request to add to it the user value
        route = request.scope.get("route")
        if (
            route
            and hasattr(route.endpoint, "is_public_route")
            and route.endpoint.is_public_route
        ):
            # For public routes, set user to None but don't raise 401
            request.state.user = None
            return
                
        try:
            request.state.user = self.authenticate(request=request)
        except Exception as e:
            print(
                "Erreur happened during authentication"
            )  # TODO: Convert to logger once implemented
            print(e)
            raise HTTPException(status_code=500)

        if request.state.user is None:
            raise HTTPException(status_code=401)


class AsyncAuthenticationBackend(SecurityBase):
    async def authenticate(self, request: Request) -> Union[Type[BaseUser], None]:
        """Authenticate."""
        return None

    async def __call__(self, request: Request) -> None:
        """Callable method."""
        # As this method is supposed to be "Provider Agnostic",
        # it only calls the authenticate method, which returns either an user or None.
        # It then modifies the request to add to it the user value
        
        route = request.scope.get("route")
        if (
            route
            and hasattr(route.endpoint, "is_public_route")
            and route.endpoint.is_public_route
        ):
            # For public routes, set user to None but don't raise 401
            request.state.user = None
            return
                
        try:
            request.state.user = await self.authenticate(request=request)
        except Exception as e:
            print(
                "Erreur happened during authentication"
            )  # TODO: Convert to logger once implemented
            print(e)
            raise HTTPException(status_code=500)

        if request.state.user is None:
            raise HTTPException(status_code=401)
