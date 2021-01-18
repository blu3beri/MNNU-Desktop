# MNNU-Desktop

### How to use the GUI
1. Install the required Python modules using: `pip3 -r requirements.txt`
2. Compile the resource file using: `pyrcc5 resources.qrc -o resource_rc.py`
3. Change directory to ui and compile the .ui files:
    1. Compile mainwindow.ui using: `pyuic5 mainwindow.ui -o MainWindow.py`
    2. Compile pending_connections.ui using: `pyuic5 pending_connections.ui -o pending_connections.py`
    3. Compile pending_records.ui using: `pyuic5 pending_records.ui -o pending_records.py`
    4. Compile settings.ui using: `pyuic5 settings.ui -o settings.py`
4. execute main.py using: `python3 main.py`

### Folder structure
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

### CHECKLIST
- [x] Revocation van een credential (gewoon weggehaald voor nu niet gefixed)
- [x] Credential versturen naar de mobile agent
- [x] Present-proof van dokter naar mobiel aanvragen
- [x] present-proof van mobile naar dokter
- [x] Optionele waardes in credential
- [ ] Credentials revoken
- [ ] Credentials overschrijven
- [x] Presen-proof delen van een credential vragen
- [x] auto-accept dingen uitzetten
- [x] alle requests handmatig accepteren
- [x] webhook relay
- [ ] Niet meer via admin api
