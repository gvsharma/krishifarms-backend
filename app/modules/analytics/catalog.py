"""Static analytics hub catalog — live vs scaffold modules."""

from app.modules.analytics.schemas import AnalyticsCatalogResponse, ModuleCatalogItem

_CATALOG: list[ModuleCatalogItem] = [
    ModuleCatalogItem(
        id="executive",
        name="Executive",
        name_te="ఎగ్జిక్యూటివ్",
        description="Org health, money strip, and ops pulse for the morning review.",
        status="live",
        href="/analytics/executive",
        group="live",
    ),
    ModuleCatalogItem(
        id="operations",
        name="Operations Command",
        name_te="ఆపరేషన్స్",
        description="Live-day procurements, field services, and fleet activity.",
        status="live",
        href="/analytics/operations",
        group="live",
    ),
    ModuleCatalogItem(
        id="procurement",
        name="Procurement Analytics",
        name_te="కొనుగోలు",
        description="Volume, value, moisture, crop/village mix for confirmed tickets.",
        status="live",
        href="/analytics/procurement",
        group="live",
    ),
    ModuleCatalogItem(
        id="finance",
        name="Finance Dashboard",
        name_te="ఫైనాన్స్",
        description="Expenses, collections, farmer outstanding, payment pace.",
        status="live",
        href="/analytics/finance",
        group="live",
    ),
    ModuleCatalogItem(
        id="farming",
        name="Farming",
        name_te="వ్యవసాయం",
        description="Own-farm activities and cost-per-acre analytics.",
        status="scaffold",
        href="/analytics/farming",
        group="scaffold",
        missing_sources=["Dedicated farm-ops KPI API; farm_activities rollups thin"],
    ),
    ModuleCatalogItem(
        id="vehicle",
        name="Vehicle",
        name_te="వాహనాలు",
        description="Fleet utilization, trip costs, diesel intensity.",
        status="scaffold",
        href="/analytics/vehicle",
        group="scaffold",
        missing_sources=["Utilization KPI endpoint; Phase 2 fleet subset"],
    ),
    ModuleCatalogItem(
        id="village",
        name="Village",
        name_te="గ్రామాలు",
        description="Village rankings and coverage heat tables.",
        status="scaffold",
        href="/analytics/village",
        group="scaffold",
        missing_sources=["Village analytics aggregate API (Village 360 is profile-only)"],
    ),
    ModuleCatalogItem(
        id="farmer",
        name="Farmer",
        name_te="రైతులు",
        description="Cohort activity, VIP/outstanding distribution.",
        status="scaffold",
        href="/analytics/farmer",
        group="scaffold",
        missing_sources=["Org-wide farmer cohort analytics (Farmer 360 is per-farmer)"],
    ),
    ModuleCatalogItem(
        id="buyer",
        name="Buyer",
        name_te="కొనుగోలుదారులు",
        description="Buyer settlement and concentration.",
        status="scaffold",
        href="/analytics/buyer",
        group="scaffold",
        missing_sources=["Buyer AR ledger — settlement is farmer/procurement-centric"],
    ),
    ModuleCatalogItem(
        id="employee",
        name="Employee",
        name_te="ఉద్యోగులు",
        description="Workforce attendance and productivity.",
        status="scaffold",
        href="/analytics/employee",
        group="scaffold",
        missing_sources=["Workers / attendance / work-orders Python routes"],
    ),
    ModuleCatalogItem(
        id="service",
        name="Service",
        name_te="సేవలు",
        description="Field-service mix, margins, diesel linkage.",
        status="scaffold",
        href="/analytics/service",
        group="scaffold",
        missing_sources=["Dedicated service analytics; Phase 2 subset planned"],
    ),
    ModuleCatalogItem(
        id="crop-intelligence",
        name="Crop Intelligence",
        name_te="పంట సమాచారం",
        description="Seasonal yield and acreage intelligence.",
        status="scaffold",
        href="/analytics/crop-intelligence",
        group="scaffold",
        missing_sources=["Yield/outcome labels; crop-history is not yield truth"],
    ),
    ModuleCatalogItem(
        id="inventory",
        name="Inventory",
        name_te="నిల్వ",
        description="Seed / fertilizer / diesel stock and low-stock alerts.",
        status="scaffold",
        href="/analytics/inventory",
        group="scaffold",
        missing_sources=["No inventory ledger schema"],
    ),
    ModuleCatalogItem(
        id="ai-prediction",
        name="AI Prediction",
        name_te="AI అంచనాలు",
        description="Churn, buyer risk, and demand forecasts.",
        status="scaffold",
        href="/analytics/ai-prediction",
        group="scaffold",
        missing_sources=["No model registry or labeled outcomes — no fake AI figures"],
    ),
    ModuleCatalogItem(
        id="alerts",
        name="Alerts",
        name_te="హెచ్చరికలు",
        description="Ops and finance threshold alerts.",
        status="scaffold",
        href="/analytics/alerts",
        group="scaffold",
        missing_sources=["Alert rules engine + weather/disease integrations"],
    ),
]


def get_catalog() -> AnalyticsCatalogResponse:
    live = [m for m in _CATALOG if m.status == "live"]
    scaffold = [m for m in _CATALOG if m.status == "scaffold"]
    return AnalyticsCatalogResponse(
        modules=list(_CATALOG),
        live_count=len(live),
        scaffold_count=len(scaffold),
    )


def get_module_meta(module_id: str) -> ModuleCatalogItem | None:
    for item in _CATALOG:
        if item.id == module_id:
            return item
    return None
