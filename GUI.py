import subprocess
import time
import tkinter as tk
from tkinter import ttk, scrolledtext, font
import traceback
from functions import list_available_com_ports, ascii_to_hex, read_meter
from contextlib import redirect_stdout, redirect_stderr
import sys
import io
import threading
import selectedTest 
from main import RTC_forcing
from tkinter import END, ttk, filedialog
from tkinter import messagebox

def toggle_all_options():
    current_state = all(var.get() for _, var in options)
    new_state = not current_state
    for _, var in options:
        var.set(new_state)
    toggle_button.config(text="Unselect All" if new_state else "Select All")

def perform_read():
    cmd_args = get_cmd_args()
    if cmd_args is None:
        
        return
    test1 = "Read"
    cmd_args = ["selectedTest.py"] + get_cmd_args()
    output = io.StringIO()
    start_time = time.time()
    
    try:
        with redirect_stdout(output), redirect_stderr(output):
            selectedTest.run_tests([test1], cmd_args)
        
        end_time = time.time()
        duration = end_time - start_time
        
        additional_output = output.getvalue()
        if additional_output:
            print_log(additional_output)
        
        print_log(f"Completed Read in {duration:.2f} seconds")
        print_log("-" * 30)
    except Exception as e:
        error_message = f"An error occurred during read operation: {str(e)}"
        #print_log(error_message)
        messagebox.showerror("Error", error_message)

def perform_connect():
    #print_log("Performing Read action...")
    test2 = "Connect/Disconnect"
    cmd_args = ["selectedTest.py"] + get_cmd_args()
    output = io.StringIO()
    start_time = time.time()
    
    with redirect_stdout(output), redirect_stderr(output):
        selectedTest.run_tests([test2], cmd_args)
    
    end_time = time.time()
    duration = end_time - start_time
    
    additional_output = output.getvalue()
    if additional_output:
        print_log(additional_output)
    
    print_log(f"Completed Read in {duration:.2f} seconds")
    print_log("-" * 30)

    

def run_selected_tests(options):
    #print("options :",options)
    selected_tests = [text for text, var in options if var.get()]
    #print("selected_tests  :",selected_tests)
    import selectedTest

    for test in selected_tests:
        print_log(f"Running selected test: {test}")
        
        # Capture stdout and stderr
        output = io.StringIO()
        start_time = time.time()
        with redirect_stdout(output), redirect_stderr(output):
            selectedTest.print_selected_tests([test], get_cmd_args())
        end_time = time.time()
        duration = end_time - start_time

        # Log any additional output captured
        additional_output = output.getvalue()
        if additional_output:
            #print_log("Additional output:")
            print_log(additional_output)

        print_log(f"Finished running selected test: {test} in {duration:.2f} seconds")
        print_log("-" * 30)

def check_missing_values(com_port, hls_password, auth_key, enc_key):
    missing_values = []
    if not com_port or com_port == "Refresh":
        missing_values.append("COM Port")
    if not hls_password:
        missing_values.append("HLS Password")
    if not auth_key:
        missing_values.append("Authentication Key")
    if not enc_key:
        missing_values.append("Encryption Key")
    
    if missing_values:
        error_message = f"Missing required values: {', '.join(missing_values)}"
        print_log(error_message)
        #messagebox.showerror(error_message)
        return False
    return True

def get_cmd_args(): 

    com_port = com_port_var.get()
    hls_password = hls_password_var.get()
    auth_key = authentication_key_var.get()
    enc_key = encryption_key_var.get()

    if not check_missing_values(com_port, hls_password, auth_key, enc_key):
        return None
        
    return [
        '-S', com_port,
        '-c', '48',
        '-a', 'High',
        '-P', hls_password,
        '-C', 'AuthenticationEncryption',
        '-T', '5A454E3132333435',
        '-A', ascii_to_hex(auth_key),
        '-B', ascii_to_hex(enc_key),
        '-D', ascii_to_hex(hls_password)
    ]

