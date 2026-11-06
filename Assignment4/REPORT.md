# Assignment 04: ArUco-Based Particle-Filter Localization

## Abstract

This assignment implemented a two-dimensional particle filter that estimates a
LeKiwi robot's pose in a classroom map by combining wheel odometry with
camera-based ArUco marker observations. The camera was calibrated at
640 x 480 pixels using 32 checkerboard images; the resulting RMS
reprojection error was 0.758 pixels, with focal lengths of
`fx = 330.86` px and `fy = 332.15` px. The ArUco detector estimates each
marker pose with square-marker PnP and the particle filter uses marker range,
bearing, and facing as its measurement. In the simulator square-path run, the
filter achieved a mean position error of 16.4 cm and a mean heading error of
2.52 degrees, while the particle-count experiment reduced mean error from
73.3 cm with 50 particles to 9.3 cm with 2000 particles. The 2000-particle
configuration also reached a permanently sub-20-cm error in an average of
53.0 s, compared with 85.4 s for 50 particles. Real-robot recordings were
collected at four named spots, but the tape-measured coordinates required to
compute absolute L5 errors were not included in the submitted data; those
results are therefore reported as incomplete rather than estimated from
unverified coordinates.

## 1. Introduction

Mobile-robot odometry provides fast relative motion information but accumulates
wheel-scale, slip, and mecanum/omni-wheel errors over time. A camera observing
known landmarks provides an absolute reference, but marker detections are
noisy, can disappear from the image, and can be ambiguous when a small square
is viewed at a shallow angle. This assignment addresses the complementary
strengths of these sensors with a particle filter. Odometry predicts how the
robot moves between observations, while ArUco measurements correct the pose
relative to a known map.

The system has interchangeable simulated and real-robot front ends. Both
publish the same ROS topics, allowing the detector, odometry, map, and
localization nodes to run without knowing whether the source is MuJoCo or
hardware. The report first describes camera calibration and marker detection,
then the map and particle-filter method, followed by simulator, stationary,
particle-count, and real-robot experiments. The final section evaluates the
observed performance and identifies measurements still required for a complete
physical validation.

## 2. Method

### 2.1 Camera calibration

The calibration used an 11 x 8-square checkerboard with 10 x 7 internal
corners and 25 mm squares. The calibration procedure followed the guide in
[`Calibration/02_calibrate.md`](Calibration/02_calibrate.md): images should
cover the image corners, several distances, and several board tilts so that
both focal length and distortion are observable.

The resulting ROS calibration is stored in
[`camera_intrinsics.yaml`](../ros_ws/src/aruco_localization/config/camera_intrinsics.yaml).
The camera matrix is

$$
K =
\begin{bmatrix}
330.863 & 0 & 329.537 \\
0 & 332.154 & 250.043 \\
0 & 0 & 1
\end{bmatrix}.
\tag{1}
$$

The distortion model is `plumb_bob`. The calibration results are:

| Quantity | Value |
|---|---:|
| Image size | 640 x 480 px |
| Images used | 32 |
| Board corners | 10 x 7 |
| Square size | 0.025 m |
| `fx` | 330.863 px |
| `fy` | 332.154 px |
| `cx` | 329.537 px |
| `cy` | 250.043 px |
| `k1` | 0.009868 |
| `k2` | 0.120944 |
| `p1` | -0.004831 |
| `p2` | 0.000915 |
| `k3` | -0.321911 |
| RMS reprojection error | 0.758 px |

Using the principal point and image boundaries, the horizontal field of view
is approximately 89.8 degrees to the left of the principal point and
86.4 degrees to the right; the corresponding vertical values are 73.9 and
69.4 degrees. A centered-image approximation gives approximately 87.8 degrees
horizontally and 71.5 degrees vertically. The RMS error is below the
one-pixel acceptance criterion in the calibration guide, although it is above
the preferred 0.5-pixel value.

### 2.2 ArUco marker detection

The detector uses OpenCV's `DICT_4X4_50` dictionary and the map's marker size
of 0.2065 m. For every image, it detects marker IDs and four ordered corners,
refines the corners to subpixel accuracy, and solves a square PnP problem.
The marker-frame corners are

$$
\mathbf{p}_1=(-s/2,s/2,0),\quad
\mathbf{p}_2=(s/2,s/2,0),\quad
\mathbf{p}_3=(s/2,-s/2,0),\quad
\mathbf{p}_4=(-s/2,-s/2,0).
\tag{2}
$$

