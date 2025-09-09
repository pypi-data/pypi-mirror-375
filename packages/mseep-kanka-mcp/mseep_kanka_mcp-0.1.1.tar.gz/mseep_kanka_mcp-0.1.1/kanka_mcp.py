import os
import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("kanka")

def get_api_key():
    api_key = os.getenv("KANKA_API_KEY")
    if not api_key:
        raise EnvironmentError("KANKA_API_KEY environment variable not set.")
    return api_key

api_key = get_api_key()

KANKA_API_URL = "https://api.kanka.io/1.0/campaigns"

def get_headers():
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

@mcp.tool()
def show_campaigns():
    """List all campaigns the user has access to.
    You may need to run this tool before running other tools to get the campaign ID."""
    response = requests.get(KANKA_API_URL, headers=get_headers())
    response.raise_for_status()
    return response.json()

@mcp.tool()
def list_characters(campaign_id: int):
    """List all characters in a campaign."""
    url = f"https://api.kanka.io/1.0/campaigns/{campaign_id}/characters"
    response = requests.get(url, headers=get_headers())
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_character(campaign_id: int, character_id: int):
    """Get a single character by ID."""
    url = f"https://api.kanka.io/1.0/campaigns/{campaign_id}/characters/{character_id}"
    response = requests.get(url, headers=get_headers())
    response.raise_for_status()
    return response.json()

