#################################################
# cycles.py - tron style light cycle game
#
# Two players (green and blue).
# input from dual gamepads
# Lose when you hit something.
################################################# 

import time
from datetime import datetime

import random

from dual_gamepad import gamepad0_read_nonblocking, gamepad1_read_nonblocking

###################################
# Graphics imports, constants and structures
###################################
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageDraw

# this is the size of ONE of our matrixes. 
matrix_rows = 32 
matrix_columns = 32 

# how many matrixes stacked horizontally and vertically 
matrix_horizontal = 5 
matrix_vertical = 3

total_rows = matrix_rows * matrix_vertical
total_columns = matrix_columns * matrix_horizontal

options = RGBMatrixOptions()
options.rows = matrix_rows 
options.cols = matrix_columns 
options.chain_length = matrix_horizontal
options.parallel = matrix_vertical 
options.hardware_mapping = 'regular'  
#options.gpio_slowdown = 2

matrix = RGBMatrix(options = options)

###################################################
# Global data
###################################################

black = (0,0,0)
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)

wall_color = red 

# All player positions are the top-left corner of our player icon.

# start positions:  
#    p1 at the top middle going down, p2 at bottom middle going up.
p1_start_x = total_columns / 2
p1_start_y = 5
p2_start_x = p1_start_x
p2_start_y = total_rows - p1_start_y

player1 = [p1_start_x,p1_start_y]
player2 = [p2_start_x,p2_start_y]

# each cycle is 5 pixels. 
cycle_size = 5

# The collision matrix is a 2d matrix of our full playfield size.
# Zero means there's nothing in that slot.
# One means you can't move there.
collision = []
#collision = [[0] * total_rows for i in range(total_columns)]

speed_delay = .1

###################################
# reset_collision()
###################################
def reset_collision():

  # The collision matrix is a 2d matrix of our full playfield size.
  # Zero means there's nothing in that slot.
  # One means you can't move there.
  global collision

  del collision[:]
  collision = [[0] * total_rows for i in range(total_columns)]

###################################
# init_walls()
###################################
def init_walls():
  global collision
  global wall_color

  #top and bottom boarders
  for x in range(total_columns):
    collision[x][0] = 1
    collision[x][total_rows-1] = 1

  #left and right boarders
  for y in range(total_rows):
    collision[0][y]= 1
    collision[total_columns-1][y] = 1

  #now draw the box
  temp_image = Image.new("RGB", (total_columns, total_rows))
  temp_draw = ImageDraw.Draw(temp_image)
  temp_draw.rectangle((0,0,total_columns-1,total_rows-1), outline=wall_color)
  matrix.SetImage(temp_image, 0,0)

###################################
# init_players
###################################
def init_players():
  global collision
  global p1_start_x
  global p1_start_y
  global p2_start_x
  global p2_start_y
  global p1_color
  global p2_color
  global player1
  global player2

  player1 = [p1_start_x,p1_start_y]
  player2 = [p2_start_x,p2_start_y]

'''
  temp_image = Image.new("RGB", (1,1))
  temp_draw = ImageDraw.Draw(temp_image)
  temp_draw.rectangle((0,0,0,0), outline=p1_color, fill=p1_color)
  matrix.SetImage(temp_image, p1_start_x, p1_start_y)
  temp_draw.rectangle((0,0,0,0), outline=p2_color, fill=p2_color)
  matrix.SetImage(temp_image, p2_start_x, p2_start_y)
'''

####################################################
# show_crash() 
####################################################
def show_crash(crash_x, crash_y):
  
  crash_color = (255,0,0)
  crash_fill = (255,255,255)
  for crashloop in range(3,13,2):
    ellipse_offset = (crashloop-1)/2
    temp_image = Image.new("RGB", (crashloop,crashloop))
    temp_draw = ImageDraw.Draw(temp_image)
    temp_draw.ellipse((0,0,crashloop-1,crashloop-1), outline=crash_color, fill=crash_fill)
    matrix.SetImage(temp_image, crash_x-ellipse_offset,crash_y-ellipse_offset)
    time.sleep(.15)

  time.sleep(1)

###################################
#  display_text()
###################################
def display_text(my_text, text_color, delay):
    temp_image = Image.new("RGB", (total_columns, total_rows))
    temp_draw = ImageDraw.Draw(temp_image)
    temp_draw.text((0,0),my_text, fill=text_color)
    matrix.SetImage(temp_image,0,0)
    time.sleep(delay)


