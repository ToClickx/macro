#Imports

# Tkinter message box for advanced error reports
from tkinter import messagebox
# Tkinter for the GUI
import tkinter as tk
# Threading for multiple task at the same time
import threading
# Keyboard used for keys and keyboard based commands
import keyboard
# Used for mouse related commands
import pyautogui
pyautogui.PAUSE = 0.01
# Used to acuratly tell time for the duration of the hold key function
import time
# Used for the mouse controller in the move command
import pynput.mouse
# Re for dettecting double quotes
import re
# Used for saving macros
import macrosaves
# Used for icon
from PIL import Image, ImageTk
# Used for going back to home launcher
import subprocess
# Used for the coordinates window
import pyperclip

# This is the class for the cordinate window
class CordsWindow:
    def __init__(self, rooot):
        self.root = tk.Toplevel(rooot)
        self.root.title("Get Coordinates")
        self.root.geometry("350x250")

        self.ico = Image.open('xycoordinate.ico')
        self.photo = ImageTk.PhotoImage(self.ico)
        self.root.wm_iconphoto(False, self.photo)

        keyboard.add_hotkey("alt", self.update_cords)

        self.copy = True
        self.x = 0
        self.y = 0

        self.cords_display = tk.Label(self.root, text=f"The coordinates are ({self.x}, {self.y})") 
        self.cords_display.pack()

        self.copy_button = tk.Button(self.root, text="Copy", command=self.copy_text)
        self.copy_button.pack()

        self.update_cords_button = tk.Label(self.root, text="Press alt to get coordinates")
        self.update_cords_button.pack()

        self.auto_copy_label = tk.Label(self.root, text=f"Auto copying is {self.copy}")
        self.auto_copy_label.pack()

        self.auto_copy_toggle = tk.Button(self.root, text=f"Toggle auto copy", command=self.toggle_copy)
        self.auto_copy_toggle.pack()

        self.prefix_label = tk.Label(self.root, text="Enter prefix below:")
        self.prefix_label.pack()

        self.prefix_box = tk.Entry(self.root)
        self.prefix_box.pack()

        self.suffix_label = tk.Label(self.root, text="Enter suffix below:")
        self.suffix_label.pack()

        self.suffix_box = tk.Entry(self.root)
        self.suffix_box.pack()

    def toggle_copy(self):
        if self.copy:
            self.copy = False
            self.auto_copy_label.config(text=f"Copying is {self.copy}")
        else:
            self.copy = True
            self.auto_copy_label.config(text=f"Copying is {self.copy}")

    def copy_text(self):
        prefix = self.prefix_box.get()
        suffix = self.suffix_box.get()
        word = str(prefix)+str(self.x)+" "+str(self.y)+str(suffix)
        pyperclip.copy(word)

    def update_cords(self, event=None):
        self.x, self.y = pyautogui.position()
        self.cords_display.config(text=f"The coordinates are ({self.x}, {self.y})")
        if self.copy:
            self.copy_text()

