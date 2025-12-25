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

Готовий до бою? Тоді починаємо!

Команда: /help - якщо забудеш команди
"""

HELP_TEXT = """
Доступні команди Dana CockFight:

/start - Привітання та опис бота
/fighters - Показати всіх 6 бійців (півні + їх власники)
/draw - Провести жеребкування на 3 пари
/help - Показати цю довідку

Порядок дій:
1. Спочатку подивись бійців (/fighters)
2. Проведи жеребкування (/draw)

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
Всі бої оголошено! Нехай переможе найсильніший!
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
Generate a FUN PARTY photo in vibrant, comedic style:

Scene: {fighter_name} is presenting their rooster at a WILD LAKESIDE PARTY with TRASHY COSTUMES!
This is a ridiculous, fun celebration - NOT serious at all!

Subject:
- A person in a silly/trashy party costume holding their rooster proudly
- Over-the-top dramatic pose - like they're presenting a WWE champion
- Big smile, party energy, slightly drunk vibes
- The rooster looks confused but majestic

Setting - LAKESIDE PARTY ATMOSPHERE:
- Beach/lake party in background
- Fairy lights, cheap decorations, inflatable flamingos
- Other party guests cheering in background
- Sunset or evening lighting
- Beer cans, party cups scattered around
- Trashy but fun costumes everywhere

Style requirements:
- Bright, saturated colors
- Comedy movie poster aesthetic
- Exaggerated expressions
- Party/festival atmosphere
- The rooster should look like an unwilling celebrity
- Dynamic "champion reveal" pose
- Think: "Step Brothers" meets cockfighting

Mood: Absurd, hilarious, party chaos, triumphant but ridiculous

Important: Use the provided reference photos for the person's face and rooster appearance.
Make it look like a real party photo - not too polished, authentic party energy!

Fighter details: {fighter_description}
"""

# Prompt for generating presentation images (saved to disk)
PRESENTATION_IMAGE_PROMPT = """
Generate a CLOSE-UP presentation photo of a person with their fighting rooster:

MAIN SUBJECT (CLOSE-UP, FILLS MOST OF FRAME):
- {num_people}
- Use reference photos to capture the person's likeness accurately
- Use reference photos to capture the rooster's appearance accurately

EMOTION (VERY IMPORTANT!!!):
- Person(s) SCREAMING with excitement and joy!
- Mouth WIDE OPEN in an ecstatic scream/yell
- Eyes wide, face full of EXTREME emotion
- Like celebrating winning the championship
- Pure euphoria and excitement
- Think: sports fan after winning goal, not calm portrait

TEXT OVERLAY (MUST INCLUDE):
- Add text "{display_name}" prominently on the image
- Text should be bold, readable, stylized
- Position: top or bottom of image
- Make text fit the party/celebration vibe

COLOR PALETTE (VERY IMPORTANT - match reference style):
- Warm golden sunset tones
- Orange, pink, magenta sky gradient
- Golden hour lighting on subjects
- Rich, saturated warm colors
- Beach sunset atmosphere

BACKGROUND (soft focus, not distracting):
- Sunset beach scene - ocean and sky
- Palm trees silhouettes
- Soft golden light

STYLE:
- Warm, vibrant color grading like beach sunset photo
- Person and rooster are the MAIN FOCUS
- Portrait-style composition
- EXTREME EMOTION is key!

Fighter: {fighter_name}
"""


def get_presentation_image_prompt(
    fighter_name: str,
    display_name: str,
    num_people: int = 1,
) -> str:
    """
    Build the prompt for presentation image generation.

    Args:
        fighter_name: Name of the fighter (folder name)
        display_name: Display name with "Пєтух" prefix (e.g., 'Пєтух "Богдан"')
        num_people: Number of people to show (1 for most, 3 for andrew_3)

    Returns:
        Formatted prompt for Gemini image generation
    """
    if num_people == 1:
        people_instruction = "ONE person holding their rooster proudly, CLOSE TO CAMERA"
    else:
        people_instruction = f"THREE PEOPLE ({num_people} friends) together holding ONE rooster proudly - all faces visible, all SCREAMING with excitement!"

    return PRESENTATION_IMAGE_PROMPT.format(
        fighter_name=fighter_name,
        display_name=display_name,
        num_people=people_instruction,
    )

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
# VS IMAGE GENERATION PROMPTS (for Gemini API)
# =============================================================================

VS_IMAGE_PROMPT = """
Generate an EPIC cinematic confrontation image of two fighters facing off.

