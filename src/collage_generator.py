"""
VS Collage generator module for Dana CockFight Telegram Bot.

Creates dramatic "VS" collage images combining two fighter presentation images
for fight announcements in the /draw command.
"""

import io
import logging
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

logger = logging.getLogger(__name__)

# Collage dimensions
COLLAGE_WIDTH = 1200
COLLAGE_HEIGHT = 600

# Colors
VS_COLOR = (255, 50, 50)  # Red
VS_OUTLINE_COLOR = (0, 0, 0)  # Black
GRADIENT_LEFT = (50, 50, 150)  # Blue-ish
GRADIENT_RIGHT = (150, 50, 50)  # Red-ish
NAME_COLOR = (255, 255, 255)  # White
NAME_SHADOW_COLOR = (0, 0, 0)  # Black


def _create_gradient_background(width: int, height: int) -> Image.Image:
    """Create a dramatic gradient background from blue to red.

    Args:
        width: Image width in pixels.
        height: Image height in pixels.

    Returns:
        PIL Image with gradient background.
    """
    img = Image.new("RGB", (width, height))

    for x in range(width):
        # Interpolate between left and right colors
        ratio = x / width
        r = int(GRADIENT_LEFT[0] * (1 - ratio) + GRADIENT_RIGHT[0] * ratio)
        g = int(GRADIENT_LEFT[1] * (1 - ratio) + GRADIENT_RIGHT[1] * ratio)
        b = int(GRADIENT_LEFT[2] * (1 - ratio) + GRADIENT_RIGHT[2] * ratio)

        for y in range(height):
            img.putpixel((x, y), (r, g, b))

    return img


def _load_and_resize_fighter(image_path: str, target_height: int) -> Image.Image | None:
    """Load fighter image and resize to fit target height.

    Args:
        image_path: Path to fighter's presentation.png.
        target_height: Desired height in pixels.

    Returns:
        Resized PIL Image or None if loading fails.
    """
    try:
        img = Image.open(image_path)

        # Calculate new width maintaining aspect ratio
        aspect_ratio = img.width / img.height
        new_width = int(target_height * aspect_ratio)

        # Resize with high quality
        img = img.resize((new_width, target_height), Image.Resampling.LANCZOS)

        # Convert to RGBA for transparency handling
        if img.mode != "RGBA":
            img = img.convert("RGBA")

        return img
    except Exception as e:
        logger.error(f"Failed to load fighter image {image_path}: {e}")
        return None


def _draw_vs_text(
    draw: ImageDraw.ImageDraw,
    center_x: int,
    center_y: int,
    font_size: int = 120,
) -> None:
    """Draw dramatic "VS" text in the center.

    Args:
        draw: PIL ImageDraw object.
        center_x: X coordinate for center.
        center_y: Y coordinate for center.
        font_size: Font size for VS text.
    """
    # Try to load a bold font, fall back to default
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Impact.ttf", font_size)
    except (OSError, IOError):
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except (OSError, IOError):
            font = ImageFont.load_default()

    text = "VS"

    # Get text bounding box for centering
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = center_x - text_width // 2
    y = center_y - text_height // 2

    # Draw outline/shadow for dramatic effect
    outline_width = 4
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=VS_OUTLINE_COLOR)

    # Draw main text
    draw.text((x, y), text, font=font, fill=VS_COLOR)


def _draw_fighter_name(
    draw: ImageDraw.ImageDraw,
    name: str,
    x: int,
    y: int,
    font_size: int = 36,
) -> None:
    """Draw fighter name with shadow effect.

    Args:
        draw: PIL ImageDraw object.
        name: Fighter name to draw.
        x: X coordinate for text center.
        y: Y coordinate for text.
        font_size: Font size for name.
    """
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", font_size)
    except (OSError, IOError):
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except (OSError, IOError):
            font = ImageFont.load_default()

    # Get text bounding box for centering
    bbox = draw.textbbox((0, 0), name, font=font)
    text_width = bbox[2] - bbox[0]

    centered_x = x - text_width // 2

    # Draw shadow
    shadow_offset = 2
    draw.text((centered_x + shadow_offset, y + shadow_offset), name, font=font, fill=NAME_SHADOW_COLOR)

    # Draw main text
    draw.text((centered_x, y), name, font=font, fill=NAME_COLOR)


