# Driver Focus and Drowsiness Detection

## Project Overview
The main goal of this project is to detect driver lack of focus and drowsiness during driving simulation.

This system is built using:
- **CARLA 0.9.16**
- **CARLA Python API**
- **ROS 2**
- **Ubuntu WSL**
- **Windows CMD / Terminal**

---

## Requirements
Before running the project, make sure the following software is installed:

- [CARLA 0.9.16](https://carla.org/)
- CARLA Python API
- ROS 2
- Ubuntu WSL
- Python environment for the detection program

---

## How to Run the Project

### Step 1: Run the detection program on Windows
Open:
- **Windows CMD / Terminal**
- **Ubuntu WSL Terminal**

In the **Windows terminal**, run:

```bash
cd C:\pixi_ws
pixi shell
call C:\pixi_ws\ros2-windows\local_setup.bat
