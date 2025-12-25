#!/usr/bin/env python3
"""Generate presentation images for all fighters.

This script generates "Trash Beach Party" style presentation images
for each fighter and saves them to data/images/{fighter}/presentation.png.

Uses all existing images in each fighter's folder as reference.

Usage:
    uv run python scripts/generate_presentation_images.py
    uv run python scripts/generate_presentation_images.py --force  # Regenerate all
    uv run python scripts/generate_presentation_images.py --fighter bohdan  # Single fighter
"""

import argparse
import logging
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env
from dotenv import load_dotenv

load_dotenv(project_root / ".env")

from src.image_generator import generate_presentation_image
from src.state_manager import load_fighters

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Fighter display names (Ukrainian)
FIGHTER_DISPLAY_NAMES: dict[str, str] = {
    "andrew_3": 'Пєтух "Три Андрія"',
    "bohdan": 'Пєтух "Богдан"',
    "oleg": 'Пєтух "Олег"',
    "petro": 'Пєтух "Петро"',
    "roma": 'Пєтух "Рома"',
    "vadym": 'Пєтух "Вадим"',
}

# Number of people for each fighter (andrew_3 has 3 people)
FIGHTER_NUM_PEOPLE: dict[str, int] = {
    "andrew_3": 3,
    "bohdan": 1,
    "oleg": 1,
    "petro": 1,
    "roma": 1,
    "vadym": 1,
}


def get_all_images(fighter_dir: Path) -> list[str]:
    """Get all image paths in a fighter directory.

    Excludes presentation.png (the output file).

    Args:
        fighter_dir: Path to fighter's image directory

    Returns:
        List of absolute paths to all images
    """
    image_extensions = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
    images = []

    for file in fighter_dir.iterdir():
        if file.is_file() and file.suffix.lower() in image_extensions:
            # Skip presentation.png (our output file)
            if file.name.lower() == "presentation.png":
                continue
            images.append(str(file))

    return sorted(images)


def generate_for_fighter(
    fighter_name: str,
    force: bool = False,
) -> bool:
    """Generate presentation image for a single fighter.

    Args:
        fighter_name: Name of the fighter (directory name)
        force: If True, regenerate even if presentation.png exists

    Returns:
        True if image was generated successfully, False otherwise
    """
    base_path = project_root / "data" / "images"
    fighter_dir = base_path / fighter_name
    output_path = fighter_dir / "presentation.png"

    if not fighter_dir.exists():
        logger.error(f"Fighter directory not found: {fighter_dir}")
        return False

    # Check if already exists
    if output_path.exists() and not force:
        logger.info(f"Skipping {fighter_name}: presentation.png already exists (use --force to regenerate)")
        return True

    # Get display name and num_people
    display_name = FIGHTER_DISPLAY_NAMES.get(fighter_name, f'Пєтух "{fighter_name}"')
    num_people = FIGHTER_NUM_PEOPLE.get(fighter_name, 1)

    # Get all reference images
    image_paths = get_all_images(fighter_dir)
    if not image_paths:
        logger.error(f"No reference images found for {fighter_name}")
        return False

    logger.info(f"Generating presentation image for {fighter_name}")
    logger.info(f"  Display name: {display_name}")
    logger.info(f"  Number of people: {num_people}")
    logger.info(f"  Using {len(image_paths)} reference images:")
    for img in image_paths:
        logger.info(f"    - {Path(img).name}")

    try:
        # Generate the image
        image_bytes = generate_presentation_image(
            image_paths=image_paths,
            fighter_name=fighter_name,
            display_name=display_name,
            num_people=num_people,
        )

        # Save to file
        with open(output_path, "wb") as f:
            f.write(image_bytes)

        logger.info(f"Saved presentation image: {output_path} ({len(image_bytes)} bytes)")
        return True

    except Exception as e:
        logger.error(f"Failed to generate image for {fighter_name}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Generate presentation images for fighters"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate images even if they already exist",
    )
    parser.add_argument(
        "--fighter",
        type=str,
        help="Generate for a specific fighter only",
    )
    args = parser.parse_args()

    # Fighter names (from the display names mapping)
    fighter_names_all = list(FIGHTER_DISPLAY_NAMES.keys())

    # Determine which fighters to process
    if args.fighter:
        if args.fighter not in fighter_names_all:
            logger.error(f"Fighter '{args.fighter}' not found. Available: {fighter_names_all}")
            sys.exit(1)
        fighter_names = [args.fighter]
    else:
        fighter_names = fighter_names_all

    logger.info(f"Processing {len(fighter_names)} fighters...")

    # Generate images
    success_count = 0
    fail_count = 0

    for name in fighter_names:
        logger.info(f"\n{'='*50}")
        logger.info(f"Processing: {name}")
        logger.info(f"{'='*50}")

        if generate_for_fighter(name, force=args.force):
            success_count += 1
        else:
            fail_count += 1

    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("SUMMARY")
    logger.info(f"{'='*50}")
    logger.info(f"Total fighters: {len(fighter_names)}")
    logger.info(f"Success: {success_count}")
    logger.info(f"Failed: {fail_count}")

    if fail_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
