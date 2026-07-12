"""KrishiFarms fleet inventory — tractors, transport, and implements.

Canonical catalog for field services, vehicle types master data, and fleet placeholders.
"""

from __future__ import annotations

FLEET_TRACTORS: list[dict] = [
    {
        "code": "JD_TRACTOR_2W",
        "name": "John Deere tractor 2W",
        "name_te": "జాన్ డియర్ ట్రాక్టర్ 2W",
        "fuel_type": "tractor",
    },
    {
        "code": "JD_TRACTOR_4W",
        "name": "John Deere tractor 4W",
        "name_te": "జాన్ డియర్ ట్రాక్టర్ 4W",
        "fuel_type": "tractor",
    },
]

FLEET_TRANSPORT: list[dict] = [
    {
        "code": "MAHINDRA_BOLERO",
        "name": "Mahindra Bolero",
        "name_te": "మహీంద్రా బోలేరో",
        "fuel_type": "diesel",
    },
    {
        "code": "EICHER_DCM",
        "name": "Eicher DCM",
        "name_te": "ఐషర్ డీసీఎం",
        "fuel_type": "diesel",
    },
]

FLEET_IMPLEMENTS: list[dict] = [
    {"code": "TROLLEY", "name": "Trolley", "name_te": "ట్రాలీ", "fuel_type": "implement"},
    {"code": "BALER", "name": "Baler", "name_te": "బేలర్", "fuel_type": "implement"},
    {"code": "PUMP", "name": "Pump", "name_te": "పంపు", "fuel_type": "implement"},
    {"code": "CULTIVATOR", "name": "Cultivator", "name_te": "కల్టివేటర్", "fuel_type": "implement"},
    {"code": "ROTAVATOR", "name": "Rotavator", "name_te": "రోటవేటర్", "fuel_type": "implement"},
    {"code": "WEEDER", "name": "Weeder", "name_te": "వీడర్", "fuel_type": "implement"},
]

# Legacy codes kept for idempotent upsert on existing orgs (name refresh only).
LEGACY_VEHICLE_ALIASES: list[dict] = [
    {
        "code": "BOLERO",
        "name": "Mahindra Bolero",
        "name_te": "మహీంద్రా బోలేరో",
        "fuel_type": "diesel",
    },
    {
        "code": "DCM",
        "name": "Eicher DCM",
        "name_te": "ఐషర్ డీసీఎం",
        "fuel_type": "diesel",
    },
]

DEFAULT_VEHICLE_TYPES: list[dict] = [
    *FLEET_TRACTORS,
    *FLEET_TRANSPORT,
    *FLEET_IMPLEMENTS,
    *LEGACY_VEHICLE_ALIASES,
]

