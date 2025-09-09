from typing import List, Type

from dependency_injector import providers
from fastapi import FastAPI, Security

from tasteful.base_flavor import BaseFlavor
from tasteful.config import TastefulConfig
from tasteful.containers.tasteful_container import TastefulContainer


class TastefulApp:
    def __init__(
        self,
        name: str = None,
        version: str = None,
        log_level: str = None,
        flavors: List[Type[BaseFlavor]] = [],
        authentication_backends: list[Security] = [],
    ):
        self.container = TastefulContainer()

        self.flavors = flavors
        self._register_flavors()

        self.container.config.from_pydantic(TastefulConfig())

        self.app = FastAPI(
            title=name or self.container.config.project.name() or "Tasteful Application",
            version=version or self.container.config.project.version() or "0.1.0",
            log_level=log_level or self.container.config.project.log_level() or "INFO",
            dependencies=authentication_backends,
        )

        self._inject_flavors()

    def _register_flavors(self) -> None:
        """Register all flavors with the app."""
        for flavor_class in self.flavors:
            setattr(
                self.container, flavor_class.__name__, providers.Singleton(flavor_class)
            )

    def _inject_flavors(self) -> None:
        """Inject flavors routes into the FastAPI application."""
        for flavor in self.flavors:
            instance = getattr(self.container, flavor.__name__)()
            self.app.include_router(instance.controller.router)