For detected image points $\mathbf{u}_i$, the detector computes

$$
\left(\mathbf{r},\mathbf{t}\right)
=
\operatorname{solvePnP}
\left(\mathbf{p}_i,\mathbf{u}_i,K,D\right),
\tag{3}
$$

using `SOLVEPNP_IPPE_SQUARE`. The rotation vector is converted to a rotation
matrix, producing the homogeneous transform
$T_{\mathrm{camera,marker}}$. The detector publishes
`/detected_markers`, marker visualization, an annotated image, and optional
TF frames named `detected_<id>`.

The camera is related to the robot by
`base -> camera_link -> camera`. This transform is essential: a correct
marker pose in the optical camera frame is not sufficient if the camera
position or pitch relative to the robot base is wrong.

### 2.3 Classroom map

The map frame has its origin below marker 2. The positive x direction points
out from marker 2's wall into the room, and positive y follows the wall to the
right when facing marker 2. The classroom map contains markers 1, 2, 4, 7,
and 8. It was generated by multi-view phone imagery, marker-pose chaining, and
bundle adjustment; the recorded median corner error is 0.569 px. The map
construction and its limitations are described in
[`Mapping/README.md`](Mapping/README.md).

The map's marker size is 0.2065 m, and the marker coordinates used by the
localization system are:

| ID | x (m) | y (m) | z (m) | Facing (deg) |
|---:|---:|---:|---:|---:|
| 1 | 1.6178 | 1.4670 | 0.2386 | -89.23 |
| 2 | 0.0000 | 0.0000 | 0.2386 | 0.00 |
| 4 | 1.0717 | -1.7707 | 0.2386 | 85.70 |
| 7 | 3.0086 | 0.2516 | 0.2386 | -86.93 |
| 8 | 7.8561 | -3.8504 | 0.2386 | 179.99 |

A tape-measure check of two marker-to-marker distances was required by M1,
but no tape measurements were included in the available project files. Thus,
the map is described here, but numerical map-versus-tape differences cannot
be claimed.

### 2.4 Particle-filter state and motion model

Each particle is a planar robot pose:

$$
\mathbf{x}^{(i)} =
\begin{bmatrix}
x^{(i)} & y^{(i)} & \theta^{(i)}
\end{bmatrix}^{T}.
\tag{4}
$$

The odometry node integrates measured base velocity into `/odom`. For an
odometry increment
$\Delta\mathbf{u}=[\Delta x,\Delta y,\Delta\theta]^T$, the prediction step
applies the increment to every particle and adds noise whose magnitude grows
with translation and rotation:

$$
\mathbf{x}^{(i)}_{t}
=
\mathbf{x}^{(i)}_{t-1}
+
\Delta\mathbf{u}_{t}
+
\boldsymbol{\epsilon}^{(i)}_t.
\tag{5}
$$

The configured motion-noise parameters are
`[0.1, 0.1, 0.002, 0.002]`. Angles are wrapped to the interval
$[-\pi,\pi)$.

### 2.5 Measurement model

The detector's three-dimensional pose is transformed into the base frame.
The filter retains three quantities for each marker: range, bearing, and
facing. For a marker at map coordinates $(m_x,m_y)$ and facing $m_\phi$, a
particle predicts

$$
r = \sqrt{(m_x-x)^2+(m_y-y)^2},
\tag{6}
$$

$$
b = \operatorname{wrap}\left(\operatorname{atan2}(m_y-y,m_x-x)-\theta\right),
\tag{7}
$$

$$
f = \operatorname{wrap}(m_\phi-\theta).
\tag{8}
$$

The measurement likelihood is evaluated in log form. The configured
measurement standard deviations are range fraction 0.1, bearing 0.087 rad,
and facing 0.1 rad per metre. For a normalized error $e_j$, the implementation
uses

$$
\log p_j = -\frac{1}{2}
\left[\min\left(\left|e_j\right|,3\right)\right]^2.
\tag{9}
$$

The three terms are summed over measurements and markers. The three-sigma
cap limits the effect of occasional bad detections or orientation ambiguity.
Markers farther than 5 m are ignored.

### 2.6 Resampling and estimate

The filter uses low-variance resampling when the effective sample size falls
below 50% of the 2000 particles. Resampling adds 0.01 m and 0.01 rad jitter,
and replaces 1% of the population with random particles. The reported pose
uses the highest-weight particle (`estimate: best`). The covariance of the
particle set is published with `/pose_estimate`, allowing the recorder to
report `std_x`, `std_y`, and `std_theta`.

