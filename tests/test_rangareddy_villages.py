from scripts.data.rangareddy_service_villages import RANGAREDDY_MANDALS, iter_village_rows


def test_keshampeta_village_count():
    villages = RANGAREDDY_MANDALS["Keshampeta"]
    assert len(villages) == 29


def test_keshampeta_villages_have_telugu_names():
    villages = RANGAREDDY_MANDALS["Keshampeta"]
    assert all(v.get("name_te") for v in villages)


def test_keshampeta_includes_bhairkhanpalle():
    names = {v["name"] for v in RANGAREDDY_MANDALS["Keshampeta"]}
    assert "Bhairkhanpalle" in names
    assert "Devunigudi Tanda" in names


def test_iter_village_rows_includes_name_te():
    row = next(r for r in iter_village_rows() if r["name"] == "Keshampet")
    assert row["name_te"] == "కేశంపేట్"
    assert row["mandal"] == "Keshampeta"


def test_kothur_village_count():
    assert len(RANGAREDDY_MANDALS["Kothur"]) == 16


def test_kothur_villages_have_telugu_names():
    assert all(v.get("name_te") for v in RANGAREDDY_MANDALS["Kothur"])


def test_kothur_includes_seriguda():
    names = {v["name"] for v in RANGAREDDY_MANDALS["Kothur"]}
    assert "Seriguda (Bhadrai Palle)" in names
    assert "Chegur" in names
