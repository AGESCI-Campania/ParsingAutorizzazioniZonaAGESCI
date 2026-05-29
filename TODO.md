# Parsing delle autorizzazioni dei gruppi

## Descrizione
Ogni anno, i gruppi dell'AGESCI inviano le autorizzazioni per la Comunità Capi. I file di autorizzazione è in formato PDF e contiene informazioni cruciali per la gestione delle attività dei gruppi. L'obiettivo di questo progetto è sviluppare un sistema di parsing che estragga automaticamente le informazioni rilevanti da questi file PDF, facilitando così la gestione e l'organizzazione delle attività dei gruppi.

## Obiettivi
1. **Sviluppare un parser PDF**: Creare un sistema che possa leggere e interpretare i file PDF contenenti le autorizzazioni dei gruppi.
2. **Sviluppare una libreria che restituisca i dati in un formato strutturato**: Convertire le informazioni estratte in un formato facilmente utilizzabile, come JSON o CSV. Deve essere una liberia python installabile via PIP.
3. **Automatizzare il processo di parsing**: Implementare un sistema che possa eseguire il parsing in modo automatico ogni volta che vengono ricevuti nuovi file PDF.
4. **Input fornito da cartella**: Il sistema deve essere in grado di prendere i file PDF da una cartella specifica, elaborare i dati e restituire un output strutturato.
5. **Output atteso**: L'output deve essere salvato in data/output con l'anno di elaborazione e formato .json o .csv a seconda del formato scelto. Ogni anno fornisce in output un unico file con tutte le autorizzazioni dei gruppi di quell'anno, se il file esiste già deve essere sovrascritto. Per ogni capo deve essere indicata la sua unità di appartenenza, la comunità capi, la branca, il genere e se è un capo o un capo in formazione. Se non è possibile riconoscere la branca, va inserita come "SCONOSIUTA". Le unità pono essere "MASCHILE", "FEMMINILE" o "MISTO", se non specificato si intende "MISTO". Alcuni PDF contengono delle pagine con "Formazione e impegni formativi" queste pagine possono essere completamente ignorate. Ogni capo può comparire più volte nello stesso PDF di autorizzazioni, in quanto può essere in più unità, quindi il codice socio (numero di 4-8 cifre presente nel pdf sulla riga di ogni singolo capo nella tabella) non è un identificativo univoco. Per ogni capo, in ogni branca, va indicato anche la "Funzione/Incarico:" che è presente nella tabella del PDF, se non specificato va indicato "SCONOSCIUTA".

## Tecnologie Utilizzate
- **Python**: Per lo sviluppo del parser e della libreria di estrazione dei dati
- **PDF Parsing Libraries**: Utilizzo di librerie come `PyPDF2`, `pdfminer.six` o `pdfplumber` per estrarre il testo dai file PDF.
- **JSON/CSV**: Per la strutturazione dei dati estratti.
- **PIP**: Per la distribuzione della libreria Python.
- **UV**: Per la creazione di un'interfaccia a riga di comando (CLI) per facilitare l'uso del parser.
- **GitHub**: Per la gestione del codice sorgente e la collaborazione.
- **MISE**: PEr la gestione dell'ambiente del progetto.

# Difficoltà e Considerazioni
- **Struttura del PDF**: i file PDF sono visivamente strutturati, ma l'esportazione del testo restitusce un testo confuso e con le porzioni che si mescolano tra loro. Sarà necessario implementare un sistema di riconoscimento dei pattern per identificare correttamente le informazioni rilevanti.
- **PDf ripetuti**: Alcuni gruppi potrebbero avere più autorizzazioni per lo steeso anno, le informazioni su gruppo e anno sono in questa riga, di esempio per il gruppo Altavilla, con codice E3279 per il 2006: "Modello Autorizzazione Unità - Anno 2026 Gruppo: ALTAVILLA - E3279", per selezionare quello corretto va scelto il più recente in base alla data di aggiornamento che si trova nella stringa "(dati aggiornati al 31/10/2025)"
- **Struttura delle cartelle**: L'input deve essere preso da data/input, qui dentro c'è una cartella con l'anno per ogni anno. La versione CLI deve permettere di specificare l'anno da cui prendere i file PDF, se non specificato deve prendere l'anno più recente. L'output deve essere salvato in data/output con l'anno di elaborazione e formato .json o .csv a seconda del formato scelto. Ogni anno fornisce in output un unico file con tutte le autorizzazioni dei gruppi di quell'anno, se il file esiste già deve essere sovrascritto. La versione CLI deve permettere di specificare il formato di output, se non specificato deve essere CSV.
- **Riconoscere la branca:** Ogni capo nel pdf può essere inserito nella unità in cui presta servizio, oltre che nella comunità capi (in genere G1 COMUNITA` CAPI). Le unità possono essere per le branche L/C, E/G, R/S, ma non si chiamano così. Le unità per la branca L/C contengono sempre "BRANCO" o "CERCHIO", quelle per la branca E/G contengono sempre "REPARTO", quelle per la branca R/S contengono sempre "CLAN" o "FUOCO". Se non è possibile riconoscere la branca, va inserita come "SCONOSIUTA". Le unità pono essere "MASCHILE", "FEMMINILE" o "MISTO", se non specificato si intende "MISTO"
- **Pagina da ignorare**: Alcuni PDF contengono delle pagine con "Formazione e impegni formativi" queste pagine possono essere completamente ignorate
