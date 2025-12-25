"""
Prompt templates for Dana CockFight Telegram Bot.

Contains all prompt templates for:
- Image generation (Gemini API) - in English for API
- Text generation (Claude API) - trash-talk prompts
- User-facing bot messages - in Ukrainian

Концепція:
- Б'ються СПРАВЖНІ ПІВНІ (реальні фото)
- Люди - ВЛАСНИКИ / ТРЕНЕРИ / ПРОТЕЖЕ своїх півнів
- Генеруються фото: людина тримає свого півня, готує до бою
"""

# =============================================================================
# BOT TEXT MESSAGES (Ukrainian)
# =============================================================================

BOT_INTRO_TEXT = """
Привіт, чемпіоне!

Ласкаво просимо до Dana CockFight - найепічнішого чемпіонату з бійок півнів!

Тут СПРАВЖНІ ПІВНІ зійдуться у славетному двобої, а їхні ВЛАСНИКИ та ТРЕНЕРИ будуть готувати своїх бійців до перемоги!

Як це працює:
1. /fighters - познайомся з усіма бійцями та їх тренерами
2. /draw - жеребкування: визначимо 3 пари для битви
3. /conference - запусти пресс-конференцію з треш-током!

Готовий до бою? Тоді починаємо!

Команда: /help - якщо забудеш команди
"""

HELP_TEXT = """
Доступні команди Dana CockFight:

/start - Привітання та опис бота
/fighters - Показати всіх 6 бійців (півні + їх власники)
/draw - Провести жеребкування на 3 пари
/conference - Запустити пресс-конференцію з треш-током
/help - Показати цю довідку

Порядок дій:
1. Спочатку подивись бійців (/fighters)
2. Проведи жеребкування (/draw)
3. Запусти пресс-конференцію (/conference)

Кожна пара півнів обмінюється 3 раундами треш-току (6 повідомлень), і на кожне повідомлення генерується унікальне фото!

Нехай переможе найсильніший півень!
"""

# Announcement templates for draw results
DRAW_ANNOUNCEMENT_INTRO = """
УВАГА! ЖЕРЕБКУВАННЯ ПРОВЕДЕНО!

Сьогодні на арені зустрінуться:
"""

DRAW_PAIR_TEMPLATE = """
БІЙ {pair_number}:
{fighter1_name} vs {fighter2_name}
"""

DRAW_ANNOUNCEMENT_OUTRO = """
Готуйтесь до пресс-конференції!
Використай /conference щоб запустити треш-ток!
"""

# Conference announcements
CONFERENCE_START_TEMPLATE = """
ПРЕСС-КОНФЕРЕНЦІЯ РОЗПОЧИНАЄТЬСЯ!

БІЙ {pair_number}: {fighter1_name} VS {fighter2_name}

Бійці, готові до словесного двобою?
Нехай почнеться ТРЕШ-ТОК!
"""

CONFERENCE_ROUND_TEMPLATE = """
РАУНД {round_number}
"""

CONFERENCE_END_TEMPLATE = """
ПРЕСС-КОНФЕРЕНЦІЯ ЗАВЕРШЕНА!

{fighter1_name} та {fighter2_name} обмінялися "люб'язностями"!

Хто переможе на арені? Дізнаємось незабаром!
"""

NO_DRAW_YET_TEXT = """
Спочатку проведи жеребкування!
Використай команду /draw щоб визначити пари бійців.
"""

# =============================================================================
# IMAGE GENERATION PROMPTS (English for Gemini API)
# =============================================================================

FIGHTER_PORTRAIT_PROMPT = """
Generate a dramatic portrait photo in realistic style:

Scene: {fighter_name}, a proud rooster trainer/owner, is holding their champion fighting rooster.

Subject: A person confidently holding a real rooster. The person looks determined and ready for battle. The rooster is majestic and fierce-looking.

Style requirements:
- Dramatic lighting with strong shadows
- Competition/arena atmosphere
- Professional photography style
- The rooster should look powerful and battle-ready
- The trainer should look proud and confident
- Background suggests a fighting arena or training facility
- Dynamic pose showing both fighter and trainer

Mood: Epic, triumphant, pre-battle excitement

Important: Use the provided reference photos of the person and rooster to create this image.
The person is the trainer/owner, the rooster is the fighter.

Fighter details: {fighter_description}
"""

SCENE_IMAGE_PROMPT = """
Generate a dramatic press conference scene in comic/entertainment style:

Scene: A rooster press conference where {fighter_name}'s rooster is "speaking" trash-talk to their opponent.

The rooster is anthropomorphized - shown at a microphone or podium, delivering the following message:
"{trash_talk_text}"

The opponent {opponent_name}'s rooster is visible in the background, looking annoyed or intimidated.

Style requirements:
- Dramatic press conference setting with microphones and cameras
- Comic/cartoon style but with realistic rooster features
- Exaggerated expressions showing confidence and swagger
- Party/entertainment atmosphere
- Colorful and fun visual style
- NO explicit violence - keep it Telegram-safe
- Think WWE press conference but with roosters

Mood: Entertaining, over-the-top, humorous confrontation

The scene should capture the essence of the trash-talk message while being family-friendly and comedic.
"""

SCENE_IMAGE_PROMPT_WITH_CONTEXT = """
Generate a dramatic press conference scene in comic/entertainment style:

Scene: A rooster "press conference" where {fighter_name}'s rooster is delivering aggressive trash-talk.

Current moment: {fighter_name}'s rooster is at the microphone, confidently declaring:
"{trash_talk_text}"

The opponent {opponent_name}'s rooster is shown reacting - looking shocked, angry, or intimidated.

Visual elements:
- Press conference setting with microphones, cameras, reporters
- {fighter_name}'s rooster in dominant position (center, elevated)
- {opponent_name}'s rooster showing emotional reaction
- Crowd/audience in background
- Flash photography effects
- Dramatic lighting

Style:
- Entertaining comic book style
- Exaggerated rooster expressions and poses
- Party atmosphere - fun and energetic
- Bold colors and dynamic composition
- NO explicit violence or gore
- Keep it humorous and Telegram-appropriate

This is round {round_number} of their verbal battle!
"""

