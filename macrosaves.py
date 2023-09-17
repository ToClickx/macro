import pickle # Used for saving macros
import tkinter as tk # Used for making the Top Level

# Used for keeping more code out of the main macro program before it is too late for coping tkinter templates
tkinter_template = '''import tkinter as tk

class GUI:
    def __init__(self):
        self.root = tk.Tk()

        self.root.mainloop()

if __name__ == "__main__":
    app = GUI()'''

simple_tkinter_template = '''import tkinter as tk

self.root = tk.Tk()

self.root.mainloop()'''

# Functions used for making more in detail templates
def tk_temp(buttons, labels, priority="buttons", oop=False):
    if not oop:
        template = "import tkinter as tk\n\nroot = tk.Tk()\n"
        
        if priority == "buttons":
            for name in buttons:
                button_stuff = f'\n{name} = tk.Button(root, text="{name}", command=lambda: print("{name}"))\n{name}.pack()\n'
                template += button_stuff

            for name, text in labels.items():
                label_stuff = f'\n{name} = tk.Label(root, text="{text}")\n{name}.pack()\n'
                template += label_stuff
        else:
            for name, text in labels.items():
                label_stuff = f'\n{name} = tk.Label(root, text="{text}")\n{name}.pack()\n'
                template += label_stuff


            for name in buttons:
                button_stuff = f'\n{name} = tk.Button(root, text="{name}", command=lambda: print("{name}"))\n{name}.pack()\n'
                template += button_stuff

        template += "\nroot.mainloop()"
    
    return template


# Note for reading uvars means user variable
# Loading all files
try:
    with open("savedmacros.pkl", "rb") as f:
        savedmacros = pickle.load(f)
except FileNotFoundError:
    savedmacros = {}

uvars = {}
try:
    with open("uvars.txt", "r") as f:
        uvars = eval(f.read())
except FileNotFoundError:
    pass

str_uvars = {}
try:
    with open("str_uvars.txt", "r") as f:
        str_uvars = eval(f.read())
except FileNotFoundError:
    pass

int_uvars = {}
try:
    with open("intuvars.txt", "r") as f:
        int_uvars = eval(f.read())
except FileNotFoundError:
    pass


# Save functions for uvars
def save_uvars():
    global uvars
    with open("uvars.txt", "w") as f:
        f.write(str(uvars))

def save_str_uvars():
    global str_uvars
    with open("struvars.txt", "w") as f:
        f.write(str(str_uvars))

def save_int_uvars():
    global int_uvars
    with open("intuvars.txt", "w") as f:
        f.write(str(int_uvars))


# Delete functions for uvars
def delete_uvar(uvar):
    global uvars
    if uvar in uvars:
        del uvars[uvar]
        save_uvars()

def delete_str_uvar(str_uvar):
    global str_uvars
    if str_uvar in str_uvars:
        del uvars[uvar]
        save_str_uvars()

def delete_int_uvar(int_uvar):
    global int_uvars
    if int_uvar in int_uvars:
        del int_uvars[int_uvar]
        save_int_uvars()


# Add function for uvars
def add_uvar(uvar, commands):
    global uvars
    uvars[uvar] = commands
    save_uvars()

def add_str_uvar(str_uvar, string):
    global str_uvars
    str_uvars[string] = commands
    save_str_uvars()

def add_int_uvar(int_uvar, integer):
    global int_uvars
    int_uvars[integer] = commands
    save_int_uvars()


# Function to save macros meant to be used externaly by the main macro program
def save_macro(macro_name, macro_content):
    savedmacros[macro_name] = macro_content
    with open("savedmacros.pkl", "wb") as f:
        pickle.dump(savedmacros, f)

# The main function for the GUI
def show_saved_macros():
    top = tk.Toplevel()
    top.title("Saved Macros")

    # Delete button to delete a macro
    def delete_macro(macro_name):
        if macro_name in savedmacros:
            del savedmacros[macro_name]
            update_display()

    # Searching for differant macros that were saved
    def search_macro():
        search_term = search_entry.get().lower()
        macro_text.configure(state=tk.NORMAL)
        macro_text.delete("1.0", tk.END)
        for name, macro in savedmacros.items():
            if search_term in name.lower():
                delete_button = tk.Button(top, text="Delete", command=lambda macro_name=name: delete_macro(macro_name))
                macro_text.window_create(tk.END, window=delete_button)
                macro_text.insert(tk.END, f"\n{name} macro: \n{macro}")
        macro_text.config(state=tk.DISABLED)
    
    # Function to update the display
    def update_display():
        macro_text.configure(state=tk.NORMAL)
        macro_text.delete("1.0", tk.END)
        for name, macro in savedmacros.items():
            delete_button = tk.Button(top, text="Delete", command=lambda macro_name=name: delete_macro(macro_name))
            macro_text.window_create(tk.END, window=delete_button)
            macro_text.insert(tk.END, f"\n{name} macro: \n{macro}")
        macro_text.configure(state=tk.DISABLED)

    # Making widgets
    macro_text = tk.Text(top, width=50, height=20)
    macro_text.pack()

    search_label = tk.Label(top, text="Search:")
    search_label.pack()

    search_entry = tk.Entry(top)
    search_entry.pack()

    search_button = tk.Button(top, text="Search", command=search_macro)
    search_button.pack()

    update_display()

    macro_text.configure(state=tk.DISABLED)  # Make the text widget read-only
