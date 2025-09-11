import asyncio
from abc import ABC, abstractmethod

import httpx

from libsms.data_model import EcoliExperiment


class IClient(ABC):
    max_retries: int
    delay_s: float
    verbose: bool
    timeout: float

    def __init__(
        self,
        max_retries: int | None = None,
        delay: float | None = None,
        verbose: bool | None = None,
        timeout: float | None = None,
    ):
        self.max_retries = max_retries or 20
        self.delay_s = delay or 1.0
        self.verbose = verbose or False
        self.timeout = timeout or 30.0

    @property
    async def value(self):
        return await self._execute(**self.params())

    @abstractmethod
    def params(self):
        pass

    @abstractmethod
    def method_type(self):
        pass

    @abstractmethod
    def url(self) -> str:
        pass

    @abstractmethod
    def body(self) -> dict | None:
        pass

    def get_url(self, **params):
        url = self.url()
        if params:
            url += "?"
            for pname, pval in params.items():
                url += f"{pname}={pval}"
        return url

    async def _execute(
        self,
        **params,
    ) -> EcoliExperiment:
        method_type = self.method_type()
        max_retries = self.max_retries
        delay_s = self.delay_s
        verbose = self.verbose

        url = self.get_url(**params)
        method = client.post if method_type.lower() == "post" else client.get
        kwargs = {"url": url, "headers": {"Accept": "application/json"}, "timeout": self.timeout}
        if method_type.lower() == "post":
            kwargs["json"] = self.body()

        attempt = 0
        async with httpx.AsyncClient() as client:
            while attempt < max_retries:
                attempt += 1
                try:
                    if verbose:
                        print(f"Attempt {attempt}...")
                    response = await method(**kwargs)

                    response.raise_for_status()  # raises for 4xx/5xx

                    data = response.json()
                    if verbose:
                        print("Success on attempt", attempt)
                    return EcoliExperiment(**data)

                except (httpx.RequestError, httpx.HTTPStatusError) as err:
                    if attempt == max_retries:
                        print(f"Attempt {attempt} failed:", err)
                        raise
                    await asyncio.sleep(delay_s)
