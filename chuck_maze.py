# This is a modified version of the raspberrypi.org marble maze.  
# This reads in a file that has a maze that can be created by th chuck_pain program.
# nJoy   Chuck

from sense_hat import SenseHat

from time import sleep
from Tkinter import *
from tkFont import Font
import Tkinter as tk
import tkFileDialog

# File name to save and load from
file_name="maze.sav"

sense = SenseHat()
sense.clear()


r = (255,0,0)
g = (0,255,0)
b = (0,0,0)
w = (255,255,255)

x = 1
y = 1

def get_int(str_in): # Input string of integers, output tuple of integers.
    ints_out = []
    ch_str=str_in.split()
    for e in ch_str:
       ints_out.append(int(e))
    return(tuple(ints_out))

root = Tk()  # Get a TK window
ifile=tkFileDialog.askopenfile(mode="r",initialfile=file_name)
if ifile is None:
     maze = [[r,r,r,r,r,r,r,r],
             [r,b,b,b,b,b,b,r],
             [r,r,b,r,b,b,b,r],
             [r,b,b,r,r,r,r,r],
             [r,b,b,b,b,b,b,r],
             [r,r,b,r,r,r,b,r],
             [r,b,b,r,b,b,b,r],
             [r,r,r,r,g,r,r,r]]

else:
    maze = [[r,r,r,r,r,r,r,r],
            [r,b,b,b,b,b,b,r],
            [r,r,b,r,b,b,b,r],
            [r,b,b,r,r,r,r,r],
            [r,b,b,b,b,b,b,r],
            [r,r,b,r,r,r,b,r],
            [r,b,b,r,b,b,b,r],
            [r,r,r,r,g,r,r,r]]
    for y in range(8):
        for x in range(8):
            instr = ifile.readline()
            maze[y][x] = get_int(instr)
root.destroy()  # Close the window

x = 1
y = 1
def move_marble(pitch,roll,x,y):
    new_x = x
    new_y = y
    if 1 < pitch < 179 and x != 0:
        new_x -= 1
    elif 359 > pitch > 179 and x != 7 :
        new_x += 1
    if 1 < roll < 179 and y != 7:
        new_y += 1
    elif 359 > roll > 179 and y != 0 :
        new_y -= 1
    x,y = check_wall(x,y,new_x,new_y)
    return x,y

def check_wall(x,y,new_x,new_y):
    if maze[new_y][new_x] != r:
        return new_x, new_y
    elif maze[new_y][x] != r:
        return x, new_y
    elif maze[y][new_x] != r:
        return new_x, y
    return x,y

game_over = False

def check_win(x,y):
    global game_over
    if maze[y][x] == g:
        game_over = True
        sense.show_message('You Win')

while not game_over:
    pitch = sense.get_orientation()['pitch']
    roll = sense.get_orientation()['roll']
    x,y = move_marble(pitch,roll,x,y)
    check_win(x,y)
    maze[y][x] = w
    sense.set_pixels(sum(maze,[]))
    sleep(0.05)
    maze[y][x] = b
exit()
