import csv
import math
import statistics

# Replace these values with tape-measured coordinates.
MEASURED = {
    "spot1": {"x": 1.11, "y": 0.60, "theta_deg": 28.0},
    "spot2": {"x": 1.93, "y": 0.60, "theta_deg": 17.0},
    "spot3": {"x": 1.6, "y": 0.17, "theta_deg": 6.0},
    "spot4": {"x": 0.67, "y": 0.49, "theta_deg": 15.0},
}


def wrap_angle(angle):
    return (angle + math.pi) % (2.0 * math.pi) - math.pi


def circular_mean(angles):
    sine = sum(math.sin(angle) for angle in angles)
    cosine = sum(math.cos(angle) for angle in angles)
    return math.atan2(sine, cosine)


def load_estimates(path):
    xs = []
    ys = []
    headings = []

    with open(path, newline="") as file:
        for row in csv.DictReader(file):
            if not row["est_x"] or not row["est_y"] or not row["est_theta"]:
                continue

            xs.append(float(row["est_x"]))
            ys.append(float(row["est_y"]))
            headings.append(float(row["est_theta"]))

    if not xs:
        raise RuntimeError(f"No pose estimates found in {path}")

    return (
        statistics.mean(xs),
        statistics.mean(ys),
        circular_mean(headings),
        statistics.stdev(xs) if len(xs) > 1 else 0.0,
        statistics.stdev(ys) if len(ys) > 1 else 0.0,
        statistics.stdev(headings) if len(headings) > 1 else 0.0,
    )


print(
    "spot,"
    "measured_x,"
    "measured_y,"
    "estimated_x,"
    "estimated_y,"
    "error_x,"
    "error_y,"
    "position_error,"
    "estimated_heading_deg,"
    "heading_error_deg,"
    "estimate_std_x,"
    "estimate_std_y,"
    "estimate_std_theta_deg"
)

for spot, measured in MEASURED.items():
    csv_path = f"l5_{spot}.csv"
    (
        estimated_x,
        estimated_y,
        estimated_theta,
        std_x,
        std_y,
        std_theta,
    ) = load_estimates(csv_path)

    error_x = estimated_x - measured["x"]
    error_y = estimated_y - measured["y"]
    position_error = math.hypot(error_x, error_y)

    measured_theta = math.radians(measured["theta_deg"])
    heading_error = math.degrees(
        abs(wrap_angle(estimated_theta - measured_theta))
    )

    print(
        f"{spot},"
        f"{measured['x']:.3f},"
        f"{measured['y']:.3f},"
        f"{estimated_x:.3f},"
        f"{estimated_y:.3f},"
        f"{error_x:.3f},"
        f"{error_y:.3f},"
        f"{position_error:.3f},"
        f"{math.degrees(estimated_theta):.2f},"
        f"{heading_error:.2f},"
        f"{std_x:.3f},"
        f"{std_y:.3f},"
        f"{math.degrees(std_theta):.2f}"
    )
