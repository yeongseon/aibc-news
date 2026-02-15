import os
from pathlib import Path

from .application.use_case import RunDailyBriefUseCase
from .collector import CompositeCollector
from .publisher import Publisher
from .quality import QualityGate
from .utils import RunLogger, ensure_dir, get_run_date, read_json, write_json
from .writer import CopilotWriter


def run_pipeline(run_date: str, dry_run: bool = False):
    data_dir = Path("data")
    logs_dir = Path("logs")
    ensure_dir(data_dir)
    ensure_dir(logs_dir)

    logger = RunLogger(logs_dir / f"{run_date}.log")
    logger.log("Pipeline start")

    collector = CompositeCollector()
    writer = CopilotWriter()
    gate = QualityGate()
    publisher = Publisher()

    use_case = RunDailyBriefUseCase(
        collector=collector,
        writer=writer,
        gate=gate,
        publisher=publisher,
        logger=logger,
    )

    result = use_case.execute(
        run_date=run_date,
        collector_path=data_dir / "collector" / f"{run_date}.json",
        quality_path=data_dir / "quality" / f"{run_date}.json",
        dry_run=dry_run,
        force_collect=os.environ.get("FORCE_COLLECT", "false").lower() == "true",
        force_publish=os.environ.get("FORCE_PUBLISH", "false").lower() == "true",
        read_json=read_json,
        write_json=write_json,
    )

    logger.log("Pipeline done")
    return result


def main() -> None:
    run_pipeline(get_run_date())


if __name__ == "__main__":
    main()