###################################
# collision_check 
#    Note x and y are the postion *before* moving.
###################################
def collision_check(x, y, dir):
  global collision
  global cycle_size

  if dir == "up":
    # need to check the middle three pixels above our icon reference
    if (collision[x+1][y-1] == 1) or (collision[x+2][y-1] == 1) or (collision[x+3][y-1] == 1):
      return True
    else:
      return False

  if dir == "down":
    # need to check middle three pixels below our icon reference
    if (collision[x+1][y+cycle_size] == 1) or (collision[x+2][y+cycle_size] == 1) or (collision[x+3][y+cycle_size] == 1):
      return True
    else: 
      return False

  if dir == "right":
    # need to check middle three pixels to the right of our reference
    if (collision[x+cycle_size][y+1] == 1) or (collision[x+cycle_size][y+2] == 1) or (collision[x+cycle_size][y+3] == 1):
      return True
    else:
      return False
    
  if dir == "left":
    # need to check middle three pixels to the left of our reference
    if (collision[x-1][y+1] == 1) or (collision[x-1][y+2] == 1) or (collision[x-1][y+3] == 1):
      return True
    else:
      return False

  # if we got here, someone passed an invalid direciton!!!
  print("Invalid dir in collision_check")
  exit(0)
 
###################################
# calc_wall_spot 
#   This function takes a given player's x and y postion (the top-left corner
#   of their icon) and their direction, and calclualtes the absolute position
#   of the resultant new "wall" block, returned as a tuple.
###################################
def calc_wall_spot(x,y,dir):
  global cycle_size
  
  if dir == "up":
    wall_x = x+2
    wall_y = y+cycle_size-1
  elif dir == "down":
    wall_x = x+2
    wall_y = y
  elif dir == "left":
    wall_x = x
    wall_y = y+2
  elif dir == "right":
    wall_x = x+cycle_size-1
    wall_y = y+2
  else:
    print("Invalid dir in calc_wall_spot")
    exit(0)
    
  return( (wall_x,wall_y) )
  
