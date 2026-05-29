# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Comandi

```bash
uv sync                          # installa dipendenze (runtime + dev)
uv run autorizzazioni            # CLI: elabora l'anno più recente in data/input/
uv run autorizzazioni --anno 2026 --formato json
uv run pytest                    # suite completa
uv run pytest tests/test_unit.py # solo unit test (veloci, nessun PDF richiesto)
uv run pytest -k test_altavilla  # singolo test per nome
uv run pytest --cov=autorizzazioni_agesci --cov-report=term-missing
```

## Architettura

Tutta la logica di parsing vive in `src/autorizzazioni_agesci/parser.py`. L'API pubblica è una singola funzione: `parse_year(input_dir, year)` → `list[dict]`. La CLI in `cli.py` la chiama e scrive CSV o JSON.

### Pipeline di parsing

1. `parse_year()` itera i PDF in `data/input/<anno>/`, invoca `_parse_pdf()` su ciascuno e per ogni codice gruppo **mantiene solo il PDF con la data `(dati aggiornati al …)` più recente** (gestione duplicati Primaria/Secondaria).
2. `_parse_pdf()` apre il PDF con pdfplumber, scarta le pagine che contengono `"Formazione e impegni formativi"`, poi scorre le righe di testo line-by-line accumulando blocchi persona.
3. Un **blocco persona** inizia quando una riga corrisponde a `^\d{4,8}\s+[A-Z]…Funzione/Incarico:`. Le righe successive (nascita, eventuale FOCA isolato) vengono accumulate finché non arriva un nuovo header di unità o un nuovo codice persona. Il flush avviene in `flush_person()`.
4. `_parse_person_block(lines)` estrae dal blocco accumulato: codice, nome, funzione, genere, livello FOCA.

### Edge case critici nel parsing

**Funzione su più righe.** Il PDF genera testo dove `Funzione/Incarico: ASSISTENTE ECCLESIASTICO DI` si interrompe e `GRUPPO` appare alla fine della riga di nascita:
```
1234567 BIANCHI MARIO Funzione/Incarico: ASSISTENTE ECCLESIASTICO DI Anno di ingresso in COCA: 2015
M Nato a: ROMA il 01/01/1970 GRUPPO
Livello FOCA: 2
```
Il parser rileva l'assenza di `Livello FOCA:` nella riga di nascita → raccoglie il testo dopo la data come continuazione della funzione → cerca `Livello FOCA:` sulla terza riga.

**"Ultima formaz. CG" che va a capo.** La riga di nascita può terminare con `Livello FOCA: 5 Ultima formaz. CG: 03/03/2024 CAMPO` e la riga successiva porta `PER CAPI GRUPPO`. Siccome `Livello FOCA:` è già sulla riga di nascita, la funzione è completa e la terza riga viene ignorata.

### Classificazioni

**Branca** (da nome unità):

| Keyword | Branca |
|---|---|
| `COMUNITA` | `Adulti` |
| `BRANCO`, `CERCHIO` | `L/C` |
| `REPARTO` | `E/G` |
| `CLAN`, `FUOCO` | `R/S` |
| tutto il resto | `SCONOSCIUTA` |

**Livello FOCA**: intero 0–5 estratto direttamente dal PDF (0 = non trovato).

**Genere unità**: `MASCHILE` / `FEMMINILE` nel nome → come da nome; altrimenti `MISTO` (default).

## Test di regressione

`tests/test_unit.py` testa le funzioni helper in isolamento (nessun PDF). `tests/test_integration.py` usa i PDF reali in `data/input/2026/` come fixture di modulo. Valori attesi ancorati:

- **218 record totali, 12 gruppi** per l'anno 2026
- `E2000`: deduplicazione corretta — il codice socio presente solo nella Secondaria (15/12/2025) non compare nell'output della Primaria (31/10/2025)
- `E3279`: 16 record; un capo con funzione su più righe (`"ASSISTENTE ECCLESIASTICO DI GRUPPO"`) ha `livello_foca == 2`

Se si aggiungono PDF a un anno esistente, aggiornare `test_total_records` in `tests/test_integration.py`.

## Aggiungere un nuovo anno

1. Creare `data/input/<anno>/` e inserire i PDF.
2. `uv run autorizzazioni --anno <anno>` genera `data/output/<anno>.csv`.
3. Aggiungere un fixture `records_<anno>` e un test `test_total_records` in `test_integration.py` per ancorare il conteggio.
