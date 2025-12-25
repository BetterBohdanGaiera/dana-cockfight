"""Main Telegram bot implementation for Dana CockFight.

Handles all command interactions for the rooster fighting press conference bot.
Coordinates fighter announcements, matchmaking, and AI-generated trash-talk
with scene images.

Commands:
    /start - Welcome message and bot introduction
    /help - List all commands and workflow
    /fighters - Display all 6 pre-loaded fighters
    /draw - Show next fight from fixed pairings with dialogue
"""

import asyncio
import json
import logging
import random
from pathlib import Path
from typing import TypedDict

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from .config import TELEGRAM_BOT_TOKEN, validate_config
from .prompts import (
    BOT_INTRO_TEXT,
    HELP_TEXT,
    NO_DRAW_YET_TEXT,
    DRAW_ANNOUNCEMENT_OUTRO,
    get_conference_start_message,
    get_conference_end_message,
)
from .image_generator import generate_scene_image_safe, generate_vs_image_with_retry
from .text_generator import generate_trash_talk, generate_fight_intro, generate_dana_chat_response
from .state_manager import get_game_state


# Type definitions for fight data
class FightMessages(TypedDict):
    dana_comment: str
    dana_question: str
    fighter1_trashtalk: str
    dana_reaction: str
    fighter2_trashtalk: str
    dana_conclusion: str


class FightData(TypedDict):
    fighter1: str
    fighter1_display_name: str
    fighter2: str
    fighter2_display_name: str
    fight_number: int
    messages: FightMessages

# Telegram message limits (conservative to be safe)
CAPTION_LIMIT = 900
MESSAGE_LIMIT = 4096

# Path to pre-generated draw content
DRAW_DATA_DIR = Path(__file__).parent.parent / "data" / "draw"

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Vote storage: {chat_id: {fight_number: {"votes": {fighter_name: count}, "voters": set(user_ids)}}}
_votes: dict[int, dict[int, dict]] = {}


def load_fight_data(fight_number: int) -> tuple[bytes | None, FightData | None]:
    """Load pre-generated fight data from disk.

    Args:
        fight_number: Fight number (1-3).

    Returns:
        Tuple of (vs_image_bytes, dialogue_data) or (None, None) if not found.
    """
    fight_dir = DRAW_DATA_DIR / f"fight_{fight_number}"

    vs_image_path = fight_dir / "vs_image.png"
    dialogue_path = fight_dir / "dialogue.json"

    vs_image: bytes | None = None
    dialogue: FightData | None = None

    if vs_image_path.exists():
        vs_image = vs_image_path.read_bytes()
        logger.info(f"Loaded VS image for fight {fight_number}")
    else:
        logger.warning(f"VS image not found: {vs_image_path}")

    if dialogue_path.exists():
        with open(dialogue_path, "r", encoding="utf-8") as f:
            dialogue = json.load(f)
        logger.info(f"Loaded dialogue for fight {fight_number}")
    else:
        logger.warning(f"Dialogue not found: {dialogue_path}")

    return vs_image, dialogue


