"""Integration tests using the real PDF files in data/input/."""

import pytest
from pathlib import Path

from autorizzazioni_agesci.parser import parse_year, _parse_pdf

DATA_INPUT = Path(__file__).parent.parent / "data" / "input"

pytestmark = pytest.mark.skipif(
    not DATA_INPUT.exists(),
    reason="data/input directory not found",
)


@pytest.fixture(scope="module")
def records_2026():
    return parse_year(DATA_INPUT, year=2026)


# ── Dataset-level assertions ──────────────────────────────────────────────────

def test_total_records(records_2026):
    assert len(records_2026) == 218


def test_total_groups(records_2026):
    groups = {r["codice_gruppo"] for r in records_2026}
    assert len(groups) == 12


def test_all_records_have_required_fields(records_2026):
    required = {"codice_socio", "nome", "gruppo", "codice_gruppo", "unita",
                "branca", "genere_unita", "genere", "livello_foca", "funzione", "anno"}
    for r in records_2026:
        assert required.issubset(r.keys()), f"Missing fields in {r}"


def test_anno_is_2026(records_2026):
    assert all(r["anno"] == 2026 for r in records_2026)


def test_branca_values(records_2026):
    valid = {"L/C", "E/G", "R/S", "Adulti", "SCONOSCIUTA"}
    for r in records_2026:
        assert r["branca"] in valid, f"Invalid branca: {r['branca']}"


def test_genere_unita_values(records_2026):
    valid = {"MASCHILE", "FEMMINILE", "MISTO"}
    for r in records_2026:
        assert r["genere_unita"] in valid


def test_genere_values(records_2026):
    for r in records_2026:
        assert r["genere"] in ("M", "F"), f"Invalid genere: {r['genere']}"


def test_livello_foca_values(records_2026):
    for r in records_2026:
        assert isinstance(r["livello_foca"], int), f"livello_foca non intero: {r}"
        assert 0 <= r["livello_foca"] <= 5, f"livello_foca fuori range: {r}"


def test_no_empty_nome(records_2026):
    for r in records_2026:
        assert r["nome"].strip(), f"Empty nome in record: {r}"


def test_no_empty_unita(records_2026):
    for r in records_2026:
        assert r["unita"].strip(), f"Empty unità in record: {r}"


# ── Deduplication: most-recent PDF wins per group ─────────────────────────────

def test_avellino4_uses_secondaria(records_2026):
    """Secondaria Avellino4 (15/12/2025) is more recent than Primaria (31/10/2025); must be selected."""
    av4 = [r for r in records_2026 if r["codice_gruppo"] == "E2000"]
    codici = {r["codice_socio"] for r in av4}
    assert "415049" in codici


def test_montoro_uses_secondaria(records_2026):
    """Secondaria Montoro1 (15/01/2026) is more recent than Primaria (07/11/2025)."""
    montoro = [r for r in records_2026 if r["codice_gruppo"] == "E3471"]
    assert montoro, "Montoro1 (E3471) must appear in output"


def test_avellino3_uses_secondaria(records_2026):
    """Secondaria Avellino3 (08/05/2026) is most recent."""
    av3 = [r for r in records_2026 if r["codice_gruppo"] == "E1681"]
    assert av3, "Avellino3 (E1681) must appear in output"


# ── Known records: Altavilla (E3279) ─────────────────────────────────────────

@pytest.fixture(scope="module")
def altavilla(records_2026):
    return [r for r in records_2026 if r["codice_gruppo"] == "E3279"]


def test_altavilla_record_count(altavilla):
    assert len(altavilla) == 16


def test_altavilla_branche_present(altavilla):
    branche = {r["branca"] for r in altavilla}
    assert "L/C" in branche
    assert "E/G" in branche
    assert "R/S" in branche
    assert "Adulti" in branche  # G1 COMUNITA' CAPI


def test_altavilla_wrapped_function_parsed(altavilla):
    """A capo with function text that wraps across lines must be parsed correctly."""
    capo = next(
        (r for r in altavilla if r["codice_socio"] == "1384748"), None
    )
    assert capo is not None
    assert capo["funzione"] == "ASSISTENTE ECCLESIASTICO DI GRUPPO"
    assert capo["livello_foca"] == 2


