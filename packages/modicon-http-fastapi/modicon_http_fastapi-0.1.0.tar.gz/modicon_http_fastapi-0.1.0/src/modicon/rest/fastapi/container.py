from dependency_injector import containers, providers
from fastapi import FastAPI


class FastAPIModule(containers.DeclarativeContainer):
    config = providers.Configuration()
    app = providers.Singleton(FastAPI, title=config.title, debug=config.debug)

    def add_router(self, router):
        self.app().include_router(router)

    # bootstrap (add on_startup/on_shutdown)
    def get_app(self):
        return self.app()