def print_log(text):
    log_window.configure(state='normal')
    log_window.insert(tk.END, text + '\n')
    log_window.see(tk.END)
    log_window.configure(state='disabled')

def clear_log():
    log_window.configure(state='normal')
    log_window.delete('1.0', tk.END)
    log_window.configure(state='disabled')


def save_log():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Text files", "*.txt"),
                                                       ("All files", "*.*")])
    if file_path:
        with open(file_path, "w") as file:
            file.write(log_window.get('1.0', tk.END))
        print_log(f"Log saved to {file_path}")


def on_com_port_change(*args):
    if com_port_var.get() == "Refresh":
        list_available_com_ports(com_port_menu, com_port_var)

def save_config(frame):
    for child in frame.winfo_children():
        if isinstance(child, ttk.Entry):
            child.config(state='disabled')
    com_port_menu.config(state='disabled')
    save_button.pack_forget()
    edit_button.pack(side=tk.LEFT, padx=(0, 10))
    read_button.pack(side=tk.LEFT)
    #print_log("Configuration saved.")

def edit_config(frame):
    for child in frame.winfo_children():
        if isinstance(child, ttk.Entry):
            child.config(state='normal')
    com_port_menu.config(state='normal')
    read_button.pack_forget()
    edit_button.pack_forget()
    save_button.pack(side=tk.LEFT, padx=(0, 10))
    #print_log("Configuration is now editable.")

# Custom styles
def create_styles():

    style = ttk.Style()    
    # Main tab style
    style.configure('Main.TNotebook', background='#2c3e50')
    style.configure('Main.TNotebook.Tab', font=('Helvetica', 12, 'bold'), padding=[10, 5], background='#34495e', foreground='black')
    style.map('Main.TNotebook.Tab', background=[('selected', '#3498db')], foreground=[('selected', 'black')])
    
    # Sub-tab style
    style.configure('Sub.TNotebook', background='#ecf0f1')
    style.configure('Sub.TNotebook.Tab', font=('Helvetica', 10), padding=[8, 3], background='#bdc3c7', foreground='#2c3e50')
    style.map('Sub.TNotebook.Tab', background=[('selected', '#3498db')], foreground=[('selected', 'black')])
    
    
    style.configure('TButton', font=('Helvetica', 10), padding=5) # Button style    
    style.configure('TLabel', font=('Helvetica', 10)) # Label style    
    style.configure('TEntry', font=('Helvetica', 10)) # Entry style

    # Remove focus border
    style.layout('Main.TNotebook.Tab', [('Notebook.tab', {'sticky': 'nswe', 'children':
        [('Notebook.padding', {'side': 'top', 'sticky': 'nswe', 'children':
            [('Notebook.label', {'side': 'top', 'sticky': ''})],
        })],
    })])
    style.layout('Sub.TNotebook.Tab', [('Notebook.tab', {'sticky': 'nswe', 'children':
        [('Notebook.padding', {'side': 'top', 'sticky': 'nswe', 'children':
            [('Notebook.label', {'side': 'top', 'sticky': ''})],
        })],
    })])

    # Adjust tab margin and overlap
    style.configure('Main.TNotebook', tabmargins=[2, 5, 2, 0])
    style.configure('Sub.TNotebook', tabmargins=[2, 5, 2, 0])
    style.configure('TNotebook.Tab', overlap=0)

# main window
root = tk.Tk()
root.title("Configuration and Programming Test")
root.configure(bg='#ecf0f1')


create_styles()

# Create a PanedWindow to separate the notebook and log window
paned_window = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
paned_window.pack(expand=True, fill='both', padx=10, pady=10)

# notebook
notebook = ttk.Notebook(paned_window, style='Main.TNotebook')
paned_window.add(notebook, weight=3)


# Global log window frame
log_frame = ttk.Frame(paned_window, style='TFrame')
paned_window.add(log_frame, weight=1)

