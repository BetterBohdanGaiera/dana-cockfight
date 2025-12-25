"""
Text generator module for Dana CockFight Telegram Bot.

Generates Ukrainian trash-talk text using Google Gemini API.
Powers the press conference dialogue between fighting roosters.
"""

import logging

from google import genai

from .config import GEMINI_API_KEY, GEMINI_TEXT_MODEL
from .prompts import (
    TRASH_TALK_SYSTEM_PROMPT,
    get_trash_talk_user_prompt,
    FIGHT_INTRO_SYSTEM_PROMPT,
    get_fight_intro_prompt,
    # New Dana dialogue prompts
    DANA_MATCH_COMMENT_SYSTEM_PROMPT,
    get_dana_match_comment_prompt,
    get_dana_question_prompt,
    get_fighter_trashtalk_prompt,
    DANA_REACTION_SYSTEM_PROMPT,
    get_dana_reaction_prompt,
    DANA_CONCLUSION_SYSTEM_PROMPT,
    get_dana_conclusion_prompt,
)

logger = logging.getLogger(__name__)

# Singleton client instance
_client: genai.Client | None = None


def _get_client() -> genai.Client:
    """
    Get or create the Gemini client singleton.

    Returns:
        genai.Client: The initialized Gemini client.
    """
    global _client
    if _client is None:
        _client = genai.Client(api_key=GEMINI_API_KEY)
        logger.debug("Gemini client initialized for text generation")
    return _client


def generate_trash_talk(
    fighter_name: str,
    fighter_description: str,
    opponent_name: str,
    opponent_description: str,
    round_number: int,
) -> str:
    """
    Generate Ukrainian trash-talk for a press conference.

    Generates aggressive, humorous Ukrainian trash-talk from a rooster's
    perspective (first person). The text is party-appropriate and consists
    of 2-3 sentences per message.

    Args:
        fighter_name: Name of the speaking fighter (rooster's owner).
        fighter_description: Description of the speaking fighter's characteristics.
        opponent_name: Name of the opponent (opponent's owner).
        opponent_description: Description of the opponent's characteristics.
        round_number: Current round number (1-3).

    Returns:
        str: Generated Ukrainian trash-talk text ready for Telegram message.
            Returns a fallback message if generation fails.
    """
    try:
        client = _get_client()

        # Build user prompt using the prompt template
        user_prompt = get_trash_talk_user_prompt(
            fighter_name=fighter_name,
            fighter_description=fighter_description,
            opponent_name=opponent_name,
            opponent_description=opponent_description,
            round_number=round_number,
        )

        # Combine system prompt and user prompt
        full_prompt = f"{TRASH_TALK_SYSTEM_PROMPT}\n\n{user_prompt}"

        # Call Gemini API
        response = client.models.generate_content(
            model=GEMINI_TEXT_MODEL,
            contents=full_prompt,
        )

        # Extract text from response
        trash_talk = response.text

        logger.info(
            f"Generated trash-talk for {fighter_name} vs {opponent_name} "
            f"(round {round_number})"
        )
        return trash_talk.strip()

    except Exception as e:
        logger.error(f"Trash-talk generation failed for {fighter_name}: {e}")
        # Return fallback text in Ukrainian
        return f"Ку-ка-рі-куууу! Я {fighter_name} і я готовий до бою!"


def generate_fight_intro(
    fighter1_name: str,
    fighter1_description: str,
    fighter2_name: str,
    fighter2_description: str,
    fight_number: int,
) -> str:
    """
    Generate dramatic fight intro announcement in Ukrainian.

    Creates an exciting, hype-style intro for a fight matchup
    using AI generation in the style of UFC/boxing announcers.

    Args:
        fighter1_name: Name of the first fighter.
        fighter1_description: Description of the first fighter.
        fighter2_name: Name of the second fighter.
        fighter2_description: Description of the second fighter.
        fight_number: Fight number (1-3).

    Returns:
        str: Generated Ukrainian fight intro text.
            Returns a fallback message if generation fails.
    """
    try:
        client = _get_client()

        # Build user prompt using the prompt template
        user_prompt = get_fight_intro_prompt(
            fighter1_name=fighter1_name,
            fighter1_desc=fighter1_description,
            fighter2_name=fighter2_name,
            fighter2_desc=fighter2_description,
            fight_number=fight_number,
        )

        # Combine system prompt and user prompt
        full_prompt = f"{FIGHT_INTRO_SYSTEM_PROMPT}\n\n{user_prompt}"

        # Call Gemini API
        response = client.models.generate_content(
            model=GEMINI_TEXT_MODEL,
            contents=full_prompt,
        )

        # Extract text from response
        intro = response.text

        logger.info(
            f"Generated fight intro for {fighter1_name} vs {fighter2_name} "
            f"(fight {fight_number})"
        )
        return intro.strip()

    except Exception as e:
        logger.error(
            f"Fight intro generation failed for {fighter1_name} vs {fighter2_name}: {e}"
        )
        # Return fallback intro in Ukrainian
        return (
            f"БІЙ #{fight_number}: На арену виходять два непереможних бійці! "
            f"{fighter1_name} проти {fighter2_name}! Хто переможе?"
        )


# =============================================================================
# DANA DIALOGUE GENERATION FUNCTIONS (for draw announcements)
# =============================================================================


