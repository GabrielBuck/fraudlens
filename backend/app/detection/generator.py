from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

import numpy as np

CITIES = [
    ("São Paulo", "SP", -23.5505, -46.6333),
    ("Rio de Janeiro", "RJ", -22.9068, -43.1729),
    ("Belo Horizonte", "MG", -19.9167, -43.9345),
    ("Curitiba", "PR", -25.4284, -49.2733),
    ("Recife", "PE", -8.0476, -34.8770),
    ("Porto Alegre", "RS", -30.0346, -51.2177),
]
SEGMENTS = ["Micro", "Pequena empresa", "Média empresa", "Grande empresa"]
PAYMENT_METHODS = ["PIX", "TED", "boleto", "cartão", "transferência interna"]
SCENARIOS = [
    "account_takeover",
    "velocity_burst",
    "split_payment",
    "impossible_travel",
    "suspicious_duplicate",
    "unusual_hour_amount",
    "low_value_testing",
    "risky_counterparty",
]


@dataclass(frozen=True)
class GeneratedData:
    accounts: list[dict[str, Any]]
    counterparties: list[dict[str, Any]]
    devices: list[dict[str, Any]]
    authentication_events: list[dict[str, Any]]
    transactions: list[dict[str, Any]]


def _identifier(prefix: str, number: int, width: int = 6) -> str:
    return f"{prefix}-{number:0{width}d}"


