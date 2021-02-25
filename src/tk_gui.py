import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk

from session import States

WIDTH = 1200
H_OFFSET = 100
HEIGHT = 675
V_OFFSET = 100
SIZE = "{0}x{1}+{2}+{3}".format(WIDTH, HEIGHT, H_OFFSET, V_OFFSET)  # width x height + horizontal offset + vertical
# offset
PADDING = 5
MARGIN = 200


class PopupWindowGet:
    """Get value information popup"""

    def __init__(self, master, title, text, choices=None):
        self.value = None  # Value that will be set when closing the popup
        # Define a new style for popup buttons
        self.button_style = ttk.Style()
        self.button_style.configure('Popup.TButton',  # Name of the style
                                    font=('calibri', 20, 'bold'),
                                    borderwidth='4')
        # When the mouse is on the button
        self.button_style.map('Popup.TButton',
                              foreground=[('active', '!disabled', 'green')],
                              background=[('active', 'black')])
        try:
            top = self.top = tk.Toplevel(master)
        except tk.TclError:  # If the master window has been closed
            return
        self.top.title(title)
        self.input_text = ttk.Label(top, text=text, style='TLabel')
        # self.input_text = tk.Label(top, text=text)
        self.input_text.pack()
        if choices:
            # self.output_value = ttk.Combobox(master=top, values=choices)
            self.output_value = tk.StringVar()
            for choice in choices:
                self.button = ttk.Radiobutton(master=top,
                                              text=choice,
                                              variable=self.output_value,
                                              command=self.cleanup,
                                              style='Popup.TButton',
                                              value=choice)
                self.button.pack()
        else:
            self.output_value = tk.Entry(top)
            self.output_value.pack()
            self.output_value.focus_set()
            self.validation_button = tk.Button(top, text='Ok', command=self.cleanup)
            self.validation_button.pack()
            self.top.geometry('+{0}+{1}'.format(MARGIN, MARGIN))
            top.bind('<Return>', self.cleanup)

    def cleanup(self, event=None):
        self.value = self.output_value.get()
        self.top.destroy()


class PopupWindowInfo:
    """Information popup window"""

    def __init__(self, master, title, text):
        try:
            top = self.top = tk.Toplevel(master)
        except tk.TclError:  # If the master window has been closed
            return
        self.top.title(title)
        self.input_text = ttk.Label(top, text=text, style='TLabel')
        self.input_text.pack()
        self.validation_button = ttk.Button(top, text='Ok', command=self.top.destroy, style='Popup.TButton')
        self.validation_button.pack()
        self.top.geometry('+{0}+{1}'.format(MARGIN, MARGIN))