###################################
# play_game 
###################################
def play_game():
  global cycle_size

  display_text("Get Ready",red, 3)
  display_text("3",red,1)
  display_text("2",red,1)
  display_text("1",red,1)
  display_text("GO!!!",red,1)

  reset_collision()
  init_walls()
  init_players()
  
  wheel_color = (0x2F,0x4F,0x4F)
  p1_body_color = (0,0x64,0)
  p2_body_color = (0,0,0x64)

  p1_image = Image.new("RGB", (cycle_size,cycle_size))
  p1_draw = ImageDraw.Draw(p1_image)
  p1_draw.rectangle( (1,0,1,1), outline = wheel_color )
  p1_draw.rectangle( (3,0,3,1), outline = wheel_color)
  p1_draw.rectangle( (1,3,1,4), outline = wheel_color)
  p1_draw.rectangle( (3,3,3,4), outline = wheel_color)
  p1_draw.rectangle( (2,0,2,4), outline = p1_body_color)
  p1_dir = "down"

  p2_image = Image.new("RGB", (cycle_size,cycle_size))
  p2_draw = ImageDraw.Draw(p2_image)
  p2_draw.rectangle( (1,0,1,1), outline = wheel_color )
  p2_draw.rectangle( (3,0,3,1), outline = wheel_color)
  p2_draw.rectangle( (1,3,1,4), outline = wheel_color)
  p2_draw.rectangle( (3,3,3,4), outline = wheel_color)
  p2_draw.rectangle( (2,0,2,4), outline = p2_body_color)
  p2_dir = "up"

  p1_wall_color = (0,255,0)
  p2_wall_color = (0,0,255)

  p1_wall_image = Image.new("RGB", (1,1))
  p1_wall_draw = ImageDraw.Draw(p1_wall_image)
  p1_wall_draw.rectangle((0,0,1,1), outline = p1_wall_color)

  p2_wall_image = Image.new("RGB", (1,1))
  p2_wall_draw = ImageDraw.Draw(p2_wall_image)
  p1_wall_draw.rectangle((0,0,1,1), outline = p2_wall_color)

  cycle_erase_image = Image.new("RGB", (cycle_size, cycle_size))
  cycle_erase_draw = ImageDraw.Draw(cycle_erase_image)
  cycle_erase_draw.rectangle((0,0,cycle_size-1,cycle_size-1),outline=(0,0,0),fill=(0,0,0))

  p1_crash = False
  p2_crash = False

  last_update_time = datetime.now()

  while True:

    dir_pressed = False
    current_time = datetime.now()
    deltaT = current_time - last_update_time

    # check for player 1 dir changes, but don't let them back into themselves
    p1_input = gamepad0_read_nonblocking()
    if (p1_input == "D-up") & (p1_dir != "down"):
      p1_dir = "up" 
      dir_pressed = True
    if (p1_input == "D-down") & (p1_dir != "up"):
      p1_dir = "down" 
      dir_pressed = True
    if (p1_input == "D-left") & (p1_dir != "right"):
      p1_dir = "left" 
      dir_pressed = True
    if (p1_input == "D-right") & (p1_dir != "left"):
      p1_dir = "right" 
      dir_pressed = True
   
    # check for player 2 dir changes, but don't let them back into themselves
    p2_input = gamepad1_read_nonblocking()
    if (p2_input == "D-up") & (p2_dir != "down"):
      p2_dir = "up" 
      dir_pressed = True
    if (p2_input == "D-down") & (p2_dir != "up"):
      p2_dir = "down" 
      dir_pressed = True
    if (p2_input == "D-left") & (p2_dir != "right"):
      p2_dir = "left" 
      dir_pressed = True
    if (p2_input == "D-right") & (p2_dir != "left"):
      p2_dir = "right" 
      dir_pressed = True

    # Should probably use positive logic here to update the current direciton,
    # but instead, I'm using the continue construct.
    if ((deltaT.total_seconds() < speed_delay) & (dir_pressed == False)):
      continue

    last_update_time = current_time

    # The engine!
    # If both p1 and p2 are going to hit something, it's a draw.
    # If only p1 or p2 hits something, it's a win for the other one.
    # if neither are going to hit anything, update the collision matrix 
    # and add the new "dot"

    #figure out next spot for p1
    p1_new_x = player1[0]
    p1_new_y = player1[1]
    if (p1_dir == "up"):
      p1_new_y = p1_new_y - 1
    if (p1_dir == "down"):
      p1_new_y = p1_new_y + 1
    if (p1_dir == "left"):
      p1_new_x = p1_new_x - 1
    if (p1_dir == "right"):
      p1_new_x = p1_new_x + 1

    # will the new spot for p1 cause a crash?
    if (collision_check(player1[0],player1[1],p1_dir)): 
      print "Player 1 crashes!!!"
      p1_crash = True
    else:
      # erase the old icon
      matrix.SetImage(cycle_erase_image,player1[0], player1[1])
  
      # where does the new wall go?
      new_wall = calc_wall_spot(player1[0],player1[1],p1_dir)
     
      # update the collision matrix with our new wall spot
      collision[new_wall[0]][new_wall[1]] = 1
  
      # draw that new wall spot
      matrix.SetImage(p1_wall_image,new_wall[0],new_wall[1])
  
      # draw the new cycle, rotating properly for the new direction
      if p1_dir == "up":
        rotated_image = p1_image
      elif p1_dir == "down":
        #not stricly necessary yet, but code present in case we change our icon.
        rotated_image = p1_image.rotate(180)
      elif p1_dir == "left":
        rotated_image = p1_image.rotate(270)
      elif p1_dir == "right":
        rotated_image = p1.image.rotate(90)
      else:
        print("bad dir in rotate p1")
        exit(0)
      matrix.SetImage(p1_image, p1_new_x, p1_new_y)

      # finally, update our player position.
      player1[0] = p1_new_x
      player1[1] = p1_new_y

    #figure out next spot for p2
    p2_new_x = player2[0]
    p2_new_y = player2[1]
    if (p2_dir == "up"):
      p2_new_y = p2_new_y - 1
    if (p2_dir == "down"):
      p2_new_y = p2_new_y + 1
    if (p2_dir == "left"):
      p2_new_x = p2_new_x - 1
    if (p2_dir == "right"):
      p2_new_x = p2_new_x + 1

    # will the new spot for p2 cause a crash?
    if (collision_check(player2[0],player2[1],p2_dir)): 
      print "Player 2 crashes!!!"
      p2_crash = True
    else:
      # erase the old icon
      matrix.SetImage(cycle_erase_image,player2[0], player2[1])
  
      # where does the new wall go?
      new_wall = calc_wall_spot(player2[0],player2[1],p2_dir)
     
      # update the collision matrix with our new wall spot
      collision[new_wall[0]][new_wall[1]] = 1
  
      # draw that new wall spot
      matrix.SetImage(p2_wall_image,new_wall[0],new_wall[1])
  
      # draw the new cycle, rotating properly for the new direction
      if p2_dir == "up":
        rotated_image = p2_image
      elif p2_dir == "down":
        #not stricly necessary yet, but code present in case we change our icon.
        rotated_image = p2_image.rotate(180)
      elif p2_dir == "left":
        rotated_image = p2_image.rotate(270)
      elif p2_dir == "right":
        rotated_image = p2.image.rotate(90)
      else:
        print("bad dir in rotate p2")
        exit(0)
      matrix.SetImage(p2_image, p2_new_x, p2_new_y)

      # finally, update our player position.
      player2[0] = p2_new_x
      player2[1] = p2_new_y

    if (p1_crash & p2_crash):
      print "Tie game!!!"
      show_crash(p1_new_x,p1_new_y)
      display_text("TIE!", red, 3)
      break;

    if (p1_crash):
      print "Player 2 wins!"
      show_crash(p1_new_x,p1_new_y)
      display_text("Player 2\nWins!",blue,3)
      break;

    if (p2_crash):
      print "Player 1 wins!"
      show_crash(p2_new_x,p2_new_y)
      display_text("Player 1\nWins!",green,3)
      break;

    time.sleep(speed_delay)

###################################
# Main loop 
###################################
while True:

  # Wait to start until one of the two players hits a key
  wait = True
  display_text("Press Any\nButton to\nStart", green, 3)
  while wait:
    input=gamepad0_read_nonblocking()
    if input != "No Input":
      wait = False
    input=gamepad1_read_nonblocking()
    if input != "No Input":
      wait = False 

  play_game()