DEFAULT_ACTIVITY_TYPES: list[dict] = [
    # Field services
    {
        "code": "FIELD_PLOUGHING",
        "name": "Ploughing",
        "name_te": "దున్నుట",
        "service_category": "field_service",
        "default_rate_type": "hourly",
    },
    {
        "code": "FIELD_SPRAYING",
        "name": "Spraying",
        "name_te": "పిచికారీ",
        "service_category": "field_service",
        "default_rate_type": "hourly",
    },
    {
        "code": "FIELD_OTHER",
        "name": "Other Field Service",
        "name_te": "ఇతర ఫీల్డ్ సేవ",
        "service_category": "field_service",
        "default_rate_type": "fixed",
    },
    # Tractor work
    {
        "code": "TRACTOR_JD_2W",
        "name": "John Deere 2W Tractor Work",
        "name_te": "జాన్ డియర్ 2W ట్రాక్టర్ పని",
        "service_category": "tractor_work",
        "default_rate_type": "hourly",
    },
    {
        "code": "TRACTOR_JD_4W",
        "name": "John Deere 4W Tractor Work",
        "name_te": "జాన్ డియర్ 4W ట్రాక్టర్ పని",
        "service_category": "tractor_work",
        "default_rate_type": "hourly",
    },
    {
        "code": "TRACTOR_CULTIVATOR",
        "name": "Cultivator Work",
        "name_te": "కల్టివేటర్ పని",
        "service_category": "tractor_work",
        "default_rate_type": "hourly",
    },
    {
        "code": "TRACTOR_ROTAVATOR",
        "name": "Rotavator Work",
        "name_te": "రోటవేటర్ పని",
        "service_category": "tractor_work",
        "default_rate_type": "hourly",
    },
    {
        "code": "TRACTOR_TROLLEY",
        "name": "Trolley Work",
        "name_te": "ట్రాలీ పని",
        "service_category": "tractor_work",
        "default_rate_type": "fixed",
    },
    {
        "code": "TRACTOR_BALER",
        "name": "Baler Work",
        "name_te": "బేలర్ పని",
        "service_category": "tractor_work",
        "default_rate_type": "fixed",
    },
    {
        "code": "TRACTOR_PUMP",
        "name": "Pump Work",
        "name_te": "పంపు పని",
        "service_category": "tractor_work",
        "default_rate_type": "hourly",
    },
    {
        "code": "TRACTOR_WEEDER",
        "name": "Weeder Work",
        "name_te": "వీడర్ పని",
        "service_category": "tractor_work",
        "default_rate_type": "hourly",
    },
    # Transport
    {
        "code": "TRANSPORT_BOLERO",
        "name": "Mahindra Bolero Carrying",
        "name_te": "మహీంద్రా బోలేరో రవాణా",
        "service_category": "transport",
        "default_rate_type": "fixed",
    },
    {
        "code": "TRANSPORT_DCM",
        "name": "Eicher DCM Carrying",
        "name_te": "ఐషర్ డీసీఎం రవాణా",
        "service_category": "transport",
        "default_rate_type": "fixed",
    },
    # Fertiliser
    {
        "code": "FERT_UREA",
        "name": "Urea Supply",
        "name_te": "యూరియా సరఫరా",
        "service_category": "fertiliser",
        "default_rate_type": "fixed",
    },
    {
        "code": "FERT_DAP",
        "name": "DAP Supply",
        "name_te": "డీఏపీ సరఫరా",
        "service_category": "fertiliser",
        "default_rate_type": "fixed",
    },
    {
        "code": "FERT_OTHER",
        "name": "Other Fertiliser",
        "name_te": "ఇతర ఎరువులు",
        "service_category": "fertiliser",
        "default_rate_type": "fixed",
    },
    # Seeds
    {
        "code": "SEED_PADDY",
        "name": "Paddy Seeds",
        "name_te": "వరి విత్తనాలు",
        "service_category": "seeds",
        "default_rate_type": "fixed",
    },
    {
        "code": "SEED_CORN",
        "name": "Corn Seeds",
        "name_te": "మొక్కజొన్న విత్తనాలు",
        "service_category": "seeds",
        "default_rate_type": "fixed",
    },
    {
        "code": "SEED_OTHER",
        "name": "Other Seeds",
        "name_te": "ఇతర విత్తనాలు",
        "service_category": "seeds",
        "default_rate_type": "fixed",
    },
    # Agri-finance
    {
        "code": "AGRI_FINANCE_LOAN",
        "name": "Agri Finance Loan",
        "name_te": "వ్యవసాయ రుణం",
        "service_category": "agri_finance",
        "default_rate_type": "fixed",
    },
    {
        "code": "AGRI_FINANCE_ADVANCE",
        "name": "Agri Finance Advance",
        "name_te": "వ్యవసాయ అడ్వాన్స్",
        "service_category": "agri_finance",
        "default_rate_type": "fixed",
    },
    # Vehicle ops
    {
        "code": "VEHICLE_REPAIR",
        "name": "Vehicle Repair",
        "name_te": "వాహన మరమ్మతు",
        "service_category": "vehicle_ops",
        "default_rate_type": "fixed",
    },
    {
        "code": "VEHICLE_MAINTENANCE",
        "name": "Vehicle Maintenance",
        "name_te": "వాహన నిర్వహణ",
        "service_category": "vehicle_ops",
        "default_rate_type": "fixed",
    },
    {
        "code": "VEHICLE_CLEANING",
        "name": "Vehicle Cleaning",
        "name_te": "వాహన శుభ్రత",
        "service_category": "vehicle_ops",
        "default_rate_type": "fixed",
    },
    # Godown
    {
        "code": "GODOWN_REPAIR",
        "name": "Godown Repair",
        "name_te": "గోడౌన్ మరమ్మతు",
        "service_category": "godown",
        "default_rate_type": "fixed",
    },
    {
        "code": "GODOWN_PURCHASE",
        "name": "Godown Purchase",
        "name_te": "గోడౌన్ కొనుగోలు",
        "service_category": "godown",
        "default_rate_type": "fixed",
    },
    {
        "code": "GODOWN_CLEANING",
        "name": "Godown Cleaning",
        "name_te": "గోడౌన్ శుభ్రత",
        "service_category": "godown",
        "default_rate_type": "fixed",
    },
]
