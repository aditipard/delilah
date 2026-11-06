import csv
import math
import statistics

PARTICLE_COUNTS = [50, 100, 500, 2000]
SEEDS = [1, 2, 3, 4, 5]


def load_run(csv_path):
    times = []
    errors = []

    with open(csv_path, newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if not row["true_x"] or not row["true_y"]:
                continue

            estimate_x = float(row["est_x"])
            estimate_y = float(row["est_y"])
            true_x = float(row["true_x"])
            true_y = float(row["true_y"])
            time_s = float(row["time"])

            error_m = math.hypot(
                estimate_x - true_x,
                estimate_y - true_y,
            )

            times.append(time_s)
            errors.append(error_m)

    if not errors:
        raise RuntimeError(f"No simulator truth data found in {csv_path}")

    mean_error_m = statistics.mean(errors)

    # Find the first time after which every remaining estimate
    # stays below 20 cm.
    settle_time_s = None

    for index, current_time in enumerate(times):
        remaining_errors = errors[index:]

        if all(error < 0.20 for error in remaining_errors):
            settle_time_s = current_time
            break

    return mean_error_m, settle_time_s


def load_runtime(runtime_path):
    with open(runtime_path) as file:
        return float(file.read().strip())


print(
    "particles,"
    "mean_error_cm,"
    "error_std_cm,"
    "mean_settle_time_s,"
    "mean_runtime_s"
)

for particles in PARTICLE_COUNTS:
    mean_errors_cm = []
    settle_times_s = []
    runtimes_s = []

    for seed in SEEDS:
        csv_path = f"l4_n{particles}_seed{seed}.csv"
        runtime_path = f"l4_n{particles}_seed{seed}.runtime.txt"

        mean_error_m, settle_time_s = load_run(csv_path)
        runtime_s = load_runtime(runtime_path)

        mean_errors_cm.append(mean_error_m * 100.0)
        runtimes_s.append(runtime_s)

        if settle_time_s is not None:
            settle_times_s.append(settle_time_s)

    mean_error = statistics.mean(mean_errors_cm)
    error_std = (
        statistics.stdev(mean_errors_cm)
        if len(mean_errors_cm) > 1
        else 0.0
    )
    mean_runtime = statistics.mean(runtimes_s)

    if settle_times_s:
        mean_settle_time = statistics.mean(settle_times_s)
        settle_text = f"{mean_settle_time:.3f}"
    else:
        settle_text = "never"

    print(
        f"{particles},"
        f"{mean_error:.2f},"
        f"{error_std:.2f},"
        f"{settle_text},"
        f"{mean_runtime:.3f}"
    )