async def _show_fighters_sequence(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show all 6 fighters with presentation images - shared logic for /start and /fighters.

    Displays all 6 pre-loaded fighters with their presentation images.
    Uses presentation.png from each fighter's folder if available,
    falls back to static competition image otherwise.
    """
    if not update.message or not update.effective_chat:
        return

    chat_id = update.effective_chat.id
    state = get_game_state(chat_id)

    if not state.fighters:
        await update.message.reply_text(
            "Помилка: бійці не завантажені. Зверніться до адміністратора."
        )
        return

    logger.info(f"Showing {len(state.fighters)} fighters to chat {chat_id}")

    # Load the fallback competition presentation image once
    fallback_image_path = Path("data/competition/presentation.png")
    fallback_image: bytes | None = None
    if fallback_image_path.exists():
        with open(fallback_image_path, "rb") as f:
            fallback_image = f.read()

    # Hype messages between fighters (5 messages for fighters 1-5, none after the last one)
    hype_messages = [
        "Але це ще тільки початок... Хто наступний? 😈🔥",
        "Йоооо! А ось і ще один претендент на корону... 👑💀",
        "Думаєш це все? ХУЙНЯ! Далі буде ще жорсткіше! 🤯",
        "Зачекай-зачекай... Ще не все! Наступний боєць — ЛЕГЕНДА! 🏆😈",
        "І НАРЕШТІ... Останній! Той, заради кого ми тут зібралися... 🎂👊",
    ]

    # Opening announcement with intro image
    intro_image_path = Path("data/data_cockfight/into_message.png")
    opening_caption = (
        "🔥🐓 DANA COCKFIGHT PRESENTS 🐓🔥\n\n"
        "Йо-йо-йоооо! Вітаю на Trash Beach Party! 🏖️🔥\n"
        "Шість божевільних півнів! Шість ще божевільніших друзів!\n"
        "Найкрейзовіший турнір півнячих боїв серед своїх!\n"
        "Хто виживе? Хто обісреться?\n"
        "Зараз дізнаємось!\n\n"
        "ОГОЛОШУЄМО БІЙЦІВ! 👊💀"
    )

    if intro_image_path.exists():
        with open(intro_image_path, "rb") as f:
            intro_image = f.read()
        await update.message.reply_photo(
            photo=intro_image,
            caption=opening_caption,
        )
    else:
        await update.message.reply_text(opening_caption)

    await asyncio.sleep(2.0)

    for idx, fighter in enumerate(state.fighters):
        try:
            # Build caption (name is already on the presentation image)
            caption = fighter.description

            # Truncate caption if too long
            if len(caption) > CAPTION_LIMIT:
                caption = caption[: CAPTION_LIMIT - 3] + "..."

            # Try to load fighter-specific presentation image
            fighter_dir = Path(fighter.rooster_image_path).parent
            presentation_path = fighter_dir / "presentation.png"

            if presentation_path.exists():
                with open(presentation_path, "rb") as f:
                    fighter_image = f.read()
                logger.info(f"Using presentation image for {fighter.name}")
            elif fallback_image:
                fighter_image = fallback_image
                logger.info(f"Using fallback image for {fighter.name}")
            else:
                # No image available at all
                await update.message.reply_text(
                    f"*{fighter.name}*\n{fighter.description}",
                    parse_mode="Markdown",
                )
                logger.warning(f"No image available for {fighter.name}")
                continue

            # Send presentation image with fighter info
            await update.message.reply_photo(
                photo=fighter_image,
                caption=caption,
                parse_mode="Markdown",
            )
            logger.info(f"Sent presentation for {fighter.name}")

            # Send hype message after each fighter (except the last one)
            if idx < len(state.fighters) - 1:
                await asyncio.sleep(1.0)
                await update.message.reply_text(hype_messages[idx])
                await asyncio.sleep(1.5)

        except Exception as e:
            logger.error(f"Error sending fighter {fighter.name}: {e}", exc_info=True)
            await update.message.reply_text(
                f"Помилка при відправці бійця {fighter.name}. Спробуй ще раз!"
            )

    await update.message.reply_text(
        "🏆💀 ОСЬ ВОНИ — 6 ЛЕГЕНД! 💀🏆\n\n"
        "Всі на місці! Півні готові!\n"
        "Trash Beach Party може починатися! 🏖️🔥"
    )


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command.

    Shows fighter announcements sequence. Blocked after all draws are complete.
    """
    if not update.message or not update.effective_chat:
        return

    chat_id = update.effective_chat.id
    state = get_game_state(chat_id)

    # Block command if draw is complete
    if state.is_draw_complete():
        await update.message.reply_text(
            "🔒 Команди заблоковано! Всі бої оголошено.\n\n"
            "Напиши мені що завгодно - я Dana CockFight, готовий обговорити бої! 🎤"
        )
        return

    try:
        await _show_fighters_sequence(update, context)
        logger.info(
            f"User {update.effective_user.id if update.effective_user else 'unknown'} "
            "started the bot"
        )
    except Exception as e:
        logger.error(f"Error in start_command: {e}", exc_info=True)
        if update.message:
            await update.message.reply_text(
                "Виникла помилка при показі бійців. Спробуй ще раз!"
            )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command.

    Sends help text with all commands and workflow description.
    """
    if update.message:
        await update.message.reply_text(HELP_TEXT)


async def fighters_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /fighters command.

    Displays all 6 pre-loaded fighters with their presentation images.
    """
    if not update.message or not update.effective_chat:
        return

    try:
        await _show_fighters_sequence(update, context)

    except Exception as e:
        logger.error(f"Error in fighters_command: {e}", exc_info=True)
        if update.message:
            await update.message.reply_text(
                "Виникла помилка при показі бійців. Спробуй ще раз!"
            )


async def draw_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /draw command.

    Shows the next fight from fixed pairings with full dialogue sequence:
    1. VS Image with fight announcement
    2. Dana CockFight comment
    3. Dana asks Fighter 1
    4. Fighter 1 trash-talk
    5. Dana reaction, passes to Fighter 2
    6. Fighter 2 trash-talk
    7. Dana conclusion

    Each call shows one fight. After all 3 fights, shows completion message.
    """
    if not update.message or not update.effective_chat:
        return

    try:
        chat_id = update.effective_chat.id
        state = get_game_state(chat_id)

        # Check if all fights have been shown - commands are blocked
        if state.is_draw_complete():
            await update.message.reply_text(
                "🔒 Команди заблоковано! Всі бої оголошено.\n\n"
                "Напиши мені що завгодно - я Dana CockFight, готовий обговорити бої! 🎤"
            )
            return

        # Get current fight
        fight_number = state.get_current_fight_number()
        current_pair = state.get_current_fight()

        if not current_pair:
            await update.message.reply_text(
                "Помилка: не вдалося отримати поточну пару. "
                "Спробуй ще раз!"
            )
            return

        fighter1, fighter2 = current_pair

        # Load pre-generated content
        vs_image, dialogue = load_fight_data(fight_number)

        if not dialogue:
            await update.message.reply_text(
                f"Помилка: контент для бою {fight_number} не знайдено.\n"
                "Спочатку запустіть скрипт генерації:\n"
                "`uv run python scripts/generate_draw_content.py`",
                parse_mode="Markdown",
            )
            return

        messages = dialogue["messages"]

        logger.info(
            f"Starting fight {fight_number} announcement: "
            f"{fighter1.display_name} vs {fighter2.display_name}"
        )

        # MESSAGE 1: VS Image with fight title
        fight_title = (
            f"🔥 БІЙ #{fight_number} 🔥\n\n"
            f"⚔️ {fighter1.display_name} VS {fighter2.display_name} ⚔️"
        )

        if vs_image:
            await update.message.reply_photo(
                photo=vs_image,
                caption=fight_title,
            )
        else:
            await update.message.reply_text(fight_title)

        await asyncio.sleep(1.5)

        # MESSAGE 2: Dana's comment about the match
        dana_comment = f"🎤 *Dana CockFight:*\n\n{messages['dana_comment']}"
        await update.message.reply_text(dana_comment, parse_mode="Markdown")
        await asyncio.sleep(1.5)

        # MESSAGE 3: Dana asks Fighter 1
        dana_question = f"🎤 *Dana CockFight:*\n\n{messages['dana_question']}"
        await update.message.reply_text(dana_question, parse_mode="Markdown")
        await asyncio.sleep(1.0)

        # MESSAGE 4: Fighter 1 trash-talk
        fighter1_msg = f"🐓 *{fighter1.display_name}:*\n\n{messages['fighter1_trashtalk']}"
        await update.message.reply_text(fighter1_msg, parse_mode="Markdown")
        await asyncio.sleep(2.0)

        # MESSAGE 5: Dana reaction, passes to Fighter 2
        dana_reaction = f"🎤 *Dana CockFight:*\n\n{messages['dana_reaction']}"
        await update.message.reply_text(dana_reaction, parse_mode="Markdown")
        await asyncio.sleep(1.0)

        # MESSAGE 6: Fighter 2 trash-talk
        fighter2_msg = f"🐓 *{fighter2.display_name}:*\n\n{messages['fighter2_trashtalk']}"
        await update.message.reply_text(fighter2_msg, parse_mode="Markdown")
        await asyncio.sleep(2.0)

        # MESSAGE 7: Dana conclusion
        dana_conclusion = f"🎤 *Dana CockFight:*\n\n{messages['dana_conclusion']}"
        await update.message.reply_text(dana_conclusion, parse_mode="Markdown")

        await asyncio.sleep(1.0)

        # MESSAGE 8: Voting poll
        keyboard = [
            [
                InlineKeyboardButton(
                    f"🗳️ {fighter1.display_name}",
                    callback_data=f"vote_{fight_number}_{fighter1.name}",
                ),
                InlineKeyboardButton(
                    f"🗳️ {fighter2.display_name}",
                    callback_data=f"vote_{fight_number}_{fighter2.name}",
                ),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"📊 Хто переможе у БОЇ #{fight_number}? Голосуйте!",
            reply_markup=reply_markup,
        )

        # Advance to next fight
        has_more = state.advance_fight()

        # Final message
        await asyncio.sleep(1.0)
        if has_more:
            remaining = 3 - fight_number
            await update.message.reply_text(
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"✅ Бій #{fight_number} оголошено!\n"
                f"📢 Залишилось боїв: {remaining}"
            )
        else:
            await update.message.reply_text(
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "🏆 ВСІ БОЇ ОГОЛОШЕНО! 🏆\n\n"
                "Жеребкування завершено!\n"
                "Півні готові до битви! 🐓⚔️🐓"
            )

        logger.info(
            f"Fight {fight_number} announced for chat {chat_id}: "
            f"{fighter1.display_name} vs {fighter2.display_name}. "
            f"More fights: {has_more}"
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


async def vote_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle voting button clicks.

    Updates vote count and shows percentage results.
    Each user can only vote once per fight.
    """
    query = update.callback_query
    if not query or not update.effective_chat or not update.effective_user:
        return

    await query.answer()

    # Parse callback data: vote_{fight_number}_{fighter_name}
    try:
        parts = query.data.split("_", 2)
        if len(parts) != 3 or parts[0] != "vote":
            return
        fight_number = int(parts[1])
        voted_fighter = parts[2]
    except (ValueError, IndexError):
        logger.error(f"Invalid vote callback data: {query.data}")
        return

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    # Initialize vote storage if needed
    if chat_id not in _votes:
        _votes[chat_id] = {}
    if fight_number not in _votes[chat_id]:
        _votes[chat_id][fight_number] = {"votes": {}, "voters": set()}

    fight_votes = _votes[chat_id][fight_number]

    # Check if user already voted
    if user_id in fight_votes["voters"]:
        await query.answer("Ви вже голосували!", show_alert=True)
        return

    # Record vote
    fight_votes["voters"].add(user_id)
    fight_votes["votes"][voted_fighter] = fight_votes["votes"].get(voted_fighter, 0) + 1

    # Calculate percentages
    total = sum(fight_votes["votes"].values())

    # Get fighter display names
    state = get_game_state(chat_id)
    fighters_by_name = {f.name: f for f in state.fighters}

    result_text = f"📊 Результати голосування БІЙ #{fight_number}:\n\n"
    for fname, count in fight_votes["votes"].items():
        pct = count / total * 100
        fighter = fighters_by_name.get(fname)
        display_name = fighter.display_name if fighter else fname
        result_text += f"{display_name}: {pct:.0f}% ({count} голосів)\n"

    result_text += f"\n👥 Всього проголосувало: {total}"

    # Update message with vote results (keep voting buttons active)
    try:
        await query.edit_message_text(
            result_text,
            reply_markup=query.message.reply_markup,
        )
    except Exception as e:
        logger.error(f"Error updating vote message: {e}")

    logger.info(f"Vote recorded: {voted_fighter} in fight {fight_number} by user {user_id}")


async def dana_chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages when draw is complete - Dana CockFight promoter mode.

    Responds as Dana CockFight, discussing fights and fighters
    in a neutral, hype-building way.
    """
    if not update.message or not update.effective_chat:
        return

    chat_id = update.effective_chat.id
    state = get_game_state(chat_id)

    # Only respond if draw is complete
    if not state.is_draw_complete():
        return

    user_message = update.message.text
    if not user_message:
        return

    logger.info(f"Dana chat mode - received message: {user_message[:50]}...")

    # Generate Dana CockFight response using Gemini
    try:
        response = await asyncio.to_thread(
            generate_dana_chat_response,
            user_message=user_message,
            pairings=state.pairings,
        )

        await update.message.reply_text(
            f"🎤 *Dana CockFight:*\n\n{response}",
            parse_mode="Markdown",
        )
        logger.info("Dana chat response sent successfully")

    except Exception as e:
        logger.error(f"Error in dana_chat_handler: {e}", exc_info=True)
        await update.message.reply_text(
            "🎤 *Dana CockFight:*\n\n"
            "Хм, давай про бої! Всі три пари оголошені - які думки маєш?",
            parse_mode="Markdown",
        )


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

    # Add callback query handler for voting
    application.add_handler(CallbackQueryHandler(vote_callback, pattern=r"^vote_"))

    # Add message handler for Dana chat mode (must be after command handlers)
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, dana_chat_handler)
    )

    # Add error handler
    application.add_error_handler(error_handler)

    logger.info("Bot is ready! Starting polling...")

    # Run the bot until interrupted
    application.run_polling(allowed_updates=Update.ALL_TYPES)

    logger.info("Bot stopped.")


if __name__ == "__main__":
    main()