class Interface:
    """Main window of the GUI. Shows the live webcam feed, the interpreted program and the last event tile"""

    def __init__(self, root, session, title="Interface"):
        # initialization
        self.root = root
        self.session = session
        self.root.title(title)
        self.popup = None  # Initialization of the popup window

        # geometry initialization
        self.full_screen = True
        self.geometry = SIZE
        self.root.geometry(SIZE)

        # Set the default layout to fullscreen
        self.root.attributes("-fullscreen", True)

        # Set the key bindings
        self.root.bind('<Escape>', self.end_fullscreen)
        self.root.bind('<F11>', self.toggle_fullscreen)
        self.root.bind('q', self.reset_program_fun)
        self.root.bind('a', self.load_program_fun)

        # Style initialization
        self.button_style = ttk.Style()
        self.button_style.configure('Interface.TButton',
                                    font=('calibri', 20),
                                    borderwidth='4')
        # When the button is pressed
        self.button_style.map('Interface.TButton',
                              foreground=[('pressed', 'red')],
                              background=[('pressed', 'black')])
        self.label_style = ttk.Style()
        self.label_style.configure('TLabel',
                                   font=('calibri', 20),
                                   borderwidth='4')

        # labels initialization
        self.webcam_title = ttk.Label(text="Current image from the webcam", style='TLabel')
        self.webcam_title.grid(row=0, column=0, padx=PADDING, pady=PADDING)
        self.webcam = tk.Label()
        self.webcam.grid(row=1, column=0, padx=PADDING, pady=PADDING)
        self.last_event_title = ttk.Label(text="Last event detected by the Thymio", style='TLabel')
        self.last_event_title.grid(row=2, column=0, padx=PADDING, pady=PADDING)
        self.last_event_tile = tk.Label()
        self.last_event_tile.grid(row=3, column=0, rowspan=2, padx=PADDING, pady=PADDING)
        self.logo_label = tk.Label()
        self.logo_label.grid(row=0, column=1, padx=PADDING, pady=PADDING)
        self.program_title = ttk.Label(text="Current program", style='TLabel')
        self.program_title.grid(row=0, column=2, columnspan=2, padx=PADDING, pady=PADDING)
        tk.Grid.columnconfigure(self.root, 2, weight=1)  # To make label of the column 2 the largest as possible
        self.program = tk.Label()
        self.program.grid(row=1, column=1, rowspan=3, columnspan=3, padx=PADDING, pady=PADDING)
        tk.Grid.rowconfigure(self.root, 3, weight=1)  # To make label of the row 2 the largest as possible
        self.load_program = ttk.Button(root, text="load program", command=self.load_program_fun,
                                       style='Interface.TButton')
        self.load_program.grid(row=4, column=1, padx=PADDING, pady=PADDING)
        self.reset_game = ttk.Button(root, text="Game selection", command=self.reset_session_state,
                                     style='Interface.TButton')
        self.reset_game.grid(row=4, column=2, padx=PADDING, pady=PADDING)
        self.reset_program = ttk.Button(root, text="reset program", command=self.reset_program_fun,
                                        style='Interface.TButton')
        self.reset_program.grid(row=4, column=3, padx=PADDING, pady=PADDING)

        # Update to show the labels
        self.update()

    def load_program_fun(self, event=None):
        if self.session.state == States.WEBCAM_MAIN:
            self.session.state = States.LAUNCH_WEBCAM
        elif self.session.state == States.IMG_FILE_MAIN:
            self.session.state = States.LAUNCH_FILE
        elif self.session.state == States.CAPTURE_MAIN:
            self.session.state = States.LAUNCH_CAPTURE

    def reset_program_fun(self, event=None):
        if self.session.state == States.LAUNCH_WEBCAM or self.session.state == States.EXECUTE_WEBCAM:
            self.session.state = States.WEBCAM_MAIN
        elif self.session.state == States.LAUNCH_FILE or self.session.state == States.EXECUTE_FILE:
            self.session.state = States.IMG_FILE_MAIN
        elif self.session.state == States.LAUNCH_CAPTURE or self.session.state == States.EXECUTE_CAPTURE:
            self.session.state = States.CAPTURE_MAIN

    def reset_session_state(self):
        self.session.state = States.GAME_CHOICE

    def toggle_fullscreen(self, event=None):
        self.program.configure(image='')
        self.full_screen = not self.full_screen
        self.root.attributes("-fullscreen", self.full_screen)

    def end_fullscreen(self, event=None):
        self.program.configure(image='')
        self.full_screen = False
        self.root.attributes("-fullscreen", False)

    def on_delete(self):
        self.session.state = States.EXIT
        # self.popup.destroy()  # Not needed, already handled by self.root.destroy()
        self.root.destroy()

    def update(self):
        self.root.update()
        # self.program.configure(height=int(self.root.winfo_height() - self.program_title.winfo_height()
        #                                   - self.load_program.winfo_height()) - 8 * PADDING)

    def update_gui(self, webcam, program):  # , last_event=0):
        last_event = self.session.current_event_tile
        # Another way to resize while keeping aspect ratio. See PIL Documentation for more infos
        size = self.root.winfo_width() - self.webcam_title.winfo_width(), self.program_title.winfo_height()
        logo_copy = self.session.module_logo.copy()  # Make a copy before doing modification
        logo_copy.thumbnail(size, Image.ANTIALIAS)
        logo_tk = ImageTk.PhotoImage(image=logo_copy)
        self.logo_label.configure(image=logo_tk)
        try:
            ratio = webcam.shape[1] / webcam.shape[0]
            webcam_height = int((self.root.winfo_height() - self.webcam_title.winfo_height()
                                 - self.last_event_title.winfo_height()) / 2)
            webcam_width = int(ratio * webcam_height)
            webcam_resized = cv2.resize(webcam, (webcam_width - 6 * PADDING, webcam_height - 6 * PADDING))
            b_webcam, g_webcam, r_webcam = cv2.split(webcam_resized)
            img_webcam = cv2.merge((r_webcam, g_webcam, b_webcam))
            img_webcam_pil = Image.fromarray(img_webcam)
            img_webcam_tk = ImageTk.PhotoImage(image=img_webcam_pil)
            self.webcam.configure(image=img_webcam_tk)
        except Exception:
            pass
        try:
            ratio = last_event.shape[1] / last_event.shape[0]
            last_event_height = webcam_height
            last_event_width = int(ratio * last_event_height)
            last_event_resized = cv2.resize(last_event,
                                            (last_event_width - 6 * PADDING, last_event_height - 6 * PADDING))
            b_last_event, g_last_event, r_last_event = cv2.split(last_event_resized)
            img_last_event = cv2.merge((r_last_event, g_last_event, b_last_event))
            img_last_event_pil = Image.fromarray(img_last_event)
            img_last_event_tk = ImageTk.PhotoImage(image=img_last_event_pil)
            self.last_event_tile.configure(image=img_last_event_tk)
        except Exception:
            pass
        try:
            ratio = program.shape[1] / program.shape[0]
            program_height = int(self.root.winfo_height() - self.program_title.winfo_height()
                                 - self.load_program.winfo_height())
            program_width = int(self.root.winfo_width() - webcam_width)
            if ratio * program_height >= program_width:
                program_height = int(program_width / ratio)
            else:
                program_width = int(program_height * ratio)
            program_resized = cv2.resize(program, (program_width - 8 * PADDING, program_height - 8 * PADDING))
            b_program, g_program, r_program = cv2.split(program_resized)
            img_program = cv2.merge((r_program, g_program, b_program))
            img_program_pil = Image.fromarray(img_program)
            img_program_tk = ImageTk.PhotoImage(image=img_program_pil)
            self.program.configure(image=img_program_tk)
        except Exception:
            self.program.configure(image='')  # Convention of TKinter
        try:
            tk.Grid.columnconfigure(self.root, 2, weight=1)  # To make label of the column 2 the largest as possible
            tk.Grid.rowconfigure(self.root, 3, weight=1)  # To make label of the row 2 the largest as possible
            self.root.update()
        except tk.TclError:  # if application has been destroyed
            pass

    def get_integer(self, title, text):
        self.popup = PopupWindowGet(self.root, title, text)
        try:
            self.root.wait_window(self.popup.top)
            return int(self.popup.value)
        except ValueError:  # If value isn't an Integer
            return
        except AttributeError:  # If window has been closed
            return
        except TypeError:  # If program has been closed
            return

    def get_choice(self, title, text, choices):
        self.popup = PopupWindowGet(self.root, title, text, choices)
        try:
            self.root.wait_window(self.popup.top)
            return str(self.popup.value)
        except ValueError:  # If value isn't a string
            return
        except AttributeError:  # If window has been closed
            return
        except TypeError:  # If program has been closed
            return

    def get_text(self, title, text):
        self.popup = PopupWindowGet(self.root, title, text)
        try:
            self.root.wait_window(self.popup.top)
            return str(self.popup.value)
        except ValueError:
            return
        except AttributeError:
            return
        except TypeError:  # If program has been closed
            return

    def show_info(self, title, text):
        self.popup = PopupWindowInfo(self.root, title, text)
        self.root.wait_window(self.popup.top)
