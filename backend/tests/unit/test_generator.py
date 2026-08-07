from app.detection.generator import SCENARIOS, generate_synthetic_data


def test_generator_is_reproducible_and_covers_all_scenarios() -> None:
    first = generate_synthetic_data(8, 120, seed=42)
    second = generate_synthetic_data(8, 120, seed=42)
    assert first.accounts == second.accounts
    assert first.transactions == second.transactions
    assert {
        row["synthetic_scenario"] for row in first.transactions if row["synthetic_ground_truth"]
    } == set(SCENARIOS)
    assert all(row["id"].startswith("ACC-") for row in first.accounts)
    assert all("cpf" not in str(row).lower() for row in first.accounts)


def test_generator_rejects_insufficient_volume() -> None:
    try:
        generate_synthetic_data(7, 100)
    except ValueError as exc:
        assert "at least 8" in str(exc)
    else:
        raise AssertionError("Expected validation error")
