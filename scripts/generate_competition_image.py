"""One-time script to generate competition presentation image.

Uses Gemini API to generate a single rooster presentation image
for use throughout the competition.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from google import genai
from google.genai import types

from src.config import GEMINI_API_KEY, GEMINI_MODEL

# Reference images from bohdan's folder
ROOSTER_IMAGE = Path("data/images/bohdan/image.png")
HUMAN_IMAGE = Path("data/images/bohdan/telegram-cloud-photo-size-2-5361762667988716719-y.jpg")
OUTPUT_PATH = Path("data/competition/presentation.png")

# Competition poster prompt - person presenting rooster
COMPETITION_POSTER_PROMPT = """
Generate a COMPETITION POSTER style image:

Scene: A person dramatically presenting their fighting rooster at a WILD LAKESIDE PARTY COMPETITION!
This is the OFFICIAL COMPETITION POSTER for "DANA COCKFIGHT"!

Subject:
- A person in a fun party/trashy costume HOLDING their rooster HIGH above their head
- Championship pose - like lifting a trophy
- Confident, triumphant expression
- The rooster looks MAJESTIC and FIERCE

Style - COMPETITION POSTER:
- Bold, dramatic composition
- Text-free (no text overlay)
- Professional sports poster aesthetic mixed with party vibes
- Dynamic lighting - spotlight effect
- Lakeside party atmosphere in background
- Fairy lights, party decorations visible
- Sunset/golden hour lighting
- Epic, heroic framing

The image should work as a universal competition promotional image.
Show the person presenting the rooster as THE CHAMPION being revealed!

Important: Use the provided reference photos for the person's appearance and rooster features.
Make it look like an official competition poster - dramatic but fun!
"""


def generate_competition_image() -> bytes:
    """Generate the competition presentation image."""
    print("Initializing Gemini client...")
    client = genai.Client(api_key=GEMINI_API_KEY)

    print(f"Loading reference images...")
    print(f"  - Rooster: {ROOSTER_IMAGE}")
    print(f"  - Human: {HUMAN_IMAGE}")

    # Read reference images
    with open(ROOSTER_IMAGE, "rb") as f:
        rooster_bytes = f.read()
    with open(HUMAN_IMAGE, "rb") as f:
        human_bytes = f.read()

    # Determine mime types
    rooster_mime = "image/png"
    human_mime = "image/jpeg"

    print(f"Generating image with Gemini ({GEMINI_MODEL})...")
    print("This may take 10-30 seconds...")

    # Build content with prompt and reference images
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=COMPETITION_POSTER_PROMPT),
                types.Part.from_bytes(data=rooster_bytes, mime_type=rooster_mime),
                types.Part.from_bytes(data=human_bytes, mime_type=human_mime),
            ],
        )
    ]

    # Generate image
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["Text", "Image"],
        ),
    )

    # Extract image from response
    if not response.candidates:
        raise ValueError("No candidates in response")

    candidate = response.candidates[0]
    if not candidate.content or not candidate.content.parts:
        raise ValueError("No content in response")

    for part in candidate.content.parts:
        if hasattr(part, "inline_data") and part.inline_data:
            if part.inline_data.mime_type and part.inline_data.mime_type.startswith("image/"):
                image_data = part.inline_data.data
                if isinstance(image_data, str):
                    import base64
                    return base64.b64decode(image_data)
                return image_data

    # Check for text response (might explain why it couldn't generate)
    for part in candidate.content.parts:
        if hasattr(part, "text") and part.text:
            print(f"Model response: {part.text}")

    raise ValueError("No image found in response")


def main():
    """Main entry point."""
    print("=" * 50)
    print("DANA COCKFIGHT - Competition Image Generator")
    print("=" * 50)

    # Check if reference images exist
    if not ROOSTER_IMAGE.exists():
        print(f"ERROR: Rooster image not found: {ROOSTER_IMAGE}")
        sys.exit(1)
    if not HUMAN_IMAGE.exists():
        print(f"ERROR: Human image not found: {HUMAN_IMAGE}")
        sys.exit(1)

    # Ensure output directory exists
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    try:
        image_bytes = generate_competition_image()

        # Save the image
        with open(OUTPUT_PATH, "wb") as f:
            f.write(image_bytes)

        print(f"\nSUCCESS! Image saved to: {OUTPUT_PATH}")
        print(f"Size: {len(image_bytes):,} bytes")

    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
