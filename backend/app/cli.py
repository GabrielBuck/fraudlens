from __future__ import annotations

import json

import typer

from app.core.config import get_settings
from app.db.session import Base, SessionLocal, engine
from app.services.pipeline import (
    ensure_demo,
    persist_generated_data,
    run_all,
    score_transactions,
    train_model,
)

app = typer.Typer(help="FraudLens command line interface")
db_app = typer.Typer(help="Database operations")
data_app = typer.Typer(help="Synthetic data operations")
model_app = typer.Typer(help="Model operations")
transactions_app = typer.Typer(help="Transaction operations")
pipeline_app = typer.Typer(help="End-to-end pipeline")
demo_app = typer.Typer(help="Demo lifecycle")
app.add_typer(db_app, name="db")
app.add_typer(data_app, name="data")
app.add_typer(model_app, name="model")
app.add_typer(transactions_app, name="transactions")
app.add_typer(pipeline_app, name="pipeline")
app.add_typer(demo_app, name="demo")


def _print(payload: object) -> None:
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2, default=str))


@db_app.command("init")
def db_init() -> None:
    Base.metadata.create_all(engine)
    typer.echo("Banco inicializado com sucesso.")


@data_app.command("generate")
def data_generate(
    accounts: int = typer.Option(1000, min=8),
    transactions: int = typer.Option(50_000, min=80),
    seed: int = typer.Option(42),
) -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as session:
        _print(persist_generated_data(session, accounts, transactions, seed))


@model_app.command("train")
def model_train() -> None:
    with SessionLocal() as session:
        _print(train_model(session))


@model_app.command("evaluate")
def model_evaluate() -> None:
    with SessionLocal() as session:
        _print(score_transactions(session))


@transactions_app.command("score")
def transactions_score() -> None:
    with SessionLocal() as session:
        _print(score_transactions(session))


@pipeline_app.command("run-all")
def pipeline_run_all(
    accounts: int = typer.Option(None),
    transactions: int = typer.Option(None),
    seed: int = typer.Option(None),
) -> None:
    settings = get_settings()
    Base.metadata.create_all(engine)
    with SessionLocal() as session:
        _print(
            run_all(
                session,
                accounts or settings.default_account_count,
                transactions or settings.default_transaction_count,
                seed if seed is not None else settings.random_seed,
                settings,
            )
        )


@pipeline_app.command("ensure-demo")
def pipeline_ensure_demo() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as session:
        _print(ensure_demo(session))


@demo_app.command("reset")
def demo_reset(
    accounts: int = typer.Option(120, min=8),
    transactions: int = typer.Option(5000, min=80),
    seed: int = typer.Option(42),
) -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as session:
        _print(run_all(session, accounts, transactions, seed))


if __name__ == "__main__":
    app()