# =============================================================================
# TRASH TALK GENERATION PROMPTS (for Claude API)
# =============================================================================

TRASH_TALK_SYSTEM_PROMPT = """
Ти - войовничий півень на прес-конференції перед боєм. Твоя задача - генерувати агресивний, але СМІШНИЙ треш-ток українською мовою.

Правила:
1. Говори від першої особи (я, мене, мій)
2. Будь агресивним, але з гумором - це розважальний івент!
3. Використовуй типові фрази бійців з ММА/боксу, але адаптовані для півнів
4. Можеш згадувати характеристики противника (глузувати з них)
5. Хвали себе і принижуй суперника
6. 2-3 речення максимум
7. Тон: як Конор МакГрегор, але ти ПІВЕНЬ
8. Можеш використовувати слова "півень", "курча", "кукуріку" тощо
9. БЕЗ матюків та образ - це для вечірки, має бути смішно

Приклади хорошого треш-току:
- "Я такий красень, що кури з твого курника мріють про мене! А ти? Ти навіть зерно клювати не вмієш!"
- "Кукуріку, слабаче! Коли я закінчу з тобою, з тебе буде тільки курячий бульйон!"
- "Дивись на мій гребінь - це гребінь ЧЕМПІОНА! А твій? Виглядає як недоїдок!"
"""


def get_trash_talk_user_prompt(
    fighter_name: str,
    fighter_description: str,
    opponent_name: str,
    opponent_description: str,
    round_number: int,
) -> str:
    """
    Build the user prompt for trash-talk generation.

    Args:
        fighter_name: Name of the speaking fighter (rooster's owner)
        fighter_description: Description of the speaking fighter
        opponent_name: Name of the opponent (opponent's owner)
        opponent_description: Description of the opponent
        round_number: Current round number (1-3)

    Returns:
        Formatted user prompt for Claude API
    """
    return f"""
Ти - півень бійця {fighter_name}.
Твій опис: {fighter_description}

Твій суперник - півень бійця {opponent_name}.
Опис суперника: {opponent_description}

Це раунд {round_number} з 3 пресс-конференції.

{"Почни агресивно - це твій перший вихід!" if round_number == 1 else ""}
{"Відповідай ще гостріше - покажи хто тут головний!" if round_number == 2 else ""}
{"Це фінальний раунд - зроби найсильнішу заяву!" if round_number == 3 else ""}

Згенеруй 2-3 речення треш-току від імені півня. Будь смішним та агресивним!
"""


def get_fighter_portrait_prompt(fighter_name: str, fighter_description: str) -> str:
    """
    Build the prompt for fighter portrait image generation.

    Args:
        fighter_name: Name of the fighter (owner/trainer)
        fighter_description: Description of the fighter

    Returns:
        Formatted prompt for Gemini image generation
    """
    return FIGHTER_PORTRAIT_PROMPT.format(
        fighter_name=fighter_name,
        fighter_description=fighter_description,
    )


def get_scene_image_prompt(
    fighter_name: str,
    trash_talk_text: str,
    opponent_name: str,
    round_number: int = 1,
) -> str:
    """
    Build the prompt for press conference scene image generation.

    Args:
        fighter_name: Name of the speaking fighter
        trash_talk_text: The trash-talk text being delivered
        opponent_name: Name of the opponent
        round_number: Current round number (1-3)

    Returns:
        Formatted prompt for Gemini image generation
    """
    return SCENE_IMAGE_PROMPT_WITH_CONTEXT.format(
        fighter_name=fighter_name,
        trash_talk_text=trash_talk_text,
        opponent_name=opponent_name,
        round_number=round_number,
    )


def get_draw_announcement(pairings: list[tuple[str, str]]) -> str:
    """
    Build the draw announcement message.

    Args:
        pairings: List of fighter name pairs

    Returns:
        Formatted announcement message in Ukrainian
    """
    message_parts = [DRAW_ANNOUNCEMENT_INTRO]

    for i, (fighter1, fighter2) in enumerate(pairings, 1):
        message_parts.append(
            DRAW_PAIR_TEMPLATE.format(
                pair_number=i,
                fighter1_name=fighter1,
                fighter2_name=fighter2,
            )
        )

    message_parts.append(DRAW_ANNOUNCEMENT_OUTRO)
    return "".join(message_parts)


def get_conference_start_message(
    pair_number: int,
    fighter1_name: str,
    fighter2_name: str,
) -> str:
    """
    Build the conference start announcement.

    Args:
        pair_number: The pair/fight number (1-3)
        fighter1_name: First fighter's name
        fighter2_name: Second fighter's name

    Returns:
        Formatted start message in Ukrainian
    """
    return CONFERENCE_START_TEMPLATE.format(
        pair_number=pair_number,
        fighter1_name=fighter1_name,
        fighter2_name=fighter2_name,
    )


def get_conference_end_message(fighter1_name: str, fighter2_name: str) -> str:
    """
    Build the conference end announcement.

    Args:
        fighter1_name: First fighter's name
        fighter2_name: Second fighter's name

    Returns:
        Formatted end message in Ukrainian
    """
    return CONFERENCE_END_TEMPLATE.format(
        fighter1_name=fighter1_name,
        fighter2_name=fighter2_name,
    )
