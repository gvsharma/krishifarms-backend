"""Rangareddy district service-area location masters (district → mandal → village).

Idempotent seed source for KrishiFarms ops around Keshampeta, Talakondapally,
Maheshwaram, Kothur, and Farooqnagar mandals. Pincodes included where known.
"""

from __future__ import annotations

STATE = "Telangana"
DISTRICT = "Rangareddy"
KESHAMPETA_PINCODE = "509408"
KOTHUR_PINCODE = "509228"

# Mandal → list of villages {name, name_te?, pincode?}
RANGAREDDY_MANDALS: dict[str, list[dict[str, str]]] = {
    "Keshampeta": [
        {"name": "Alwal", "name_te": "అల్వాల్", "pincode": KESHAMPETA_PINCODE},
        {"name": "Bhairkhanpalle", "name_te": "భైర్‌ఖన్‌పల్లి", "pincode": KESHAMPETA_PINCODE},
        {"name": "Bodanampalle", "name_te": "బోదనమ్పల్లె", "pincode": KESHAMPETA_PINCODE},
        {"name": "Chintakuntapalle", "name_te": "చింతకుంటపల్లి", "pincode": KESHAMPETA_PINCODE},
        {"name": "Chowlapalle", "name_te": "చౌలపల్లె (తూర్పు చౌలపల్లె)", "pincode": KESHAMPETA_PINCODE},
        {"name": "Dattaipalle", "name_te": "దత్తైపల్లి", "pincode": KESHAMPETA_PINCODE},
        {"name": "Eklaskhanpeta", "name_te": "ఎక్లాస్ఖాన్ పేట", "pincode": KESHAMPETA_PINCODE},
        {"name": "Ippalapalle", "name_te": "ఇప్పలపల్లె", "pincode": KESHAMPETA_PINCODE},
        {"name": "Kakunoor", "name_te": "కాకునూర్", "pincode": KESHAMPETA_PINCODE},
        {"name": "Keshampet", "name_te": "కేశంపేట్ (ప్రధాన కార్యాలయం)", "pincode": KESHAMPETA_PINCODE},
        {"name": "Kondareddipalle", "name_te": "కొండరెడ్డిపల్లె", "pincode": KESHAMPETA_PINCODE},
        {"name": "Kothapeta", "name_te": "కొత్తపేట", "pincode": KESHAMPETA_PINCODE},
        {"name": "Lemamidi", "name_te": "లెమామిడి", "pincode": KESHAMPETA_PINCODE},
        {"name": "Lingamdana", "name_te": "లింగందాన", "pincode": KESHAMPETA_PINCODE},
        {"name": "Nirdavelly", "name_te": "నిర్దావెల్లి", "pincode": KESHAMPETA_PINCODE},
        {"name": "Papireddiguda", "name_te": "పాపిరెడ్డిగూడ", "pincode": KESHAMPETA_PINCODE},
        {"name": "Pomalpalle", "name_te": "పోమల్‌పల్లె", "pincode": KESHAMPETA_PINCODE},
        {"name": "Sangam", "name_te": "సంగం (సంగేం)", "pincode": KESHAMPETA_PINCODE},
        {"name": "Santhapur", "name_te": "సంతపూర్", "pincode": KESHAMPETA_PINCODE},
        {"name": "Thommidirekula", "name_te": "తోమ్మిడిరేకుల", "pincode": KESHAMPETA_PINCODE},
        {"name": "Vemulanarva", "name_te": "వేములనార్వ", "pincode": KESHAMPETA_PINCODE},
        {"name": "Devunigudi Tanda", "name_te": "దేవునిగూడి తండా", "pincode": KESHAMPETA_PINCODE},
        {"name": "Polkongutta Tanda", "name_te": "పోల్కొంగుట్ట తండా", "pincode": KESHAMPETA_PINCODE},
        {"name": "Thurpugadda Tanda", "name_te": "తూర్పుగడ్డ తండా", "pincode": KESHAMPETA_PINCODE},
        {"name": "Sundarapur", "name_te": "సుందరాపూర్", "pincode": KESHAMPETA_PINCODE},
        {"name": "Patigadda", "name_te": "పాటిగడ్డ", "pincode": KESHAMPETA_PINCODE},
        {"name": "Puttavaniguda", "name_te": "పుట్టవాణిగూడ", "pincode": KESHAMPETA_PINCODE},
        {"name": "Mangaliguda", "name_te": "మంగలిగూడ", "pincode": KESHAMPETA_PINCODE},
        {"name": "Konaipalle", "name_te": "కొనాయిపల్లి", "pincode": KESHAMPETA_PINCODE},
    ],
    "Talakondapally": [
        {"name": "Talakondapally", "pincode": "509320"},
        {"name": "Antharam", "pincode": "509320"},
        {"name": "Chowderguda", "pincode": "509320"},
        {"name": "Gundlapochampally", "pincode": "509320"},
        {"name": "Serilingampally", "pincode": "509320"},
        {"name": "Ravalkole", "pincode": "509320"},
    ],
    "Maheshwaram": [
        {"name": "Maheshwaram", "pincode": "501359"},
        {"name": "Imamguda", "pincode": "501359"},
        {"name": "Thummaloor", "pincode": "501359"},
        {"name": "Sardarnagar", "pincode": "501359"},
        {"name": "Kongarakalan", "pincode": "501359"},
        {"name": "Mansanpally", "pincode": "501359"},
        {"name": "Raviryal", "pincode": "501359"},
    ],
    "Kothur": [
        {"name": "Chegur", "name_te": "చేగూర్", "pincode": KOTHUR_PINCODE},
        {"name": "Edulapalle", "name_te": "ఏడులపల్లి", "pincode": KOTHUR_PINCODE},
        {"name": "Gudur", "name_te": "గూడూరు", "pincode": KOTHUR_PINCODE},
        {"name": "Inmulnarva", "name_te": "ఇన్ములనర్వ", "pincode": KOTHUR_PINCODE},
        {"name": "Khajiguda", "name_te": "ఖాజిగూడ", "pincode": KOTHUR_PINCODE},
        {"name": "Kodicherla", "name_te": "కొడిచెర్ల", "pincode": KOTHUR_PINCODE},
        {"name": "Kothur", "name_te": "కొత్తూరు", "pincode": KOTHUR_PINCODE},
        {"name": "Mallapur", "name_te": "మల్లాపూర్", "pincode": KOTHUR_PINCODE},
        {"name": "Mamidipalle", "name_te": "మామిడిపల్లి", "pincode": KOTHUR_PINCODE},
        {"name": "Nandigam", "name_te": "నందిగామ", "pincode": KOTHUR_PINCODE},
        {"name": "Penjerla", "name_te": "పెంజర్ల", "pincode": KOTHUR_PINCODE},
        {"name": "Seriguda (Bhadrai Palle)", "name_te": "సెరిగూడ (భద్రాయిపల్లి)", "pincode": KOTHUR_PINCODE},
        {"name": "Siddapur", "name_te": "సిద్ధాపూర్", "pincode": KOTHUR_PINCODE},
        {"name": "Theegapur", "name_te": "తీగాపూర్", "pincode": KOTHUR_PINCODE},
        {"name": "Thimmapur", "name_te": "తిమ్మాపూర్", "pincode": KOTHUR_PINCODE},
        {"name": "Veerlapalle", "name_te": "వీర్లపల్లి", "pincode": KOTHUR_PINCODE},
    ],
    "Farooqnagar": [
        {"name": "Farooqnagar", "pincode": "509216"},
        {"name": "Burgula", "pincode": "509216"},
        {"name": "Solipur", "pincode": "509216"},
        {"name": "Chinchode", "pincode": "509216"},
        {"name": "Elikatta", "pincode": "509216"},
        {"name": "Raikal", "pincode": "509216"},
        {"name": "Shadnagar", "pincode": "509216"},
    ],
}


def iter_village_rows() -> list[dict[str, str]]:
    """Flat village rows suitable for Village upsert (name, name_te, mandal, district, state, pincode)."""
    rows: list[dict[str, str]] = []
    for mandal, villages in RANGAREDDY_MANDALS.items():
        for village in villages:
            rows.append(
                {
                    "name": village["name"],
                    "name_te": village.get("name_te", ""),
                    "mandal": mandal,
                    "district": DISTRICT,
                    "state": STATE,
                    "pincode": village.get("pincode", ""),
                }
            )
    return rows
