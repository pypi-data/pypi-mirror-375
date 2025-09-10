#!/usr/bin/env python3
"""
Example usage of the professional EsiClient
"""

from pyesi_client import EsiClient, EsiScope

# Initialize client with required scopes
client = EsiClient(client_id="7704f80cb19a403abf1a1b8c4d184bc5", scopes=EsiScope.all_values())

# Get authentication URL
print("🔗 Authentication URL:")
auth_url = client.get_auth_url()
print(auth_url)

# Get authorization code from user
auth_code = input("\n📝 Enter authorization code: ")

# Complete authentication
try:
    client.authenticate(auth_code)
    print("✅ Authentication successful!")

    # Verify token and get character info
    char_info = client.verify_token()
    print(f"👤 Character: {char_info.character_name} (ID: {char_info.character_id})")
    print(f"🔐 Scopes: {', '.join(char_info.scp)}")

    # Example API calls using the professional client
    print("\n🌟 Making API calls...")

    # Get character public information
    character_id = char_info.character_id
    character_data = client.character.get_characters_character_id(
        character_id=character_id, x_compatibility_date=client.compatibility_date
    )
    print(f"📊 Character info: {character_data}")
    char_wallet = client.wallet.get_characters_character_id_wallet(
        character_id=character_id, x_compatibility_date=client.compatibility_date
    )
    print(f"📊 Character wallet: {char_wallet}")
    # Get server status (no authentication required)
    server_status = client.status.get_status(client.compatibility_date)
    print(f"🖥️  Server status: {server_status.players} players online")

except Exception as e:
    print(f"❌ Error: {e}")

print("\n🎉 Example completed!")