@mcp.tool()
def create_character(
    campaign_id: int,  # The ID of the campaign to add the character to
    name: str,         # The name of the character (required)
    title: str = None, # The character's title (optional)
    type: str = None,  # The type or class of the character (optional)
    age: str = None,   # The age of the character (optional)
    sex: str = None,   # The sex/gender of the character (optional)
    pronouns: str = None, # The pronouns of the character (optional)
    race_id: int = None,  # The ID of the race entity (optional)
    family_id: int = None, # The ID of the family entity (optional)
    is_dead: bool = None,  # Whether the character is dead (optional)
    image: str = None,     # URL or path to the character's image (optional)
    tags: str = None,      # Comma-separated list of tags (optional)
    entry: str = None,     # # The character's entry/description (optional, must be HTML)
    is_private: bool = None # If the character is only visible to admin members (optional)
):
    """Create a new character in a campaign.
    Fields:
        campaign_id: The ID of the campaign to add the character to
        name: The name of the character (required)
        title: The character's title (optional)
        type: The type or class of the character (optional)
        age: The age of the character (optional)
        sex: The sex/gender of the character (optional)
        pronouns: The pronouns of the character (optional)
        race_id: The ID of the race entity (optional)
        family_id: The ID of the family entity (optional)
        is_dead: Whether the character is dead (optional)
        image: URL or path to the character's image (optional)
        tags: Comma-separated list of tags (optional)
        entry: The character's entry/description (optional, must be HTML. If not HTML, it will be wrapped in <p> tags.)
        is_private: If the character is only visible to admin members (optional)
    """
    url = f"https://api.kanka.io/1.0/campaigns/{campaign_id}/characters"
    data = {"name": name}
    if title is not None:
        data["title"] = title
    if type is not None:
        data["type"] = type
    if age is not None:
        data["age"] = age
    if sex is not None:
        data["sex"] = sex
    if pronouns is not None:
        data["pronouns"] = pronouns
    if race_id is not None:
        data["race_id"] = race_id
    if family_id is not None:
        data["family_id"] = family_id
    if is_dead is not None:
        data["is_dead"] = is_dead
    if image is not None:
        data["image"] = image
    if tags is not None:
        data["tags"] = tags
    if entry is not None:
        entry_str = entry.strip()
        if not (entry_str.startswith('<') and entry_str.endswith('>')):
            entry_str = f"<p>{entry_str}</p>"
        data["entry"] = entry_str
    if is_private is not None:
        data["is_private"] = is_private
    response = requests.post(url, headers=get_headers(), json=data)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def update_character(
    campaign_id: int,      # The ID of the campaign
    character_id: int,     # The ID of the character to update
    name: str = None,      # The name of the character (optional)
    title: str = None,     # The character's title (optional)
    type: str = None,      # The type or class of the character (optional)
    age: str = None,       # The age of the character (optional)
    sex: str = None,       # The sex/gender of the character (optional)
    pronouns: str = None,  # The pronouns of the character (optional)
    race_id: int = None,   # The ID of the race entity (optional)
    family_id: int = None, # The ID of the family entity (optional)
    is_dead: bool = None,  # Whether the character is dead (optional)
    image: str = None,     # URL or path to the character's image (optional)
    tags: str = None,      # Comma-separated list of tags (optional)
    entry: str = None,     # The character's entry/description (optional, must be HTML)
    is_private: bool = None # If the character is only visible to admin members (optional)
):
    """Update an existing character.
    Fields:
        campaign_id: The ID of the campaign
        character_id: The ID of the character to update
        name: The name of the character (optional)
        title: The character's title (optional)
        type: The type or class of the character (optional)
        age: The age of the character (optional)
        sex: The sex/gender of the character (optional)
        pronouns: The pronouns of the character (optional)
        race_id: The ID of the race entity (optional)
        family_id: The ID of the family entity (optional)
        is_dead: Whether the character is dead (optional)
        image: URL or path to the character's image (optional)
        tags: Comma-separated list of tags (optional)
        entry: The character's entry/description (optional, must be HTML. If not HTML, it will be wrapped in <p> tags.)
        is_private: If the character is only visible to admin members (optional)
    """
    url = f"https://api.kanka.io/1.0/campaigns/{campaign_id}/characters/{character_id}"
    data = {}
    if name is not None:
        data["name"] = name
    if title is not None:
        data["title"] = title
    if type is not None:
        data["type"] = type
    if age is not None:
        data["age"] = age
    if sex is not None:
        data["sex"] = sex
    if pronouns is not None:
        data["pronouns"] = pronouns
    if race_id is not None:
        data["race_id"] = race_id
    if family_id is not None:
        data["family_id"] = family_id
    if is_dead is not None:
        data["is_dead"] = is_dead
    if image is not None:
        data["image"] = image
    if tags is not None:
        data["tags"] = tags
    if entry is not None:
        entry_str = entry.strip()
        if not (entry_str.startswith('<') and entry_str.endswith('>')):
            entry_str = f"<p>{entry_str}</p>"
        data["entry"] = entry_str
    if is_private is not None:
        data["is_private"] = is_private
    response = requests.put(url, headers=get_headers(), json=data)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def delete_character(campaign_id: int, character_id: int):
    """Delete a character by ID."""
    url = f"https://api.kanka.io/1.0/campaigns/{campaign_id}/characters/{character_id}"
    response = requests.delete(url, headers=get_headers())
    if response.status_code == 204:
        return {"success": True}
    response.raise_for_status()
    return {"success": False, "error": response.text}

@mcp.tool()
def list_locations(campaign_id: int):
    """List all locations in a campaign."""
    url = f"https://api.kanka.io/1.0/campaigns/{campaign_id}/locations"
    response = requests.get(url, headers=get_headers())
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_location(campaign_id: int, location_id: int):
    """Get a single location by ID."""
    url = f"https://api.kanka.io/1.0/campaigns/{campaign_id}/locations/{location_id}"
    response = requests.get(url, headers=get_headers())
    response.raise_for_status()
    return response.json()

