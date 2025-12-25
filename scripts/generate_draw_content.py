#!/usr/bin/env python3
"""
Generate all pre-saved content for the /draw command.

This script generates:
- VS images for each fight
- All dialogue text (Dana comments, trash-talk, reactions, conclusions)

Run once to generate content, then the bot will use saved files.

Usage:
    uv run python scripts/generate_draw_content.py
"""

import json
import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

from src.config import validate_config
from src.state_manager import FIXED_PAIRINGS, load_fighters, Fighter
from src.image_generator import generate_vs_image_with_retry
from src.text_generator import (
    generate_dana_match_comment,
    generate_dana_question,
    generate_fighter_trashtalk,
    generate_dana_reaction,
    generate_dana_conclusion,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def get_fighter_by_name(fighters: list[Fighter], name: str) -> Fighter | None:
    """Find fighter by name."""
    for f in fighters:
        if f.name == name:
            return f
    return None


def get_presentation_path(fighter: Fighter) -> str:
    """Get path to fighter's presentation image."""
    base_path = Path(__file__).parent.parent / "data" / "images" / fighter.name
    return str(base_path / "presentation.png")


def generate_fight_content(
    fight_number: int,
    fighter1: Fighter,
    fighter2: Fighter,
    output_dir: Path,
) -> bool:
    """Generate all content for a single fight.

    Args:
        fight_number: Fight number (1-3)
        fighter1: First fighter
        fighter2: Second fighter
        output_dir: Directory to save content

    Returns:
        True if successful, False otherwise
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"GENERATING FIGHT {fight_number}: {fighter1.display_name} vs {fighter2.display_name}")
    logger.info(f"{'='*60}\n")

    # Create output directory
    fight_dir = output_dir / f"fight_{fight_number}"
    fight_dir.mkdir(parents=True, exist_ok=True)

    # 1. Generate VS image
    logger.info("Generating VS image...")
    vs_image_path = fight_dir / "vs_image.png"

    if not vs_image_path.exists():
        presentation1 = get_presentation_path(fighter1)
        presentation2 = get_presentation_path(fighter2)

        vs_bytes = generate_vs_image_with_retry(
            fighter1_presentation_path=presentation1,
            fighter2_presentation_path=presentation2,
            fighter1_display_name=fighter1.display_name,
            fighter2_display_name=fighter2.display_name,
            max_retries=3,
            retry_delay=2.0,
        )

        if vs_bytes:
            vs_image_path.write_bytes(vs_bytes)
            logger.info(f"✓ VS image saved: {vs_image_path}")
        else:
            logger.error("✗ Failed to generate VS image!")
            return False
    else:
        logger.info(f"✓ VS image already exists: {vs_image_path}")

    # 2. Generate dialogue text
    logger.info("\nGenerating dialogue...")
    dialogue_path = fight_dir / "dialogue.json"

    if not dialogue_path.exists():
        # Dana's opening comment
        logger.info("  - Generating Dana's match comment...")
        dana_comment = generate_dana_match_comment(
            fighter1_display_name=fighter1.display_name,
            fighter1_description=fighter1.description,
            fighter2_display_name=fighter2.display_name,
            fighter2_description=fighter2.description,
            fight_number=fight_number,
        )
        logger.info(f"    Dana: {dana_comment[:50]}...")

        # Dana's question to fighter 1
        logger.info("  - Generating Dana's question...")
        dana_question = generate_dana_question(fighter1.display_name)
        logger.info(f"    Dana: {dana_question[:50]}...")

        # Fighter 1 trash-talk
        logger.info(f"  - Generating {fighter1.display_name}'s trash-talk...")
        fighter1_trashtalk = generate_fighter_trashtalk(
            fighter_display_name=fighter1.display_name,
            fighter_description=fighter1.description,
            opponent_display_name=fighter2.display_name,
            opponent_description=fighter2.description,
        )
        logger.info(f"    {fighter1.display_name}: {fighter1_trashtalk[:50]}...")

        # Dana's reaction
        logger.info("  - Generating Dana's reaction...")
        dana_reaction = generate_dana_reaction(
            fighter1_trashtalk=fighter1_trashtalk,
            fighter2_display_name=fighter2.display_name,
        )
        logger.info(f"    Dana: {dana_reaction[:50]}...")

        # Fighter 2 trash-talk
        logger.info(f"  - Generating {fighter2.display_name}'s trash-talk...")
        fighter2_trashtalk = generate_fighter_trashtalk(
            fighter_display_name=fighter2.display_name,
            fighter_description=fighter2.description,
            opponent_display_name=fighter1.display_name,
            opponent_description=fighter1.description,
        )
        logger.info(f"    {fighter2.display_name}: {fighter2_trashtalk[:50]}...")

        # Dana's conclusion
        logger.info("  - Generating Dana's conclusion...")
        dana_conclusion = generate_dana_conclusion(
            fighter1_display_name=fighter1.display_name,
            fighter2_display_name=fighter2.display_name,
            fight_number=fight_number,
        )
        logger.info(f"    Dana: {dana_conclusion[:50]}...")

        # Save dialogue JSON
        dialogue = {
            "fighter1": fighter1.name,
            "fighter1_display_name": fighter1.display_name,
            "fighter2": fighter2.name,
            "fighter2_display_name": fighter2.display_name,
            "fight_number": fight_number,
            "messages": {
                "dana_comment": dana_comment,
                "dana_question": dana_question,
                "fighter1_trashtalk": fighter1_trashtalk,
                "dana_reaction": dana_reaction,
                "fighter2_trashtalk": fighter2_trashtalk,
                "dana_conclusion": dana_conclusion,
            }
        }

        with open(dialogue_path, "w", encoding="utf-8") as f:
            json.dump(dialogue, f, ensure_ascii=False, indent=2)

        logger.info(f"✓ Dialogue saved: {dialogue_path}")
    else:
        logger.info(f"✓ Dialogue already exists: {dialogue_path}")

    logger.info(f"\n✓ Fight {fight_number} content complete!")
    return True


def main():
    """Main entry point."""
    logger.info("="*60)
    logger.info("DANA COCKFIGHT DRAW CONTENT GENERATOR")
    logger.info("="*60)

    # Validate config
    try:
        validate_config()
        logger.info("✓ Configuration validated")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)

    # Load fighters
    logger.info("Loading fighters...")
    fighters = load_fighters()
    logger.info(f"✓ Loaded {len(fighters)} fighters")

    # Setup output directory
    output_dir = Path(__file__).parent.parent / "data" / "draw"
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Output directory: {output_dir}")

    # Generate content for each fight
    success_count = 0
    for fight_num, (name1, name2) in enumerate(FIXED_PAIRINGS, 1):
        fighter1 = get_fighter_by_name(fighters, name1)
        fighter2 = get_fighter_by_name(fighters, name2)

        if not fighter1 or not fighter2:
            logger.error(f"Could not find fighters: {name1}, {name2}")
            continue

        if generate_fight_content(fight_num, fighter1, fighter2, output_dir):
            success_count += 1

    # Summary
    logger.info("\n" + "="*60)
    logger.info("GENERATION COMPLETE")
    logger.info("="*60)
    logger.info(f"Successfully generated: {success_count}/{len(FIXED_PAIRINGS)} fights")

    if success_count == len(FIXED_PAIRINGS):
        logger.info("\n✓ All content ready! You can now run the bot.")
        return 0
    else:
        logger.warning("\n⚠ Some content failed to generate. Check logs above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
