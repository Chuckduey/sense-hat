#!/usr/bin/python
# Chuck paint for Sense Hat 
# This program can draw any color on any square on a Sense Hat.  
# This can also save the picture in a text format that can be read back in.
# There is also a modification to tthis that can create the maze for the raspberrypi.or marble maze.
# This program makes heavy use of TKinter.
# nJoy   Chuck 

from Tkinter import *
from tkFont import Font
import Tkinter as tk
import tkFileDialog
import spidev
import smbus
import time
import os
from sense_hat import SenseHat

# File name to save and load from
file_name="chuck.sav"

hex_vals=('0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f')
paint = (0,0,0)
r = (255, 0, 0)
o = (255, 127, 0)
y = (255, 216, 0)  # The Green LEDS are a little too bright, turned it down.
g = (0, 255, 0)
b = (0, 0, 255)
i = (80, 0, 127)
v = (249, 0, 255)
e = (0, 0, 0)  # e stands for empty/black
w = (255, 255, 255)

def_colors=[r,o,y,g,b,i,e,w]

default_frame = [r,r,r,r,r,r,r,r,
                 r,e,e,e,e,e,e,r,
                 r,e,e,e,e,e,e,r,
                 r,e,e,e,e,e,e,r,
                 r,e,e,e,e,e,e,r,
                 r,e,e,e,e,e,e,r,
                 r,e,e,e,e,g,e,r,
                 r,r,r,r,r,r,r,r]

clear_pxls = [e,e,e,e,e,e,e,e,
              e,e,e,e,e,e,e,e,
              e,e,e,e,e,e,e,e,
              e,e,e,e,e,e,e,e,
              e,e,e,e,e,e,e,e,
              e,e,e,e,e,e,e,e,
              e,e,e,e,e,e,e,e,
              e,e,e,e,e,e,e,e]

sense = SenseHat()
sense.set_rotation(0)
sense.clear()

def color_but(z):  # Color button and LED array z is x,y input
   global buts,ya,sense_image,sense   
   zy=z[0]*8+z[1]
   zx = z[1]*8 +z[0]
   buts[zy]["bg"]=color_conv(paint)
   sense_image[zx]=paint
   sense.set_pixels(sense_image)

def color_conv(tupin):  # Convert from LED array tuple to Python hex color code
    cout = '#%02x%02x%02x' % (tupin[0], tupin[1], tupin[2])
    return(cout)

def update_paint():  # take spin box values and update numbers and current color settings.
    global paint,sp_val,paint_button,red_val,grn_val,blu_val
    rout = 16*int(sp_val[0].get(), 16) + int(sp_val[1].get(), 16)
    gout = 16*int(sp_val[2].get(), 16) + int(sp_val[3].get(), 16)
    bout = 16*int(sp_val[4].get(), 16) + int(sp_val[5].get(), 16)
    paint=(rout, gout, bout)
    paint_button["bg"]=color_conv(paint)
    red_val["text"]=str(rout)
    grn_val["text"]=str(gout)
    blu_val["text"]=str(bout)

