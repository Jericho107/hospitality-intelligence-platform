from hospitality_intelligence.reconciliation import canonical_hash


def test_canonical_hash_is_stable_for_same_rows() -> None:
    rows = [
        ("2026-09-01", "P001", "10.00"),
        ("2026-09-02", "P001", "12.00"),
    ]

    assert canonical_hash(rows) == canonical_hash(list(rows))


def test_canonical_hash_changes_when_one_value_changes() -> None:
    source = [
        ("2026-09-01", "P001", "10.00"),
        ("2026-09-02", "P001", "12.00"),
    ]
    mutated = [
        ("2026-09-01", "P001", "10.00"),
        ("2026-09-02", "P001", "12.01"),
    ]

    assert canonical_hash(source) != canonical_hash(mutated)