def generate_synthetic_data(
    account_count: int = 1000,
    transaction_count: int = 50_000,
    seed: int = 42,
) -> GeneratedData:
    if account_count < 8:
        raise ValueError("account_count must be at least 8 to cover every scenario")
    if transaction_count < 80:
        raise ValueError("transaction_count must be at least 80")

    rng = np.random.default_rng(seed)
    end_at = datetime(2026, 6, 30, 23, 59, tzinfo=UTC)
    accounts: list[dict[str, Any]] = []
    devices: list[dict[str, Any]] = []
    counterparties: list[dict[str, Any]] = []
    auth_events: list[dict[str, Any]] = []

    for index in range(account_count):
        city, state, latitude, longitude = CITIES[index % len(CITIES)]
        segment = SEGMENTS[index % len(SEGMENTS)]
        age = int(rng.integers(30, 2200))
        monthly_volume = float([18_000, 75_000, 300_000, 1_200_000][index % 4])
        accounts.append(
            {
                "id": _identifier("ACC", index + 1),
                "created_at": end_at - timedelta(days=age),
                "customer_segment": segment,
                "home_city": city,
                "home_state": state,
                "home_latitude": latitude,
                "home_longitude": longitude,
                "account_age_days": age,
                "usual_transaction_hour_start": 7 + index % 3,
                "usual_transaction_hour_end": 18 + index % 4,
                "average_monthly_volume": monthly_volume,
                "risk_profile": ["baixo", "moderado", "elevado"][index % 3],
                "is_active": True,
            }
        )
        for device_index in range(2):
            first_seen = end_at - timedelta(days=int(rng.integers(4, max(5, age))))
            devices.append(
                {
                    "id": _identifier("DEV", index * 2 + device_index + 1),
                    "account_id": accounts[-1]["id"],
                    "first_seen_at": first_seen,
                    "last_seen_at": end_at,
                    "device_type": "desktop" if device_index == 0 else "mobile",
                    "operating_system": ["Windows", "Android", "Linux", "iOS"][
                        (index + device_index) % 4
                    ],
                    "browser": ["Chrome", "Firefox", "Edge", "Safari"][(index + device_index) % 4],
                    "trusted": device_index == 0,
                }
            )

    counterparty_count = max(40, account_count * 3)
    for index in range(counterparty_count):
        city, state, _, _ = CITIES[(index * 3) % len(CITIES)]
        counterparties.append(
            {
                "id": _identifier("CP", index + 1),
                "created_at": end_at - timedelta(days=int(rng.integers(30, 2500))),
                "category": ["serviços", "varejo", "fornecedor", "logística", "utilidades"][
                    index % 5
                ],
                "city": city,
                "state": state,
                "historical_risk_level": "alto" if index >= counterparty_count - 3 else "baixo",
                "is_known": index < int(counterparty_count * 0.85),
            }
        )

    transactions: list[dict[str, Any]] = []
    per_account = np.full(account_count, transaction_count // account_count)
    per_account[: transaction_count % account_count] += 1
    tx_number = 1
    for account_index, count in enumerate(per_account):
        account = accounts[account_index]
        dates = sorted(
            end_at - timedelta(minutes=int(value))
            for value in rng.integers(60, 90 * 24 * 60, size=int(count))
        )
        scale = account["average_monthly_volume"] / max(int(count) * 12, 1)
        for local_index, timestamp in enumerate(dates):
            cp_index = (account_index * 5 + int(rng.integers(0, 8))) % counterparty_count
            device = devices[account_index * 2]
            status = str(
                rng.choice(
                    ["aprovada", "negada", "pendente", "estornada"],
                    p=[0.91, 0.045, 0.025, 0.02],
                )
            )
            amount = float(np.clip(rng.lognormal(np.log(max(scale, 20)), 0.85), 2, 250_000))
            transactions.append(
                {
                    "id": _identifier("TX", tx_number, 8),
                    "account_id": account["id"],
                    "counterparty_id": counterparties[cp_index]["id"],
                    "device_id": device["id"],
                    "timestamp": timestamp,
                    "amount": round(amount, 2),
                    "currency": "BRL",
                    "payment_method": str(
                        rng.choice(PAYMENT_METHODS, p=[0.42, 0.08, 0.2, 0.22, 0.08])
                    ),
                    "direction": str(rng.choice(["saída", "entrada"], p=[0.77, 0.23])),
                    "status": status,
                    "merchant_category": counterparties[cp_index]["category"],
                    "ip_country": "BR",
                    "ip_city": account["home_city"],
                    "latitude": account["home_latitude"] + float(rng.normal(0, 0.025)),
                    "longitude": account["home_longitude"] + float(rng.normal(0, 0.025)),
                    "description": f"Pagamento sintético {local_index + 1}",
                    "synthetic_scenario": None,
                    "synthetic_ground_truth": False,
                }
            )
            tx_number += 1

    transactions.sort(key=lambda row: (row["account_id"], row["timestamp"], row["id"]))
    _inject_scenarios(transactions, accounts, counterparties, devices, auth_events, end_at)
    transactions.sort(key=lambda row: row["id"])

    for index, account in enumerate(accounts):
        trusted_device = devices[index * 2]
        auth_events.append(
            {
                "id": _identifier("AUTH", len(auth_events) + 1, 8),
                "account_id": account["id"],
                "device_id": trusted_device["id"],
                "timestamp": end_at - timedelta(days=index % 30, hours=2),
                "success": True,
                "ip_country": "BR",
                "ip_region": account["home_state"],
                "ip_city": account["home_city"],
                "latitude": account["home_latitude"],
                "longitude": account["home_longitude"],
                "failure_reason": None,
            }
        )

    return GeneratedData(accounts, counterparties, devices, auth_events, transactions)


def _inject_scenarios(
    transactions: list[dict[str, Any]],
    accounts: list[dict[str, Any]],
    counterparties: list[dict[str, Any]],
    devices: list[dict[str, Any]],
    auth_events: list[dict[str, Any]],
    end_at: datetime,
    expand: bool = True,
) -> None:
    by_account: dict[str, list[dict[str, Any]]] = {}
    for row in transactions:
        by_account.setdefault(row["account_id"], []).append(row)
    risky_cp = counterparties[-1]

    for scenario_index, scenario in enumerate(SCENARIOS):
        account = accounts[scenario_index]
        candidates = by_account[account["id"]][-5:]
        base_time = end_at - timedelta(days=7 - scenario_index, hours=2)
        for offset, row in enumerate(candidates):
            row.update(
                synthetic_scenario=scenario,
                synthetic_ground_truth=True,
                timestamp=base_time + timedelta(minutes=offset * 2),
                direction="saída",
                status="aprovada",
                payment_method="PIX",
            )

        if scenario == "account_takeover":
            for row in candidates:
                row.update(
                    device_id=devices[scenario_index * 2 + 1]["id"],
                    counterparty_id=counterparties[-2]["id"],
                    ip_country="AR",
                    ip_city="Buenos Aires",
                    latitude=-34.6037,
                    longitude=-58.3816,
                    amount=round(25_000 + 2500 * candidates.index(row), 2),
                    timestamp=row["timestamp"].replace(hour=2),
                )
            for attempt in range(4):
                auth_events.append(
                    {
                        "id": _identifier("AUTH", len(auth_events) + 1, 8),
                        "account_id": account["id"],
                        "device_id": devices[scenario_index * 2 + 1]["id"],
                        "timestamp": candidates[0]["timestamp"] - timedelta(minutes=8 - attempt),
                        "success": attempt == 3,
                        "ip_country": "AR",
                        "ip_region": "BA",
                        "ip_city": "Buenos Aires",
                        "latitude": -34.6037,
                        "longitude": -58.3816,
                        "failure_reason": None if attempt == 3 else "invalid_credentials",
                    }
                )
        elif scenario == "velocity_burst":
            for offset, row in enumerate(candidates):
                row.update(
                    amount=1490.0 + offset, counterparty_id=counterparties[20 + offset]["id"]
                )
        elif scenario == "split_payment":
            for offset, row in enumerate(candidates):
                row.update(amount=4950.0, counterparty_id=counterparties[30 + offset]["id"])
        elif scenario == "impossible_travel":
            candidates[-2].update(ip_city="Recife", latitude=-8.0476, longitude=-34.877)
            candidates[-1].update(
                ip_country="CL",
                ip_city="Santiago",
                latitude=-33.4489,
                longitude=-70.6693,
                device_id=devices[scenario_index * 2 + 1]["id"],
                timestamp=candidates[-2]["timestamp"] + timedelta(minutes=12),
                amount=18_500.0,
            )
        elif scenario == "suspicious_duplicate":
            for row in candidates:
                row.update(amount=7777.77, counterparty_id=counterparties[12]["id"])
        elif scenario == "unusual_hour_amount":
            for offset, row in enumerate(candidates):
                row.update(
                    amount=45_000.0 + offset * 1000,
                    timestamp=row["timestamp"].replace(hour=3),
                    counterparty_id=counterparties[-2]["id"],
                )
        elif scenario == "low_value_testing":
            for offset, row in enumerate(candidates):
                row.update(amount=1.0 + offset, status="negada" if offset < 4 else "aprovada")
            candidates[-1]["amount"] = 12_000.0
        elif scenario == "risky_counterparty":
            for offset, row in enumerate(candidates):
                row.update(counterparty_id=risky_cp["id"], amount=9000.0 + offset * 500)

    if expand:
        group_count = min(10, max(1, len(accounts) // 50))
        for group_index in range(1, group_count):
            account_start = group_index * len(SCENARIOS)
            device_start = account_start * 2
            _inject_scenarios(
                transactions,
                accounts[account_start : account_start + len(SCENARIOS)],
                counterparties,
                devices[device_start : device_start + len(SCENARIOS) * 2],
                auth_events,
                end_at,
                expand=False,
            )