@mcp.tool()
def create_location(
    campaign_id: int,  # The ID of the campaign to add the location to
    name: str,         # The name of the location (required)
    entry: str = None, # The location's entry/description (optional, must be HTML)
    type: str = None,  # Type of location (optional)
    location_id: int = None, # The parent location id (optional)
    tags: list = None, # Array of tag ids (optional)
    is_destroyed: bool = None, # If the location is destroyed (optional)
    is_private: bool = None    # If the location is only visible to admin members (optional)
):
    """Create a new location in a campaign.
    Fields:
        campaign_id: The ID of the campaign to add the location to
        name: The name of the location (required)
        entry: The location's entry/description (optional, must be HTML. If not HTML, it will be wrapped in <p> tags.)
        type: Type of location (optional)
        location_id: The parent location id (optional)
        tags: Array of tag ids (optional)
        is_destroyed: If the location is destroyed (optional)
        is_private: If the location is only visible to admin members (optional)
    """
    url = f"https://api.kanka.io/1.0/campaigns/{campaign_id}/locations"
    data = {"name": name}
    if entry is not None:
        entry_str = entry.strip()
        if not (entry_str.startswith('<') and entry_str.endswith('>')):
            entry_str = f"<p>{entry_str}</p>"
        data["entry"] = entry_str
    if type is not None:
        data["type"] = type
    if location_id is not None:
        data["location_id"] = location_id
    if tags is not None:
        data["tags"] = tags
    if is_destroyed is not None:
        data["is_destroyed"] = is_destroyed
    if is_private is not None:
        data["is_private"] = is_private
    response = requests.post(url, headers=get_headers(), json=data)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def update_location(
    campaign_id: int,      # The ID of the campaign
    location_id: int,      # The ID of the location to update
    name: str = None,      # The name of the location (optional)
    entry: str = None,     # The location's entry/description (optional, must be HTML)
    type: str = None,      # Type of location (optional)
    parent_location_id: int = None, # Deprecated, do not use
    new_parent_location_id: int = None, # The parent location id (optional, use this instead of location_id)
    tags: list = None,     # Array of tag ids (optional)
    is_destroyed: bool = None, # If the location is destroyed (optional)
    is_private: bool = None    # If the location is only visible to admin members (optional)
):
    """Update an existing location.
    Fields:
        campaign_id: The ID of the campaign
        location_id: The ID of the location to update
        name: The name of the location (optional)
        entry: The location's entry/description (optional, must be HTML. If not HTML, it will be wrapped in <p> tags.)
        type: Type of location (optional)
        new_parent_location_id: The parent location id (optional)
        tags: Array of tag ids (optional)
        is_destroyed: If the location is destroyed (optional)
        is_private: If the location is only visible to admin members (optional)
    """
    url = f"https://api.kanka.io/1.0/campaigns/{campaign_id}/locations/{location_id}"
    data = {}
    if name is not None:
        data["name"] = name
    if entry is not None:
        entry_str = entry.strip()
        if not (entry_str.startswith('<') and entry_str.endswith('>')):
            entry_str = f"<p>{entry_str}</p>"
        data["entry"] = entry_str
    if type is not None:
        data["type"] = type
    if new_parent_location_id is not None:
        data["location_id"] = new_parent_location_id
    if tags is not None:
        data["tags"] = tags
    if is_destroyed is not None:
        data["is_destroyed"] = is_destroyed
    if is_private is not None:
        data["is_private"] = is_private
    response = requests.put(url, headers=get_headers(), json=data)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def delete_location(campaign_id: int, location_id: int):
    """Delete a location by ID."""
    url = f"https://api.kanka.io/1.0/campaigns/{campaign_id}/locations/{location_id}"
    response = requests.delete(url, headers=get_headers())
    if response.status_code == 204:
        return {"success": True}
    response.raise_for_status()
    return {"success": False, "error": response.text}

@mcp.tool()
def list_posts(campaign_id: int, entity_id: int):
    """List all posts for a given entity in a campaign. Note: entity_id is the ID of the entity, not the post object ID."""
    url = f"https://api.kanka.io/1.0/campaigns/{campaign_id}/entities/{entity_id}/posts"
    response = requests.get(url, headers=get_headers())
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_post(campaign_id: int, entity_id: int, post_id: int):
    """Get a single post by ID for a given entity. Note: entity_id is the ID of the entity, not the post object ID."""
    url = f"https://api.kanka.io/1.0/campaigns/{campaign_id}/entities/{entity_id}/posts/{post_id}"
    response = requests.get(url, headers=get_headers())
    response.raise_for_status()
    return response.json()

