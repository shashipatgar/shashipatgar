# Meter Programming Application Documentation

## Project Overview
This project is a meter programming application that utilizes the Gurux DLMS library for communication with meters. It provides a graphical user interface for various meter programming and testing operations.

## Project Structure

The project consists of the following main files:

1. **GXDLMSReader.py**: Part of the Gurux library, handling DLMS reader functionality.
2. **GXCmdParameter.py**: Part of the Gurux library, handling command parameters.
3. **GXSettings.py**: Part of the Gurux library, managing settings.
4. **main.py**: Contains functions for Billing and Daily Load Survey tests.
5. **functions.py**: Contains supporting functions for meter programming, imported by other files.
6. **GUI.py**: Implements the graphical user interface using Tkinter.
7. **selectedTest.py**: Executes all programming tests.

## Libraries Used

The project relies on the following libraries:

- gurux-common==1.0.13
- gurux-serial==1.0.20
- gurux_dlms==1.0.156
- gurux_net==1.0.21
- pyserial==3.5
- setuptools==70.3.0
- pyinstaller==6.9.0
- Tkinter (built-in Python library for GUI)

## Development Environment Prerequisites

To set up the development environment:

1. Install Python (version compatible with the libraries used).
2. Use Visual Studio Code or any preferred code editor.
3. Install the required libraries using pip:
 pip install gurux-common==1.0.13 gurux-serial==1.0.20 gurux_dlms==1.0.156 gurux_net==1.0.21 pyserial==3.5 setuptools==70.3.0 pyinstaller==6.9.0
 
## Key Components

### GXDLMSReader.py, GXCmdParameter.py, GXSettings.py
These are core components of the Gurux DLMS library, providing essential functionality for DLMS communication with meters.

### main.py
Contains the main logic for Billing and Daily Load Survey tests. These are likely the primary operations performed on the meters.

### functions.py
A collection of utility functions supporting various meter programming operations. These functions are imported and used across other files in the project.

### GUI.py
Implements the graphical user interface using Tkinter. This file creates the visual components of the application and handles user interactions.

### selectedTest.py
Orchestrates the execution of all programming tests. This file likely contains the logic for running various tests on the meters based on user selection or predefined criteria.

## User Interface

The application uses Tkinter for its graphical user interface. Key features of the UI might include:
- Test selection options
- Configuration settings for meter communication
- Execution buttons for tests
- Display areas for test results and logs

## Building the Executable

To create a standalone executable of the application:

1. Ensure pyinstaller is installed: `pip install pyinstaller==6.9.0`
2. Use the following command to build the executable:
    pyinstaller --onefile --windowed GUI.py
    
This will create a single executable file.

Alternatively, other tools like cx_Freeze can be used for creating the executable.

## Best Practices

- Regularly update the Gurux libraries to ensure compatibility with the latest meter protocols.
- Implement comprehensive error handling and logging throughout the application.
- Maintain clear separation of concerns between UI, business logic, and data handling.
- Document any meter-specific operations or configurations for future reference.

## Future Enhancements

Consider the following for future development:
- Implementing automated testing scripts
- Adding support for additional meter types or protocols
- Enhancing the UI for better user experience
- Implementing data export features for test results

grux python library available : https://github.com/gurux/gurux.dlms.python



# Project Setup Guide

## Prerequisites

1. Install Python (preferably Python 3.8 or later)
2. Install Visual Studio Code (VSCode) or any preferred code editor

## Setup Steps

1. **Create Project Folder**
   Open a terminal or command prompt and run:

    mkdir meter_programming_project
    cd meter_programming_project

2. **Create a Virtual Environment**
    python -m venv venv

3. **Activate the Virtual Environment**
    venv\Scripts\activate


4. **Copy the Project Files**
    Copy all project files into the `meter_programming_project` folder.

5. **Navigate to the Project Directory**
    cd meter_programming_project

6. **Install Requirements**
    pip install -r requirements.txt

7. **Verify Installation**
    pip list

    This should display all the installed packages, including gurux libraries.

## Development Tips

- Always activate the virtual environment before working on the project
- Update `requirements.txt` if you add new dependencies:
    pip freeze > requirements.txt

## Troubleshooting

- If you encounter any "module not found" errors, ensure you're in the activated virtual environment and all requirements are installed.
- For Windows users: If you can't activate the virtual environment, you might need to change PowerShell execution policy:
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser


Now your setup is ready. Happy coding!