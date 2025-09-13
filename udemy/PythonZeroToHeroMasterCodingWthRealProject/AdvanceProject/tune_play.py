from tkinter.filedialog import askdirectory

import pygame
import tkinter as tkr
import os

music_player = tkr.Tk()
music_player.title('My Music Player')
music_player.geometry('450x350')

directory = askdirectory()
os.chdir(directory)

song_list = os.listdir()
play_list = tkr.Listbox(music_player, font=('Helvetica', 12, 'bold'), bg='yellow', selectmode=tkr.SINGLE)

for item in song_list:
    pos = 0
    play_list.insert(pos, item)
    pos += 1

pygame.init()
pygame.mixer.init()


def play():
    pygame.mixer.music.load(play_list.get(tkr.ACTIVE))
    var.set(play_list.get(tkr.ACTIVE))

    pygame.mixer.music.play()


def stop():
    pygame.mixer.music.stop()


def pause():
    pygame.mixer.music.pause()


def resume():
    pygame.mixer.music.unpause()


btn1 = tkr.Button(
    music_player,
    width=5,
    height=3,
    font=('Helvetica', 12, 'bold'),
    text='play',
    command=play,
    bg='blue',
    fg='white'
)

btn2 = tkr.Button(
    music_player,
    width=5,
    height=3,
    font=('Helvetica', 12, 'bold'),
    text='stop',
    command=stop,
    bg='red',
    fg='white'
)

btn3 = tkr.Button(
    music_player,
    width=5,
    height=3,
    font=('Helvetica', 12, 'bold'),
    text='pause',
    command=pause,
    bg='purple',
    fg='white'
)

btn4 = tkr.Button(
    music_player,
    width=5,
    height=3,
    font=('Helvetica', 12, 'bold'),
    text='resume',
    command=resume,
    bg='orange',
    fg='white'
)

var = tkr.StringVar()
song_title = tkr.Label(music_player, font=('Helvetica', 12, 'bold'), textvariable=var)

song_title.pack()
btn1.pack(fill='x')
btn2.pack(fill='x')
btn3.pack(fill='x')
btn4.pack(fill='x')

play_list.pack(fill='both', expand=True)

music_player.mainloop()