## 3. Experiment design

### 3.1 Simulator and online topics

The simulator publishes the same core interfaces as the robot:

```text
/base_velocity -> odometry_node -> /odom
/camera/image + /camera/camera_info -> aruco_detector
/detected_markers + /map_markers -> localization_node
/pose_estimate and /particles -> RViz
```

The simulator's ArUco scene contains ten wall markers. The localization launch
file can disable the particle filter for detector testing, or enable it for
online localization. The simulator experiment used a repeatable square path
and recorded the estimate, odometry, true pose, and marker count.

### 3.2 L1 square-path experiment

The available simulator recording is
[`square.csv`](Localization/scripts/square.csv), with the corresponding plot
[`square.png`](Localization/scripts/square.png). The run lasted 60.3 s and
contained 56 pose estimates. The true simulator pose provides the reference
for position and heading error.

### 3.3 L2 stationary variance experiment

Three recordings were available:

* [`stationary_one_marker.csv`](Localization/scripts/stationary_one_marker.csv)
* [`stationary_two_markers.csv`](Localization/scripts/stationary_two_markers.csv)
* [`stationary_three_markers.csv`](Localization/scripts/stationary_three_markers.csv)

The files were intended to represent one-, two-, and three-marker conditions.
The recorded marker counts and durations were checked rather than assumed,
because the files do not all contain the requested nominal condition for the
full 60 s.

### 3.4 L4 particle-count experiment

One common simulator run was replayed using 50, 100, 500, and 2000 particles,
with seeds 1 through 5. The replay used the same bag and the same filter input
sequence for every configuration. Mean position error was computed against
`true_pose`; convergence time was defined as the first recorded time after
which all remaining errors stayed below 0.20 m. Runtime files provide the
wall-clock replay time.

### 3.5 L5 real-robot experiment

The available recordings are
[`l5_spot1.csv`](Localization/scripts/l5_spot1.csv),
[`l5_spot2.csv`](Localization/scripts/l5_spot2.csv),
[`l5_spot3.csv`](Localization/scripts/l5_spot3.csv), and
[`l5_spot4.csv`](Localization/scripts/l5_spot4.csv). They contain
`/pose_estimate`, odometry, marker count, and particle-spread information.
The tape-measured coordinates for the four floor spots were not present in the
repository, so absolute position errors cannot be calculated from these CSVs
alone.

## 4. Experimental results

### 4.1 C1: camera calibration

The calibration achieved 0.758 px RMS reprojection error with 32 images.
The focal lengths differ by only 1.29 px, or approximately 0.39%, which is
consistent with nearly square pixels. The principal point is near the image
center, with a modest vertical offset. The result is suitable for the
640 x 480 camera stream and was used by the real-camera node.

### 4.2 L1: simulator localization accuracy

The square-path recording gave the following results:

| Metric | Value |
|---|---:|
| Duration | 60.3 s |
| Pose estimates | 56 |
| Mean position error | 16.4 cm |
| Maximum position error | 17.0 cm |
| Mean heading error | 2.52 deg |
| Maximum heading error | 2.67 deg |
| Mean detected-marker count | 2.0 |
| Final odometry position error | 0.01 cm |

The final odometry error in this particular short simulated run is unusually
small despite the configured odometry noise; it should not be generalized to
longer paths. The time-series plot is
[`square.png`](Localization/scripts/square.png). It shows the estimate,
odometry-only path, true path, particle spread, error, and marker count.

The L1 result demonstrates that the filter can track the simulated robot at
centimeter-to-decimeter scale when markers are available. It does not by
itself establish real-robot accuracy, because the simulator has known ground
truth and a different camera/marker imaging process.

### 4.3 L2: stationary variance and particle spread

The following values were computed directly from the supplied CSV files.
Estimate standard deviations are the temporal standard deviations of
`est_x`, `est_y`, and `est_theta`. Particle spread is the temporal mean of
the CSV `std_*` columns.

