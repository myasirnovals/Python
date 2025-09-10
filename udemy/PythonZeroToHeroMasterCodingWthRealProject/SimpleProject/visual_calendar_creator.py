from tkinter import *

import calendar


def show_calendar():
    gui = Tk()
    gui.config(background='grey')
    gui.title('calendar for year')
    gui.geometry('550x600')
    year = int(year_field.get())
    gui_content = calendar.calendar(year)
    calYear = Label(gui, text=gui_content)
    calYear.grid(row=5, column=1, padx=20)
    gui.mainloop()


if __name__ == '__main__':
    new = Tk()
    new.config(background='grey')
    new.title('Calendar')
    new.geometry('250x140')
    cal = Label(new, text='Calendar', bg='grey', font=('Courier', 28, 'bold'))
    year = Label(new, text='show calendar', bg='dark grey')
    year_field = Entry(new)
    button = Button(new, text='show calendar', fg='Black', bg='Blue', command=show_calendar)
    exit_button = Button(new, text='Exit', fg='Black', bg='Red', command=new.destroy)

    cal.grid(row=1, column=1)
    year.grid(row=2, column=1)
    year_field.grid(row=3, column=1)
    button.grid(row=4, column=1)
    exit_button.grid(row=5, column=1)
    new.mainloop()
