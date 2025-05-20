# CS561 - Independent Study 
Patrick Sun

## Literature Review
### Finding our Drone
We started the Independent Study with very little direction besides the idea that we wanted to do 
something with drones. Much of the initial research was spent on figuring out which kind of drones
to purchase and what software to use to control them. Several different approaches came up, including 
autopilot software such as [ArduPilot](https://github.com/ArduPilot/ardupilot) and using an onboard
Arduino or Raspberry Pi.

We wanted to focus more on the software side of programming drones, and thus, didn't want to delve into
the world of assembling our drones. Upon more discussion, we decided to get the **DJI Tello** due to its
affordability and support for programming via Python wrappers such as 
[DJITelloPy](https://github.com/damiafuentes/DJITelloPy).

### Deciding on a Research Project
The bulk of the next couple of weeks following obtaining our drones went towards deciding what projects 
would be interesting enough to work on, but also feasible with the limited hardware and software capabilities
of the DJI Tello. Throughout this process, we came up with many ideas that each were met with some obstacle that 
prevented us from progressing further. 

#### 1. Drone Autonomy
Our initial idea was to use a combination of machine learning and/or computer vision to train our drones to 
perform object evasion and autonomous path-finding. Libraries such as [OpenCV](https://opencv.org/) 
and [YOLO](https://docs.ultralytics.com/) made this seem possible but we ended up giving up on the idea
due to the Tello's lack of onboard sensors that would allow it to detect and avoid objects. On top of that,
we were only able to access the Tello's front facing camera, making it hard to properly implement things such as
path-finding.

It is worth noting that projects such as [(Tello) Indoor Autonomous Drone Navigation using monocamera and openVSLAM in a known map (ROS)](https://www.youtube.com/watch?v=cx2MV2OOG7U) and [Autonomous Drone Scanning and Mapping
](https://github.com/waseemtannous/Autonomous-Drone-Scanning-and-Mapping) demonstrate that the idea is not impossible
by using [SLAM](https://www.mathworks.com/discovery/slam.html).

#### 2. Drone WIFI Probing
A search and rescue inspired project where we sought to try and use the Tello's WIFI capabilities to act as
almost an access point to discover local devices. We believed that this was an interesting topic to explore
due to its applications in locating disaster victims by using their mobile devices.

This idea came to an end when we failed to find any way of capturing the beaconing and probing packets
from the Tello (maybe protected by manufacturer).

#### 3. Drone Object Finder
An idea that would use YOLO to perform object detection and find specific objects. The application of this
was more for a common pain point of losing items such as keys. However, because this required a degree of 
drone autonomy that we couldn't quite figure out, we decided not to follow through with this.


#### 4. Gesture Control
There were a number of other ideas that we went through in addition to the ones above, but eventually, we settled on 
gesture control because of how libraries such as [MediaPipe](https://github.com/google-ai-edge/mediapipe) exist
for hand gesture recognition.

On top of that, we found a handful of projects such as [Tello Face Follower](https://github.com/youngsoul/tello-sandbox)
and [Computer Vision with Tello](https://github.com/mrsojourn/computer_vision_with_tello_drone?tab=readme-ov-file) that
do similar things and thus made it much easier to learn how to implement gesture controls with the Tello.

## Implementing Gesture Controls
Much of the end result and code was written with reference to [Computer Vision with Tello](https://github.com/mrsojourn/computer_vision_with_tello_drone?tab=readme-ov-file), and so the overall logic of the program was not very difficult. 

The program is split up into effectively 2 parts: 
1. The detector class that uses mediapipe to classify hand gestures based on which fingers are up
2. The main program that sends the commands to the tello based on which gestures are detected



