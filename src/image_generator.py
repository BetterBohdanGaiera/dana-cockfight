"""Gemini-powered image generation for Dana CockFight Telegram Bot.

Provides image generation for fighter portraits and press conference scenes.
Uses Google's Gemini API with image generation capabilities.

Main functions:
- generate_fighter_portrait: Creates portrait of person holding their rooster
- generate_scene_image: Creates press conference trash-talk scene
"""

import base64
import logging
from pathlib import Path
from typing import Optional

from google import genai
from google.genai import types

from .config import GEMINI_API_KEY, GEMINI_MODEL
from .prompts import get_fighter_portrait_prompt, get_scene_image_prompt

logger = logging.getLogger(__name__)

# Singleton client instance
_client: Optional[genai.Client] = None


def _get_client() -> genai.Client:
    """Get or create the Gemini client.

    Implements singleton pattern to reuse client across calls.

    Returns:
        genai.Client: Initialized Gemini client.

    Raises:
        ValueError: If GEMINI_API_KEY is not configured.
    """
    global _client
    if _client is None:
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not configured. Check your .env file.")
        _client = genai.Client(api_key=GEMINI_API_KEY)
        logger.info("Gemini client initialized")
    return _client


def _extract_image_from_response(response) -> bytes:
    """Extract image bytes from Gemini response.

    Args:
        response: Gemini API response object.

    Returns:
        bytes: Decoded image data.

    Raises:
        ValueError: If no image was found in the response.
    """
    # Get candidates from response
    if not response.candidates or len(response.candidates) == 0:
        # Check for text-only response (model may have refused)
        if hasattr(response, 'text') and response.text:
            logger.warning(f"Model returned text instead of image: {response.text[:200]}")
        raise ValueError("No candidates in response - image generation may have been refused")

    # Get parts from first candidate
    candidate = response.candidates[0]
    if not hasattr(candidate, 'content') or not candidate.content:
        raise ValueError("No content in response candidate")

    parts = candidate.content.parts
    if not parts:
        raise ValueError("No parts in response content")

    # Find image parts
    for part in parts:
        if hasattr(part, 'inline_data') and part.inline_data:
            inline_data = part.inline_data
            if hasattr(inline_data, 'mime_type') and inline_data.mime_type:
                if inline_data.mime_type.startswith('image/'):
                    # Decode base64 image data
                    image_data = inline_data.data
                    if isinstance(image_data, str):
                        return base64.b64decode(image_data)
                    elif isinstance(image_data, bytes):
                        return image_data

    # Check for text response (model may explain why it couldn't generate)
    for part in parts:
        if hasattr(part, 'text') and part.text:
            logger.warning(f"Model returned text: {part.text[:200]}")

    raise ValueError("No image found in response parts")


def _read_image_file(image_path: str) -> tuple[bytes, str]:
    """Read image file and determine mime type.

    Args:
        image_path: Path to the image file.

    Returns:
        tuple: (image_bytes, mime_type)

    Raises:
        FileNotFoundError: If image file doesn't exist.
        ValueError: If file extension is not supported.
    """
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    # Determine mime type from extension
    extension = path.suffix.lower()
    mime_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
    }

    mime_type = mime_types.get(extension)
    if not mime_type:
        raise ValueError(f"Unsupported image extension: {extension}")

    with open(path, 'rb') as f:
        image_bytes = f.read()

    return image_bytes, mime_type


def generate_fighter_portrait(
    rooster_image_path: str,
    human_image_path: str,
    fighter_name: str,
    rooster_description: str,
) -> bytes:
    """Generate a fighter portrait with person holding their rooster.

    Uses real rooster photo and real person photo as reference to generate
    a dramatic portrait of the trainer/owner holding their fighting rooster.

    Args:
        rooster_image_path: Path to the real rooster photo.
        human_image_path: Path to the real person photo.
        fighter_name: Name of the fighter (owner/trainer).
        rooster_description: Description of the rooster fighter.

    Returns:
        bytes: Generated image data (PNG/JPEG).

    Raises:
        FileNotFoundError: If reference images are not found.
        ValueError: If image generation fails.
        Exception: For other API errors.
    """
    logger.info(f"Generating fighter portrait for {fighter_name}")

    try:
        # Read reference images
        rooster_bytes, rooster_mime = _read_image_file(rooster_image_path)
        human_bytes, human_mime = _read_image_file(human_image_path)

        logger.debug(
            f"Loaded reference images: rooster={len(rooster_bytes)} bytes, "
            f"human={len(human_bytes)} bytes"
        )

        # Build prompt
        prompt = get_fighter_portrait_prompt(fighter_name, rooster_description)

        # Get client
        client = _get_client()

        # Build content with prompt and reference images
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt),
                    types.Part.from_bytes(
                        data=rooster_bytes,
                        mime_type=rooster_mime,
                    ),
                    types.Part.from_bytes(
                        data=human_bytes,
                        mime_type=human_mime,
                    ),
                ],
            )
        ]

        # Generate image with square aspect ratio for portrait
        logger.info(f"Calling Gemini API for fighter portrait (model: {GEMINI_MODEL})")
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["Text", "Image"],
                image_generation_config=types.ImageGenerationConfig(
                    aspect_ratio="1:1",
                ),
            ),
        )

        # Extract image from response
        image_bytes = _extract_image_from_response(response)
        logger.info(f"Successfully generated portrait for {fighter_name} ({len(image_bytes)} bytes)")

        return image_bytes

    except FileNotFoundError:
        logger.error(f"Reference image not found for {fighter_name}")
        raise
    except ValueError as e:
        logger.error(f"Image generation failed for {fighter_name}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error generating portrait for {fighter_name}: {e}")
        raise


