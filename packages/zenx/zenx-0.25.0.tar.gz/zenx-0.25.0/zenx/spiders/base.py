from __future__ import annotations 
import asyncio
from abc import ABC, abstractmethod
from typing import Any, ClassVar, Coroutine, Dict, List, Literal, Optional, Type
from structlog import BoundLogger
import html_text

from zenx.clients.http import HttpClient, Response
from zenx.monitors.base import Monitor
from zenx.pipelines.manager import PipelineManager
from zenx.settings import Settings



class Spider(ABC):
    # central registry
    name: ClassVar[str]
    _registry: ClassVar[Dict[str, Type[Spider]]] = {}
    pipelines: ClassVar[List[str]]
    monitor_name: ClassVar[Literal["itxp"]] = "itxp"
    client_name: ClassVar[Literal["curl_cffi"]] = "curl_cffi"
    custom_settings: ClassVar[Dict[str, Any]] = {}


    def __init_subclass__(cls, **kwargs) -> None:
        # for multiple inheritence to work
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "name"):
            raise TypeError(f"Spider subclass {cls.__name__} must have a 'name' attribute.")

        # add spider to registry
        cls._registry[cls.name] = cls


    @classmethod
    def get_spider(cls, name: str) -> Type[Spider]:
        if name not in cls._registry:
            raise ValueError(f"Spider '{name}' is not registered. Available spiders: {list(cls._registry.keys())}")
        return cls._registry[name]


    @classmethod
    def spider_list(cls) -> List[str]:
        return list(cls._registry.keys())


    def __init__(self, client: HttpClient, pm: PipelineManager, logger: BoundLogger, settings: Settings, monitor: Monitor | None = None) -> None:
        self.client = client
        self.pm = pm
        self.logger = logger
        self.settings = settings
        self.monitor = monitor
        self.background_tasks = set()

    
    def create_task(self, coro: Coroutine, name: Optional[str] = None) -> None:
        t = asyncio.create_task(coro, name=name)
        self.background_tasks.add(t)
        t.add_done_callback(self.background_tasks.discard)


    def extract_text(self, html: str, **kwargs) -> str:
        return html_text.extract_text(html, **kwargs)
    

    async def request(self,
        url: str,
        method: str = "GET",
        headers: Dict | None = None,
        proxy: str | None = None,
        use_session_pool: bool = False,
        dont_filter: bool = False,
        **kwargs,
    ) -> Response:
        response = await self.client.request(
            url=url,
            method=method,
            headers=headers,
            proxy=proxy,
            use_session_pool=use_session_pool,
            dont_filter=dont_filter,
            **kwargs,
        )
        if response and self.monitor and response.status == self.monitor.trigger_status_code:
            await self.monitor.process_stats({"type": "heartbeat"}, self.name)
        return response


    @abstractmethod
    async def crawl(self) -> None:
        """ Short-lived scrape """
        ...


    @abstractmethod
    async def process_response(self, response: Response) -> None:
        ...

