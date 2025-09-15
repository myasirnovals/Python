import tkinter as tk
import pyshorteners

def shorten_url():
    shortener_obj = pyshorteners.Shortener()

    long_url = long_url_entry.get()

    try:
        short_url = shortener_obj.tinyurl.short(long_url)
        short_url_entry.delete(0, tk.END)
        short_url_entry.insert(0, short_url)
    except Exception as e:
        short_url_entry.delete(0, tk.END)
        short_url_entry.insert(0, f'Error: {str(e)}')

root = tk.Tk()

root.title('URL Shortener')
root.geometry('300x300')

long_url_label = tk.Label(root, text='Enter your long URL here...')
long_url_label.pack()

long_url_entry = tk.Entry(root)
long_url_entry.pack()

short_url_label = tk.Label(root, text='Shortened URL: ')
short_url_label.pack()

short_url_entry = tk.Entry(root)
short_url_entry.pack()

shorten_btn = tk.Button(root, text='Shorten URL', command=shorten_url)
shorten_btn.pack()

root.mainloop()