# Label row with Clear and Save buttons
label_frame = ttk.Frame(log_frame)
label_frame.pack(anchor=tk.W, pady=(0, 5), fill=tk.X)

log_label = ttk.Label(label_frame, text="Log Window", font=('Helvetica', 12, 'bold'))
log_label.grid(row=0, column=0, sticky=tk.W)

clear_button = ttk.Button(label_frame, text="Clear", command=clear_log)
clear_button.grid(row=0, column=1, padx=10)

save_button = ttk.Button(label_frame, text="Save", command=save_log)
save_button.grid(row=0, column=2, padx=10)

# ScrolledText for displaying the log
log_window = scrolledtext.ScrolledText(log_frame, width=40, height=30, wrap=tk.WORD, font=('Courier', 9))
log_window.pack(expand=True, fill='both')

# Config tab
config_frame = ttk.Frame(notebook, style='TFrame', padding=20)
notebook.add(config_frame, text='Config')

# Create a style for the config frame
style = ttk.Style()
style.configure('Config.TFrame', background='#f0f0f0')
config_frame.configure(style='Config.TFrame')

# Create and configure the COM port menu
com_port_label = ttk.Label(config_frame, text="COM PORT:", style='TLabel')
com_port_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))

com_port_var = tk.StringVar()
com_port_menu = ttk.OptionMenu(config_frame, com_port_var, "")
com_port_menu.grid(row=0, column=1, sticky=tk.W, pady=(0, 10))

# Set up the trace to handle the "Refresh" option
com_port_var.trace_add('write', on_com_port_change)

# Populate the COM port menu with available ports
list_available_com_ports(com_port_menu, com_port_var)

# IP Address and Port fields
ip_address_label = ttk.Label(config_frame, text="Meter IP Address:", style='TLabel')
ip_address_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
ip_address_var = tk.StringVar()
ip_address_entry = ttk.Entry(config_frame, textvariable=ip_address_var, style='TEntry')
ip_address_entry.grid(row=1, column=1, sticky=tk.W, pady=(0, 10))


# Common fields
encryption_key_label = ttk.Label(config_frame, text="Encryption key:", style='TLabel')
encryption_key_label.grid(row=3, column=0, sticky=tk.W, pady=(0, 10))
encryption_key_var = tk.StringVar()
encryption_key_entry = ttk.Entry(config_frame, textvariable=encryption_key_var, style='TEntry')
encryption_key_entry.grid(row=3, column=1, sticky=tk.W, pady=(0, 10))

authentication_key_label = ttk.Label(config_frame, text="Authentication key:", style='TLabel')
authentication_key_label.grid(row=4, column=0, sticky=tk.W, pady=(0, 10))
authentication_key_var = tk.StringVar()
authentication_key_entry = ttk.Entry(config_frame, textvariable=authentication_key_var, style='TEntry')
authentication_key_entry.grid(row=4, column=1, sticky=tk.W, pady=(0, 10))

hls_password_label = ttk.Label(config_frame, text="HLS password:", style='TLabel')
hls_password_label.grid(row=5, column=0, sticky=tk.W, pady=(0, 10))
hls_password_var = tk.StringVar()
hls_password_entry = ttk.Entry(config_frame, textvariable=hls_password_var, style='TEntry')
hls_password_entry.grid(row=5, column=1, sticky=tk.W, pady=(0, 10))

# Button frame
button_frame = ttk.Frame(config_frame, style='Config.TFrame')
button_frame.grid(row=6, column=0, columnspan=2, pady=(20, 0))

# Save button
save_button = ttk.Button(button_frame, text="Save", command=lambda: save_config(config_frame), style='TButton')
save_button.pack(side=tk.LEFT, padx=(0, 10))

# Edit button
edit_button = ttk.Button(button_frame, text="Edit", command=lambda: edit_config(config_frame), style='TButton')
edit_button.pack(side=tk.LEFT, padx=(0, 10))


