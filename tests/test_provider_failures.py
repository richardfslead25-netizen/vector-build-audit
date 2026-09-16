from vector.contracts.enums import DataStatus
from vector.contracts.provenance import Provenance

def test_failed_provider_is_explicit_not_substituted():
    prov = Provenance(provider="webull-proposed", dataset="option-chain", instrument="SPY",
                      data_status=DataStatus.UNKNOWN, entitlement="not-connected", notes="rate-limit-or-auth-failure")
    assert prov.entitlement == "not-connected"

def test_synthetic_fixtures_are_labeled():
    prov = Provenance(provider="synthetic-fixture", dataset="stage1-offline", instrument="SPY",
                      data_status=DataStatus.SYNTHETIC, synthetic=True)
    assert prov.synthetic is True
