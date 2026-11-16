"""Point d'entrée : `venturi <pipeline>` ou `venturi --list`."""

import argparse
import logging

from .config import PROJECT_ROOT, load_landing, load_tables
from .core.context import Context
from .core.spark import build_spark
from .pipeline.registry import PIPELINES


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="venturi", description="Lance un pipeline VENTURI.")
    parser.add_argument("pipeline", nargs="?", choices=sorted(PIPELINES), help="pipeline à lancer")
    parser.add_argument("--list", action="store_true", help="affiche les pipelines disponibles")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    args = parser.parse_args(argv)
    if not args.list and args.pipeline is None:
        parser.error("indiquer un pipeline, ou --list pour voir ceux disponibles")
    return args


def build_context(pipeline_name: str, log_level: str) -> Context:
    logging.basicConfig(level=log_level, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
    return Context(
        spark=build_spark(f"venturi-{pipeline_name}"),
        tables=load_tables(),
        landing=load_landing(),
        logger=logging.getLogger(f"venturi.{pipeline_name}"),
        project_root=PROJECT_ROOT,
    )


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    if args.list:
        for name, pipeline in sorted(PIPELINES.items()):
            print(f"{name:<24}{pipeline.description}")
        return

    context = build_context(args.pipeline, args.log_level)
    context.logger.info("Début du pipeline")
    try:
        PIPELINES[args.pipeline]().run(context)
    except Exception:
        context.logger.exception("Échec du pipeline")
        raise
    finally:
        context.spark.stop()
    context.logger.info("Fin du pipeline")


if __name__ == "__main__":
    main()