# Read button
read_var = tk.BooleanVar()
read_button = ttk.Button(button_frame, text="Read", command=lambda: perform_read(), style='TButton')
read_button.pack(side=tk.LEFT)
read_button.pack_forget()

# Configure grid weights
config_frame.columnconfigure(1, weight=1)
config_frame.rowconfigure(6, weight=1)

# Programming tab
programming_frame = ttk.Frame(notebook, style='TFrame', padding=20)
notebook.add(programming_frame, text='Programming')

programming_notebook = ttk.Notebook(programming_frame, style='Sub.TNotebook')
programming_notebook.pack(expand=True, fill='both', padx=10, pady=10)

# parameter tab
parameter_frame = ttk.Frame(programming_notebook, style='TFrame')
programming_notebook.add(parameter_frame, text='Programming')

# Left frame for checkboxes and buttons
left_frame = ttk.Frame(parameter_frame, style='TFrame', padding=10)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

# Right frame for future use
right_frame = ttk.Frame(parameter_frame, style='TFrame', padding=10)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Style for checkbuttons
style.configure('TCheckbutton', font=('Helvetica', 10))

# Function to create a row with checkbox and run button
def create_row(parent, row, text, variable, options):
    check = ttk.Checkbutton(parent, text=text, variable=variable, style='TCheckbutton')
    check.grid(row=row, column=0, sticky=tk.W, pady=5)
    run_button = ttk.Button(parent, text="Run", command=lambda t=text, v=variable: threading.Thread(target=run_selected_tests, args=([(t, v)],)).start(), style='TButton', width=10)
    run_button.grid(row=row, column=1, padx=10, pady=5)
    return variable

# Create rows for each option
options = [    
    ("RTC Programming", tk.BooleanVar()),
    ("Demand Integration Period", tk.BooleanVar()),
    ("Profle Capture Integration Period", tk.BooleanVar()),
    ("Billing Dates", tk.BooleanVar()),
    ("TOD (Read)", tk.BooleanVar()),
    ("Load limit set (Read)", tk.BooleanVar()),
    ("Disconnect Control", tk.BooleanVar()),
    ("Metering Mode", tk.BooleanVar()),
    ("Payment Mode", tk.BooleanVar()),
    
]


checkbox_vars = []

for i, (text, var) in enumerate(options):
    checkbox_vars.append(create_row(left_frame, i, text, var, options))
    

# Select/Unselect All button
toggle_button = ttk.Button(left_frame, text="Select All", command=toggle_all_options, style='TButton', width=20)
toggle_button.grid(row=len(options), column=0, columnspan=2, pady=(10, 0))


# Run all tests button
run_all_button = ttk.Button(left_frame, text="Run Selected Tests", command=lambda: threading.Thread(target=run_selected_tests, args=(options,)).start(), style='TButton', width=20)
run_all_button.grid(row=len(options)+1, column=0, columnspan=2, pady=(10, 0))


# Configure grid weights
left_frame.columnconfigure(0, weight=1)
left_frame.columnconfigure(1, weight=0)
for i in range(len(options) + 1):
    left_frame.rowconfigure(i, weight=0)
left_frame.rowconfigure(len(options) + 1, weight=1)

# Add a label to the right frame (placeholder for future content)
ttk.Label(right_frame, text="Future Content Area", style='TLabel').pack(expand=True)


# Meter Config Tab
meter_config_frame = ttk.Frame(programming_notebook, style='TFrame')
programming_notebook.add(meter_config_frame, text='Meter Config')

# Relay Controls Frame
relay_controls_frame = ttk.Frame(meter_config_frame, style='TFrame', padding=10)
relay_controls_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nw')
relay_controls_frame.configure(borderwidth=2, relief='groove')

# Relay Controls Label
relay_controls_label = ttk.Label(relay_controls_frame, text="Relay Controls", style='TLabel')
relay_controls_label.pack(side=tk.TOP, fill=tk.X)

