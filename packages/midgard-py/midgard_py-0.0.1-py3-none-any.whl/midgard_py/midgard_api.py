import requests
from midgard_py.models.midgard_models_health import MidgardHealthResponse
from midgard_py.models.midgard_models_pool import MidgardPool


class MidgardAPI:
    def __init__(self, base_url: str = "https://midgard.ninerealms.com", timeout: int = 15):
        self.base_url = base_url
        self.timeout = timeout



    # Health
    #-------------------------------------------------------------------------------------------------------------------
    def health(self) -> MidgardHealthResponse:
        url = f"{self.base_url}/v2/health"
        response = requests.get(url, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return MidgardHealthResponse.model_validate(data)
    #-------------------------------------------------------------------------------------------------------------------



    # Pools
    #-------------------------------------------------------------------------------------------------------------------
    def pools(self) -> list[MidgardPool]:
        url = f"{self.base_url}/v2/pools"
        response = requests.get(url, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return [MidgardPool.model_validate(item) for item in data]
    #-------------------------------------------------------------------------------------------------------------------