@mcp.tool()
def create_post(
    campaign_id: int,  # The ID of the campaign
    entity_id: int,    # The ID of the entity this post belongs to (Required)
    name: str,         # The name/title of the post (required)
    entry: str = None, # The post content (optional, must be HTML)
    position: int = None, # The position/order of the post for ordering pinned posts (optional)
    visibility_id: int = None, # The visibility: 1 for all, 2 self, 3 admin, 4 self-admin or 5 members (optional)
    is_pinned: bool = None,    # Whether the post is pinned (optional)
    settings: dict = None,     # Settings object. E.g. collapsed:1 if pinned post should be collapsed on load (optional)
    tags: list = None           # Array of tag ids (optional)
):
    """Create a new post for an entity in a campaign.
    Fields:
        campaign_id: The ID of the campaign
        entity_id: The ID of the entity this post belongs to (Required)
        name: The name/title of the post (required)
        entry: The post content (optional, must be HTML. If not HTML, it will be wrapped in <p> tags.)
        position: The position/order of the post for ordering pinned posts (optional)
        visibility_id: The visibility: 1 for all, 2 self, 3 admin, 4 self-admin or 5 members (optional)
        is_pinned: Whether the post is pinned (optional)
        settings: Settings object. E.g. {'collapsed': 1} if pinned post should be collapsed on load (optional)
        tags: Array of tag ids (optional)
    """
    url = f"https://api.kanka.io/1.0/campaigns/{campaign_id}/entities/{entity_id}/posts"
    data = {"name": name, "entity_id": entity_id}
    if entry is not None:
        entry_str = entry.strip()
        if not (entry_str.startswith('<') and entry_str.endswith('>')):
            entry_str = f"<p>{entry_str}</p>"
        data["entry"] = entry_str
    if position is not None:
        data["position"] = position
    if visibility_id is not None:
        data["visibility_id"] = visibility_id
    if is_pinned is not None:
        data["is_pinned"] = is_pinned
    if settings is not None:
        data["settings"] = settings
    if tags is not None:
        data["tags"] = tags
    response = requests.post(url, headers=get_headers(), json=data)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def update_post(
    campaign_id: int,  # The ID of the campaign
    entity_id: int,    # The ID of the entity this post belongs to
    post_id: int,      # The ID of the post to update
    name: str = None,  # The name/title of the post (optional)
    entry: str = None, # The post content (optional, must be HTML)
    position: int = None, # The position/order of the post for ordering pinned posts (optional)
    visibility_id: int = None, # The visibility: 1 for all, 2 self, 3 admin, 4 self-admin or 5 members (optional)
    is_pinned: bool = None,    # Whether the post is pinned (optional)
    settings: dict = None,     # Settings object. E.g. collapsed:1 if pinned post should be collapsed on load (optional)
    tags: list = None          # Array of tag ids (optional)
):
    """Update a post for an entity in a campaign.
    Fields:
        campaign_id: The ID of the campaign
        entity_id: The ID of the entity this post belongs to
        post_id: The ID of the post to update
        name: The name/title of the post (optional)
        entry: The post content (optional, must be HTML. If not HTML, it will be wrapped in <p> tags.)
        position: The position/order of the post for ordering pinned posts (optional)
        visibility_id: The visibility: 1 for all, 2 self, 3 admin, 4 self-admin or 5 members (optional)
        is_pinned: Whether the post is pinned (optional)
        settings: Settings object. E.g. {'collapsed': 1} if pinned post should be collapsed on load (optional)
        tags: Array of tag ids (optional)
    """
    url = f"https://api.kanka.io/1.0/campaigns/{campaign_id}/entities/{entity_id}/posts/{post_id}"
    data = {}
    if name is not None:
        data["name"] = name
    if entry is not None:
        entry_str = entry.strip()
        if not (entry_str.startswith('<') and entry_str.endswith('>')):
            entry_str = f"<p>{entry_str}</p>"
        data["entry"] = entry_str
    if position is not None:
        data["position"] = position
    if visibility_id is not None:
        data["visibility_id"] = visibility_id
    if is_pinned is not None:
        data["is_pinned"] = is_pinned
    if settings is not None:
        data["settings"] = settings
    if tags is not None:
        data["tags"] = tags
    response = requests.put(url, headers=get_headers(), json=data)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def delete_post(campaign_id: int, entity_id: int, post_id: int):
    """Delete a post by ID for a given entity. Note: entity_id is the ID of the entity, not the post object ID."""
    url = f"https://api.kanka.io/1.0/campaigns/{campaign_id}/entities/{entity_id}/posts/{post_id}"
    response = requests.delete(url, headers=get_headers())
    if response.status_code == 204:
        return {"success": True}
    response.raise_for_status()
    return {"success": False, "error": response.text}