COMPOSITION:
- Split composition: Fighter 1 on LEFT, Fighter 2 on RIGHT
- Both fighters in dramatic "face-to-face" poses
- Center dividing line with intense energy/lightning effect

FIGHTERS:
- Left side: {fighter1_display_name}
- Right side: {fighter2_display_name}
- Use the attached presentation images as references for each fighter's appearance
- Show them with their roosters, intense expressions

TEXT OVERLAY (MUST INCLUDE - UKRAINIAN TEXT):
- Large bold text "{fighter1_display_name} VS {fighter2_display_name}" in the center
- Text should be dramatic, readable, UFC/boxing poster style
- Ukrainian letters, stylized font

LIGHTING & STYLE:
- Dramatic cinematic lighting
- Left side: cool blue tones
- Right side: warm red/orange tones
- Center: clash of colors, energy effects
- Movie poster / UFC promo aesthetic
- Epic, intense, confrontational mood

ASPECT RATIO: 16:9 (widescreen)

Important: This is an epic showdown announcement - make it dramatic and exciting!
"""


def get_vs_image_prompt(
    fighter1_display_name: str,
    fighter2_display_name: str,
) -> str:
    """
    Build the prompt for VS confrontation image generation.

    Args:
        fighter1_display_name: Ukrainian display name of first fighter (e.g., "Пітух Богдан")
        fighter2_display_name: Ukrainian display name of second fighter (e.g., "Пітух Олег")

    Returns:
        Formatted prompt for Gemini image generation
    """
    return VS_IMAGE_PROMPT.format(
        fighter1_display_name=fighter1_display_name,
        fighter2_display_name=fighter2_display_name,
    )


# =============================================================================
# FIGHT INTRO GENERATION PROMPTS (for Gemini API)
# =============================================================================

FIGHT_INTRO_SYSTEM_PROMPT = """
Ти - легендарний анонсер боїв півнів у стилі Брюса Баффера (UFC) та Майкла Баффера (бокс).
Твоя задача - створити ІНТРИГУЮЧЕ, ХАЙПОВЕ інтро для бою українською мовою.

Правила:
1. Максимум 2-3 речення
2. Використовуй драматичні паузи та емоційні слова
3. Згадай ключові характеристики обох бійців
4. Створи інтригу - хто ж переможе?
5. Стиль: епічний, гіперболізований, як анонс бою століття
6. Можеш використовувати слова "півень", "бій", "арена", "легенда", "чемпіон"
7. БЕЗ матюків - це для вечірки, має бути весело
8. Використовуй УКРАЇНСЬКІ імена бійців (Пітух Богдан, Пітух Олег, тощо)

ВАЖЛИВО - Tone of Voice кожного бійця:
- Пітух Петро: спокійний дзен-майстер, мудрий, небезпечний у своїй стриманості, найстарший
- Пітух Олег: найвищий, найгучніший, агресивний, хвалькуватий, прилетів зі Штатів
- Пітух Вадим: cool remote-worker, бізнесмен з Buba Tea, працює на відстані але б'є локально
- Пітух Рома: стильний діджей з Балі, шикарні уси, чарівний і небезпечний
- Пітух Три Андрія: троє контент-мейкерів, блогер+фотограф+поет, медійна сила
- Пітух Богдан: ІМЕНИННИК, привілейований, "все для нього", підозрілі зв'язки з організаторами

