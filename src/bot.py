"""Main Telegram bot implementation for Dana CockFight.

Handles all command interactions for the rooster fighting press conference bot.
Coordinates fighter announcements, matchmaking, and AI-generated trash-talk
with scene images.

Commands:
    /start - Welcome message and bot introduction
    /help - List all commands and workflow
    /fighters - Display all 6 pre-loaded fighters
    /draw - Randomly create 3 pairs for battles
    /conference - Run press conference with trash-talk
"""

import asyncio
import logging
import random
from pathlib import Path

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from .config import TELEGRAM_BOT_TOKEN, validate_config
from .prompts import (
    BOT_INTRO_TEXT,
    HELP_TEXT,
    NO_DRAW_YET_TEXT,
    get_draw_announcement,
    get_conference_start_message,
    get_conference_end_message,
)
from .image_generator import generate_scene_image_safe
from .text_generator import generate_trash_talk
from .state_manager import get_game_state

# Telegram message limits (conservative to be safe)
CAPTION_LIMIT = 900
MESSAGE_LIMIT = 4096

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command.

    Sends welcome message explaining the bot's purpose and available commands.
    """
    if update.message:
        await update.message.reply_text(BOT_INTRO_TEXT)
        logger.info(
            f"User {update.effective_user.id if update.effective_user else 'unknown'} "
            "started the bot"
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command.

    Sends help text with all commands and workflow description.
    """
    if update.message:
        await update.message.reply_text(HELP_TEXT)


async def fighters_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /fighters command.

    Displays all 6 pre-loaded fighters with their rooster images and descriptions.
    Sends one photo per fighter with caption containing name and description.
    """
    if not update.message or not update.effective_chat:
        return

    try:
        chat_id = update.effective_chat.id
        state = get_game_state(chat_id)

        if not state.fighters:
            await update.message.reply_text(
                "Помилка: бійці не завантажені. Зверніться до адміністратора."
            )
            return

        logger.info(f"Showing {len(state.fighters)} fighters to chat {chat_id}")

        for fighter in state.fighters:
            try:
                # Load rooster image
                rooster_path = Path(fighter.rooster_image_path)
                if not rooster_path.exists():
                    logger.warning(f"Rooster image not found: {rooster_path}")
                    await update.message.reply_text(
                        f"*{fighter.name}*\n{fighter.description}\n"
                        "(Фото недоступне)",
                        parse_mode="Markdown",
                    )
                    continue

                with open(rooster_path, "rb") as f:
                    image_bytes = f.read()

                # Build caption
                caption = f"*{fighter.name}*\n{fighter.description}"

                # Truncate caption if too long
                if len(caption) > CAPTION_LIMIT:
                    caption = caption[: CAPTION_LIMIT - 3] + "..."

                # Send photo with caption
                await update.message.reply_photo(
                    photo=image_bytes,
                    caption=caption,
                    parse_mode="Markdown",
                )

                # Small delay between fighters to avoid rate limiting
                await asyncio.sleep(0.5)

            except Exception as e:
                logger.error(f"Error sending fighter {fighter.name}: {e}", exc_info=True)
                await update.message.reply_text(
                    f"Помилка при відправці бійця {fighter.name}. Спробуй ще раз!"
                )

        await update.message.reply_text(
            "Ось усі 6 бійців! Використай /draw для жеребкування."
        )

    except Exception as e:
        logger.error(f"Error in fighters_command: {e}", exc_info=True)
        if update.message:
            await update.message.reply_text(
                "Виникла помилка при показі бійців. Спробуй ще раз!"
            )


async def draw_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /draw command.

    Randomly pairs 6 fighters into 3 matches and announces the pairings.
    """
    if not update.message or not update.effective_chat:
        return

    try:
        chat_id = update.effective_chat.id
        state = get_game_state(chat_id)

        # Check we have exactly 6 fighters
        if len(state.fighters) != 6:
            await update.message.reply_text(
                f"Помилка: потрібно 6 бійців для жеребкування, "
                f"але знайдено тільки {len(state.fighters)}."
            )
            return

        # Perform the draw
        pairings = state.draw_pairings()

        # Format pairing names for announcement
        pairing_names = [(p[0].name, p[1].name) for p in pairings]

        # Get formatted announcement
        announcement = get_draw_announcement(pairing_names)

        await update.message.reply_text(announcement)

        logger.info(
            f"Draw completed for chat {chat_id}: "
            f"{[(p[0].name, p[1].name) for p in pairings]}"
        )

    except Exception as e:
        logger.error(f"Error in draw_command: {e}", exc_info=True)
        if update.message:
            await update.message.reply_text(
                "Виникла помилка при жеребкуванні. Спробуй ще раз!"
            )