# The main class for the macro
class MacroApp:

    # BIG NOTE FOR ME DELETE BUTTONS ARE ABOVE

    # On Start
    def __init__(self, root):
        self.root = root
        self.root.title("Macro Application")
        self.root.geometry("625x450")

        self.ico = Image.open('mouse_cursor.ico')
        self.photo = ImageTk.PhotoImage(self.ico)
        self.root.wm_iconphoto(False, self.photo)

        self.root.protocol("WM_DELETE_WINDOW", self.root.quit())
        self.root.resizable(False, False)
        self.loop_var = tk.IntVar()
        self.advanced_errorss = tk.IntVar()
        # Amount of frames in movement
        # Btw I zoomed in
        self.steps = 1
        # The mouse controller to do stuff with the mouse
        self.mouse = pynput.mouse.Controller()
        # A bool to determine if the program should loop
        self.is_looping = False
        # A bool to store the run state of the macro
        self.is_running = False
        # A bool that determins if errors are presented to the user GUI
        self.advanced_errors = False
        # Defining listbox
        self.listbox = None
        # Dictionary where user command based user variables are stored
        self.uvars = macrosaves.uvars
        # Dictionary where user strings are stored
        self.ustrings = macrosaves.str_uvars
        # Dictionary where user numbers are stored
        self.unums = macrosaves.int_uvars
        # List of keys
        self.keys = ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', ':', "'", 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '<', '.', '>', '/', '?', '1', '!', '2', '@', '3', '#', '4', '$', '5', '%', '6', '^', '7', '&', '8', '*', '9', '(', '0', ')', '-', '_', '=', '+', 'enter', 'shift', 'ctrl', 'alt', '`', '~', 'escape']
        # Idk if this is even still used but determins the delay between inputs in the hold key function
        self.holdspeed = 0.045
        # Variable to determin if the time of a task is given
        self.give_time = False

        # Used to call the creation widgets
        self.create_widgets()
        
        # Used to call the creation of hotkeys
        self.hotkeys()
    
    # Function to make hotkeys for the window
    def hotkeys(self):
        self.define_macro_entry.bind("<Control-l>", self.load_macro)
        self.define_macro_entry.bind("<Control-s>", self.save_macro)
        self.command_line_text.bind("<Control-w>", self.type_wait)
        self.command_line_text.bind("<Control-m>", self.type_move)
        self.command_line_text.bind("<Control-Shift-M>", self.type_move_nodelay)
        self.command_line_text.bind("<Control-Shift-Alt-M>", self.type_move_thread)
        self.command_line_text.bind("<Control-Shift-BackSpace>", self.delete_current_line)
        self.root.bind("<Control-Return>", self.start_macro)
    
    # Used for not having a lot of or statements when comparing a string to something
    def switch(self, string, comparisons):
        try:
            return string in comparisons
        except TypeError:
            return False

    # Function for making advanced error statements fast
    def error(self, title, error):
        if isinstance(error, str) and isinstance(title, str):
            if self.advanced_errors:
                messagebox.showerror(title=title, message=error)
            print(f"{title}: {error}")
        elif isinstance(error, str) and not isinstance(title, str):
            print("The title is not a string")
        elif not isinstance(error, str) and isinstance(title, str):
            print("The error message is not a string")
        elif not isinstance(error, str) and isinstance(title, str):
            print("The error mesage and title are not strings")
    
    # Defining all widgets that will be used in the program
    def create_widgets(self):

        # The check box for the looping
        self.loop_checkbox = tk.Checkbutton(self.root, text="Loop", variable=self.loop_var)
        self.loop_checkbox.grid(row=0, column=0, columnspan=2, sticky="w")  # Centered in two columns

        # Toggles if errors are displayed in a user-visible GUI report
        self.advanced_errors_checkbox = tk.Checkbutton(self.root, text="Advanced Error Report", variable=self.advanced_errorss)
        self.advanced_errors_checkbox.grid(row=1, column=0, columnspan=2, sticky="w")  # Centered in two columns

        # The start button to execute all commands in the command line
        self.start_button = tk.Button(self.root, text="Start", command=self.start_macro, width=20, height=0)
        self.start_button.grid(row=2, column=0, columnspan=2, sticky="w")  # Centered in two columns

        # The stop button to stop the program from executing commands in the command line
        self.stop_button = tk.Button(self.root, text="Stop", command=self.on_stop_macro, width=20, height=0)
        self.stop_button.grid(row=3, column=0, columnspan=2, sticky="w")  # Centered in two columns

        # The window for the display of current mouse coordinates
        self.open_window_button = tk.Button(self.root, text="Open Mouse Coordinates Window", command=self.open_coordinates_window)
        self.open_window_button.grid(row=4, column=0, columnspan=2, sticky="w")  # Centered in two columns

        # The text to label the command line entry box
        self.command_line_label = tk.Label(self.root, text="Command Line:")
        self.command_line_label.grid(row=5, column=0, columnspan=2, sticky="w")  # Centered in two columns

        # The command line that stores all commands to run
        self.command_line_text = tk.Text(self.root, width=50, height=8)  # Entry box
        self.command_line_text.grid(row=6, column=0, columnspan=2)  # Centered in two columns

        # Entry box to define a new macro
        self.define_macro_entry = tk.Entry(self.root, width=62)
        self.define_macro_entry.grid(row=7, column=0, columnspan=1, padx=5, pady=5, sticky="w")

        # Home button to go back to launcher
        self.back_to_launcher_button = tk.Button(self.root, text="Exit", command=self.root.quit, width=62)
        self.back_to_launcher_button.grid(row=8, column=0, pady=10, columnspan=1)
        self.back_to_launcher_button.configure(bg="#FE0000", activebackground="#33CC33")

        # Save button to save the current macro
        self.save_button = tk.Button(self.root, text="Save Macro", command=self.save_macro)
        self.save_button.grid(row=7, column=2, padx=10, sticky="w")

        # Load button to open the macro menu
        self.load_button = tk.Button(self.root, text="Load Macro", command=self.load_macro)
        self.load_button.grid(row=6, column=2, padx=10, sticky="s")

        self.show_saved_macros_button = tk.Button(self.root, text="Show Macros", command=macrosaves.show_saved_macros)
        self.show_saved_macros_button.grid(row=5, column=2, sticky="s")

        self.documentation_button = tk.Button(self.root, )

    # Used for loading scripts
    def load_macro(self, event=None):
        selected_macro_name = self.define_macro_entry.get()
        if selected_macro_name in macrosaves.savedmacros:
            macro_content = macrosaves.savedmacros[selected_macro_name]
            self.command_line_text.delete("1.0", tk.END)
            self.command_line_text.insert(tk.END, macro_content)
        if selected_macro_name == "":
            messagebox.showerror("Load Macro", "Please enter the name of the macro you would like to load in the box below the command line.")
        else:
            messagebox.showerror("Load Macro", "Selected macro not found in the saved macros.")

    # Function used to save a macro
    def save_macro(self, event=None):
        macro_name = self.define_macro_entry.get()
        macro_content = self.command_line_text.get("1.0", tk.END)
        if macro_name and macro_content:
            macrosaves.save_macro(macro_name, macro_content)  # Use the save_macro function from macrosaves.py
            messagebox.showinfo("Save Macro", f"Macro '{macro_name}' has been saved successfully.")
        else:
            messagebox.showerror("Save Macro", "Please enter a valid macro name and content.")

    # Go back to launcher function  
    def back_to_launcher(self):
        self.root.destroy()
        subprocess.Popen(["python", "UltimatepythonGUI.py"])

    # Used for parsing scripts
    def scriptsplit(self, cmdd):
        for commandd in validscriptcommands:
            if cmdd.startswith(commandd):
                # Extract the command and argument part
                command_part, argument_part = cmdd.split(":", 1)

                # Split the argument part at the comma to get the two numbers if the command is click or click delta
                if command_part == "clickat" or command_part == "clickatdelta":
                    try:
                        x, y = map(int, argument_part.split(","))
                    except ValueError:
                        print("Invalid input format. Please provide two numbers separated by a comma.")
                    break
        else:
            print("Invalid command. Please enter a valid script command.")

    # Used for detecting what variable the user is defining in user scripting
    def ffdq(self, string):
        matches = re.findall(r'"([^"]*)"', string)
        if matches:
            return matches
        return None

    # The main code for the move command
    def smove(self, xm, ym): 
        startx, starty = pyautogui.position()
        difx = xm - startx
        dify = ym - starty
        distance = ((difx ** 2) + (dify ** 2)) ** 0.5  # Calculate the total distance

        if self.steps <= 0:
            raise ValueError("Number of steps should be greater than zero.")

        xstep = difx / self.steps
        ystep = dify / self.steps

        if xstep == 0 and ystep == 0:
            return

        # Set a constant duration to achieve a constant speed
        constant_duration = 0.2

        for _ in range(self.steps):
            pyautogui.moveTo(startx + xstep, starty + ystep, duration=constant_duration)
            startx += xstep
            starty += ystep
        
    # The main code for the hold command
    def hold_key(self, key, duration):
        if key.lower() == 'left':
            self.mouse.press(pynput.mouse.Button.left)
            time.sleep(duration)
            self.mouse.release(pynput.mouse.Button.left)
        elif key.lower() == 'right':
            self.mouse.press(pynput.mouse.Button.right)
            time.sleep(duration)
            self.mouse.release(pynput.mouse.Button.right)
        else:
            start = time.time()
            while time.time() - start < duration:
                pyautogui.keyDown(key)

    # Starts the macro thread
    def start_macro_thread(self):
        macro_thread = threading.Thread(target=self.execute_macro_loop)
        macro_thread.start()
    
    # The handler for starting the macro
    def start_macro(self, event=None):
        # Start time
        self.startime = time.time()
        self.is_running = True
        self.advanced_errors = bool(self.advanced_errorss.get())
        self.is_looping = bool(self.loop_var.get())
        if self.is_looping:
            self.start_macro_thread()
        else:
            self.execute_macro_once(True)

    # How the macro runs if loop is on
    def execute_macro_loop(self):
        while self.is_looping and self.is_running:
            commands = self.command_line_text.get("1.0", tk.END).splitlines()
            for command in commands:
                if not self.is_running:
                    break
                self.parse_and_execute_command(command)

    # How the macro runs if loop is off
    def execute_macro_once(self, default):
        if default == True:
            commands = self.command_line_text.get("1.0", tk.END).splitlines()
        elif type(default) == list:
            commands = default
        for command in commands:
            if type(command) == str:
                self.parse_and_execute_command(command)

    # Most of the code for the program is the parce and execute if I lose it fully I quit the project
    # The code that will parse the command line and execute the commands that it contains
    def parse_and_execute_command(self, command):
        # Check of any command at all was given
        if command == None or command == "":
            cmd = ""
            pass
        else:
            command = command.split('#')[0]

            # Save the full command
            full_command = command
            
            # Split the command and arguments
            parts = command.lower().split()
            cmd = parts[0].lower()
            args = parts[1:]

        # All click commands
        if "click" in cmd:
            # The click command. Will click at a x and y coordinate on the screen.
            if cmd == "click":
                # Normal Click
                if len(args) == 2:
                    try:
                        x, y = map(int, args)
                        pyautogui.moveTo(x, y, 0)
                        pyautogui.click()
                    except ValueError:
                        if self.advanced_errors == True:
                            self.error("Click Command Error", "Please enter 2 numbers with no other characters for the x and y.")

                # No cords click
                elif len(args) == 0:
                    pyautogui.click(button="left")
                
                # Delta Click
                elif len(args) == 3:
                    if args[0] == "delta":
                        try:
                            x, y = map(int, args)
                            xm, ym = pyautogui.position()
                            x += xm
                            y += ym
                            pyautogui.moveTo(xm, ym, 0)
                            pyautogui.click()
                        except ValueError:
                            if self.advanced_errors == True:
                                messagebox.showerror(title="Click Command Error", message="Please enter 2 numbers with no other characters for the x and y.")
                            print("Invalid arguments for 'click' command. Please type numbers.")
                    
                    # Threaded Click
                    elif args[0] == "thread":
                        try:
                            x, y = map(int, args)
                            def dothis():
                                pyautogui.moveTo(x, y, 0)
                                pyautogui.click()
                            thread4 = threading.Thread(target=dothis, daemon=True)
                        except ValueError:
                            if self.advanced_errors == True:
                                messagebox.showerror(title="Click Command Error", message="Please enter 2 numbers with no other characters for the x and y.")
                            print("Invalid arguments for 'click' command. Please type numbers.")

                # Threaded delta click and shift click           
                elif len(args) == 4:
                    if args[0] == "thread":
                        if args[1] == "delta":
                            try:
                                x, y = map(int, args)
                                xm, ym = pyautogui.position()
                                x += xm
                                y += ym
                                def dothiss():
                                    pyautogui.moveTo(xm, ym, 0)
                                    pyautogui.click()
                                thread5 = threading.Thread(target=dothiss, daemon=True)
                                thread5.start()
                            except ValueError:
                                if self.advanced_errors == True:
                                    messagebox.showerror(title="Click Command Error", message="Please enter 2 numbers with no other characters for the x and y.")
                                print("Invalid arguments for 'click' command. Please type numbers.")

                   # Shift click 
                    elif args[0] == "click" and cmd == "shift":
                        try:
                            pyautogui.keyDown('shift')
                            pyautogui.click(button="left")
                            pyautogui.keyUp('shift')
                        except ValueError:
                            if self.advanced_errors == True:
                                messagebox.showerror(title="Shift Click Command Error", message="Please enter 2 numbers with no other characters for the x and y.")
                            print("Invalid arguments for 'shiftclick' command. Please type numbers.")

                    else:
                        if self.advanced_errors == True:
                            messagebox.showerror(title="Click Command Error", message="Please enter 2 numbers with no other characters for the x and y.")
                
                else:
                    if self.advanced_errors == True:
                        messagebox.showerror(title="Click Error", message="Please only use 2 arguments.")
                    print("Invalid arguments for 'click' command. Please only use 2 arguments.")

            # The right click comand.
            elif cmd == "rightclick":
                pyautogui.rightClick()


            # The shift click command. Will shift click at a x and y coordinate on the screen.
            elif cmd == "shiftclick":
                if cmd == "shiftclick":
                    try:
                        x, y = map(int, args[0:])
                        pyautogui.moveTo(x, y)
                        pyautogui.keyDown('shift')
                        pyautogui.click(button="left")
                        pyautogui.keyUp('shift')
                    except ValueError:
                        if self.advanced_errors == True:
                            messagebox.showerror(title="Shift Click Command Error", message="Please enter 2 numbers with no other characters for the x and y.")
                        print("Invalid arguments for 'shiftclick' command. Please type numbers.")

                # These don't work    
                elif args[0] == "right" and args[1] == "click" and cmd == "shift":
                    try:
                        x, y = map(int, args)
                        pyautogui.moveTo(x, y)
                        pyautogui.keyDown('shift')
                        pyautogui.click(button="right")
                        pyautogui.keyUp('shift')
                    except ValueError:
                        if self.advanced_errors == True:
                            messagebox.showerror(title="Click Command Error", message="Please enter 2 numbers with no other characters for the x and y.")
                        print("Invalid arguments for 'shiftclick' command. Please type numbers.")

                elif args[0] == "double" and args[1] == "click" and cmd == "shift":
                    try:
                        pyautogui.keyDown('shift')
                        pyautogui.click(clicks=2, interval=0.1)
                        pyautogui.keyUp('shift')
                    except ValueError:
                        if self.advanced_errors == True:
                            messagebox.showerror(title="Double Click Command Error", message="Please enter 2 numbers with no other characters for the x and y.")
                        print("Invalid arguments for 'doubleclick' command. Please type numbers.")

        
        # All typing commands
        elif "type" in cmd:
            match cmd:

            # The type command. Will type what the user specify. Only takes 1 argument aka no spaces.
                case "type":
                    if len(args) == 1:
                        chars = repr(args[0])[1:-1]
                        pyautogui.typewrite(chars)

                    if len(args) == 2: 
                        if args[0] == "thread":
                            chars = repr(args[0])[1:-1]
                            thread3 = threading.Thread(target=lambda: pyautogui.typewrite(chars), daemon=True)
                            thread3.start()
                        
                        elif args[0] == "var":
                            if args[1] in self.str_uvars:
                                pyautogui.typewrite(self.str_uvars[args[1]])
                        
                        else:
                            if self.advanced_errors == True:
                                messagebox.showerror(title="Type Command Error", message="When you use 3 arguments for the type command the first argument is expected to be thread or a variable.")
                            print("When you use 3 arguments for the type command the first argument is expected to be thread or a variable.")

                    else:
                        if self.advanced_errors == True:
                                messagebox.showerror(title="Type Command Error", message="Invalid amount of arguments. Please do not use spaces.")
                        print("Invalid arguments for 'type' command. Use no spaces")
        
            # This command will type everything in double quotes and join multiple pairs of double quotes
                case ["typef" | "typestr" | "type_str" | "strtype" | "str_type" | "ftype" | "stype"]:
                    list_msg = self.ffdq(repr(full_command)[1:-1])
                    if list_msg == []:
                        self.error("Type String Error", "Please put what you would like to type in quotes for type string.")
                        print("Type String Error: Please put what you would like to type in quotes for type string.")
                    else:
                        msg = "".join(list_msg)
                        if args[0] != "thread":
                            if len(args) >= 1:
                                pyautogui.typewrite(msg)

                        elif len(args) >= 2:
                            if args[0] == "thread":
                                type_thread = threading.Thread(target=lambda: pyautogui.typewrite(msg), daemon=True)
                                type_thread.start()                   
                            
                            else:
                                if self.advanced_errors == True:
                                    messagebox.showerror(title="Type Command Error", message="Error in type string thread.")
                                print("Error in type string thread.")

                        else:
                            if self.advanced_errors == True:
                                    messagebox.showerror(title="Type Command Error", message="Invalid amount of arguments. Please do not use spaces.")
                            print("Invalid arguments for 'type' command. Use no spaces")


        # The wait command. Will make the macro wait the users specified amount of time.
        elif cmd == "wait":
            if len(args) == 1:
                try:
                    wait_time = float(args[0])
                    time.sleep(wait_time)
                except ValueError:
                    if self.advanced_errors == True:
                        messagebox.showerror(title="Wait Command Error", message="Please use a number for the wait argument.")
                    print("Invalid argument for 'wait' command. Must be a number.")
            
            else:
                if self.advanced_errors == True:
                        messagebox.showerror(title="Wait Command Error", message="Pleae only use 1 argument for the wait command.")
                print("Invalid amount of arguments for 'wait' command.")
        

        # The press command. Will press the button the user inputs.
        elif self.switch(cmd, ["press", "input", "key"]):
            if len(args) == 1:
                try:
                    key = args[0]
                    keyboard.press_and_release(key)
                except ValueError:
                    if self.advanced_errors == True:
                        messagebox.showerror(title="Press Command Error", message="Please enter a key for the press argument.")
                    print("Invalid arguments for 'press' command.")
            
            elif len(args) == 2:
                if args[0] == "thread":
                    try:
                        key = args[0]
                        thread2 = threading.Thread(target=lambda: pyautogui.press(key), daemon=True)
                        thread2.start()
                    except ValueError:
                        if self.advanced_errors == True:
                            messagebox.showerror(title="Press Command Error", message="Please enter a key for the press argument.")
                        print("Invalid arguments for 'press' command.")
            
            else:
                if self.advanced_errors == True:
                        messagebox.showerror(title="Press Command Error", message="Invalid arguments for press command. DO NOT use spaces.")
                print("Invalid arguments for 'press' command.")
        

        # For coding related commands
        elif self.switch(cmd, ["code", "coding", "python", "py"]):
            match args:
                case ["tk" | "tkinter"]:
                    top = tk.Toplevel(self.root)
                    top.title("OOP Tkinter GUI")

                    ico = Image.open('screen.ico')
                    photo = ImageTk.PhotoImage(ico)
                    top.wm_iconphoto(False, photo)

                    text = tk.Text(top)
                    text.insert("1.0", macrosaves.tkinter_template)
                    text.pack()
                    copy_button = tk.Button(top, text="Copy", command=lambda: pyperclip.copy(text.get("1.0", "end-1c")))
                    copy_button.pack()

                case ["tk" | "tkinter", "gui" | "screen"]:
                    top = tk.Toplevel(self.root)
                    top.title("OOP Tkinter GUI")
                    ico = Image.open('screen.ico')
                    photo = ImageTk.PhotoImage(ico)
                    top.wm_iconphoto(False, photo)
                    text = tk.Text(top)
                    text.insert("1.0", macrosaves.tkinter_template)
                    text.pack()
                    copy_button = tk.Button(top, text="Copy", command=lambda: pyperclip.copy(text.get("1.0", "end-1c")))
                    copy_button.pack()
                
                case ["tk" | "tkinter", "copy"] | ["tk" | "tkinter", "gui" | "screen", "copy" | "duplicate" | "dupe"]:
                    pyperclip.copy(macrosaves.tkinter_template)

                

        # A fast way of typing common minecraft commands
        elif cmd == "minecraft" or cmd == "mc":
            if len(args) >= 1:
                match args:

                    case ["onxy", "sell", "copper" | "copper_slab" | "slab"]:
                        pyautogui.typewrite(r"/sellall waxed_oxidized_cut_copper_slab")

                    case "sell":
                        if len(args) == 2: 
                            pyautogui.typewrite(r"/sell")
                            pyautogui.typewrite(f" {args[1]}")
                
                    case ["raw", "input"]:
                        self.execute_macro_once(['press esc', 'wait 0.1', 'click 843 487', 'wait 0.1', 'click 1133 334', 'wait 0.1', 'click 891 186', 'wait 0.1', 'click 1111 214', 'wait 0.1', 'click 918 992', 'wait 0.1', 'click 968 337', 'wait 0.1', 'click 978 541', 'wait 0.1', 'click 973 279'])

                    case "ri":
                        self.execute_macro_once(['press esc', 'wait 0.1', 'click 843 487', 'wait 0.1', 'click 1133 334', 'wait 0.1', 'click 891 186', 'wait 0.1', 'click 1111 214', 'wait 0.1', 'click 918 992', 'wait 0.1', 'click 968 337', 'wait 0.1', 'click 978 541', 'wait 0.1', 'click 973 279'])

                    case "pv":
                        if len(args) == 1:
                            pyautogui.typewrite(r"/pv 1")
                        elif len(args) == 2:
                            if args[1].isdigit():
                                word = r"/pv "+ args[1]
                                pyautogui.typewrite(word)


        # Faster way of pressing spaceabr 
        elif cmd == "space":
            keyboard.press_and_release("spacebar")


        # The hold command. Will hold the specified key for the specified amount of time. The rate of witch the inputs are registered can be modified using the speed argumemt. Hold left and right hold the left and right key
        elif "hold" in cmd:
            match cmd:
                
                case "hold":
                    # Hold a key
                    if len(args) == 2:

                        # The normal hold arguments handler
                        if args[0] in self.keys:
                            if args[1].isdigit():
                                self.hold_key(key=args[0], duration=float(args[1]))
                            else:
                                self.error("Hold Command Error", "Please enter a number for the second argument.")
                        else:
                            self.error("Hold Command Error", "Please enter a key for the first argument.")
                    
                    # The threaded hold argument handler       
                    elif len(args) == 3:
                        if args[0] == "thread":
                            if args[1] in self.keys:
                                if type(args[2]) == int or type(args[2]) == float:
                                    thread = threading.Thread(target=self.hold_key, args=(args[1], float(args[2])), daemon=True)
                                    thread.start()
                                else:
                                    if self.advanced_errors == True:
                                        messagebox.showerror(title="Hold Command Error", message="Please enter a number for the third argument.")
                                    print("Invalid arguments for hold command.")
                            else:
                                if self.advanced_errors == True:
                                    messagebox.showerror(title="Hold Command Error", message="Please enter a key for the second argument.")
                                print("Invalid arguments for hold command.")

                        else:
                            # Advanced Error Message
                            if self.advanced_errors == True:
                                messagebox.showerror(title="Hold Command Error", message="Invalid arguments for threading a hold")
                            print("Invalid arguments for 'hold' command.")
                    
                    # More than the max amount of arguments
                    elif len(args) > 3 or len(args) == 1:
                        if self.advanced_errors == True:
                            messagebox.showerror(title="Hold Command Error", message="Invalid amount of arguments for the hold command")
                        print("Invalid amount of arguments for the hold command")


                case ["holdleft"| "lefthold"]:
                    if len(args) == 1:
                        try:
                            duration = float(args[0])
                            self.hold_key('left', duration)
                        except ValueError:
                            if self.advanced_errors == True:
                                messagebox.showerror(title="HoldLeft Command Error", message="Please use a number for the duration.")
                            print("Invalid arguments for 'holdleft' command.")


                case ["righthold" | "holdright"]:
                    if len(args) == 1:
                        try:
                            duration = float(args[0])
                            self.hold_key('right', duration)
                        except ValueError:
                            if self.advanced_errors == True:
                                messagebox.showerror(title="HoldRight Command Error", message="Please use a number for the duration.")
                            print("Invalid arguments for 'holdright' command.")


        # The move command will move the mouse to a specified x and y coordinate or reletive to the current x and y. Can also be a thread.
        elif cmd == "move":
            if len(args) == 3:
                if args[0] == "thread":
                    try:
                        args[1] = int(args[1])
                        args[2] = int(args[2])
                        thread = threading.Thread(target=self.smove, args=(args[1], args[2]), daemon=True)
                        thread.start()
                    except ValueError:
                        if self.advanced_errors == True:
                            messagebox.showerror(title="Move Command Error", message="Please use numbers for the 2 non floating point numbers for the x and y arguments.")
                        print("Invalid arguments for threading the move command.")
                
                elif args[0] == "delta":
                    try:
                        xmm1 = int(args[1])
                        ymm1 = int(args[2])
                        xm1, ym1 = pyautogui.position()
                        xm1 += xmm1
                        ym1 += ymm1
                        self.smove(xm1, ym1)
                    except ValueError:
                        if self.advanced_errors == True:
                            messagebox.showerror(title="Move Command Error", message="Please use numbers for the 2 non decimal numbers for the x and y arguments.")
                        print("Invalid arguments for threading the move command.")
                
                    print("Invalid arguments for move command.")

            elif len(args) == 2:
                try:
                    args[0] = int(args[0])
                    args[1] = int(args[1])
                    self.smove(args[0], args[1])
                except ValueError:
                    print("Error in move command: Enter numbers")

            elif len(args) == 4:

                if args[0] == "thread":
                    if args[1] == "delta":
                        try:
                            args[2] = int(args[1])
                            args[3] = int(args[2])
                            xm1, ym1 = pyautogui.position()
                            xm1 += args[2]
                            ym1 += args[3]
                            thread2 = threading.Thread(target=self.smove, args=(xm1, ym1), daemon=True)
                            thread2.start()
                        except ValueError:
                            if self.advanced_errors == True:
                                messagebox.showerror(title="Move Command Error", message="Please use numbers for the 2 non floating point numbers for the x and y arguments.")
                        print("Invalid arguments for threading the move command.")

                if args[0] == "delta":
                    if args[1] == "nodelay":
                        try:
                            xmm1 = int(args[2])
                            ymm1 = int(args[3])
                            xm1, ym1 = pyautogui.position()
                            xm1 += xmm1
                            ym1 += ymm1
                            pyautogui.move(xm1, ym1)
                            print(f"{xm1}, {ym1}")
                        except ValueError:
                            if self.advanced_errors == True:
                                messagebox.showerror(title="Move Command Error", message="Please use numbers for the 2 non decimal numbers for the x and y arguments.")
                            print("Invalid arguments for threading the move command.")

                elif args[0] == "nodelay":
                    if args[1] == "delta":
                        try:
                            xmm1 = int(args[2])
                            ymm1 = int(args[3])
                            xm1, ym1 = pyautogui.position()
                            xm1 += xmm1
                            ym1 += ymm1
                            for i in range(5):
                                pyautogui.move(xm1/5, ym1/5)

                            pyautogui.move(xm1, ym1)
                            print(f"{xm1}, {ym1}")
                        except ValueError:
                            if self.advanced_errors == True:
                                messagebox.showerror(title="Move Command Error", message="Please use numbers for the 2 non decimal numbers for the x and y arguments.")
                            print("Invalid arguments for threading the move command.")

            else:
                if self.advanced_errors == True:
                    messagebox.showerror(title="Move Error", message="Invalid arguments for move command. Please enter numbers.")


        # Used to define user variables
        elif self.switch(cmd, ["def", "define", "assign"]):            
            if len(args) >= 3:
                if self.switch(args[0], ["presistant", "stay", "staying", "save"]):
                    if args[1] == "var":
                        variable_name = args[2]
                        if self.switch(variable_name, ["delete", "presistant", "save"]):
                            print("Variable name cannot be delete, save or presistant")
                            self.error("User Variable Error", "Variable name cannot be delete, save or presistant")   
                        else:
                            variable_commands = self.ffdq(full_command)  # Split the commands within the variable
                            self.uvars[variable_name] = variable_commands  # Store the list of commands
                            macrosaves.add_uvar(variable_name, variable_commands)
                            print(f'Defined variable: "{variable_name}" with command(s): {variable_commands}')
                
                elif args[0] == "var":
                    variable_name = args[1]
                    if self.switch(variable_name, ["delete", "presistant", "save"]):
                        print("Variable name cannot be delete, save or presistant")
                        self.error("User Variable Error", "Variable name cannot be delete, save or presistant")   
                    else:
                        variable_commands = self.ffdq(full_command)  # Split the commands within the variable
                        print(variable_commands)
                        self.uvars[variable_name] = variable_commands  # Store the list of commands
                        print(f'Defined variable: "{variable_name}" with command(s): {variable_commands}')


        # Used to load variable
        elif cmd == "var" or cmd == "vr" or cmd == "v" or cmd == "variable":
            variable_name = args[0]
            if variable_name in self.uvars:
                print(f'Found variable: "{variable_name}"')
                for var_cmd in self.uvars[variable_name]:
                    print(f'In variable "{variable_name}" executed {var_cmd}')
                    self.parse_and_execute_command(command=var_cmd.strip())  # Execute each command in the variable
            
            elif variable_name == "delete":
                if args[1] in self.uvars:
                    del self.uvars[args[1]]
                    if args[1] in macrosaves.uvars:
                        macrosaves.delete_uvar(args[1])
                    print(f'Deleted variable: "{args[1]}"')
                elif not args[1] in self.uvars:
                    self.error("User Variable Error", f"{args[1]} is not defined")
                    print(f"{args[1]} not defined")

            elif self.switch(variable_name, ["save", "presistant"]):
                if args[1] in self.uvars:
                    macrosaves.add_uvar(args[1], self.uvars[args[1]])
                    print(str(args[1]))

            else:
                if self.advanced_errors:
                    messagebox.showerror(title="User Variable Error", message=f"Variable '{variable_name}' not found.")
                print(f"Variable '{variable_name}' not found.")


        # Used for displaying something to the screen such as the current user variables or a message
        elif self.switch(cmd, ["show", "display", "present"]):
            if self.switch(args[0], ["uvars", "variables", "vars"]):
                print("\n")
                print("Displaying Variables")
                top = tk.Toplevel(self.root)
                top.title("Variables")
                for key, value in self.uvars.items():
                    print(f"{key}: {value}")
                    label = tk.Label(top, text=f"{key}: {value}")
                    label.pack()

            elif self.switch(args[0], ["string", "text", "message", "msg"]):
                if args[1]:
                    if len(args) >=2:
                        msgg = self.ffdq(full_command)
                        msg = "".join(msgg)
                        print(f"Message: {msg}")
                        messagebox.showinfo(title=args[1], message=msg)


        # Used for changing pyautogui pause time
        elif self.switch(cmd, ["pausetime", "pause_time", "stoptime", "stop_time", "inputtime", "inputime", "input_time", "delay", "default_delay", "defaultdelay"]):
            if args[0]:
                try:
                    num = int(args[0])
                    pyautogui.PAUSE = num
                except Exception:
                    self.error("Delay Change Error", "When changing the input delay please input a non decimal number")
                    print("Delay Change Error: When changing the input delay please input a non decimal number")

        elif self.switch(cmd, ["test", "testing"]):
            if args[0] == "print":
                print("Printed")


        # No command was valid not in use right now because it doesn't work as intended. Used to just be a else statement but it did not work so I got rid of it

    # Used to typing text into the command line
    def ty(self, text):
        keyboard.write(text)

    # Delete current line
    def delete_current_line(self, event):
        self.command_line_text.delete('current linestart', 'current lineend+1c')

    # The function that types wait
    def type_wait(self, event):
        self.ty(text="wait 0.1")

    # The function that types move
    def type_move(self, event):
        self.ty(text="move ")

    # The function that types move nodelay
    def type_move_nodelay(self, event):
        self.ty(text="move nodelay ")

    # The function that types move nodelay
    def type_move_thread(self, event):
        self.ty(text="move thread ")

    # Open the window to get coordinates
    def open_coordinates_window(self):
        cords_win = CordsWindow(self.root)
        root.mainloop()

    def stop_macro(self, event=None):
        self.is_running = False
        if self.give_time:
            try:
                endtime = time.time()
                totaltime = endtime - self.startime
                print(f"Total time ran was: {totaltime}")
            except Exception:
                pass

    def on_stop_macro(self, event=None):
        app.stop_macro()
        
if __name__ == "__main__":

    root = tk.Tk()
    app = MacroApp(root)

    # Page Up to run the macro
    keyboard.add_hotkey("page up", app.start_macro, args=(), suppress=True)

    # Page Down to stop the macro loop
    keyboard.add_hotkey("page down", app.stop_macro, args=(), suppress=True)

    root.mainloop()
    