def create_vs_collage(
    image1_path: str,
    image2_path: str,
    fighter1_name: str = "",
    fighter2_name: str = "",
) -> bytes:
    """Create a VS collage from two fighter presentation images.

    Creates a dramatic collage with:
    - Gradient background (blue to red)
    - Fighter 1 on the left side
    - Fighter 2 on the right side
    - "VS" text in the center
    - Fighter names below their images

    Args:
        image1_path: Path to first fighter's presentation.png.
        image2_path: Path to second fighter's presentation.png.
        fighter1_name: Name of first fighter (optional).
        fighter2_name: Name of second fighter (optional).

    Returns:
        PNG image as bytes.
    """
    try:
        # Create gradient background
        collage = _create_gradient_background(COLLAGE_WIDTH, COLLAGE_HEIGHT)

        # Load fighter images
        fighter1_img = _load_and_resize_fighter(image1_path, COLLAGE_HEIGHT - 80)
        fighter2_img = _load_and_resize_fighter(image2_path, COLLAGE_HEIGHT - 80)

        # Calculate positions
        center_x = COLLAGE_WIDTH // 2

        if fighter1_img:
            # Position fighter 1 on the left (right-aligned to center with padding)
            f1_x = center_x - 80 - fighter1_img.width
            f1_y = 20
            collage.paste(fighter1_img, (max(0, f1_x), f1_y), fighter1_img if fighter1_img.mode == "RGBA" else None)

        if fighter2_img:
            # Position fighter 2 on the right (left-aligned from center with padding)
            f2_x = center_x + 80
            f2_y = 20
            collage.paste(fighter2_img, (min(COLLAGE_WIDTH - fighter2_img.width, f2_x), f2_y), fighter2_img if fighter2_img.mode == "RGBA" else None)

        # Draw VS text in center
        draw = ImageDraw.Draw(collage)
        _draw_vs_text(draw, center_x, COLLAGE_HEIGHT // 2)

        # Draw fighter names if provided
        if fighter1_name:
            left_quarter = COLLAGE_WIDTH // 4
            _draw_fighter_name(draw, fighter1_name, left_quarter, COLLAGE_HEIGHT - 50)

        if fighter2_name:
            right_quarter = 3 * COLLAGE_WIDTH // 4
            _draw_fighter_name(draw, fighter2_name, right_quarter, COLLAGE_HEIGHT - 50)

        # Convert to bytes
        output = io.BytesIO()
        collage.save(output, format="PNG", quality=95)
        output.seek(0)

        logger.info(f"Created VS collage for {fighter1_name} vs {fighter2_name}")
        return output.getvalue()

    except Exception as e:
        logger.error(f"Failed to create VS collage: {e}", exc_info=True)
        # Return a simple fallback image
        return _create_fallback_collage(fighter1_name, fighter2_name)


def _create_fallback_collage(fighter1_name: str, fighter2_name: str) -> bytes:
    """Create a simple text-only VS collage as fallback.

    Args:
        fighter1_name: Name of first fighter.
        fighter2_name: Name of second fighter.

    Returns:
        PNG image as bytes.
    """
    # Create a simple gradient background
    collage = _create_gradient_background(COLLAGE_WIDTH, COLLAGE_HEIGHT)
    draw = ImageDraw.Draw(collage)

    # Draw VS text
    _draw_vs_text(draw, COLLAGE_WIDTH // 2, COLLAGE_HEIGHT // 2)

    # Draw fighter names
    if fighter1_name:
        _draw_fighter_name(draw, fighter1_name, COLLAGE_WIDTH // 4, COLLAGE_HEIGHT // 2)
    if fighter2_name:
        _draw_fighter_name(draw, fighter2_name, 3 * COLLAGE_WIDTH // 4, COLLAGE_HEIGHT // 2)

    # Convert to bytes
    output = io.BytesIO()
    collage.save(output, format="PNG")
    output.seek(0)

    return output.getvalue()
