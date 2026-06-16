from framework.comparators import ProtocolComparator, PayloadComparator


def test_protocol_comparator_passes():
    comparator = ProtocolComparator("1.0")
    result = comparator.compare_version("1.0")

    assert result.passed is True


def test_protocol_comparator_fails():
    comparator = ProtocolComparator("1.0")
    result = comparator.compare_version("2.0")

    assert result.passed is False


def test_payload_comparator_passes():
    comparator = PayloadComparator()
    result = comparator.require_keys({"message": "hello"}, {"message"})

    assert result.passed is True


def test_payload_comparator_fails():
    comparator = PayloadComparator()
    result = comparator.require_keys({}, {"message"})

    assert result.passed is False