| Recording | Rows | Duration (s) | Mean markers | Estimate SD x (m) | Estimate SD y (m) | Estimate SD heading (rad) | Mean particle SD x (m) | Mean particle SD y (m) | Mean particle SD heading (rad) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| one-marker file | 182 | 60.4 | 0.97 | 0.251 | 0.417 | 0.226 | 0.042 | 0.042 | 0.027 |
| two-marker file | 334 | 60.1 | 0.95 | 1.138 | 1.126 | 2.239 | 0.143 | 0.147 | 0.044 |
| three-marker file | 845 | 118.1 | 1.32 | 0.818 | 0.757 | 1.842 | 0.074 | 0.072 | 0.035 |

These recordings do not show the expected monotonic improvement with marker
count. In particular, the files labeled two and three markers have mean
detected counts below the nominal labels, and the three-marker file lasted
118.1 s rather than 60 s. The temporal estimate variation is also much larger
than the particle covariance reported by the filter. This indicates that the
recorded files likely include localization jumps, particle-mode changes, or
conditions that did not match their filenames. They should not be presented
as a clean one-versus-two-versus-three-marker controlled experiment. A repeat
should enforce the marker count using the live `/detected_markers` topic and
stop each recording at 60 s.

### 4.4 L4: number of particles

The particle-count results are summarized below. Values are means over five
seeds; the values in parentheses are standard deviations across seeds.

| Particles | Mean position error (cm) | Error SD across seeds (cm) | Mean settle time (s) | Settle-time SD (s) | Mean replay runtime (s) |
|---:|---:|---:|---:|---:|---:|
| 50 | 73.3 | 91.2 | 85.4 | 38.2 | 7.16 |
| 100 | 24.6 | 16.5 | 77.1 | 25.7 | 6.62 |
| 500 | 17.2 | 8.1 | 59.8 | 25.0 | 7.06 |
| 2000 | 9.3 | 1.5 | 53.0 | 10.6 | 8.45 |

The representative plots available in the repository are
[`l4_n50_seed1.png`](Localization/scripts/l4_n50_seed1.png),
[`l4_n100_seed1.png`](Localization/scripts/l4_n100_seed1.png),
[`l4_n500_seed1.png`](Localization/scripts/l4_n500_seed1.png), and
[`l4_n2000_seed1.png`](Localization/scripts/l4_n2000_seed1.png).

The results show a strong accuracy and robustness benefit from increasing the
particle count. Fifty particles are inadequate: the mean error is 73.3 cm and
the run-to-run variation is 91.2 cm. At 500 particles, the mean error falls
to 17.2 cm. The 2000-particle configuration produces the best result, with
9.3 cm mean error and only 1.5 cm standard deviation across seeds. Its replay
runtime is about 1.3 s longer than the 50-particle runtime, a moderate cost
relative to its much better reliability. For this map and sensor model, 2000
particles is therefore the recommended setting. If compute time were more
limited, 500 particles would be a reasonable compromise.

### 4.5 L5: real-robot recordings

The four real-robot recordings demonstrate that pose estimates and marker
observations were collected, but the required tape-measured ground-truth
coordinates are absent. The temporal summaries are:

| Spot | Recording duration (s) | Estimates | Mean estimated x (m) | Mean estimated y (m) | Mean estimated heading (rad) | Estimate SD x (m) | Estimate SD y (m) | Mean marker count |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 85.4 | 99 | 1.767 | -1.005 | 2.812 | 0.041 | 0.128 | 1.00 |
| 2 | 54.9 | 68 | 2.601 | -0.587 | 1.452 | 0.212 | 0.126 | 0.99 |
| 3 | 45.5 | 74 | 2.126 | 0.344 | 0.695 | 0.300 | 0.230 | 1.00 |
| 4 | 35.4 | 67 | 2.217 | 0.327 | -0.607 | 0.176 | 0.210 | 1.00 |

The filenames and durations do not match the requested ten-second L5 protocol,
so these files should be treated as preliminary stationarity recordings.
Without the measured coordinates from the floor tape marks, it is not valid
to report absolute x/y errors or claim that one spot is more accurate than
another. The missing quantities are the measured $(x,y)$ coordinates and,
optionally, the intended heading at each spot. Once supplied, the position
error for spot $j$ is

$$
e_j =
\sqrt{
(\hat{x}_j-x_j)^2+
(\hat{y}_j-y_j)^2
}.
\tag{10}
$$

### 4.6 D2 and marker consistency

The detector guide requires a distance-accuracy experiment at 0.5, 1, 1.5,
2, and 3 m, plus the maximum detection distance and marker pixel width. The
repository contains the detector implementation and calibration, but no
distance-accuracy CSV or marker-error recording that supports a numerical D2
plot. Likewise, no `record_marker_errors.py` output was available for an L2
marker-consistency plot. These results must be collected rather than
reconstructed from pose-estimate CSVs.

