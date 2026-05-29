# autorizzazioni-agesci

Parser per le autorizzazioni annuali AGESCI dei gruppi scout. Legge i PDF ufficiali del modello "Autorizzazione Unità" ed estrae i dati di ogni capo (unità, branca, genere, funzione, tipo) in un file CSV o JSON.

## Requisiti

- Python ≥ 3.10
- [uv](https://docs.astral.sh/uv/) – gestore pacchetti e runner
- [mise](https://mise.jdx.dev/) – gestore versioni (opzionale, gestisce Python + uv)

## Installazione

### Con mise (consigliato)

```bash
mise install        # installa Python e uv dalla versione in .mise.toml
uv sync             # installa le dipendenze nel virtualenv locale
```

### Solo con uv

```bash
uv sync
```

### Come libreria installabile via pip

```bash
pip install git+https://github.com/…/autorizzazioni.git
# oppure, in locale:
pip install .
```

## Struttura delle cartelle

```
data/
  input/
    2026/         ← PDF dell'anno 2026
      AutorizzazionePrimariaGruppo1.pdf
      AutorizzazioneSecondariaGruppo2.pdf
      …
  output/
    2026.csv      ← generato dalla CLI
    2026.json
```

Metti i PDF nella cartella `data/input/<anno>/`. Se per lo stesso gruppo esistono più PDF (es. una versione "Primaria" e una "Secondaria"), viene selezionato automaticamente il più recente in base alla data nel campo `(dati aggiornati al …)`.

## Utilizzo CLI

```bash
# CSV dell'anno più recente (default)
uv run autorizzazioni

# Anno specifico
uv run autorizzazioni --anno 2026

# Formato JSON
uv run autorizzazioni --anno 2026 --formato json

# Cartelle personalizzate
uv run autorizzazioni --input /percorso/input --output /percorso/output

# Aiuto
uv run autorizzazioni --help
```

L'output viene salvato in `data/output/<anno>.csv` (o `.json`). Se il file esiste già viene sovrascritto.

## Utilizzo come libreria

```python
from autorizzazioni_agesci import parse_year

records = parse_year("data/input", year=2026)
# records è una lista di dict con le chiavi:
# codice_socio, nome, comunita_capi, unita, branca,
# genere_unita, genere, tipo_capo, funzione, anno
```

### Schema dell'output

| Campo | Valori possibili | Descrizione |
|---|---|---|
| `codice_socio` | stringa numerica | Codice AGESCI del capo |
| `nome` | stringa maiuscola | Cognome e nome |
| `comunita_capi` | es. `ALTAVILLA - E3279` | Nome e codice del gruppo |
| `unita` | es. `L1 BRANCO/CERCHIO MISTO` | Codice e nome dell'unità |
| `branca` | `L/C`, `E/G`, `R/S`, `SCONOSCIUTA` | Branca scout |
| `genere_unita` | `MASCHILE`, `FEMMINILE`, `MISTO` | Genere dell'unità |
| `genere` | `M`, `F` | Genere del capo |
| `tipo_capo` | `CAPO`, `CAPO IN FORMAZIONE` | FOCA ≤ 2 → in formazione |
| `funzione` | stringa maiuscola | Funzione/Incarico nel PDF |
| `anno` | intero | Anno scout dell'autorizzazione |

## Sviluppo e test

```bash
# Esegui la suite completa
uv run pytest

# Con copertura
uv run pytest --cov=autorizzazioni_agesci --cov-report=term-missing
```

I test sono suddivisi in:

- `tests/test_unit.py` – funzioni di parsing isolate (nessun PDF reale)
- `tests/test_integration.py` – parsing completo sui PDF reali + test CLI

## Note sul parsing

- Le pagine **"Formazione e impegni formativi"** vengono ignorate completamente.
- La funzione/incarico può spezzarsi su più righe nel PDF; il parser ricompone correttamente il testo.
- Il campo `tipo_capo` si basa sul **Livello FOCA**: ≤ 2 → `CAPO IN FORMAZIONE`, ≥ 3 → `CAPO`.
- Il genere dell'unità è `MISTO` di default se non specificato nel nome dell'unità.
