# import motor class
from gpiozero import Robot
import time

# create robot instnace using pins
robot = Robot(left=(12, 13), right=(20, 21)) # need to get actual pins from motors

while True:
  # drive motor using forward function
  robot.forward()
  print("Forward")
  time.sleep(3)

  # drive motor using backware function
  robot.backward()
  print("Backward")
  time.sleep(3)

  # try to reverse
  robot.reverse()
  print("Reverse")
  time.sleep(3)

  # try half speed
  robot.forward(0.5)
  print("Half speed forward.")
  time.sleep(3)

  # move right and left
  robot.right()
  print("Moving right.")
  time.sleep(3)

  #robot.left()
  print("Moving left.")
  time.sleep(3)

  # stop robot
  robot.stop()
  print("Stopping now.")
  time.sleep(3)
