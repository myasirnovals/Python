import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
from tkinter import colorchooser
from PIL import Image, ImageOps, ImageTk, ImageFilter

max_width = 750
max_height = 600


def add_image():
    global file_path
    file_path = filedialog.askopenfilename(initialdir='H://Downloads')

    if not file_path:
        return

    image = Image.open(file_path)
    image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

    canvas.config(width=image.width, height=image.height)

    image_tk = ImageTk.PhotoImage(image)
    canvas.image = image_tk
    canvas.delete('all')
    canvas.create_image(0, 0, image=image_tk, anchor='nw')


def draw(event):
    x1, y1 = (event.x - pen_size), (event.y - pen_size)
    x2, y2 = (event.x + pen_size), (event.y + pen_size)

    canvas.create_oval(x1, y1, x2, y2, fill=pen_color, outline='')


def change_color():
    global pen_color
    pen_color = colorchooser.askcolor(title='Select pen color')[1]


def change_size(size):
    global pen_size
    pen_size = size


def clear_canvas():
    canvas.delete('all')

    canvas.create_image(0, 0, image=canvas.image, anchor='nw')


def apply_filter(filter_name):
    if not file_path:
        messagebox.showerror('Error', 'No image selected.')
        return

    image = Image.open(file_path)

    image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

    if filter_name == 'Default':
        pass
    elif filter_name == 'Black and white':
        image = ImageOps.grayscale(image)
    elif filter_name == 'Blur':
        image = image.filter(ImageFilter.BLUR)
    elif filter_name == 'Emboss':
        image = image.filter(ImageFilter.EMBOSS)
    elif filter_name == 'Sharpen':
        image = image.filter(ImageFilter.SHARPEN)
    elif filter_name == 'Smooth':
        image = image.filter(ImageFilter.SMOOTH)

    canvas.delete('all')

    image_tk = ImageTk.PhotoImage(image)
    canvas.image = image_tk
    canvas.create_image(0, 0, image=image_tk, anchor='nw')


root = tk.Tk()
root.geometry('1000x600')
root.title('Image Drawing Tool')
root.config(bg='white')

pen_color = 'black'
pen_size = 5
file_path = ''

left_frame = tk.Frame(root, width=200, height=600, bg='white')
left_frame.pack(side='left', fill='y')

canvas = tk.Canvas(root, width=750, height=600, bg='gray')
canvas.pack()

image_btn = tk.Button(left_frame, text='Add Image', command=add_image, bg='white')
image_btn.pack(pady=15)

color_btn = tk.Button(left_frame, text='Change pe color', command=change_color, bg='white')
color_btn.pack(pady=5)

pen_size_frame = tk.Frame(left_frame, bg='white')
pen_size_frame.pack(pady=5)

pen_size_1 = tk.Radiobutton(pen_size_frame, text='small', value=3, command=lambda: change_size(2), bg='white')
pen_size_1.pack(side='left')

pen_size_2 = tk.Radiobutton(pen_size_frame, text='medium', value=5, command=lambda: change_size(5), bg='white')
pen_size_2.pack(side='left')
pen_size_2.select()

pen_size_3 = tk.Radiobutton(pen_size_frame, text='large', value=7, command=lambda: change_size(7), bg='white')
pen_size_3.pack(side='left')

clear_btn = tk.Button(left_frame, text='Clear', command=clear_canvas, bg='#ff9797')
clear_btn.pack(pady=10)

filter_label = tk.Label(left_frame, text='Select Filter', bg='white')
filter_label.pack()

filter_combobox = ttk.Combobox(left_frame, values=[
    'Default',
    'Black and white',
    'Blur',
    'Emboss',
    'Sharpen',
    'Smooth'
])
filter_combobox.pack()

filter_combobox.bind('<<ComboboxSelected>>', lambda event: apply_filter(filter_combobox.get()))

canvas.bind('<B1-Motion>', draw)

root.mainloop()