# Connect/Disconnect Button
connect_button = ttk.Button(relay_controls_frame, text="Connect/Disconnect", command=lambda: perform_connect(), style='TButton', width=20)
connect_button.pack(side=tk.LEFT, padx=(0, 10))


# Rollover tab
rollover_frame = ttk.Frame(notebook, style='TFrame')
notebook.add(rollover_frame, text='Rollover')

rollover_notebook = ttk.Notebook(rollover_frame, style='Sub.TNotebook')
rollover_notebook.pack(expand=True, fill='both', padx=10, pady=10)

# Power Fail tab
power_fail_frame = ttk.Frame(rollover_notebook, style='TFrame')
rollover_notebook.add(power_fail_frame, text='Power Fail')

# ... (keep the Power Fail tab content, but use the new styles) ...

# Dummy Tab 1 (Low Voltage)
dummy_tab1_frame = ttk.Frame(rollover_notebook, style='TFrame')
rollover_notebook.add(dummy_tab1_frame, text='Low Voltage')

# Dummy Tab 2 (High Voltage)
dummy_tab2_frame = ttk.Frame(rollover_notebook, style='TFrame')
rollover_notebook.add(dummy_tab2_frame, text='High Voltage')

# DLS_MD_RTC_Forcing tab
MDLS_frame = ttk.Frame(notebook, style='TFrame', padding=20)
notebook.add(MDLS_frame, text='DLS_MD_RTC_Forcing')

def show_fields():
    selection = radio_var.get()
    count_days_frame.pack(side="top", pady=(10, 5))
    
    if selection == 1:  # Billing
        count_label.grid(row=0, column=0, padx=(0, 5))
        count_entry.grid(row=0, column=1, padx=(0, 5))
        days_label.grid_remove()
        days_entry.grid_remove()
    elif selection == 2:  # Daily Load Profile
        days_label.grid(row=0, column=2, padx=(10, 5))
        days_entry.grid(row=0, column=3)
        count_label.grid_remove()
        count_entry.grid_remove()
    elif selection == 3:  # Run Both
        count_label.grid(row=0, column=0, padx=(0, 5))
        count_entry.grid(row=0, column=1, padx=(0, 5))
        days_label.grid(row=0, column=2, padx=(10, 5))
        days_entry.grid(row=0, column=3)

def disable_ui_elements():   
    start_button['state'] = 'disabled'    
    stop_button['state'] = 'normal'
    radio1['state'] = 'disabled'
    radio2['state'] = 'disabled'
    rtc_duration_entry['state'] = 'disabled'
    count_entry['state'] = 'disabled'
    radio3['state'] = 'disabled'
    days_entry['state'] = 'disabled'

def enable_ui_elements():    
    start_button['state'] = 'normal'    
    stop_button['state'] = 'disabled'
    radio1['state'] = 'normal'
    radio2['state'] = 'normal'
    rtc_duration_entry['state'] = 'normal'
    count_entry['state'] = 'normal'
    radio3['state'] = 'normal'
    days_entry['state'] = 'normal'

# Custom color scheme
bg_color = "#f2f2f2"
accent_color = "#4c6ef5"
text_color = "#333333"

# Custom fonts
custom_font = font.Font(family="Helvetica", size=10)
button_font = font.Font(family="Helvetica", size=9, weight="bold")

# Update style for ttk widgets
style = ttk.Style()
style.configure("TLabel", foreground=text_color, font=custom_font)
style.configure("TEntry", fieldbackground="white", font=custom_font)
style.configure("TButton", background=accent_color, foreground="black", font=button_font, padding=5)
style.configure("TRadiobutton", foreground=text_color, font=custom_font)
style.configure("TCombobox", fieldbackground="white", font=custom_font)
style.configure("Horizontal.TProgressbar", background=accent_color)

