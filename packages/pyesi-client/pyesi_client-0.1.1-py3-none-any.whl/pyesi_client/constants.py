"""
eve-esi-python

EVE SSO Constants
"""

from enum import Enum

DEFAULT_ESI_HOST = "https://esi.evetech.net"
DEFAULT_ESI_AGENT = "pyesi-client/0.1.1"
DEFAULT_ESI_ENDPOINTS_URL = "https://login.eveonline.com/.well-known/oauth-authorization-server"
DEFAULT_ESI_ISSUER_ENDPOINT = "https://login.eveonline.com"
DEFAULT_ESI_AUTH_ENDPOINT = "https://login.eveonline.com/v2/oauth/authorize"
DEFAULT_ESI_TOKEN_ENDPOINT = "https://login.eveonline.com/v2/oauth/token"
DEFAULT_ESI_JWKS_URI = "https://login.eveonline.com/oauth/jwks"
DEFAULT_ESI_REVOCATION_ENDPOINT = "https://login.eveonline.com/v2/oauth/revoke"
DEFAULT_ESI_JWK_KID = "JWT-Signature-Key"
DEFAULT_ESI_AUDIENCE = "EVE Online"
DEFAULT_MAX_RETRIES = 5


class EsiResponseType(str, Enum):
    CODE = "code"
    TOKEN = "token"


class EsiSubjectType(str, Enum):
    PUBLIC = "public"


class EsiRevocationEndpointAuthMethod(str, Enum):
    CLIENT_SECRET_BASIC = "client_secret_basic"
    CLIENT_SECRET_POST = "client_secret_post"
    CLIENT_SECRET_JWT = "client_secret_jwt"


class EsiTokenEndpointAuthMethod(str, Enum):
    CLIENT_SECRET_BASIC = "client_secret_basic"
    CLIENT_SECRET_POST = "client_secret_post"
    CLIENT_SECRET_JWT = "client_secret_jwt"


class EsiIdTokenSigningAlgValue(str, Enum):
    HS256 = "HS256"


class EsiTokenEndpointAuthSigningAlgValue(str, Enum):
    HS256 = "HS256"


class EsiCodeChallengeMethod(str, Enum):
    S256 = "S256"


class EsiGrantType(str, Enum):
    AUTHORIZATION_CODE = "authorization_code"
    REFRESH_TOKEN = "refresh_token"


