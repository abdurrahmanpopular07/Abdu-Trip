"""
TripGenius — AI-generated destination images.

Uses Pollinations.ai's free text-to-image endpoint. No API key required —
the endpoint itself returns image bytes for a URL built from the prompt, so
the "generation" is literally just building a well-formed URL. The browser
requests the image directly (<img src="...">), so no image bytes ever pass
through our own server.

Docs: https://pollinations.ai (image.pollinations.ai/prompt/{prompt})
"""

import hashlib
import urllib.parse

IMAGE_BASE_URL = "https://image.pollinations.ai/prompt"
IMAGE_WIDTH = 900
IMAGE_HEIGHT = 560
# A fixed seed per destination keeps the same place returning the same
# image on repeat visits instead of a new random one every time.
SEED_BASE = 42


def build_image_prompt(destination_key, dest_info):
    """Compose a descriptive, safe prompt from curated destination data."""
    landmark = dest_info["things"][0] if dest_info.get("things") else dest_info["label"]
    return (
        f"{dest_info['label']}, {dest_info['state']}, India, {landmark}, "
        f"travel photography, golden hour lighting, vibrant colours, ultra detailed"
    )


def _stable_seed(destination_key):
    # Python's built-in hash() is randomized per process for strings, so it
    # would give a different "same" image on every server restart. Use a
    # stable hash instead so each destination always maps to the same seed.
    digest = hashlib.md5(destination_key.encode("utf-8")).hexdigest()
    return SEED_BASE + (int(digest[:8], 16) % 10000)


def get_destination_image_url(destination_key, dest_info):
    """Return a deterministic Pollinations.ai image URL for this destination."""
    prompt = build_image_prompt(destination_key, dest_info)
    encoded_prompt = urllib.parse.quote(prompt)
    seed = _stable_seed(destination_key)
    return (
        f"{IMAGE_BASE_URL}/{encoded_prompt}"
        f"?width={IMAGE_WIDTH}&height={IMAGE_HEIGHT}&seed={seed}&nologo=true"
    )