def test_altavilla_lc_unit(altavilla):
    lc = [r for r in altavilla if r["branca"] == "L/C"]
    assert len(lc) == 5
    assert all(r["genere_unita"] == "MISTO" for r in lc)
    assert all("BRANCO" in r["unita"] or "CERCHIO" in r["unita"] for r in lc)


def test_altavilla_eg_unit(altavilla):
    eg = [r for r in altavilla if r["branca"] == "E/G"]
    assert len(eg) == 4
    assert all(r["genere_unita"] == "MISTO" for r in eg)


def test_altavilla_rs_unit(altavilla):
    rs = [r for r in altavilla if r["branca"] == "R/S"]
    assert len(rs) == 4


def test_altavilla_capo_in_formazione(altavilla):
    """New capi (FOCA 1-2) have livello_foca <= 2."""
    capo = next(
        (r for r in altavilla if r["codice_socio"] == "1346897"), None
    )
    assert capo is not None
    assert capo["livello_foca"] <= 2
    assert capo["genere"] == "F"


# ── Known records: Avellino 4 (E2000) – unit gender ─────────────────────────

@pytest.fixture(scope="module")
def avellino4(records_2026):
    return [r for r in records_2026 if r["codice_gruppo"] == "E2000"]


def test_avellino4_branco_maschile(avellino4):
    h1 = [r for r in avellino4 if "H1" in r["unita"]]
    assert h1
    assert all(r["genere_unita"] == "MASCHILE" for r in h1)
    assert all(r["branca"] == "L/C" for r in h1)


def test_avellino4_cerchio_femminile(avellino4):
    i1 = [r for r in avellino4 if "I1" in r["unita"]]
    assert i1
    assert all(r["genere_unita"] == "FEMMINILE" for r in i1)
    assert all(r["branca"] == "L/C" for r in i1)


# ── Error handling ────────────────────────────────────────────────────────────

def test_missing_year_dir_raises():
    with pytest.raises(FileNotFoundError):
        parse_year(DATA_INPUT, year=1900)


def test_missing_input_dir_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        parse_year(tmp_path / "nonexistent", year=2026)


def test_default_year_picks_most_recent():
    """parse_year() without explicit year uses the latest folder."""
    result = parse_year(DATA_INPUT)
    assert all(r["anno"] == 2026 for r in result)


# ── CLI ───────────────────────────────────────────────────────────────────────

def test_cli_csv(tmp_path):
    from autorizzazioni_agesci.cli import main
    rc = main(["--input", str(DATA_INPUT), "--output", str(tmp_path),
               "--anno", "2026", "--formato", "csv"])
    assert rc == 0
    out = tmp_path / "2026.csv"
    assert out.exists()
    lines = out.read_text(encoding="utf-8").splitlines()
    assert lines[0].startswith("codice_socio")
    assert len(lines) == 219  # header + 218 records


def test_cli_json(tmp_path):
    import json
    from autorizzazioni_agesci.cli import main
    rc = main(["--input", str(DATA_INPUT), "--output", str(tmp_path),
               "--anno", "2026", "--formato", "json"])
    assert rc == 0
    out = tmp_path / "2026.json"
    assert out.exists()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert len(data) == 218
    assert "codice_socio" in data[0]


def test_cli_overwrite_existing(tmp_path):
    """Running CLI twice overwrites the previous file."""
    from autorizzazioni_agesci.cli import main
    args = ["--input", str(DATA_INPUT), "--output", str(tmp_path),
            "--anno", "2026", "--formato", "csv"]
    main(args)
    main(args)
    out = tmp_path / "2026.csv"
    lines = out.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 219  # not doubled


def test_cli_invalid_year_returns_error(tmp_path):
    from autorizzazioni_agesci.cli import main
    rc = main(["--input", str(DATA_INPUT), "--output", str(tmp_path), "--anno", "1900"])
    assert rc == 1
