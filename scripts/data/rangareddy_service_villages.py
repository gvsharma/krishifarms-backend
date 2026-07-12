"""KrishiFarms service-area village master data.

Sources: Census 2011 revenue villages, Telangana district portals, VillageInfo.in
(2026). Mandal spellings follow official revenue records (Keshampet, Kothur, Midjil,
Farooqnagar, Maheshwaram, Talakondapally, Balanagar, Amangal).

Note: Midjil and Balanagar mandals lie in Mahabubnagar district but border the
Rangareddy service belt around Keshampet / Shamshabad.
"""

from __future__ import annotations

from typing import TypedDict


class MandalVillages(TypedDict):
    mandal: str
    district: str
    state: str
    villages: list[str]
    source: str


STATE = "Telangana"

# Official mandal names (revenue records). User aliases noted in comments.
RANGAREDDY_SERVICE_MANDALS: list[MandalVillages] = [
    {
        # Alias: keshampeta
        "mandal": "Keshampet",
        "district": "Rangareddy",
        "state": STATE,
        "source": "Census 2011 / VillageInfo.in (Rangareddy Keshampet)",
        "villages": [
            "Alwal",
            "Bhairkhanpalle",
            "Bodanampalle",
            "Chintakuntapalle",
            "Chowlapalle (East)",
            "Dattaipalle",
            "Eklaskhanpeta",
            "Ippalapalle",
            "Kakunoor",
            "Keshampet",
            "Kondareddipalle",
            "Kothapeta",
            "Lemamidi",
            "Lingamdana",
            "Nirdavelly",
            "Papireddiguda",
            "Pomalpalle",
            "Sangam",
            "Santhapur",
            "Thommidirekula",
            "Vemulanarva",
        ],
    },
    {
        # Alias: kotur
        "mandal": "Kothur",
        "district": "Rangareddy",
        "state": STATE,
        "source": "Census 2011 / VillageInfo.in (Rangareddy Kothur)",
        "villages": [
            "Gudur",
            "Inmulnarva",
            "Khajiguda",
            "Kodicherla",
            "Kothur",
            "Mallapur",
            "Mekaguda",
            "Narsappaguda",
            "Penjerla",
            "Rangapur",
            "Seriguda (Bhadrai Palle)",
            "Siddapur",
            "Theegapur",
            "Thimmapur",
        ],
    },
    {
        # Alias: midl
        "mandal": "Midjil",
        "district": "Mahabubnagar",
        "state": STATE,
        "source": "Census 2011 (Midjil sub-district, Mahabubnagar)",
        "villages": [
            "Bhairampalle",
            "Boinpalle",
            "Bommarasipalle",
            "Chedughattu",
            "Chiluveru",
            "Donur",
            "Gudiganpalle",
            "Ippaipahad",
            "Jagboinpalle",
            "Jakanalapalle",
            "Kanchanpalle",
            "Kothapalle",
            "Kothur (Midjil)",
            "Madharam",
            "Masigundlapalle",
            "Midjil",
            "Munnanur",
            "Narsampalle",
            "Rachalapalle",
            "Ramreddipalle",
            "Revally",
            "Singamdoddi",
            "Urkonda",
            "Urkondapeta",
            "Vaspula",
            "Velugommula",
            "Vemula",
            "Wadiyal",
        ],
    },
    {
        # Alias: farooq nagar
        "mandal": "Farooqnagar",
        "district": "Rangareddy",
        "state": STATE,
        "source": "Census 2011 / VillageInfo.in (Rangareddy Farooqnagar)",
        "villages": [
            "Allisabguda",
            "Annaram",
            "Ayyavaripalle",
            "Bheemaram",
            "Buchchiguda",
            "Burgul",
            "Chattanpalle",
            "Chilkamarri (Chelka)",
            "Chinchode",
            "Chintalaguda",
            "Chowlapalle (West)",
            "Devunipalle",
            "Dooskal",
            "Elkatta",
            "Farooqnagar",
            "Gantlavelli",
            "Gundlakunta",
            "Hajipalle",
            "Jogammaguda",
            "Kammadanam",
            "Kamsanpalle",
            "Kandivanam",
            "Kishannagar",
            "Kondannaguda",
            "Kongaguda",
            "Lingareddy Guda",
            "Madhurapur",
            "Mogalgidda",
            "Nagulapalle",
            "Raikal",
            "Ramakrishnapur",
            "Rangasamudram (Yellampalle)",
            "Seriguda Madhurapur",
            "Solipur",
            "Suryaraoguda",
            "Thimmajipalle",
            "Veljerla",
            "Vittyal",
        ],
    },
    {
        "mandal": "Maheshwaram",
        "district": "Rangareddy",
        "state": STATE,
        "source": "Census 2011 / VillageInfo.in (Rangareddy Maheshwaram)",
        "villages": [
            "Akanpalle",
            "Almasguda",
            "Ameerpet",
            "Baghmankhal",
            "Dabilguda",
            "Dilwarguda",
            "Dubbacherla",
            "Gangaram",
            "Ghatpalle",
            "Gollor",
            "Imamguda",
            "Kalwakole",
            "Kollapadkal",
            "Kongar Khurd (A)",
            "Kongar Khurd (B)",
            "Maheshwaram",
            "Malikdanguda",
            "Mankhal",
            "Mansanpalle",
            "Mohabatnagar",
            "Nagaram",
            "Nagireddipalle",
            "Nandipalle",
            "Pendyal",
            "Porandla",
            "Raviryal",
            "Sardar Nagar",
            "Sirigiripur",
            "Sreenagar",
            "Subhanpur",
            "Thummaloor",
            "Toopra Khurd",
            "Venkannaguda",
        ],
    },
    {
        # Alias: talakondapalle
        "mandal": "Talakondapally",
        "district": "Rangareddy",
        "state": STATE,
        "source": "Census 2011 (Talakondapally sub-district, Rangareddy)",
        "villages": [
            "Antharam",
            "Badnapur",
            "Chandradana",
            "Cheepunuthala",
            "Chennaram",
            "Chukkapur",
            "Garvipalle",
            "Gattu Ippalapalle",
            "Julapalle",
            "Khanapur",
            "Lingarapalle",
            "Medakpalle",
            "Padakal",
            "Rampur",
            "Seriramakrishnapur",
            "Talakondapalle",
            "Thimmapur (Talakondapally)",
            "Veljala",
            "Venkatraopeta",
            "Venkatapurpatti Veljala",
            "Yadavalli",
        ],
    },
    {
        # Alias: balangara — rural Balanagar mandal (Mahabubnagar), not GHMC Balanagar
        "mandal": "Balanagar",
        "district": "Mahabubnagar",
        "state": STATE,
        "source": "Census 2011 / VillageInfo.in (Mahabubnagar Balanagar)",
        "villages": [
            "Appajipalle",
            "Balanagar",
            "Bodajanampeta",
            "Chinna Revalli",
            "Gouthapur",
            "Gunded",
            "Hemajipur",
            "Kethireddipalle",
            "Lingaram",
            "Macharam",
            "Modampalle",
            "Mothighanapur",
            "Nandaram",
            "Nerellapalle",
            "Peddarevelly",
            "Peddayapalle",
            "Seriguda",
            "Suraram",
            "Thirmalagiri",
            "Udithyal",
            "Vanamavaniguda",
        ],
    },
    {
        # Alias: amangala
        "mandal": "Amangal",
        "district": "Rangareddy",
        "state": STATE,
        "source": "Census 2011 / VillageInfo.in (Rangareddy Amangal)",
        "villages": [
            "Akuthotapalle",
            "Amangal",
            "Chennampalle",
            "Cherikonda Pattikalwakurthy",
            "Cherikondapattipadkal",
            "Jangareddy Pally",
            "Konapur",
            "Murthujapally",
            "Polepalle",
            "Ramanuthula",
            "Settipalle",
            "Singam Palle",
            "Vithaipalle",
        ],
    },
]


def flatten_service_villages() -> list[dict[str, str]]:
    """Return org-scoped village rows: name, mandal, district, state."""
    rows: list[dict[str, str]] = []
    for block in RANGAREDDY_SERVICE_MANDALS:
        for village_name in block["villages"]:
            rows.append(
                {
                    "name": village_name,
                    "mandal": block["mandal"],
                    "district": block["district"],
                    "state": block["state"],
                }
            )
    return rows


def mandal_village_counts() -> dict[str, int]:
    return {block["mandal"]: len(block["villages"]) for block in RANGAREDDY_SERVICE_MANDALS}
