# PyStudioMusic

[![Licenza: GPLv3](https://img.shields.io/badge/Licenza-GPLv3-blue.svg)](LICENSE) [![Piattaforma: Debian%2FUbuntu](https://img.shields.io/badge/Piattaforma-Debian%2FUbuntu-orange.svg)](https://www.debian.org/)

Manager GTK3 professionale per software audio e di produzione musicale su Debian e Ubuntu.

---

## Sommario

- [Descrizione](#descrizione)  
- [Funzionalità](#funzionalità)  
- [Screenshot](#screenshot)  
- [Requisiti](#requisiti)  
- [Installazione](#installazione)  
- [Utilizzo](#utilizzo)  
- [Configurazione](#configurazione)  
- [App personalizzate](#app-personalizzate)  
- [Contribuire](#contribuire)  
- [Licenza](#licenza)  
- [Ringraziamenti](#ringraziamenti)  

---

## Descrizione

PyStudioMusic è un’applicazione desktop basata su GTK3 che ti permette di installare, rimuovere, avviare e gestire con un’interfaccia chiara i tuoi strumenti audio e di produzione musicale preferiti.  

Progettata per utenti Debian e Ubuntu, offre un’esperienza moderna e intuitiva per DAW, editor, server audio, sintetizzatori e molto altro.

---

## Funzionalità

- Catalogo curato di applicazioni audio e musicali  
- Installazione, rimozione o purge con un clic  
- Visualizzazione in tempo reale dello stato (installato/non installato)  
- Avvio contemporaneo di più applicazioni  
- Aggiunta, modifica e rimozione di app personalizzate  
- Organizzazione per categorie (DAW, Editor, Server, Sintetizzatore, ecc.)  
- Pannello di aiuto e documentazione integrato  
- File di configurazione in `~/.pystudiomusic` per backup e personalizzazioni  

---

## Screenshot

| Gestione App                   | Aggiungi App                      |
| ------------------------------ | --------------------------------- |
| ![Gestione](docs/screenshots/manage.png) | ![Aggiungi](docs/screenshots/add.png) |

| Stato App                      | Pannello Aiuto                    |
| ------------------------------ | --------------------------------- |
| ![Stato](docs/screenshots/status.png) | ![Aiuto](docs/screenshots/help.png) |

---

## Requisiti

- Debian 11+ o Ubuntu 20.04+  
- Python 3.8 o superiore  
- GTK 3 (`gir1.2-gtk-3.0`)  
- PyGObject per Python 3 (`python3-gi`, `python3-gi-cairo`)  

---

## Installazione

1. Clona il repository:  
   ```bash
   git clone https://github.com/yourusername/PyStudioMusic.git
   cd PyStudioMusic
   ```

2. Installa le dipendenze di sistema:  
   ```bash
   sudo apt update
   sudo apt install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0
   ```

3. Rendi eseguibile lo script principale:  
   ```bash
   chmod +x PyStudioMusic.py
   ```

4. (Opzionale) Installa la voce di menu desktop:  
   ```bash
   sudo cp data/PyStudioMusic.desktop /usr/share/applications/
   update-desktop-database
   ```

---

## Utilizzo

Avvia l’applicazione da terminale o dal menu desktop:

```bash
./PyStudioMusic.py
```

Oppure, se hai installato la voce di menu, cerca **PyStudioMusic** nelle tue applicazioni.

---

## Configurazione

Tutte le impostazioni utente e le app personalizzate sono salvate in:

```
~/.pystudiomusic/
└── apps.custom      # Definizioni delle app personalizzate
```

Puoi eseguire il backup o modificare manualmente questi file; l’interfaccia li ricaricherà al prossimo avvio.

---

## App personalizzate

1. Vai alla sezione **Add App** nel menu laterale.  
2. Compila i campi:
   - **Unique ID:** identificatore univoco  
   - **Name:** nome visualizzato  
   - **Category:** scegli da elenco  
   - **Description:** breve descrizione  
   - **APT Package:** nome del pacchetto Debian  
   - **Launch Command:** comando di avvio  
3. Clicca **Add to Catalog**.  
4. Riavvia PyStudioMusic per vedere la nuova voce nel catalogo.

---

## Contribuire

I contributi sono i benvenuti! Per favore:

1. Fai fork del progetto  
2. Crea un branch per la tua feature:
   ```bash
   git checkout -b feature/NomeFeature
   ```
3. Aggiungi le tue modifiche e committa:
   ```bash
   git commit -m "Descrizione delle modifiche"
   git push origin feature/NomeFeature
   ```
4. Apri una pull request descrivendo le modifiche apportate.

Seguι il codice esistente e aggiungi commenti e test ove opportuno.

---

## Licenza

Questo progetto è rilasciato sotto licenza **GPLv3**. Vedi il file [LICENSE](LICENSE) per i dettagli.

---

## Ringraziamenti

- Grazie alla comunità open-source audio per gli eccellenti strumenti  
- Icone e risorse are courtesy of the GNOME Project  
- Ispirato allo script originale StudioBand di Luca Bocaletto
