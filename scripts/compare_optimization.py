"""Compare baseline and optimized WareMind experiment CSVs."""

import csv
from pathlib import Path
from statistics import mean, median, pstdev


RESULTS = Path("results")
BASELINE = RESULTS / "advanced_comparison_baseline.csv"
OPTIMIZED = RESULTS / "advanced_comparison_optimized.csv"


def read_csv(path):
    with path.open("r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def as_float(row, field):
    value = row.get(field, "")
    return float(value) if value not in ("", None) else None


def successful(row):
    return row["all_completed"].strip().lower() == "true"


def summarize(rows):
    count = len(rows)
    successes = [row for row in rows if successful(row)]
    ticks = [int(row["ticks"]) for row in rows]
    successful_ticks = [int(row["ticks"]) for row in successes]
    completed = sum(int(row["completed"]) for row in rows)
    total = sum(int(row["total_orders"]) for row in rows)
    distance = sum(int(row["observed_distance"]) for row in rows)
    energy = sum(as_float(row, "estimated_energy_consumed") or 0.0 for row in rows)
    messages = sum(int(row["messages"]) for row in rows)
    recoveries = sum(int(row["recoveries"]) for row in rows)
    overlaps = sum(int(row["overlap_ticks"]) for row in rows)
    mean_completion = mean(
        as_float(row, "mean_order_completion_ticks")
        for row in successes
        if as_float(row, "mean_order_completion_ticks") is not None
    ) if successes else 0.0

    deliveries = [
        int(row["robot_1_deliveries"]) + int(row["robot_2_deliveries"]) + int(row["robot_3_deliveries"])
        for row in rows
    ]
    return {
        "experiment_count": count,
        "successful_count": len(successes),
        "incomplete_count": count - len(successes),
        "success_rate": len(successes) / count if count else 0.0,
        "order_completion_rate": completed / total if total else 0.0,
        "mean_ticks": mean(ticks) if ticks else 0.0,
        "median_ticks": median(ticks) if ticks else 0.0,
        "ticks_std": pstdev(ticks) if len(ticks) > 1 else 0.0,
        "mean_successful_ticks": mean(successful_ticks) if successful_ticks else 0.0,
        "median_successful_ticks": median(successful_ticks) if successful_ticks else 0.0,
        "total_distance": distance,
        "mean_distance": distance / count if count else 0.0,
        "estimated_energy": energy,
        "mean_energy": energy / count if count else 0.0,
        "energy_per_completed_order": energy / completed if completed else 0.0,
        "messages": messages,
        "mean_messages": messages / count if count else 0.0,
        "recoveries": recoveries,
        "overlap_ticks": overlaps,
        "mean_order_completion_ticks": mean_completion,
        "total_deliveries": sum(deliveries),
    }


def write_csv(path, fieldnames, rows):
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


def main():
    baseline = read_csv(BASELINE)
    optimized = read_csv(OPTIMIZED)
    baseline_by_key = {(r["scenario"], r["strategy"], r["seed"]): r for r in baseline}
    optimized_by_key = {(r["scenario"], r["strategy"], r["seed"]): r for r in optimized}
    common = sorted(set(baseline_by_key) & set(optimized_by_key))

    summary_fields = [
        "version", "experiment_count", "successful_count", "incomplete_count",
        "success_rate", "order_completion_rate", "mean_ticks", "median_ticks",
        "ticks_std", "mean_successful_ticks", "median_successful_ticks",
        "total_distance", "mean_distance", "estimated_energy", "mean_energy",
        "energy_per_completed_order", "messages", "mean_messages", "recoveries",
        "overlap_ticks", "mean_order_completion_ticks",
    ]
    summary_rows = []
    for version, rows in (("baseline", baseline), ("optimized", optimized)):
        row = {"version": version, **summarize(rows)}
        summary_rows.append(row)
    write_csv(RESULTS / "optimization_summary.csv", summary_fields, summary_rows)

    paired_fields = [
        "scenario", "strategy", "seed", "baseline_completed", "optimized_completed",
        "baseline_ticks", "optimized_ticks", "paired_tick_delta",
        "baseline_all_completed", "optimized_all_completed",
        "baseline_distance", "optimized_distance", "baseline_energy", "optimized_energy",
        "baseline_messages", "optimized_messages", "baseline_recoveries", "optimized_recoveries",
    ]
    paired = []
    for key in common:
        before = baseline_by_key[key]
        after = optimized_by_key[key]
        paired.append({
            "scenario": key[0],
            "strategy": key[1],
            "seed": key[2],
            "baseline_completed": before["completed"],
            "optimized_completed": after["completed"],
            "baseline_ticks": before["ticks"],
            "optimized_ticks": after["ticks"],
            "paired_tick_delta": int(after["ticks"]) - int(before["ticks"]),
            "baseline_all_completed": before["all_completed"],
            "optimized_all_completed": after["all_completed"],
            "baseline_distance": before["observed_distance"],
            "optimized_distance": after["observed_distance"],
            "baseline_energy": before["estimated_energy_consumed"],
            "optimized_energy": after["estimated_energy_consumed"],
            "baseline_messages": before["messages"],
            "optimized_messages": after["messages"],
            "baseline_recoveries": before["recoveries"],
            "optimized_recoveries": after["recoveries"],
        })
    write_csv(RESULTS / "optimization_paired_comparison.csv", paired_fields, paired)

    remaining = [r for r in optimized if not successful(r)]
    write_csv(
        RESULTS / "remaining_failures.csv",
        list(optimized[0].keys()) if optimized else [],
        remaining,
    )

    grouped_fields = summary_fields
    for dimension in ("scenario", "strategy"):
        rows_out = []
        for version, rows in (("baseline", baseline), ("optimized", optimized)):
            values = sorted({r[dimension] for r in rows})
            for value in values:
                subset = [r for r in rows if r[dimension] == value]
                rows_out.append({dimension: value, "version": version, **summarize(subset)})
        write_csv(
            RESULTS / f"optimization_by_{dimension}.csv",
            [dimension, *summary_fields],
            rows_out,
        )

    print("=" * 70)
    print("OPTIMIZATION COMPARISON")
    print("=" * 70)
    for row in summary_rows:
        print(
            f"{row['version']:9s} "
            f"success={row['successful_count']}/{row['experiment_count']} "
            f"({row['success_rate']:.2%}), "
            f"order_completion={row['order_completion_rate']:.2%}, "
            f"mean_ticks={row['mean_ticks']:.2f}"
        )
    print(f"Matched keys: {len(common)}")
    print(f"Remaining optimized failures: {len(remaining)}")


if __name__ == "__main__":
    main()
