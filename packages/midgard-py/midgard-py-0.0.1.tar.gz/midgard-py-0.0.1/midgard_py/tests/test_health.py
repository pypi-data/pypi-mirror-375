import pytest
from midgard_py import MidgardAPI
from midgard_py.models.midgard_models_health import MidgardHealthResponse


@pytest.mark.integration
def test_health():
    api = MidgardAPI()

    health = api.health()
    print(f"test_health(): Health {health}")
    assert isinstance(health, MidgardHealthResponse)
