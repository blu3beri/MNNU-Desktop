# MNNU-Desktop
Desktop application for the MNNU care group made for healthcare providers.

# Table of Contents
* [Table of Contents](#table-of-contents)
* [Installation &amp; usage](#installation--usage)
* [Folder structure](#folder-structure)
* [Checklist](#checklist)
* [Application development](#application-development)
  * [IDE](#ide)
  * [Code documentation](#code-documentation)
  * [Naming convention](#naming-convention)
  * [Logging](#logging)
* [Known bugs](#known-bugs)

# Installation & usage
1. Clone or download this repository and unpack the files.
   1. Open a terminal inside the `MNNU-Desktop` folder.
2. Install the required Python modules using: `pip3 -r requirements.txt`
3. Compile the resource file using: `pyrcc5 resources.qrc -o resource_rc.py`
4. Change directory to ui and compile the .ui files:
    1. Compile mainwindow.ui using: `pyuic5 mainwindow.ui -o MainWindow.py`
    2. Compile pending_connections.ui using: `pyuic5 pending_connections.ui -o pending_connections.py`
    3. Compile pending_records.ui using: `pyuic5 pending_records.ui -o pending_records.py`
    4. Compile settings.ui using: `pyuic5 settings.ui -o settings.py`
5. execute main.py using: `python3 main.py`

# Folder structure
    .
    ├── controller              # Controllers for ui dialogs
    ├── helpers                 # Helper functions (utilities)
    ├── img                     # Images used inside the QT UI
    ├── library                 # Custom libraries (ApiHandler)
    ├── schemas                 # Schema.py files
    ├── tests                   # Tests for the ApiHandler class
    ├── ui                      # QT .ui files
    ├── main.py                 # Program entrypoint
    ├── README.md
    ├── requirements.txt        # Python module requirements
    └── resource.qrc            # QT resource file

# Checklist

**NOTE:** Checklist might be incomplete, code itself also includes TODO comments.

- [x] Generate QR invitation code to create a connection with the mobile app.
   - [x] Dialog menu to show pending connections.
   - [x] Ability to remove a pending connection.
- [x] Remove active connection with confirmation pop-up.
- [x] Send proof-request to mobile app.
   - [x] Specify which credential to send a proof request for.
   - [x] Supply a reason with the proof-request.
   - [x] Dialog menu to show pending proof-requests.
      - [x] Button inside dialog menu to verify received credential.
- [x] Settings menu.
   - [x] Select profession of healthcare provider (**does nothing yet**).
   - [x] Setup ACA-Py server IP/Port (**not saved on application exit**).
   - [x] Button to test connection with ACA-Py server.
- [ ] Creating and sending healthcare provider diagnostics to mobile app.
- [ ] Overwriting credentials (when updating existing credentials).
- [ ] Credential revocation.
- [ ] Secure the Admin Api.

# Application development
This section describes the basics in order to continue developing the Desktop application.
Basic knowledge of QT Creator and Python is mandatory

## IDE
The IDE used for development is [PyCharm](https://www.jetbrains.com/pycharm/download). PyCharm will show all TODO comments inside the code in a structured manner. See the PyCharm [documentation](https://www.jetbrains.com/help/pycharm/using-todo.html) for more information.

## Code documentation
All `.py` files are documented using Python [docstrings](https://www.python.org/dev/peps/pep-0257/).

## Naming convention
Private & "helper" functions are prefixed with a double underscore example: `def __example():`.

## Logging
Every action caused by the user eq. button presses are being logged and written to a file `MNNU-Desktop.log` and the terminal.

# Known bugs
No known bugs, please create an issue when finding any (with clear steps to reproduce).