def color_set(z):
    global paint, paint_button, var, red_val, grn_val, blu_val
    paint=def_colors[z]
    paint_button["bg"]=color_conv(paint)
    var[0].set(hex_vals[int(def_colors[z][0] // 16)])
    var[1].set(hex_vals[int(def_colors[z][0] % 16)])
    var[2].set(hex_vals[int(def_colors[z][1] // 16)])
    var[3].set(hex_vals[int(def_colors[z][1] % 16)])
    var[4].set(hex_vals[int(def_colors[z][2] // 16)])
    var[5].set(hex_vals[int(def_colors[z][2] % 16)])
    red_val["text"]=paint[0]
    grn_val["text"]=paint[1]
    blu_val["text"]=paint[2]

def get_int(str_in): # Input string of integers, output array of integers.
    ints_out = []
    ch_str=str_in.split()
    for e in ch_str:
       ints_out.append(int(e))
    return(ints_out)

def maze_convert():  # Convert picture to maze values if red > 128 = wall green > 128 goal, else blank
    global sense_image, buts, sense
    for i in range(64):
        pixel = sense_image[i]
        if pixel[0] > 128:
           pixel = (255, 0, 0) 
        elif pixel[1] > 128:
           pixel = (0, 255, 0)
        else:
           pixel = (0, 0, 0)

        sense_image[i] = pixel
        zy = (i // 8) + ( i % 8)*8
        buts[zy]["bg"]=color_conv(sense_image[i])
    sense.set_pixels(sense_image)

def load_file():
    global sense_image, buts, sense

    ifile=tkFileDialog.askopenfile(mode="r",initialfile=file_name)
    if ifile is None:
       return

    for i in range(64):

        instr = ifile.readline()
        sense_image[i] = get_int(instr)
        zy = (i // 8) + ( i % 8)*8
        buts[zy]["bg"]=color_conv(sense_image[i])

    ifile.close()
    print("loaded  ")
    sense.set_pixels(sense_image)

def save_file():
    global sense_image

    ifile=tkFileDialog.asksaveasfile(mode="w",initialfile=file_name)
    if ifile is None:
       return

    for i in range(64):
       for k in range(3):
          ifile.write(str(sense_image[i][k]) + "  ")
       ifile.write("\n")
    ifile.close()
    print("saved")

def set_buffer(set_of_pixels):
    global sense_image,buts,sense
    sense_image = set_of_pixels
    for i in range(64):
        zy = (i // 8) + ( i % 8)*8
        buts[zy]["bg"]=color_conv(sense_image[i])
    sense.set_pixels(sense_image)


root = Tk()
root.title("Chuck's Paint")
frame = Frame(root, bd=2, width=300, height=400, bg="green")
frame.grid(column=0, row=0)
sense_image=[]
# Make 8x8 button array
buts=[]
col_buts=[]
row_off = 0
col_off = 0
for x in range(8):
    for y in range(8):
        z=y*8+x
        b=Button(frame,bg=color_conv(paint), text=str(y*8+x), height=2, width=3,  command=lambda z=[x,y]: color_but(z))
        b.grid(row=y+col_off, column=x+row_off)
        buts.append(b)
        sense_image.append(paint)

# Make default pallet

for x in range(8):
        b=Button(frame,bg=color_conv(def_colors[x]),  height=2, width=3,  command=lambda z=x: color_set(z))
        b.grid(row=x+col_off, column=8+row_off, padx=8)
        col_buts.append(b)
# Make spin boxes for color settings with lables above and decimal values below
sp_val=[]
red_lab=Label(frame,text="Red", fg="red", font = Font(size=14))
red_lab.grid(row=8,column=0,columnspan=2,pady=3)
grn_lab=Label(frame,text="Green", fg="green", font = Font(size=14))
grn_lab.grid(row=8,column=3,columnspan=2,pady=3)
blu_lab=Label(frame,text="Blue", fg="blue", font = Font(size=14))
blu_lab.grid(row=8,column=6,columnspan=2,pady=3)
var=[StringVar(), StringVar(), StringVar(), StringVar(), StringVar(), StringVar()]
for x in range(6):
   th=Spinbox(frame,values=hex_vals, width=2, font=Font(size=14), textvariable=var[x],command=update_paint)
   th.grid(row=9,column=x+x//2,columnspan=1, pady=4)
   var[x].set('7')
   sp_val.append(th)

rout = 16*int(sp_val[0].get(), 16) + int(sp_val[1].get(), 16)
gout = 16*int(sp_val[2].get(), 16) + int(sp_val[3].get(), 16)
bout = 16*int(sp_val[4].get(), 16) + int(sp_val[5].get(), 16)
paint=(rout,gout,bout)

paint_button=Button(frame, bg=color_conv(paint),  height=2, width=3)
paint_button.grid(row=9, column=8)
red_val=Label(frame,text=str(rout), fg="red", font = Font(size=14))
red_val.grid(row=10,column=0,columnspan=2,pady=3)
grn_val=Label(frame,text=str(gout), fg="green", font = Font(size=14))
grn_val.grid(row=10,column=3,columnspan=2,pady=3)
blu_val=Label(frame,text=str(bout), fg="blue", font = Font(size=14))
blu_val.grid(row=10,column=6,columnspan=2,pady=3)

# Buttons for save, load and maze fuctions
load_button=Button(frame, bg="grey", text="load", font = Font(size=14), command=load_file)
load_button.grid(row=11,column=0, columnspan=2, pady = 5)
save_button=Button(frame, bg="grey", text="save", font = Font(size=14), command=save_file)
save_button.grid(row=11,column=2, columnspan=2, pady = 5)

maze_conv=Button(frame, bg="grey", text="mz conv", font = Font(size=14), command=maze_convert)
maze_conv.grid(row=11,column=4, columnspan=2, pady = 5)

maze_frm=Button(frame, bg="grey", text="frame", font = Font(size=14), command=lambda p=default_frame: set_buffer(p))
maze_frm.grid(row=11,column=6, columnspan=2, pady = 5)


clr_but=Button(frame, bg="grey", text="clr", font = Font(size=14), command=lambda p=clear_pxls: set_buffer(p))
clr_but.grid(row=11,column=8, columnspan=1, pady = 5)

sense.set_pixels(sense_image)
root.mainloop()
exit
