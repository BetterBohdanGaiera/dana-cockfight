"""
Text generator module for Dana CockFight Telegram Bot.

Generates Ukrainian trash-talk text using Google Gemini API.
Powers the press conference dialogue between fighting roosters.
"""

import logging

from google import genai

from .config import GEMINI_API_KEY, GEMINI_TEXT_MODEL
from .prompts import TRASH_TALK_SYSTEM_PROMPT, get_trash_talk_user_prompt

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
