# pyesi-client

[![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-ruff-black)](https://github.com/astral-sh/ruff)
[![Type Checker](https://img.shields.io/badge/type%20checker-pyright-blue)](https://github.com/microsoft/pyright)

A professional, modern Python client for the EVE Online ESI (Electronic Systems Interface) API. Built on top of `pyesi-openapi` with intelligent token management, caching, and utility functions.

## ✨ Features

- **🔐 Smart Authentication**: Automatic token refresh, PKCE support, and secure token storage
- **⚡ High Performance**: Built on the generated `pyesi-openapi` client for maximum efficiency  
- **🛡️ Type Safe**: Full Pydantic v2 type annotations for all API responses
- **🔄 Token Management**: Intelligent JWT token validation and refresh handling
- **📊 Scope Management**: Easy ESI scope selection and validation
- **🚀 Modern Python**: Requires Python 3.13+ with full async/await support
- **🔧 Developer Friendly**: Rich error handling and comprehensive logging

## 📦 Installation

### Using uv (Recommended)

```bash
uv add pyesi-client
```

### Using pip

```bash
pip install pyesi-client
```

## 🚀 Quick Start

### Basic Usage

```python
from pyesi_client import EsiClient, EsiScope

# Initialize the client
client = EsiClient(
    client_id="your_eve_app_client_id",
    client_secret="your_eve_app_client_secret",  # Optional for PKCE
    scopes=[
        EsiScope.CHARACTERS_READ_CHARACTER,
        EsiScope.CHARACTERS_READ_CORPORATION_HISTORY,
    ]
)

# Use as context manager (recommended)
with client:
    # Get character information
    character_info = client.character.get_characters_character_id(
        character_id=123456789
    )
    print(f"Character: {character_info.name}")
    
    # Get corporation information
    corp_info = client.corporation.get_corporations_corporation_id(
        corporation_id=character_info.corporation_id
    )
    print(f"Corporation: {corp_info.name}")
```

### Authentication Flow

```python
from pyesi_client import EsiClient, EsiScope

# Initialize client for OAuth flow
client = EsiClient(
    client_id="your_eve_app_client_id",
    redirect_uri="http://localhost:8000/callback",
    scopes=[
        EsiScope.CHARACTERS_READ_CHARACTER,
        EsiScope.ASSETS_READ_ASSETS,
        EsiScope.WALLET_READ_CHARACTER_WALLET,
    ]
)

# Step 1: Get authorization URL
auth_url = client.get_authorization_url()
print(f"Visit: {auth_url}")

# Step 2: After user authorization, exchange code for tokens
# (callback_code comes from your redirect URI)
tokens = client.authenticate_with_code(callback_code)

# Step 3: Client is now authenticated and ready to use
character_info = client.character.get_characters_character_id(
    character_id=tokens.character_id
)
```

## 📚 API Reference

The client provides access to all EVE ESI endpoints through intuitive API groups:

### Available API Groups

| API Group     | Description           | Example Usage                                                                          |
| ------------- | --------------------- | -------------------------------------------------------------------------------------- |
| `alliance`    | Alliance information  | `client.alliance.get_alliances_alliance_id(alliance_id)`                               |
| `assets`      | Character/corp assets | `client.assets.get_characters_character_id_assets(character_id)`                       |
| `calendar`    | Calendar events       | `client.calendar.get_characters_character_id_calendar(character_id)`                   |
| `character`   | Character information | `client.character.get_characters_character_id(character_id)`                           |
| `clones`      | Clone information     | `client.clones.get_characters_character_id_clones(character_id)`                       |
| `contacts`    | Contact lists         | `client.contacts.get_characters_character_id_contacts(character_id)`                   |
| `contracts`   | Contracts             | `client.contracts.get_characters_character_id_contracts(character_id)`                 |
| `corporation` | Corporation data      | `client.corporation.get_corporations_corporation_id(corporation_id)`                   |
| `dogma`       | Dogma information     | `client.dogma.get_dogma_attributes()`                                                  |
| `fittings`    | Ship fittings         | `client.fittings.get_characters_character_id_fittings(character_id)`                   |
| `fleets`      | Fleet information     | `client.fleets.get_fleets_fleet_id(fleet_id)`                                          |
| `industry`    | Industry jobs         | `client.industry.get_characters_character_id_industry_jobs(character_id)`              |
| `killmails`   | Killmail data         | `client.killmails.get_killmails_killmail_id_killmail_hash(killmail_id, killmail_hash)` |
| `location`    | Character location    | `client.location.get_characters_character_id_location(character_id)`                   |
| `loyalty`     | Loyalty points        | `client.loyalty.get_characters_character_id_loyalty_points(character_id)`              |
| `mail`        | EVE Mail              | `client.mail.get_characters_character_id_mail(character_id)`                           |
| `market`      | Market data           | `client.market.get_markets_region_id_orders(region_id)`                                |
| `planets`     | Planetary interaction | `client.planets.get_characters_character_id_planets(character_id)`                     |
| `routes`      | Route planning        | `client.routes.get_route_origin_destination(origin, destination)`                      |
| `search`      | Search functionality  | `client.search.get_characters_character_id_search(character_id, search)`               |
| `skills`      | Character skills      | `client.skills.get_characters_character_id_skills(character_id)`                       |
| `sovereignty` | Sovereignty data      | `client.sovereignty.get_sovereignty_structures()`                                      |
| `status`      | Server status         | `client.status.get_status()`                                                           |
| `universe`    | Universe data         | `client.universe.get_universe_systems_system_id(system_id)`                            |
| `ui`          | UI interactions       | `client.ui.post_ui_openwindow_information(target_id)`                                  |
| `wallet`      | Wallet transactions   | `client.wallet.get_characters_character_id_wallet(character_id)`                       |
| `wars`        | War information       | `client.wars.get_wars_war_id(war_id)`                                                  |

### ESI Scopes

All available ESI scopes are provided through the `EsiScope` enum:

```python
from pyesi_client import EsiScope

# Character scopes
EsiScope.CHARACTERS_READ_CHARACTER
EsiScope.CHARACTERS_READ_CORPORATION_HISTORY
EsiScope.CHARACTERS_READ_CONTACTS

# Assets scopes
EsiScope.ASSETS_READ_ASSETS
EsiScope.ASSETS_READ_CORPORATION_ASSETS

# Wallet scopes
EsiScope.WALLET_READ_CHARACTER_WALLET
EsiScope.WALLET_READ_CORPORATION_WALLET

# And many more...
```

## 🔐 Authentication & Security

### OAuth2 Flow

pyesi-client supports the standard EVE SSO OAuth2 flow:

1. **Authorization**: Redirect users to EVE SSO for permission
2. **Token Exchange**: Exchange authorization code for access/refresh tokens
3. **Automatic Refresh**: Tokens are automatically refreshed when needed
4. **Secure Storage**: JWT tokens are validated and stored securely

### PKCE Support

For enhanced security, PKCE (Proof Key for Code Exchange) is supported:

```python
client = EsiClient(
    client_id="your_public_client_id",
    redirect_uri="http://localhost:8000/callback",
    scopes=[EsiScope.CHARACTERS_READ_CHARACTER]
    # client_secret=None  # PKCE flow automatically enabled
)

# PKCE flow automatically enabled when client_secret is None
auth_url = client.get_authorization_url()  # Includes code_challenge
```

### Token Management

```python
# Check authentication status
if client.is_authenticated():
    print("Client is ready to make authenticated requests")

# Get current token info
token_info = client.get_token_info()
print(f"Character ID: {token_info.character_id}")
print(f"Expires: {token_info.expires_at}")

# Manually refresh tokens (usually automatic)
client.refresh_tokens()
```

## ⚙️ Configuration

### Client Configuration

```python
client = EsiClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    redirect_uri="https://yourapp.com/callback",
    scopes=[EsiScope.CHARACTERS_READ_CHARACTER],
    
    # Optional configuration
    user_agent="YourApp/1.0.0 (contact@yourapp.com)",
    timeout=30,  # Request timeout in seconds
    retries=3,   # Number of retry attempts
    host="https://esi.evetech.net"  # ESI base URL
)
```

### Custom User Agent

It's recommended to set a custom user agent for your application:

```python
client = EsiClient(
    client_id="your_client_id",
    user_agent="MyEVEApp/2.1.0 (maintainer@example.com)"
)
```

## 🧪 Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/your-username/pyesi-client.git
cd pyesi-client

# Install with development dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=pyesi_client

# Run specific test file
uv run pytest tests/test_client.py -v
```

### Code Quality

```bash
# Type checking
uv run pyright

# Linting and formatting
uv run ruff check
uv run ruff format

# Run all quality checks
uv run pre-commit run --all-files
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and quality checks (`uv run pre-commit run --all-files`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- **[pyesi-openapi](https://github.com/your-username/pyesi-openapi)** - Generated OpenAPI client for EVE ESI
- **[EVE ESI Documentation](https://esi.evetech.net/ui/)** - Official ESI API documentation
- **[EVE Developer Portal](https://developers.eveonline.com/)** - EVE Online developer resources

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/pyesi-client/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/pyesi-client/discussions)
- **EVE Online**: [EVE Online Third-Party Developers](https://discord.gg/eveonline-developers)

## ⭐ Acknowledgments

- **CCP Games** for providing the EVE Online ESI API
- **The EVE Online community** for continued support and feedback
- **OpenAPI Generator** for code generation capabilities

---

Built with ❤️ for the EVE Online community