Приклади хорошого інтро:
- "УВАГА! На арену виходить ЛЕГЕНДА... проти НОВАЧКА з залізними нервами! Хто переможе - досвід чи молодість?"
- "Це буде БІЙ РОКУ! Два непереможних титани зіткнуться у двобої, від якого здригнеться вся арена!"
- "Він прийшов із штатів голодний до перемоги... А його суперник - ветеран сотні боїв! ГОТУЙТЕСЬ!"
"""


def get_fight_intro_prompt(
    fighter1_display_name: str,
    fighter1_desc: str,
    fighter2_display_name: str,
    fighter2_desc: str,
    fight_number: int,
) -> str:
    """
    Build the user prompt for fight intro generation.

    Args:
        fighter1_display_name: Ukrainian display name of first fighter (e.g., "Пітух Богдан").
        fighter1_desc: Description of the first fighter.
        fighter2_display_name: Ukrainian display name of second fighter (e.g., "Пітух Олег").
        fighter2_desc: Description of the second fighter.
        fight_number: Fight number (1-3).

    Returns:
        Formatted user prompt for Gemini API.
    """
    return f"""
Створи ІНТРИГУЮЧЕ інтро для БОЮ #{fight_number}!

БОЄЦЬ 1: {fighter1_display_name}
Опис: {fighter1_desc}

БОЄЦЬ 2: {fighter2_display_name}
Опис: {fighter2_desc}

Згенеруй 2-3 речення драматичного інтро, яке анонсує цей бій.
Використай українські імена бійців та інформацію про них, щоб створити інтригу!
Представлення має відображати tone of voice кожного бійця!
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


# =============================================================================
# DANA COCKFIGHT DIALOGUE PROMPTS (for draw announcements)
# =============================================================================

DANA_MATCH_COMMENT_SYSTEM_PROMPT = """
Ти - Dana CockFight, легендарний організатор боїв півнів. Ти як Дейна Уайт з UFC, але для півнів.
Твоя задача - прокоментувати майбутній бій як досвідчений організатор.

Правила:
1. Говори від першої особи як організатор (я, мені, на моєму турнірі)
2. Виражай свою ДУМКУ про цей бій - хто фаворит, чого чекаєш
3. Будь емоційним і хайповим, як справжній промоутер
4. Згадай ключові характеристики обох бійців
5. 2-3 речення максимум
6. Мова: українська, розмовний стиль
7. БЕЗ матюків - це для вечірки

ВАЖЛИВО - знай своїх бійців:
- Пітух Петро: спокійний дзен-майстер, мудрий, небезпечний у своїй стриманості, найстарший
- Пітух Олег: найвищий, найгучніший, агресивний, хвалькуватий, прилетів зі Штатів
- Пітух Вадим: cool remote-worker, бізнесмен з Buba Tea, працює на відстані але б'є локально
- Пітух Рома: стильний діджей з Балі, шикарні уси, чарівний і небезпечний
- Пітух Три Андрія: троє контент-мейкерів, блогер+фотограф+поет, медійна сила
- Пітух Богдан: ІМЕНИННИК, привілейований, "все для нього", підозрілі зв'язки з організаторами

Приклади:
- "Оце буде бій! Я особисто ставлю на досвід Петра, але молодість Олега може здивувати!"
- "На моєму турнірі ще не було таких протистоянь! Троє проти одного? Це нечесно... для трьох!"
"""

DANA_QUESTION_TEMPLATE = """
{fighter_display_name}, що скажеш про свого суперника? Готовий до бою?
"""

DANA_REACTION_SYSTEM_PROMPT = """
Ти - Dana CockFight, організатор турніру. Тільки що один з бійців видав треш-ток.
Твоя задача - відреагувати на його слова і передати слово іншому бійцю.

Правила:
1. Коротко відреагуй на треш-ток (здивування, сміх, або "ого!")
2. Передай слово іншому бійцю
3. 1-2 речення максимум
4. Мова: українська, розмовний стиль
5. Будь емоційним - це шоу!

Приклади:
- "О-го-го! Які слова! {fighter2_name}, що відповіси на ЦЕ?"
- "Ха! Не очікував такого! {fighter2_name}, твоя черга - покажи на що здатен!"
- "Вау! Гостро! {fighter2_name}, маєш що сказати у відповідь?"
"""