@mcp.tool()
def list_notes(campaign_id: int):
    """List all notes in a campaign."""
    url = f"https://api.kanka.io/1.0/campaigns/{campaign_id}/notes"
    response = requests.get(url, headers=get_headers())
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_note(campaign_id: int, note_id: int):
    """Get a single note by ID."""
    url = f"https://api.kanka.io/1.0/campaigns/{campaign_id}/notes/{note_id}"
    response = requests.get(url, headers=get_headers())
    response.raise_for_status()
    return response.json()

@mcp.tool()
def create_note(
    campaign_id: int,  # The ID of the campaign to add the note to
    name: str,         # The name of the note (required)
    entry: str = None, # The note's entry/description (optional, must be HTML)
    type: str = None,  # The note's type (optional)
    note_id: int = None, # The parent note id (optional)
    tags: list = None,   # Array of tag ids (optional)
    entity_image_uuid: str = None, # Gallery image UUID for the entity image (optional)
    entity_header_uuid: str = None, # Gallery image UUID for the entity header (limited to premium campaigns) (optional)
    is_private: bool = None    # If the note is only visible to admin members (optional)
):
    """Create a new note in a campaign.
    Fields:
        campaign_id: The ID of the campaign to add the note to
        name: The name of the note (required)
        entry: The note's entry/description (optional, must be HTML. If not HTML, it will be wrapped in <p> tags.)
        type: The note's type (optional)
        note_id: The parent note id (optional)
        tags: Array of tag ids (optional)
        entity_image_uuid: Gallery image UUID for the entity image (optional)
        entity_header_uuid: Gallery image UUID for the entity header (limited to premium campaigns) (optional)
        is_private: If the note is only visible to admin members (optional)
    """
    url = f"https://api.kanka.io/1.0/campaigns/{campaign_id}/notes"
    data = {"name": name}
    if entry is not None:
        entry_str = entry.strip()
        if not (entry_str.startswith('<') and entry_str.endswith('>')):
            entry_str = f"<p>{entry_str}</p>"
        data["entry"] = entry_str
    if type is not None:
        data["type"] = type
    if note_id is not None:
        data["note_id"] = note_id
    if tags is not None:
        data["tags"] = tags
    if entity_image_uuid is not None:
        data["entity_image_uuid"] = entity_image_uuid
    if entity_header_uuid is not None:
        data["entity_header_uuid"] = entity_header_uuid
    if is_private is not None:
        data["is_private"] = is_private
    response = requests.post(url, headers=get_headers(), json=data)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def update_note(
    campaign_id: int,     # The ID of the campaign
    note_id: int,         # The ID of the note to update
    name: str = None,     # The name of the note (optional)
    entry: str = None,    # The note's entry/description (optional, must be HTML)
    type: str = None,     # The note's type (optional)
    parent_note_id: int = None, # The parent note id (optional)
    tags: list = None,    # Array of tag ids (optional)
    entity_image_uuid: str = None, # Gallery image UUID for the entity image (optional)
    entity_header_uuid: str = None, # Gallery image UUID for the entity header (limited to premium campaigns) (optional)
    is_private: bool = None     # If the note is only visible to admin members (optional)
):
    """Update an existing note.
    Fields:
        campaign_id: The ID of the campaign
        note_id: The ID of the note to update
        name: The name of the note (optional)
        entry: The note's entry/description (optional, must be HTML. If not HTML, it will be wrapped in <p> tags.)
        type: The note's type (optional)
        parent_note_id: The parent note id (optional)
        tags: Array of tag ids (optional)
        entity_image_uuid: Gallery image UUID for the entity image (optional)
        entity_header_uuid: Gallery image UUID for the entity header (limited to premium campaigns) (optional)
        is_private: If the note is only visible to admin members (optional)
    """
    url = f"https://api.kanka.io/1.0/campaigns/{campaign_id}/notes/{note_id}"
    data = {}
    if name is not None:
        data["name"] = name
    if entry is not None:
        entry_str = entry.strip()
        if not (entry_str.startswith('<') and entry_str.endswith('>')):
            entry_str = f"<p>{entry_str}</p>"
        data["entry"] = entry_str
    if type is not None:
        data["type"] = type
    if parent_note_id is not None:
        data["note_id"] = parent_note_id
    if tags is not None:
        data["tags"] = tags
    if entity_image_uuid is not None:
        data["entity_image_uuid"] = entity_image_uuid
    if entity_header_uuid is not None:
        data["entity_header_uuid"] = entity_header_uuid
    if is_private is not None:
        data["is_private"] = is_private
    response = requests.put(url, headers=get_headers(), json=data)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def delete_note(campaign_id: int, note_id: int):
    """Delete a note by ID."""
    url = f"https://api.kanka.io/1.0/campaigns/{campaign_id}/notes/{note_id}"
    response = requests.delete(url, headers=get_headers())
    if response.status_code == 204:
        return {"success": True}
    response.raise_for_status()
    return {"success": False, "error": response.text}

