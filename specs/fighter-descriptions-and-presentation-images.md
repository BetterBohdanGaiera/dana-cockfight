# Plan: Описи бійців та генерація презентаційних фото

## Task Description
Оновити описи бійців на основі task.md та згенерувати фото презентації півня перед битвою.
**Тон: ТРЕШ-ВЕЧІРКА НА ЗАТОНІ З ТРЕШ КОСТЮМАМИ!**

## Objective
1. Оновити описи бійців з task.md (українською, трешовий стиль)
2. Згенерувати AI-фото для кожного бійця у стилі "презентація півня на трешовій вечірці"
3. Зберегти згенеровані фото для використання в боті

## Problem Statement
Поточні описи бійців generic англійською (наприклад "Bohdan the Thunderer -- invincible warrior"). Потрібно оновити на справжні описи з task.md українською. Також при показі бійців показуються лише статичні фото, а потрібно генерувати AI-фото презентації.

## Solution Approach
1. Оновити `state_manager.py` з новими описами бійців з task.md
2. Модифікувати команду `/fighters` в `bot.py` щоб генерувати презентаційне фото через Gemini API
3. Оновити prompt в `prompts.py` для генерації фото "людина презентує півня перед битвою"

## Relevant Files
- `src/state_manager.py` - описи бійців у словнику `descriptions`
- `src/bot.py` - команда `fighters_command()` яка показує бійців
- `src/prompts.py` - prompt для генерації портрету бійця `FIGHTER_PORTRAIT_PROMPT`
- `src/image_generator.py` - функція `generate_fighter_portrait()` для генерації фото

### Дані бійців з task.md:
| Код | Ім'я | Опис |
|-----|------|------|
| petro | Петя | Спокійний і розсудливий. Але як треба - легко дасть пізди. Найстарший пєтух. |
| oleg | Олег | Найвищий петух. Найголосніший пєтух. Найрозумніший пєтух. Прилетів зі штатів - давно не бачив ципочок. Тому найагресивніший… та чи цього вистачить? |
| vadym | Вадим | Найбагатший пєтух. Приводить лідів і варить кращі чаї. |
| andrew_3 | Три Андрія | Погану людину Андрієм не назвеш… в гарного пєтуха - назвеш. |
| roma | Рома | Найгармонійніший спів. Від треків і зводів його кукарікання ти прокидаєшся із задоволенням. |
| bohdan | Богдан | Ну і куди ж без винуватця цього свята. Кажуть, що змагання підкуплене. Адже у цього півня є зв'язки з організаторами. Але це не точно. |

## Implementation Phases

### Phase 1: Оновлення описів бійців
Замінити generic описи англійською на справжні описи з task.md українською.

### Phase 2: Оновлення prompt для презентації
Оновити `FIGHTER_PORTRAIT_PROMPT` щоб генерувати фото людини, яка ПРЕЗЕНТУЄ свого півня перед битвою (драматична поза, тримає півня над головою, готує до бою).

### Phase 3: Інтеграція генерації фото в /fighters
Модифікувати `fighters_command()` щоб генерувати AI-фото замість показу статичного зображення.

## Step by Step Tasks

### 1. Оновити описи бійців у state_manager.py
- Відкрити `src/state_manager.py`
- Замінити словник `descriptions` на нові описи з task.md
- Зберегти українські імена (Петя, Олег, Вадим, Три Андрія, Рома, Богдан)

```python
descriptions: dict[str, str] = {
    "andrew_3": "Три Андрія — Погану людину Андрієм не назвеш… в гарного пєтуха - назвеш.",
    "bohdan": "Богдан — Ну і куди ж без винуватця цього свята. Кажуть, що змагання підкуплене. Адже у цього півня є зв'язки з організаторами. Але це не точно.",
    "oleg": "Олег — Найвищий петух. Найголосніший пєтух. Найрозумніший пєтух. Прилетів зі штатів - давно не бачив ципочок. Тому найагресивніший… та чи цього вистачить?",
    "petro": "Петя — Спокійний і розсудливий. Але як треба - легко дасть пізди. Найстарший пєтух.",
    "roma": "Рома — Найгармонійніший спів. Від треків і зводів його кукарікання ти прокидаєшся із задоволенням.",
    "vadym": "Вадим — Найбагатший пєтух. Приводить лідів і варить кращі чаї.",
}
```

### 2. Оновити prompt для презентації півня в prompts.py
- Модифікувати `FIGHTER_PORTRAIT_PROMPT` для створення фото "презентація півня перед битвою"
- Prompt має описувати: людина тримає півня, готує до бою, драматична поза

```python
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
```

### 3. Модифікувати fighters_command() в bot.py
- Імпортувати `generate_fighter_portrait_safe` якщо ще не імпортовано
- Замінити показ статичного фото на генерацію AI-фото
- Додати fallback на статичне фото якщо генерація не вдалась

```python
async def fighters_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # ... existing code ...

    for fighter in state.fighters:
        # Generate presentation image via Gemini
        generated_image = await asyncio.to_thread(
            generate_fighter_portrait_safe,
            fighter.rooster_image_path,
            fighter.human_image_path,
            fighter.name,
            fighter.description,
        )

        if generated_image:
            # Send generated AI photo
            await update.message.reply_photo(
                photo=generated_image,
                caption=caption,
                parse_mode="Markdown",
            )
        else:
            # Fallback to static rooster photo
            with open(rooster_path, "rb") as f:
                image_bytes = f.read()
            await update.message.reply_photo(
                photo=image_bytes,
                caption=caption,
                parse_mode="Markdown",
            )
```

### 4. Додати імпорт в bot.py
- Імпортувати `generate_fighter_portrait_safe` з `image_generator`

### 5. Тестування
- Запустити бота: `uv run python -m src.bot`
- Виконати команду /fighters
- Перевірити що описи українською
- Перевірити що генеруються AI-фото презентацій

## Testing Strategy
1. Unit test: перевірити що описи коректно завантажуються з state_manager
2. Manual test: запустити бота і виконати /fighters
3. Verify: кожен боєць має опис українською з task.md
4. Verify: для кожного бійця генерується AI-фото (або fallback на статичне)

## Acceptance Criteria
- [ ] Описи бійців українською з task.md (не generic англійською)
- [ ] При /fighters генерується AI-фото презентації для кожного бійця
- [ ] Фото показує людину, яка презентує півня перед битвою
- [ ] Fallback на статичне фото якщо AI-генерація не працює
- [ ] Бот працює без помилок

## Validation Commands
- `uv run python -c "from src.state_manager import load_fighters; fighters = load_fighters(); print([f.description for f in fighters])"` - перевірити описи
- `uv run python -m src.bot` - запустити бота для тестування

## Notes
- Gemini API може відхилити деякі запити на генерацію зображень - тому важливий fallback
- Генерація займає час (~5-15 сек на фото) - користувач має бачити прогрес
- Можливо варто додати повідомлення "Генерую фото..." перед кожним бійцем
