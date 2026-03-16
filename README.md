In this project. The main goal is detect driver lack of focus and dozing off. 
To run code : 
   - Need : Dowload Carla 0.9.16 + API , ROS2
How to run code :
   Step1 : Open Terminal of CMD on windown.
        Open Terminal of Ubuntu WSL
           - At terminal of Windown : 
                      - cd C:\pixi_ws
                        pixi shell
                      - call C:\pixi_ws\ros2-windows\local_setup.bat
                   -> Tao moi truong ROS2 tren windown.
                      - cd ... on folder of program detect.
                      - set ROS_DOMAIN_ID=30
                      - python detect_function_test.py
     Step2 : 
      - Run server carla: CarLaEU4.exe.
      - Open another terminal Ubuntu : 
                - run : source ~/carla-ros-bridge/install/setup.bash -> tao moi truong ros_bridge
                - run : ros2 launch carla_ros_bridge carla_ros_bridge.launch.py synchronous_mode:=Fasle  host:=172.27.224.1 passive:=true
     Step3 :
       - Open termianl of Ubuntu:
                 - run : source /opt/ros/humble/setup.bash -> tao moi truong ros2 cho ubuntu
                 - run : export ROS_DOMAIN_ID=30
                 - run : cd ~/carla-ros-bridge/src/ros-bridge/... go on folder have file progame control client
                 - run : python3 ..... --host 172.27.224.1 --agent Basic --loop 
  
     
