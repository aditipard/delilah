# 1. ROS Concepts

A robot program has many jobs at once: read the leader arm, simulate or drive the robot, read a camera, show something on screen. Writing all of that as one big program quickly becomes unmanageable.

**ROS 2** (Robot Operating System) lets you split it into small programs that run at the same time and send each other messages. This page explains the three words you need: **node**, **topic** and **message**.

## Node

A **node** is one running program that does one job. Examples from this course:

| Node | Its job |
| --- | --- |
| `leader_node` | read the leader arm's joint angles |
| `sim_node` | run the simulator |
| `follower` (you write it) | compare commands with what the arm does |

Each node is started separately, usually in its own terminal. Nodes can be started and stopped independently, and they can run on different computers.

## Topic

Nodes do not call each other directly. They talk through **topics**. A topic is a named channel, like a radio frequency. Its name starts with a slash, for example `/arm_commands`.

- A node that sends on a topic is a **publisher**.
- A node that receives from a topic is a **subscriber**.

```
 leader_node  ── publishes ──►  /arm_commands  ── delivers to ──►  sim_node
 (publisher)                      (topic)                         (subscriber)
```

The important property: **publishers and subscribers do not know each other.** The publisher only knows the topic's name. This is what makes ROS programs easy to rearrange:

- Replace `leader_node` by any other node that publishes on `/arm_commands`, and `sim_node` works unchanged.
- Add a second subscriber that records `/arm_commands`, and nobody else notices.
- Replace `sim_node` by a node that drives the real robot, and the leader side works unchanged.

A topic can have any number of publishers and any number of subscribers, including none. Publishing on a topic nobody listens to is not an error. The messages are simply dropped.

## Message

Everything sent on a topic is a **message**, and every topic has one fixed **message type**. The type says what a message contains.

| Message type | Contains | Used here for |
| --- | --- | --- |
| `std_msgs/String` | one text | the talker and listener demo |
| `std_msgs/Float64MultiArray` | a list of numbers | arm commands and arm state |
| `sensor_msgs/Image` | one picture | the camera |

A type name has two parts: the package it comes from (`std_msgs`) and its name (`Float64MultiArray`). A publisher and a subscriber only connect if they use the same topic name **and** the same type.

## You have already seen this

At the end of the [ROS install page](../Setup/01_install_ros2.md) you ran two demo nodes:

```bash
ros2 run demo_nodes_cpp talker
```

```bash
ros2 run demo_nodes_py listener
```

Now you can name what happened. `talker` is a node that publishes a `std_msgs/String` message on the topic `/chatter` once per second. `listener` is a node that subscribes to `/chatter` and prints what it receives. Neither knows the other exists. One is written in C++ and the other in Python, and it makes no difference.

## The `ros2` command

`ros2` is the command-line tool for looking at a running ROS system. You will use these forms on the next page.

| Command | Question it answers |
| --- | --- |
| `ros2 run PACKAGE NODE` | (starts a node) |
| `ros2 node list` | Which nodes are running? |
| `ros2 node info /NODE` | What does this node publish and subscribe to? |
| `ros2 topic list` | Which topics exist? |
| `ros2 topic info /TOPIC` | What type is it, and how many publishers and subscribers does it have? |
| `ros2 topic echo /TOPIC` | What is being sent right now? |
| `ros2 topic hz /TOPIC` | How many messages per second? |
| `ros2 topic pub /TOPIC TYPE "DATA"` | (publishes a message by hand) |
| `ros2 interface show TYPE` | What is inside this message type? |

## Other things ROS has

ROS has more ways to communicate than topics. You do not need them yet, but you will meet the words:

| Word | Idea |
| --- | --- |
| **Parameter** | A named setting of a node, such as which serial port to use. You will use these. |
| **Service** | A question-and-answer call between two nodes. |
| **Action** | A long-running task with progress reports, such as "drive to this point". |
| **Launch file** | A file that starts many nodes at once. |

## Read more

- ROS 2 concepts: <https://docs.ros.org/en/jazzy/Concepts/Basic.html>
- ROS 2 beginner tutorials: <https://docs.ros.org/en/jazzy/Tutorials.html>

---

Back to the [overview](README.md) | Next: [2. Build and run](02_build_and_run.md)
