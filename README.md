# MNNU-Desktop

### How to use the GUI
1. Install the required Python modules using: `pip3 -r requirements.txt`
2. Compile mainwindow.ui using: `pyuic5 mainwindow.ui -o MainWindow.py`
3. Compile the resource file using: `pyrcc5 resources.qrc -o resource_rc.py`
4. execute main.py using: `python3 main.py`

### CHECKLIST -> 1
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


### CHECKLIST -> 2
- [ ] Niet meer via admin api
- [ ] design?
 
### VRAGEN
- Moeten we auto accept van credentials versturen erin laten?
- Mag het via de admin endpoint voor POC?
- Moet TRACE aan of uit bij de endpoints?
- Cred def gaat soms de eerste keer fout, na een retry gaat ie weer goed, how come :(?
