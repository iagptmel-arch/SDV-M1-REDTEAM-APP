"""
Tests unitaires des services métier
"""


def test_calculate_severity():
    from app.services.vulnerability import calculate_severity

    assert calculate_severity(9.5) == "critical"
    assert calculate_severity(7.5) == "high"
    assert calculate_severity(5.0) == "medium"
    assert calculate_severity(2.0) == "low"
    assert calculate_severity(0.0) == "info"
