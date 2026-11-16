import asyncio
import csv
import sys
import time
from pathlib import Path
from typing import Optional

import aiohttp


WARMUP_REQUESTS = 5
MEASURED_REQUESTS = 30
CONCURRENCY_LEVELS = (1, 5, 10, 20)
REQUEST_TIMEOUT_SECONDS = 10
APPLICATIONS = (
    ("PHP", "http://127.0.0.1:8000/"),
    ("Node.js", "http://127.0.0.1:3000/"),
    ("Python", "http://127.0.0.1:5000/"),
    ("Java", "http://127.0.0.1:8080/"),
)

BENCHMARKS_DIRECTORY = Path(__file__).resolve().parent
RAW_RESULTS_PATH = BENCHMARKS_DIRECTORY / "resultats_http_bruts.csv"
SUMMARY_RESULTS_PATH = BENCHMARKS_DIRECTORY / "resultats_http_synthese.csv"


def percentile(values: list[float], percentile_rank: float) -> float:
    sorted_values = sorted(values)
    index = max(0, min(len(sorted_values) - 1, int((len(sorted_values) * percentile_rank) + 0.999999) - 1))
    return sorted_values[index]


def median(values: list[float]) -> float:
    sorted_values = sorted(values)
    middle = len(sorted_values) // 2
    if len(sorted_values) % 2:
        return sorted_values[middle]
    return (sorted_values[middle - 1] + sorted_values[middle]) / 2


async def request_home(
    session: aiohttp.ClientSession,
    url: str,
) -> tuple[float, Optional[int], str]:
    started_at = time.perf_counter_ns()
    status: Optional[int] = None
    error = ""
    try:
        async with session.get(url, allow_redirects=True) as response:
            status = response.status
            await response.read()
            if not 200 <= status < 400:
                error = f"HTTP {status}"
    except asyncio.TimeoutError:
        error = f"timeout après {REQUEST_TIMEOUT_SECONDS}s"
    except aiohttp.ClientError as exception:
        error = f"{type(exception).__name__}: {exception}"
    except OSError as exception:
        error = f"{type(exception).__name__}: {exception}"
    duration_ms = (time.perf_counter_ns() - started_at) / 1_000_000
    return duration_ms, status, error


async def run_batch(
    session: aiohttp.ClientSession,
    url: str,
    request_count: int,
    concurrency: int,
) -> list[tuple[float, Optional[int], str]]:
    semaphore = asyncio.Semaphore(concurrency)

    async def limited_request() -> tuple[float, Optional[int], str]:
        async with semaphore:
            return await request_home(session, url)

    return await asyncio.gather(*(limited_request() for _ in range(request_count)))


async def benchmark_application(
    technology: str,
    url: str,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    raw_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []
    timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT_SECONDS)
    connector = aiohttp.TCPConnector(limit=0)

    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        for concurrency in CONCURRENCY_LEVELS:
            print(
                f"{technology} - concurrence {concurrency}: "
                f"échauffement ({WARMUP_REQUESTS} requêtes)"
            )
            warmup_measurements = await run_batch(
                session, url, WARMUP_REQUESTS, concurrency
            )
            for trial_number, (_, _, error) in enumerate(
                warmup_measurements, start=1
            ):
                if error:
                    print(
                        f"ERREUR échauffement {technology} "
                        f"concurrence {concurrency} essai {trial_number}: {error}",
                        file=sys.stderr,
                    )

            print(
                f"{technology} - concurrence {concurrency}: "
                f"mesure ({MEASURED_REQUESTS} requêtes)"
            )
            measured_started_at = time.perf_counter_ns()
            measurements = await run_batch(
                session, url, MEASURED_REQUESTS, concurrency
            )
            measured_duration_seconds = (
                time.perf_counter_ns() - measured_started_at
            ) / 1_000_000_000

            durations = [measurement[0] for measurement in measurements]
            errors = [measurement[2] for measurement in measurements if measurement[2]]
            for trial_number, (duration, status, error) in enumerate(
                measurements, start=1
            ):
                raw_rows.append(
                    {
                        "technologie": technology,
                        "niveau de concurrence": concurrency,
                        "numéro d'essai": trial_number,
                        "durée en ms": f"{duration:.3f}",
                        "code HTTP": "" if status is None else status,
                        "éventuelle erreur": error,
                    }
                )
                if error:
                    print(
                        f"ERREUR {technology} concurrence {concurrency} "
                        f"essai {trial_number}: {error}",
                        file=sys.stderr,
                    )

            summary_rows.append(
                {
                    "technologie": technology,
                    "niveau de concurrence": concurrency,
                    "temps moyen en ms": f"{sum(durations) / len(durations):.3f}",
                    "médiane en ms": f"{median(durations):.3f}",
                    "95e percentile en ms": f"{percentile(durations, 0.95):.3f}",
                    "taux d'erreur": f"{len(errors) / len(measurements):.6f}",
                    "débit en requêtes par seconde": (
                        f"{len(measurements) / measured_duration_seconds:.3f}"
                    ),
                }
            )

    return raw_rows, summary_rows


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


async def main() -> None:
    all_raw_rows: list[dict[str, object]] = []
    all_summary_rows: list[dict[str, object]] = []

    for technology, url in APPLICATIONS:
        print(f"\n{technology}: {url}")
        raw_rows, summary_rows = await benchmark_application(technology, url)
        all_raw_rows.extend(raw_rows)
        all_summary_rows.extend(summary_rows)

    write_csv(
        RAW_RESULTS_PATH,
        [
            "technologie",
            "niveau de concurrence",
            "numéro d'essai",
            "durée en ms",
            "code HTTP",
            "éventuelle erreur",
        ],
        all_raw_rows,
    )
    write_csv(
        SUMMARY_RESULTS_PATH,
        [
            "technologie",
            "niveau de concurrence",
            "temps moyen en ms",
            "médiane en ms",
            "95e percentile en ms",
            "taux d'erreur",
            "débit en requêtes par seconde",
        ],
        all_summary_rows,
    )
    print(f"\nRésultats bruts : {RAW_RESULTS_PATH}")
    print(f"Synthèse : {SUMMARY_RESULTS_PATH}")


if __name__ == "__main__":
    asyncio.run(main())