def generate_scene_image(
    fighter_name: str,
    trash_talk_text: str,
    opponent_name: str,
    round_number: int = 1,
) -> bytes:
    """Generate a press conference scene image.

    Creates a dramatic scene showing a rooster delivering trash-talk
    at a press conference, with the opponent reacting.

    Args:
        fighter_name: Name of the speaking fighter.
        trash_talk_text: The trash-talk message being delivered.
        opponent_name: Name of the opponent.
        round_number: Current round number (1-3).

    Returns:
        bytes: Generated image data (PNG/JPEG).

    Raises:
        ValueError: If image generation fails.
        Exception: For other API errors.
    """
    logger.info(
        f"Generating scene image: {fighter_name} vs {opponent_name} (round {round_number})"
    )

    try:
        # Build prompt
        prompt = get_scene_image_prompt(
            fighter_name=fighter_name,
            trash_talk_text=trash_talk_text,
            opponent_name=opponent_name,
            round_number=round_number,
        )

        # Get client
        client = _get_client()

        # Generate image with 16:9 aspect ratio for scene
        logger.info(f"Calling Gemini API for scene image (model: {GEMINI_MODEL})")
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["Text", "Image"],
                image_generation_config=types.ImageGenerationConfig(
                    aspect_ratio="16:9",
                ),
            ),
        )

        # Extract image from response
        image_bytes = _extract_image_from_response(response)
        logger.info(
            f"Successfully generated scene for {fighter_name} vs {opponent_name} "
            f"({len(image_bytes)} bytes)"
        )

        return image_bytes

    except ValueError as e:
        logger.error(
            f"Scene image generation failed for {fighter_name} vs {opponent_name}: {e}"
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error generating scene for {fighter_name} vs {opponent_name}: {e}"
        )
        raise


def generate_scene_image_safe(
    fighter_name: str,
    trash_talk_text: str,
    opponent_name: str,
    round_number: int = 1,
    fallback_text: Optional[str] = None,
) -> Optional[bytes]:
    """Generate scene image with fallback behavior.

    Same as generate_scene_image but returns None instead of raising
    on failure, with optional logging of fallback behavior.

    Args:
        fighter_name: Name of the speaking fighter.
        trash_talk_text: The trash-talk message being delivered.
        opponent_name: Name of the opponent.
        round_number: Current round number (1-3).
        fallback_text: Optional text to log when falling back.

    Returns:
        Optional[bytes]: Generated image data or None if generation failed.
    """
    try:
        return generate_scene_image(
            fighter_name=fighter_name,
            trash_talk_text=trash_talk_text,
            opponent_name=opponent_name,
            round_number=round_number,
        )
    except Exception as e:
        if fallback_text:
            logger.warning(f"{fallback_text}: {e}")
        else:
            logger.warning(f"Scene image generation failed, returning None: {e}")
        return None


def generate_fighter_portrait_safe(
    rooster_image_path: str,
    human_image_path: str,
    fighter_name: str,
    rooster_description: str,
    fallback_text: Optional[str] = None,
) -> Optional[bytes]:
    """Generate fighter portrait with fallback behavior.

    Same as generate_fighter_portrait but returns None instead of raising
    on failure, with optional logging of fallback behavior.

    Args:
        rooster_image_path: Path to the real rooster photo.
        human_image_path: Path to the real person photo.
        fighter_name: Name of the fighter (owner/trainer).
        rooster_description: Description of the rooster fighter.
        fallback_text: Optional text to log when falling back.

    Returns:
        Optional[bytes]: Generated image data or None if generation failed.
    """
    try:
        return generate_fighter_portrait(
            rooster_image_path=rooster_image_path,
            human_image_path=human_image_path,
            fighter_name=fighter_name,
            rooster_description=rooster_description,
        )
    except Exception as e:
        if fallback_text:
            logger.warning(f"{fallback_text}: {e}")
        else:
            logger.warning(f"Fighter portrait generation failed, returning None: {e}")
        return None
