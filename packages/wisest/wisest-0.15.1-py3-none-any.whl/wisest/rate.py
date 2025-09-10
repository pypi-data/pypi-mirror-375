from __future__ import annotations

from datetime import datetime
from enum import Enum
from functools import cache

import httpx
from pydantic import BaseModel
from pydantic import field_validator


# {"source":"EUR","target":"USD","value":1.05425,"time":1697653800557}
class Rate(BaseModel):
    source: str
    target: str
    value: float
    time: datetime

    @field_validator("time")
    @classmethod
    def validate_time(cls, v: int | datetime) -> datetime:
        if isinstance(v, datetime):
            return v
        elif isinstance(v, int):
            return datetime.fromtimestamp(v // 1000)
        else:
            msg = f"invalid time: {v}"
            raise TypeError(msg)


class Resolution(str, Enum):
    HOURLY = "hourly"
    DAILY = "daily"


class Unit(str, Enum):
    DAY = "day"
    MONTH = "month"
    YEAR = "year"


class RateRequest(BaseModel):
    source: str
    target: str

    def do(self) -> Rate:
        resp = httpx.get(
            url="https://wise.com/rates/live",
            params=self.model_dump(),
        )
        resp.raise_for_status()
        return Rate.model_validate(resp.json())

    async def async_do(self) -> Rate:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                url="https://wise.com/rates/live",
                params=self.model_dump(),
            )
            resp.raise_for_status()
            return Rate.model_validate(resp.json())


@cache
def query_rate(source: str, target: str) -> Rate:
    return RateRequest(source=source, target=target).do()


# https://wise.com/rates/history?source=EUR&target=USD&length=10&resolution=daily&unit=day
class RateHistoryRequest(BaseModel):
    source: str
    target: str
    length: int
    resolution: Resolution
    unit: Unit

    def do(self) -> list[Rate]:
        resp = httpx.get(
            url="https://wise.com/rates/history",
            params=self.model_dump(mode="json"),
        )
        resp.raise_for_status()
        return [Rate.model_validate(data) for data in resp.json()]

    async def async_do(self) -> list[Rate]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                url="https://wise.com/rates/history",
                params=self.model_dump(mode="json"),
            )
            resp.raise_for_status()
            return [Rate.model_validate(data) for data in resp.json()]