# Frame for Radio Buttons
radio_frame = ttk.Frame(MDLS_frame)
radio_frame.pack(pady=10)

# Radio buttons
radio_var = tk.IntVar()
radio_var.set(1)

radio1 = ttk.Radiobutton(radio_frame, text="Billing", variable=radio_var, value=1, command=show_fields)
radio1.grid(row=0, column=0, padx=10)

radio2 = ttk.Radiobutton(radio_frame, text="Daily Load Profile", variable=radio_var, value=2, command=show_fields)
radio2.grid(row=0, column=1, padx=10)

radio3 = ttk.Radiobutton(radio_frame, text="Run Both", variable=radio_var, value=3, command=show_fields)
radio3.grid(row=0, column=2, padx=10)

# RTC Duration
rtc_duration_label = ttk.Label(MDLS_frame, text="RTC Duration (min)")
rtc_duration_label.pack(pady=(20, 5))

rtc_duration_var = tk.StringVar(value="1")
rtc_duration_entry = ttk.Spinbox(MDLS_frame, textvariable=rtc_duration_var, from_=1, to=30, state="readonly")
rtc_duration_entry.pack()

# Frame to hold the Count and Days fields
count_days_frame = ttk.Frame(MDLS_frame)
# Note: We don't pack this frame here, as it will be packed by the show_fields() function

# Count
count_label = ttk.Label(count_days_frame, text="Count")
count_var = tk.StringVar(value="1")
count_entry = ttk.Spinbox(count_days_frame, textvariable=count_var, from_=1, to=12, state="readonly")

# Days
days_label = ttk.Label(count_days_frame, text="Days")
days_var = tk.StringVar(value="1")
days_entry = ttk.Spinbox(count_days_frame, textvariable=days_var, from_=1, to=100)

def start_rtc_forcing():
    test_val = radio_var.get()
    test_duration = int(rtc_duration_var.get())
    bill_count = int(count_var.get()) if test_val in [1, 3] else 0
    LS_days = int(days_var.get()) if test_val in [2, 3] else 0
    args = ['main.py'] + get_cmd_args() 

    threading.Thread(target=run_rtc_forcing, args=(test_val, test_duration, bill_count, LS_days, args)).start()

class RealTimeStringIO(io.StringIO):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def write(self, s):
        super().write(s)
        if self.callback:
            self.callback(s)

def run_rtc_forcing(test_val, test_duration, bill_count, LS_days, args):
  global stop_event
  stop_event.clear()  # Clear the stop event at the start of the process
  disable_ui_elements()

  def real_time_print(message):
    print_log(message.rstrip())  # Remove trailing newline before printing

  output = RealTimeStringIO(real_time_print)

  try:
    with redirect_stdout(output), redirect_stderr(output):
      start_time = time.time()

      rtc_force = RTC_forcing(test_val, test_duration, bill_count, LS_days, args, stop_event)
      rtc_force.printvals()
      rtc_force.start_test()

      end_time = time.time()
      duration = end_time - start_time

      print_log(f"Finished running RTC forcing in {duration:.2f} seconds")
      print_log("-" * 30)

  except Exception as e:
    print_log(f"Error in RTC forcing: {str(e)}")

  finally:
    enable_ui_elements()

stop_event = threading.Event()

def stop_rtc_forcing():
    global stop_event
    stop_event.set()
    print_log("Stopping RTC forcing process...")
# Buttons
button_frame = ttk.Frame(MDLS_frame)
button_frame.pack(pady=20)
start_button = ttk.Button(button_frame, text="Start", command=start_rtc_forcing)
start_button.pack(side=tk.LEFT, padx=10)

stop_button = ttk.Button(button_frame, text="Stop", command=stop_rtc_forcing)
stop_button.pack(side=tk.LEFT, padx=10)

# Call show_fields() initially to set up the correct layout
show_fields()
def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        
        root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

# Start the main event loop
root.mainloop()