from evdev import InputDevice, categorize, ecodes

try:
  gamepad0 = InputDevice('/dev/input/event0')
except:
  print("First Gamepad not connected")
  exit(1)

try:
  gamepad1 = InputDevice('/dev/input/event1')
except:
  print("Second Gamepad not connected")
  exit(1)

#################################
# gamepad_parse
#   parses a single event and returns a string that represents that event.
#################################
def gamepad_parse(event):

    # These are the key definitions for the generic USB joystick
    d_up = 544
    d_down = 545
    d_left = 546
    d_right = 547
    x = 288
    y = 291
    a = 289
    b = 290
    select = 296
    start = 297
    right_bumper = 293
    left_bumper = 292 

    # parse keypress events
    if event.type ==ecodes.EV_KEY:

      # 1 indicates key press.  0 indicates release
      if event.value == 1:
        if event.code == x:
          return("X")
        elif event.code == y:
          return("Y")
        elif event.code == a:
          return("A") 
        elif event.code == b: 
          return("B")
        elif event.code == select:
          return("Select")
        elif event.code == start:
          return("Start")
        elif event.code == right_bumper:
          return("Right-bumper")
        elif event.code == left_bumper:
          return("Left-bumper")

    # type 3 are absolute axis events.  The D-pad uses these.
    if event.type == 3:
      # code 0 are x axis events
      if (event.code == 0):
        if event.value == 0:
          return("D-left")
        if event.value == 255:
          return("D-right")
        # ignoring the "return to center" value of 127.

      # code 1 are y axis events
      if (event.code == 1):
        if event.value == 0:
          return("D-up")
        if event.value == 255:
          return("D-down")
  
################################################
# gamepad_read_blocking
#   This returns a single event from the gamepad...blocking until we get one.
################################################
def gamepad_read_blocking(gamepad):

  # This isn't perfect...since we're returning the first value we see, if there are
  #   "chorded" presses, we can miss events.
  for event in gamepad.read_loop():
    event_string = gamepad_parse(event)
    if (event_string != None):
      return gamepad_parse(event)

################################################
# gamepad_read_nonblocking
#   This returns a single event from the gamepad....
################################################
def gamepad_read_nonblocking(gamepad):

  # This isn't perfect...since we're returning the first value we see, if there are
  #   "chorded" presses, we can miss events.
  event = gamepad.read_one()
  if event == None:
    return "No Input"
  else:
    event_string = gamepad_parse(event)
    if (event_string != None):
      return gamepad_parse(event)
    else:
      return "No Input"

################################################
# gamepad0_read_nonblocking
#   This returns a single event from gamepad0
################################################
def gamepad0_read_nonblocking():
  return gamepad_read_nonblocking(gamepad0)

################################################
# gamepad1_read_nonblocking
#   This returns a single event from gamepad0
################################################
def gamepad1_read_nonblocking():
  return gamepad_read_nonblocking(gamepad1)

################################################
# gamepad0_read_locking
#   This returns a single event from gamepad0
################################################
def gamepad0_read_blocking():
  return gamepad_read_blocking(gamepad0)

################################################
# gamepad1_read_blocking
#   This returns a single event from gamepad1
################################################
def gamepad1_read_blocking():
  return gamepad_read_blocking(gamepad1)
