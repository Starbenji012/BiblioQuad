import csv
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


BENCHMARKS_DIRECTORY = Path(__file__).resolve().parent
INPUT_PATH = BENCHMARKS_DIRECTORY / "resultats_http_synthese.csv"
OUTPUT_DIRECTORY = BENCHMARKS_DIRECTORY / "figures"
BAR_OUTPUT_PATH = OUTPUT_DIRECTORY / "temps_medians_concurrence_20.png"
LINE_OUTPUT_PATH = OUTPUT_DIRECTORY / "temps_medians_par_concurrence.png"

TECHNOLOGIES = ("PHP", "Node.js", "Python", "Java")
CONCURRENCIES = (1, 5, 10, 20)


def load_medians() -> dict[str, dict[int, float]]:
    medians: dict[str, dict[int, float]] = defaultdict(dict)
    with INPUT_PATH.open(newline="", encoding="utf-8") as input_file:
        rows = csv.DictReader(input_file)
        required_columns = {
            "technologie",
            "niveau de concurrence",
            "médiane en ms",
        }
        if not required_columns.issubset(rows.fieldnames or set()):
            raise ValueError(
                f"Colonnes manquantes dans {INPUT_PATH}: "
                f"{sorted(required_columns - set(rows.fieldnames or []))}"
            )
        for row in rows:
            technology = row["technologie"]
            concurrency = int(row["niveau de concurrence"])
            medians[technology][concurrency] = float(row["médiane en ms"])

    expected_points = {
        technology: set(CONCURRENCIES) for technology in TECHNOLOGIES
    }
    if set(medians) != set(TECHNOLOGIES):
        raise ValueError(
            f"Technologies inattendues dans {INPUT_PATH}: {sorted(medians)}"
        )
    for technology in TECHNOLOGIES:
        if set(medians[technology]) != expected_points[technology]:
            raise ValueError(
                f"Concurrences incomplètes pour {technology}: "
                f"{sorted(medians[technology])}"
            )
    return medians


def configure_plot() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 120,
            "savefig.dpi": 300,
            "font.size": 11,
            "axes.titlesize": 14,
            "axes.labelsize": 12,
        }
    )


def create_bar_chart(medians: dict[str, dict[int, float]]) -> None:
    values = [medians[technology][20] for technology in TECHNOLOGIES]
    figure, axis = plt.subplots(figsize=(9, 5.5))
    bars = axis.bar(TECHNOLOGIES, values, color=["#4472C4", "#ED7D31", "#70AD47", "#A5A5A5"])
    axis.set_title("Temps de réponse médian à concurrence 20")
    axis.set_xlabel("Technologie")
    axis.set_ylabel("Temps médian (ms)")
    axis.grid(axis="y", linestyle="--", alpha=0.35)
    axis.set_axisbelow(True)
    axis.bar_label(bars, fmt="%.3f ms", padding=3)
    figure.tight_layout()
    figure.savefig(BAR_OUTPUT_PATH, bbox_inches="tight")
    plt.close(figure)


def create_line_chart(medians: dict[str, dict[int, float]]) -> None:
    figure, axis = plt.subplots(figsize=(9, 5.5))
    for technology in TECHNOLOGIES:
        values = [medians[technology][concurrency] for concurrency in CONCURRENCIES]
        axis.plot(
            CONCURRENCIES,
            values,
            marker="o",
            linewidth=2,
            markersize=6,
            label=technology,
        )
    axis.set_title("Temps de réponse médian selon la concurrence")
    axis.set_xlabel("Niveau de concurrence (requêtes simultanées)")
    axis.set_ylabel("Temps médian (ms)")
    axis.set_xticks(CONCURRENCIES)
    axis.grid(True, linestyle="--", alpha=0.35)
    axis.legend(title="Technologie")
    axis.set_axisbelow(True)
    figure.tight_layout()
    figure.savefig(LINE_OUTPUT_PATH, bbox_inches="tight")
    plt.close(figure)


def main() -> None:
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    configure_plot()
    medians = load_medians()
    create_bar_chart(medians)
    create_line_chart(medians)
    print(BAR_OUTPUT_PATH)
    print(LINE_OUTPUT_PATH)


if __name__ == "__main__":
    main()