The expected error mechanisms are:

* marker-size error scales all estimated distances;
* calibration error changes PnP depth and bearing;
* subpixel corner noise becomes more significant when the marker occupies few
  pixels;
* camera-mount translation, pitch, or yaw errors bias every transformed
  measurement;
* a marker map error produces a persistent offset for that marker;
* shallow viewing angles can produce square-pose ambiguity.

## 5. Discussion

The simulator results establish that the implemented pipeline can combine
odometry and visual landmarks successfully. The particle-count experiment is
especially informative: low particle counts sometimes fail to represent the
correct hypothesis, while 2000 particles consistently converge. The
measurement model's facing term helps resolve the circular ambiguity that
would remain if only range and bearing were used for a single marker.

The calibration is adequate but not ideal. A 0.758-pixel RMS error is within
the documented acceptable range, yet improved calibration images could reduce
systematic PnP error. The map was produced with bundle adjustment and has a
reported median corner error of 0.569 px, but physical tape checks are still
needed because marker movement and map-scale errors cannot be detected from
the map file alone.

The stationary files show why experiment metadata matters. A nominal
three-marker recording averaged only 1.32 detected markers and lasted nearly
twice the requested time. The temporal estimate variation also exceeded the
reported instantaneous particle spread. This may indicate multimodal particle
sets or occasional pose jumps; reporting only the covariance would hide that
behavior. Future runs should record the actual marker count, enforce the
60-second duration, and inspect the time series for mode switches.

The real-robot files show approximately one marker per recording, so they do
not yet test the requested range of marker visibility. Their pose estimates
have visible variation, particularly in heading, but absolute accuracy cannot
be evaluated without the tape coordinates. This is a measurement-completeness
issue, not evidence that the robot is accurate or inaccurate.

## 6. Conclusion

The assignment produced a complete localization architecture: calibrated
camera imagery is converted to ArUco marker poses, those observations are
transformed into the robot base frame, and a particle filter fuses them with
wheel odometry. The camera calibration used 32 images and achieved 0.758 px
RMS reprojection error. In simulation, a square-path run produced 16.4 cm
mean position error and 2.52 degrees mean heading error. In the controlled
particle-count study, increasing the population from 50 to 2000 particles
reduced mean error from 73.3 cm to 9.3 cm and reduced mean permanent
sub-20-cm convergence time from 85.4 s to 53.0 s. The 2000-particle setting
is consequently the best choice for this map, while 500 particles offers a
lower-cost compromise.

The principal limitations are incomplete physical ground truth. The
repository does not contain the requested D2 marker-distance measurements,
marker-consistency recording, M1 tape checks, or L5 tape coordinates.
Therefore, this report gives reproducible simulator and calibration results,
documents the available real-robot recordings, and explicitly identifies the
measurements needed before claiming final real-world localization accuracy.

## 7. Reproducibility and deliverables

The main implementation files are:

* [`aruco_detector.py`](../ros_ws/src/aruco_localization/aruco_localization/aruco_detector.py)
* [`particle_filter.py`](../ros_ws/src/aruco_localization/aruco_localization/particle_filter.py)
* [`localization_node.py`](../ros_ws/src/aruco_localization/aruco_localization/localization_node.py)
* [`camera_intrinsics.yaml`](../ros_ws/src/aruco_localization/config/camera_intrinsics.yaml)
* [`localization.yaml`](../ros_ws/src/aruco_localization/config/localization.yaml)
* [`localization.launch.py`](../ros_ws/src/aruco_localization/launch/localization.launch.py)

The assignment guides are:

* [`Calibration/README.md`](Calibration/README.md)
* [`Detection/README.md`](Detection/README.md)
* [`Localization/README.md`](Localization/README.md)
* [`Localization/04_experiments.md`](Localization/04_experiments.md)

The available analysis scripts are:

* [`analyze_l4.py`](Localization/scripts/analyze_l4.py)
* [`analyze_l5.py`](Localization/scripts/analyze_l5.py)
* [`plot_localization.py`](Localization/scripts/plot_localization.py)
* [`plot_marker_errors.py`](Localization/scripts/plot_marker_errors.py)

For a complete final submission, add the missing physical measurements and
plots to the corresponding sections, and include the required D1, L-sim, and
L-real videos.
