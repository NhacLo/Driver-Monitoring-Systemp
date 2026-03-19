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

cd Code_Detect_Face
set ROS_DOMAIN_ID=30
python ver_test.py
```
### Step 2: initialization server.

Run the CARLA server:
```bash
 CarlaUE4.exe
```
Connect to server on Ubuntu:
```bash
source ~/carla-ros-bridge/install/setup.bash
ros2 launch carla_ros_bridge carla_ros_bridge.launch.py synchronous_mode:=Fasle  host:=172.27.224.1 passive:=true
```
### Step 3: Control client on server by ROS-Bridge.
Open: 
Terminal Unbuntu.
- Run:
  ```bash
  source /opt/ros/humble/setup.bash
  export ROS_DOMAIN_ID=30
  cd ~/carla-ros-bridge/src/ros-bridge/Code_Control_Client
  python3 control_client_carla.py
  ```
  
