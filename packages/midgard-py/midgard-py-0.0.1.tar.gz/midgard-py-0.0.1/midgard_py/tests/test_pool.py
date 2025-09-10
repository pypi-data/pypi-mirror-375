import pytest
from midgard_py import MidgardAPI
from midgard_py.models.midgard_models_pool import MidgardPool


@pytest.mark.integration
def test_pools():
    api = MidgardAPI()

    pools = api.pools()
    print(f"test_pools(): Has {len(pools)} pools")
    assert len(pools) > 0

    first = pools[0]
    last = pools[-1]
    print(f"test_pools(): First pool {first}")
    print(f"test_pools(): Last pool {last}")
    assert isinstance(first, MidgardPool)
    assert isinstance(last, MidgardPool)
