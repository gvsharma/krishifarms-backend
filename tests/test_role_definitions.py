"""Unit tests for CRM ROLE_DEFINITIONS / ROLE_PERMISSIONS alignment (web + Android)."""

from app.shared.permissions import ROLE_DEFINITIONS, ROLE_PERMISSIONS, SYSTEM_PERMISSIONS


def test_role_definitions_match_erp_display_names():
    by_code = dict(ROLE_DEFINITIONS)
    assert by_code["OWNER"] == "Admin / Owner"
    assert by_code["MANAGER"] == "Manager"
    assert by_code["SUPERVISOR"] == "Farming Supervisor"
    assert by_code["DRIVER"] == "Vehicle Supervisor"
    assert by_code["AGENT"] == "Agent"
    assert by_code["FARMER"] == "Farmer"
    assert by_code["WORKER"] == "Worker"
    assert by_code["HAMALI"] == "Hamali / Porter"


def test_role_permissions_keys_match_definitions():
    definition_codes = {code for code, _ in ROLE_DEFINITIONS}
    assert definition_codes == set(ROLE_PERMISSIONS.keys())


def test_owner_has_every_system_permission():
    owner = set(ROLE_PERMISSIONS["OWNER"])
    system = {code for code, _ in SYSTEM_PERMISSIONS}
    assert system <= owner


def test_manager_can_create_users_but_not_delete():
    manager = set(ROLE_PERMISSIONS["MANAGER"])
    assert "users:create" in manager
    assert "users:delete" not in manager
    assert "delete" not in manager
    assert not any(p.endswith(":delete") for p in manager)


def test_location_reads_for_field_roles():
    for role in ("SUPERVISOR", "AGENT", "DRIVER", "FARMER"):
        perms = set(ROLE_PERMISSIONS[role])
        assert "districts:read" in perms
        assert "mandals:read" in perms
        assert "villages:read" in perms


def test_driver_has_transport_diesel_soft_wire():
    driver = set(ROLE_PERMISSIONS["DRIVER"])
    assert "vehicles:read" in driver
    assert "assets:read" in driver
    assert "transport:create" in driver
    assert "diesel:create" in driver
    assert "field_services:read" in driver
    assert "field_services:create" in driver


def test_agent_field_services_not_procurement_create():
    agent = set(ROLE_PERMISSIONS["AGENT"])
    assert "field_services:create" in agent
    assert "farmers:read" in agent
    assert "procurements:create" not in agent
    assert "documents:create" in agent


def test_hamali_role_is_read_only_hamali_module():
    hamali = set(ROLE_PERMISSIONS["HAMALI"])
    assert hamali == {"hamali:read", "dashboard:read"}
    assert "hamali:create" not in hamali
    assert "hamali:update" not in hamali
    assert "hamali:pay" not in hamali


def test_farmer_can_comment_on_posted_field_work():
    farmer = set(ROLE_PERMISSIONS["FARMER"])
    assert "comments:read" in farmer
    assert "comments:create" in farmer
    assert "field_services:read" in farmer
    assert "documents:create" not in farmer


def test_driver_can_upload_documents_for_diesel_receipts():
    driver = set(ROLE_PERMISSIONS["DRIVER"])
    assert "documents:read" in driver
    assert "documents:create" in driver
    assert "field_services:create" in driver
