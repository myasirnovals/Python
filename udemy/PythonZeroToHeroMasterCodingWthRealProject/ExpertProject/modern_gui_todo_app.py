import customtkinter as ctk

def add_todo():
    todo = entry.get()
    label = ctk.CTkLabel(scrollable_frame, text=todo)
    label.pack()
    entry.delete(0, ctk.END)

root = ctk.CTk()

root.geometry('1000x720')
root.title('Todo App')

title_label = ctk.CTkLabel(root, text='Daily Task', font=ctk.CTkFont(size=20, weight='bold'))
title_label.pack(padx=10, pady=(40, 20))

scrollable_frame = ctk.CTkScrollableFrame(root, width=700, height=400)
scrollable_frame.pack()

entry = ctk.CTkEntry(scrollable_frame, placeholder_text='Enter your task here...', width=600)
entry.pack(pady=10, fill='x')

add_button = ctk.CTkButton(root, text='Add Task', width=500, command=add_todo)
add_button.pack(pady=30)

root.mainloop()
