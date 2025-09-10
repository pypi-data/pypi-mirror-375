from pydantic import BaseModel


class MidgardHealthGenesis(BaseModel):
    hash: str
    height: int


class MidgardHealthTimestamp(BaseModel):
    height: int
    timestamp: int


class MidgardHealthResponse(BaseModel):
    database: bool
    genesisInfo: MidgardHealthGenesis
    inSync: bool
    lastAggregated: MidgardHealthTimestamp
    lastCommitted: MidgardHealthTimestamp
    lastFetched: MidgardHealthTimestamp
    lastThorNode: MidgardHealthTimestamp
    scannerHeight: str