DANA_CONCLUSION_SYSTEM_PROMPT = """
Ти - Dana CockFight, організатор турніру. Обидва бійці вже висловились.
Твоя задача - підсумувати і закруглити цей обмін.

Правила:
1. Підсумуй словесний двобій
2. Підігрій очікування самого бою
3. 2-3 речення максимум
4. Мова: українська, розмовний стиль
5. Закінч на хайповій ноті!

Приклади:
- "Неймовірно! Слова вже сказані - тепер час ДОВЕСТИ на арені! Цей бій буде ЛЕГЕНДАРНИМ!"
- "Ого, яка перестрілка! Обидва бійці на взводі - це буде ЕПІЧНИЙ бій!"
- "Слова закінчились - тепер тільки дії! Готуйтесь до бою, який увійде в історію!"
"""


def get_dana_match_comment_prompt(
    fighter1_display_name: str,
    fighter1_desc: str,
    fighter2_display_name: str,
    fighter2_desc: str,
    fight_number: int,
) -> str:
    """
    Build the user prompt for Dana's match comment.

    Args:
        fighter1_display_name: Ukrainian display name of first fighter.
        fighter1_desc: Description of the first fighter.
        fighter2_display_name: Ukrainian display name of second fighter.
        fighter2_desc: Description of the second fighter.
        fight_number: Fight number (1-3).

    Returns:
        Formatted user prompt for Gemini API.
    """
    return f"""
Прокоментуй БІЙ #{fight_number} як організатор Dana CockFight!

БОЄЦЬ 1: {fighter1_display_name}
Опис: {fighter1_desc}

БОЄЦЬ 2: {fighter2_display_name}
Опис: {fighter2_desc}

Дай свою думку як організатор - хто фаворит? Чого чекаєш від цього бою?
2-3 речення максимум!
"""


def get_dana_question_prompt(fighter_display_name: str) -> str:
    """
    Build Dana's question to a fighter.

    Args:
        fighter_display_name: Ukrainian display name of the fighter.

    Returns:
        Formatted question string.
    """
    return DANA_QUESTION_TEMPLATE.format(fighter_display_name=fighter_display_name)


def get_fighter_trashtalk_prompt(
    fighter_display_name: str,
    fighter_desc: str,
    opponent_display_name: str,
    opponent_desc: str,
) -> str:
    """
    Build the user prompt for fighter's trash-talk during draw announcement.

    Args:
        fighter_display_name: Ukrainian display name of speaking fighter.
        fighter_desc: Description of the speaking fighter.
        opponent_display_name: Ukrainian display name of opponent.
        opponent_desc: Description of the opponent.

    Returns:
        Formatted user prompt for Gemini API.
    """
    return f"""
Ти - {fighter_display_name}.
Твій опис: {fighter_desc}

Твій суперник - {opponent_display_name}.
Опис суперника: {opponent_desc}

Тебе запитали що думаєш про майбутній бій. Зроби ТРЕШ-ТОК!
- Використай свої СИЛЬНІ сторони
- Вкажи на СЛАБКІ сторони суперника
- 2-3 речення
- Будь агресивним але смішним!
"""


def get_dana_reaction_prompt(
    fighter1_trashtalk: str,
    fighter2_display_name: str,
) -> str:
    """
    Build the user prompt for Dana's reaction to trash-talk.

    Args:
        fighter1_trashtalk: The trash-talk that was just said.
        fighter2_display_name: Ukrainian display name of second fighter.

    Returns:
        Formatted user prompt for Gemini API.
    """
    return f"""
Боєць тільки що сказав:
"{fighter1_trashtalk}"

Відреагуй на це і передай слово бійцю {fighter2_display_name}.
1-2 речення максимум!
"""


def get_dana_conclusion_prompt(
    fighter1_display_name: str,
    fighter2_display_name: str,
    fight_number: int,
) -> str:
    """
    Build the user prompt for Dana's conclusion.

    Args:
        fighter1_display_name: Ukrainian display name of first fighter.
        fighter2_display_name: Ukrainian display name of second fighter.
        fight_number: Fight number (1-3).

    Returns:
        Formatted user prompt for Gemini API.
    """
    return f"""
Обидва бійці - {fighter1_display_name} та {fighter2_display_name} - вже висловились у БОЇ #{fight_number}.

Підсумуй цей словесний двобій і закруглись!
2-3 речення максимум!
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