async def conference_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /conference command.

    Runs press conference for current pair with 3 rounds of trash-talk.
    Each round has both fighters exchange AI-generated trash-talk with scene images.
    """
    if not update.message or not update.effective_chat:
        return

    try:
        chat_id = update.effective_chat.id
        state = get_game_state(chat_id)

        # Check if pairings exist
        if not state.pairings:
            await update.message.reply_text(NO_DRAW_YET_TEXT)
            return

        # Get current pair
        current_pair = state.get_current_pair()
        if current_pair is None:
            await update.message.reply_text(
                "Усі пресс-конференції завершені! "
                "Використай /draw для нового жеребкування."
            )
            return

        fighter1, fighter2 = current_pair
        pair_number = state.current_conference + 1

        logger.info(
            f"Starting conference {pair_number}: {fighter1.name} vs {fighter2.name}"
        )

        # Send conference start message
        start_message = get_conference_start_message(
            pair_number=pair_number,
            fighter1_name=fighter1.name,
            fighter2_name=fighter2.name,
        )
        await update.message.reply_text(start_message)

        # Reset round counter for this conference
        state.conference_round = 0

        # 3 rounds of trash-talk
        for round_num in range(1, 4):
            # Send round announcement
            await update.message.reply_text(f"--- РАУНД {round_num} ---")
            await asyncio.sleep(1)

            # Fighter 1 speaks
            await _send_trash_talk_message(
                update=update,
                speaking_fighter=fighter1,
                opponent_fighter=fighter2,
                round_number=round_num,
            )

            # Dramatic delay
            await asyncio.sleep(2.5)

            # Fighter 2 speaks
            await _send_trash_talk_message(
                update=update,
                speaking_fighter=fighter2,
                opponent_fighter=fighter1,
                round_number=round_num,
            )

            # Delay between rounds (unless last round)
            if round_num < 3:
                await asyncio.sleep(2.5)

            state.conference_round += 1

        # Randomly select winner
        winner = random.choice([fighter1, fighter2])
        loser = fighter2 if winner == fighter1 else fighter1

        # Send conference end message
        end_message = get_conference_end_message(
            fighter1_name=winner.name,
            fighter2_name=loser.name,
        )
        await update.message.reply_text(end_message)

        # Advance to next pair
        has_more = state.advance_conference()

        if has_more:
            await update.message.reply_text(
                "Готові до наступної пресс-конференції? Використай /conference!"
            )
        else:
            await update.message.reply_text(
                "Усі пресс-конференції завершені! "
                "Дякую за участь у Dana CockFight!\n\n"
                "Для нової гри: /draw"
            )

        logger.info(
            f"Conference {pair_number} completed. Winner: {winner.name}. "
            f"More conferences: {has_more}"
        )

    except Exception as e:
        logger.error(f"Error in conference_command: {e}", exc_info=True)
        if update.message:
            await update.message.reply_text(
                "Виникла помилка під час пресс-конференції. Спробуй ще раз!"
            )


async def _send_trash_talk_message(
    update: Update,
    speaking_fighter,
    opponent_fighter,
    round_number: int,
) -> None:
    """Send a single trash-talk message with scene image.

    Generates trash-talk text via Claude API and scene image via Gemini API.
    Falls back to text-only if image generation fails.

    Args:
        update: Telegram update object.
        speaking_fighter: Fighter who is speaking.
        opponent_fighter: Opponent fighter.
        round_number: Current round number (1-3).
    """
    if not update.message:
        return

    try:
        # Generate trash-talk text
        trash_talk = generate_trash_talk(
            fighter_name=speaking_fighter.name,
            fighter_description=speaking_fighter.description,
            opponent_name=opponent_fighter.name,
            opponent_description=opponent_fighter.description,
            round_number=round_number,
        )

        # Format caption with fighter name
        caption = f"*{speaking_fighter.name}:*\n{trash_talk}"

        # Truncate if too long
        if len(caption) > CAPTION_LIMIT:
            caption = caption[: CAPTION_LIMIT - 3] + "..."

        # Generate scene image (async to not block)
        scene_image = await asyncio.to_thread(
            generate_scene_image_safe,
            speaking_fighter.name,
            trash_talk,
            opponent_fighter.name,
            round_number,
        )

        if scene_image:
            # Send photo with trash-talk as caption
            await update.message.reply_photo(
                photo=scene_image,
                caption=caption,
                parse_mode="Markdown",
            )
            logger.info(
                f"Sent trash-talk with image: {speaking_fighter.name} "
                f"(round {round_number})"
            )
        else:
            # Fallback: send text only
            await update.message.reply_text(caption, parse_mode="Markdown")
            logger.info(
                f"Sent trash-talk (text only): {speaking_fighter.name} "
                f"(round {round_number})"
            )

    except Exception as e:
        logger.error(
            f"Error sending trash-talk for {speaking_fighter.name}: {e}",
            exc_info=True,
        )
        # Send fallback message
        fallback = f"*{speaking_fighter.name}:*\nКу-ка-рі-куууу! Я готовий до бою!"
        await update.message.reply_text(fallback, parse_mode="Markdown")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the bot.

    Logs the error and sends a user-friendly message in Ukrainian.
    """
    logger.error(
        f"Exception while handling an update: {context.error}",
        exc_info=context.error,
    )

    if isinstance(update, Update) and update.message:
        await update.message.reply_text(
            "Виникла технічна помилка. Спробуй ще раз пізніше!"
        )


def main() -> None:
    """Start the Dana CockFight Telegram bot.

    Validates configuration, sets up handlers, and starts polling.
    """
    # Validate configuration before starting
    validate_config()

    logger.info("Starting Dana CockFight Bot...")

    # Create the Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("fighters", fighters_command))
    application.add_handler(CommandHandler("draw", draw_command))
    application.add_handler(CommandHandler("conference", conference_command))

    # Add error handler
    application.add_error_handler(error_handler)

    logger.info("Bot is ready! Starting polling...")

    # Run the bot until interrupted
    application.run_polling(allowed_updates=Update.ALL_TYPES)

    logger.info("Bot stopped.")


if __name__ == "__main__":
    main()