def generate_dana_match_comment(
    fighter1_display_name: str,
    fighter1_description: str,
    fighter2_display_name: str,
    fighter2_description: str,
    fight_number: int,
) -> str:
    """
    Generate Dana CockFight's comment about an upcoming match.

    Creates an opinionated comment from the organizer's perspective
    about the fight matchup.

    Args:
        fighter1_display_name: Ukrainian display name of first fighter.
        fighter1_description: Description of the first fighter.
        fighter2_display_name: Ukrainian display name of second fighter.
        fighter2_description: Description of the second fighter.
        fight_number: Fight number (1-3).

    Returns:
        str: Generated Ukrainian comment from Dana CockFight.
    """
    try:
        client = _get_client()

        user_prompt = get_dana_match_comment_prompt(
            fighter1_display_name=fighter1_display_name,
            fighter1_desc=fighter1_description,
            fighter2_display_name=fighter2_display_name,
            fighter2_desc=fighter2_description,
            fight_number=fight_number,
        )

        full_prompt = f"{DANA_MATCH_COMMENT_SYSTEM_PROMPT}\n\n{user_prompt}"

        response = client.models.generate_content(
            model=GEMINI_TEXT_MODEL,
            contents=full_prompt,
        )

        comment = response.text
        logger.info(f"Generated Dana comment for fight {fight_number}")
        return comment.strip()

    except Exception as e:
        logger.error(f"Dana comment generation failed for fight {fight_number}: {e}")
        return (
            f"Оце буде бій! {fighter1_display_name} проти {fighter2_display_name} - "
            f"це буде щось неймовірне!"
        )


def generate_dana_question(fighter_display_name: str) -> str:
    """
    Generate Dana's question to a fighter.

    Simple template-based question - no AI needed.

    Args:
        fighter_display_name: Ukrainian display name of the fighter.

    Returns:
        str: Dana's question to the fighter.
    """
    return get_dana_question_prompt(fighter_display_name).strip()


def generate_fighter_trashtalk(
    fighter_display_name: str,
    fighter_description: str,
    opponent_display_name: str,
    opponent_description: str,
) -> str:
    """
    Generate fighter's trash-talk during draw announcement.

    Uses fighter's strengths and opponent's weaknesses for context.

    Args:
        fighter_display_name: Ukrainian display name of speaking fighter.
        fighter_description: Description of the speaking fighter.
        opponent_display_name: Ukrainian display name of opponent.
        opponent_description: Description of the opponent.

    Returns:
        str: Generated Ukrainian trash-talk from the fighter.
    """
    try:
        client = _get_client()

        user_prompt = get_fighter_trashtalk_prompt(
            fighter_display_name=fighter_display_name,
            fighter_desc=fighter_description,
            opponent_display_name=opponent_display_name,
            opponent_desc=opponent_description,
        )

        full_prompt = f"{TRASH_TALK_SYSTEM_PROMPT}\n\n{user_prompt}"

        response = client.models.generate_content(
            model=GEMINI_TEXT_MODEL,
            contents=full_prompt,
        )

        trashtalk = response.text
        logger.info(f"Generated trashtalk for {fighter_display_name}")
        return trashtalk.strip()

    except Exception as e:
        logger.error(f"Trashtalk generation failed for {fighter_display_name}: {e}")
        return f"Ку-ка-рі-куууу! Я {fighter_display_name} і я готовий розірвати суперника!"


def generate_dana_reaction(
    fighter1_trashtalk: str,
    fighter2_display_name: str,
) -> str:
    """
    Generate Dana's reaction to a fighter's trash-talk.

    Reacts to the trash-talk and passes the word to the other fighter.

    Args:
        fighter1_trashtalk: The trash-talk that was just said.
        fighter2_display_name: Ukrainian display name of the next fighter to speak.

    Returns:
        str: Generated Ukrainian reaction from Dana.
    """
    try:
        client = _get_client()

        user_prompt = get_dana_reaction_prompt(
            fighter1_trashtalk=fighter1_trashtalk,
            fighter2_display_name=fighter2_display_name,
        )

        full_prompt = f"{DANA_REACTION_SYSTEM_PROMPT}\n\n{user_prompt}"

        response = client.models.generate_content(
            model=GEMINI_TEXT_MODEL,
            contents=full_prompt,
        )

        reaction = response.text
        logger.info(f"Generated Dana reaction, passing to {fighter2_display_name}")
        return reaction.strip()

    except Exception as e:
        logger.error(f"Dana reaction generation failed: {e}")
        return f"Ого! Гостро! {fighter2_display_name}, що скажеш у відповідь?"


def generate_dana_conclusion(
    fighter1_display_name: str,
    fighter2_display_name: str,
    fight_number: int,
) -> str:
    """
    Generate Dana's conclusion after both fighters spoke.

    Wraps up the verbal exchange and hypes the upcoming fight.

    Args:
        fighter1_display_name: Ukrainian display name of first fighter.
        fighter2_display_name: Ukrainian display name of second fighter.
        fight_number: Fight number (1-3).

    Returns:
        str: Generated Ukrainian conclusion from Dana.
    """
    try:
        client = _get_client()

        user_prompt = get_dana_conclusion_prompt(
            fighter1_display_name=fighter1_display_name,
            fighter2_display_name=fighter2_display_name,
            fight_number=fight_number,
        )

        full_prompt = f"{DANA_CONCLUSION_SYSTEM_PROMPT}\n\n{user_prompt}"

        response = client.models.generate_content(
            model=GEMINI_TEXT_MODEL,
            contents=full_prompt,
        )

        conclusion = response.text
        logger.info(f"Generated Dana conclusion for fight {fight_number}")
        return conclusion.strip()

    except Exception as e:
        logger.error(f"Dana conclusion generation failed for fight {fight_number}: {e}")
        return (
            f"Неймовірно! {fighter1_display_name} vs {fighter2_display_name} - "
            f"це буде ЛЕГЕНДАРНИЙ бій!"
        )