class EsiScope(str, Enum):
    """ESI OAuth scopes"""

    @classmethod
    def all_values(cls):
        return [m for m in cls]

    ALLIANCES_READ_CONTACTS = "esi-alliances.read_contacts.v1"
    ASSETS_READ_ASSETS = "esi-assets.read_assets.v1"
    ASSETS_READ_CORPORATION_ASSETS = "esi-assets.read_corporation_assets.v1"
    CALENDAR_READ_CALENDAR_EVENTS = "esi-calendar.read_calendar_events.v1"
    CALENDAR_RESPOND_CALENDAR_EVENTS = "esi-calendar.respond_calendar_events.v1"
    CHARACTERS_READ_AGENTS_RESEARCH = "esi-characters.read_agents_research.v1"
    CHARACTERS_READ_BLUEPRINTS = "esi-characters.read_blueprints.v1"
    CHARACTERS_READ_CONTACTS = "esi-characters.read_contacts.v1"
    CHARACTERS_READ_CORPORATION_ROLES = "esi-characters.read_corporation_roles.v1"
    CHARACTERS_READ_FATIGUE = "esi-characters.read_fatigue.v1"
    CHARACTERS_READ_FW_STATS = "esi-characters.read_fw_stats.v1"
    CHARACTERS_READ_LOYALTY = "esi-characters.read_loyalty.v1"
    CHARACTERS_READ_MEDALS = "esi-characters.read_medals.v1"
    CHARACTERS_READ_NOTIFICATIONS = "esi-characters.read_notifications.v1"
    CHARACTERS_READ_STANDINGS = "esi-characters.read_standings.v1"
    CHARACTERS_READ_TITLES = "esi-characters.read_titles.v1"
    CHARACTERS_WRITE_CONTACTS = "esi-characters.write_contacts.v1"
    CLONES_READ_CLONES = "esi-clones.read_clones.v1"
    CLONES_READ_IMPLANTS = "esi-clones.read_implants.v1"
    CONTRACTS_READ_CHARACTER_CONTRACTS = "esi-contracts.read_character_contracts.v1"
    CONTRACTS_READ_CORPORATION_CONTRACTS = "esi-contracts.read_corporation_contracts.v1"
    CORPORATIONS_READ_BLUEPRINTS = "esi-corporations.read_blueprints.v1"
    CORPORATIONS_READ_CONTACTS = "esi-corporations.read_contacts.v1"
    CORPORATIONS_READ_CONTAINER_LOGS = "esi-corporations.read_container_logs.v1"
    CORPORATIONS_READ_CORPORATION_MEMBERSHIP = "esi-corporations.read_corporation_membership.v1"
    CORPORATIONS_READ_DIVISIONS = "esi-corporations.read_divisions.v1"
    CORPORATIONS_READ_FACILITIES = "esi-corporations.read_facilities.v1"
    CORPORATIONS_READ_FW_STATS = "esi-corporations.read_fw_stats.v1"
    CORPORATIONS_READ_MEDALS = "esi-corporations.read_medals.v1"
    CORPORATIONS_READ_STANDINGS = "esi-corporations.read_standings.v1"
    CORPORATIONS_READ_STARBASES = "esi-corporations.read_starbases.v1"
    CORPORATIONS_READ_STRUCTURES = "esi-corporations.read_structures.v1"
    CORPORATIONS_READ_TITLES = "esi-corporations.read_titles.v1"
    CORPORATIONS_TRACK_MEMBERS = "esi-corporations.track_members.v1"
    FITTINGS_READ_FITTINGS = "esi-fittings.read_fittings.v1"
    FITTINGS_WRITE_FITTINGS = "esi-fittings.write_fittings.v1"
    FLEETS_READ_FLEET = "esi-fleets.read_fleet.v1"
    FLEETS_WRITE_FLEET = "esi-fleets.write_fleet.v1"
    INDUSTRY_READ_CHARACTER_JOBS = "esi-industry.read_character_jobs.v1"
    INDUSTRY_READ_CHARACTER_MINING = "esi-industry.read_character_mining.v1"
    INDUSTRY_READ_CORPORATION_JOBS = "esi-industry.read_corporation_jobs.v1"
    INDUSTRY_READ_CORPORATION_MINING = "esi-industry.read_corporation_mining.v1"
    KILLMAILS_READ_CORPORATION_KILLMAILS = "esi-killmails.read_corporation_killmails.v1"
    KILLMAILS_READ_KILLMAILS = "esi-killmails.read_killmails.v1"
    LOCATION_READ_LOCATION = "esi-location.read_location.v1"
    LOCATION_READ_ONLINE = "esi-location.read_online.v1"
    LOCATION_READ_SHIP_TYPE = "esi-location.read_ship_type.v1"
    MAIL_ORGANIZE_MAIL = "esi-mail.organize_mail.v1"
    MAIL_READ_MAIL = "esi-mail.read_mail.v1"
    MAIL_SEND_MAIL = "esi-mail.send_mail.v1"
    MARKETS_READ_CHARACTER_ORDERS = "esi-markets.read_character_orders.v1"
    MARKETS_READ_CORPORATION_ORDERS = "esi-markets.read_corporation_orders.v1"
    MARKETS_STRUCTURE_MARKETS = "esi-markets.structure_markets.v1"
    PLANETS_MANAGE_PLANETS = "esi-planets.manage_planets.v1"
    PLANETS_READ_CUSTOMS_OFFICES = "esi-planets.read_customs_offices.v1"
    SEARCH_SEARCH_STRUCTURES = "esi-search.search_structures.v1"
    SKILLS_READ_SKILLQUEUE = "esi-skills.read_skillqueue.v1"
    SKILLS_READ_SKILLS = "esi-skills.read_skills.v1"
    UI_OPEN_WINDOW = "esi-ui.open_window.v1"
    UI_WRITE_WAYPOINT = "esi-ui.write_waypoint.v1"
    UNIVERSE_READ_STRUCTURES = "esi-universe.read_structures.v1"
    WALLET_READ_CHARACTER_WALLET = "esi-wallet.read_character_wallet.v1"
    WALLET_READ_CORPORATION_WALLETS = "esi-wallet.read_corporation_wallets.v1"