@mcp.tool()
def list_journals(campaign_id: int):
    """List all journals in a campaign."""
    url = f"https://api.kanka.io/1.0/campaigns/{campaign_id}/journals"
    response = requests.get(url, headers=get_headers())
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_journal(campaign_id: int, journal_id: int):
    """Get a single journal by ID."""
    url = f"https://api.kanka.io/1.0/campaigns/{campaign_id}/journals/{journal_id}"
    response = requests.get(url, headers=get_headers())
    response.raise_for_status()
    return response.json()

@mcp.tool()
def create_journal(
    campaign_id: int,  # The ID of the campaign to add the journal to
    name: str,         # The name of the journal (required)
    entry: str = None, # The journal's entry/description (optional, must be HTML)
    type: str = None,  # The journal's type (optional)
    date: str = None,  # The date of the session (optional)
    journal_id: int = None, # The ID of the journal's parent journal (optional)
    author_id: int = None,  # The "author" of the journal (entity id) (optional)
    tags: list = None,      # Array of tag ids (optional)
    entity_image_uuid: str = None, # Gallery image UUID for the entity image (optional)
    entity_header_uuid: str = None, # Gallery image UUID for the entity header (premium campaigns) (optional)
    is_private: bool = None    # If the journal is only visible to admin members (optional)
):
    """Create a new journal in a campaign.
    Fields:
        campaign_id: The ID of the campaign to add the journal to
        name: The name of the journal (required)
        entry: The journal's entry/description (optional, must be HTML. If not HTML, it will be wrapped in <p> tags.)
        type: The journal's type (optional)
        date: The date of the session (optional)
        journal_id: The ID of the journal's parent journal (optional)
        author_id: The "author" of the journal (entity id) (optional)
        tags: Array of tag ids (optional)
        entity_image_uuid: Gallery image UUID for the entity image (optional)
        entity_header_uuid: Gallery image UUID for the entity header (premium campaigns) (optional)
        is_private: If the journal is only visible to admin members (optional)
    """
    url = f"https://api.kanka.io/1.0/campaigns/{campaign_id}/journals"
    data = {"name": name}
    if entry is not None:
        entry_str = entry.strip()
        if not (entry_str.startswith('<') and entry_str.endswith('>')):
            entry_str = f"<p>{entry_str}</p>"
        data["entry"] = entry_str
    if type is not None:
        data["type"] = type
    if date is not None:
        data["date"] = date
    if journal_id is not None:
        data["journal_id"] = journal_id
    if author_id is not None:
        data["author_id"] = author_id
    if tags is not None:
        data["tags"] = tags
    if entity_image_uuid is not None:
        data["entity_image_uuid"] = entity_image_uuid
    if entity_header_uuid is not None:
        data["entity_header_uuid"] = entity_header_uuid
    if is_private is not None:
        data["is_private"] = is_private
    response = requests.post(url, headers=get_headers(), json=data)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def update_journal(
    campaign_id: int,     # The ID of the campaign
    journal_id: int,      # The ID of the journal to update
    name: str = None,     # The name of the journal (optional)
    entry: str = None,    # The journal's entry/description (optional, must be HTML)
    type: str = None,     # The journal's type (optional)
    date: str = None,     # The date of the session (optional)
    parent_journal_id: int = None, # The ID of the journal's parent journal (optional)
    author_id: int = None,  # The "author" of the journal (entity id) (optional)
    tags: list = None,      # Array of tag ids (optional)
    entity_image_uuid: str = None, # Gallery image UUID for the entity image (optional)
    entity_header_uuid: str = None, # Gallery image UUID for the entity header (premium campaigns) (optional)
    is_private: bool = None     # If the journal is only visible to admin members (optional)
):
    """Update an existing journal.
    Fields:
        campaign_id: The ID of the campaign
        journal_id: The ID of the journal to update
        name: The name of the journal (optional)
        entry: The journal's entry/description (optional, must be HTML. If not HTML, it will be wrapped in <p> tags.)
        type: The journal's type (optional)
        date: The date of the session (optional)
        parent_journal_id: The ID of the journal's parent journal (optional)
        author_id: The "author" of the journal (entity id) (optional)
        tags: Array of tag ids (optional)
        entity_image_uuid: Gallery image UUID for the entity image (optional)
        entity_header_uuid: Gallery image UUID for the entity header (premium campaigns) (optional)
        is_private: If the journal is only visible to admin members (optional)
    """
    url = f"https://api.kanka.io/1.0/campaigns/{campaign_id}/journals/{journal_id}"
    data = {}
    if name is not None:
        data["name"] = name
    if entry is not None:
        entry_str = entry.strip()
        if not (entry_str.startswith('<') and entry_str.endswith('>')):
            entry_str = f"<p>{entry_str}</p>"
        data["entry"] = entry_str
    if type is not None:
        data["type"] = type
    if date is not None:
        data["date"] = date
    if parent_journal_id is not None:
        data["journal_id"] = parent_journal_id
    if author_id is not None:
        data["author_id"] = author_id
    if tags is not None:
        data["tags"] = tags
    if entity_image_uuid is not None:
        data["entity_image_uuid"] = entity_image_uuid
    if entity_header_uuid is not None:
        data["entity_header_uuid"] = entity_header_uuid
    if is_private is not None:
        data["is_private"] = is_private
    response = requests.put(url, headers=get_headers(), json=data)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def delete_journal(campaign_id: int, journal_id: int):
    """Delete a journal by ID."""
    url = f"https://api.kanka.io/1.0/campaigns/{campaign_id}/journals/{journal_id}"
    response = requests.delete(url, headers=get_headers())
    if response.status_code == 204:
        return {"success": True}
    response.raise_for_status()
    return {"success": False, "error": response.text}

def main_mcp():
    mcp.run(transport="stdio")

def main():
    main_mcp()

