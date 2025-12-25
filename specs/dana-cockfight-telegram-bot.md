# Plan: Dana CockFight Telegram Bot

## Task Description

Build a Telegram entertainment bot called "Dana CockFight" for a party event. The bot simulates a rooster fighting championship where **REAL roosters** compete, and their **human owners/trainers** prepare them for battle.

**Концепція:**
- Б'ються СПРАВЖНІ ПІВНІ (реальні фото)
- Люди - ВЛАСНИКИ / ТРЕНЕРИ / ПРОТЕЖЕ своїх півнів
- Генеруються фото: людина тримає свого півня, готує до бою

Key features:
- Bot self-introduction with custom image
- Fighter announcements with AI-generated images (owner holding their rooster)
- Random matchmaking for 3 pairs of roosters
- Pre-match "press conference" with AI-generated trash-talk and accompanying images
- Ukrainian language interface with party-appropriate tone

## Objective

Create a fully functional Telegram bot that:
1. Introduces itself with a themed image when started
2. Announces fighters on demand, generating unique person+rooster images for each
3. Randomly pairs 6 fighters into 3 match pairs and remembers the pairings
4. Runs interactive "press conferences" where paired roosters exchange 3 rounds of trash-talk (6 messages total per pair), with each message accompanied by a generated image depicting the scene

## Problem Statement

The user needs an entertainment bot for a party event that:
- Creates an engaging, interactive cockfight-themed experience
- Uses AI to generate both text (trash-talk) and images (fighter portraits, scene depictions)
- Maintains state across commands (remembers fighter pairings)
- Delivers content in Ukrainian with a fun, party-appropriate tone
- Integrates with Telegram's message and photo APIs

## Solution Approach

Build upon patterns from the TokopediaImageInspiration reference project while adding:
1. **Image Generation**: Use Google Gemini `gemini-3-pro-image-preview` API (Pure Python port of existing `generate-image.ts`)
2. **Text Generation**: Use Anthropic Claude for Ukrainian trash-talk generation
3. **Pre-generated Fighters**: Use 6 existing fighter images from `data/images/` directory
4. **State Management**: In-memory dictionary to store fighter data and pairings
5. **Modular Architecture**: Separate concerns into config, bot handlers, image generation, and text generation modules

The bot will follow the `python-telegram-bot` async patterns from the reference project but add image generation capabilities and conversation state.

## Design Decisions (Confirmed)

| Decision | Choice |
|----------|--------|
| Image Generation | **Gemini 3 Pro** - Pure Python using google-genai (port of generate-image.ts) |
| Fighters | **Pre-generated only** - use existing 6 fighters from data/images/ |
| Conference Images | **All 6 messages** - generate scene image for every trash-talk message |

## Relevant Files

Use these files as references:

### Existing Project Files
- `generate-image.ts` - **Reference for Python port** - Gemini image generation script (TypeScript)
- `.env` - Environment variables (GEMINI_API_KEY already configured)
- `data/images/` - **6 pre-generated fighter images**:
  - `data/images/andrew_3/image.png`
  - `data/images/bohdan/image.png`
  - `data/images/oleg/image.png`
  - `data/images/petro/image.png`
  - `data/images/roma/image.png`
  - `data/images/vadym/image.png`

### Reference Files (TokopediaImageInspiration)
- `/Users/bohdanpytaichuk/Documents/TokopediaImageInspiration/src/bot.py` - Bot architecture, command handlers, async patterns, message sending
- `/Users/bohdanpytaichuk/Documents/TokopediaImageInspiration/src/config.py` - Configuration pattern with dotenv, validation
- `/Users/bohdanpytaichuk/Documents/TokopediaImageInspiration/src/gemini_analyzer.py` - AI client singleton pattern, prompt engineering
- `/Users/bohdanpytaichuk/Documents/TokopediaImageInspiration/src/response_formatter.py` - Telegram message formatting, length handling
- `/Users/bohdanpytaichuk/Documents/TokopediaImageInspiration/pyproject.toml` - Project structure, dependencies

### New Files to Create
- `src/bot.py` - Main bot with command handlers (/start, /fighters, /draw, /conference)
- `src/config.py` - Configuration loading (TELEGRAM_BOT_TOKEN, GEMINI_API_KEY, ANTHROPIC_API_KEY)
- `src/image_generator.py` - **Gemini image generation** (Python port of generate-image.ts)
- `src/text_generator.py` - Claude-powered Ukrainian trash-talk generation
- `src/state_manager.py` - In-memory state for fighters and pairings (pre-load 6 fighters)
- `src/prompts.py` - Prompt templates for image and text generation
- `src/__init__.py` - Package initialization
- `pyproject.toml` - Project configuration and dependencies
- `.env.example` - Template for environment variables

## Implementation Phases

### Phase 1: Foundation
- Set up project structure with uv
- Create configuration module with API key validation
- Implement basic bot skeleton with /start command
- Test Telegram API connectivity

### Phase 2: Core Implementation
- Implement image generation module (Gemini - port from generate-image.ts)
- Implement text generation module (Claude)
- Create state manager with pre-loaded 6 fighters from data/images/
- Build /fighters command to display existing fighters
- Build /draw command for matchmaking
- Build /conference command for trash-talk exchanges (6 messages with scene images)

### Phase 3: Integration & Polish
- Add error handling and user feedback
- Implement message splitting for long responses
- Add logging throughout
- Test all command flows end-to-end
- Add /help command with usage instructions

## Step by Step Tasks

IMPORTANT: Execute every step in order, top to bottom.

### 1. Initialize Project Structure
- Create `src/` directory
- Create `pyproject.toml` with dependencies:
  - `python-telegram-bot>=21.0`
  - `google-genai>=1.0.0`
  - `anthropic>=0.20.0`
  - `python-dotenv>=1.0.0`
- Create `src/__init__.py` (empty)
- Create `.env.example` with required variables template

### 2. Implement Configuration Module
- Create `src/config.py`
- Load environment variables using dotenv
- Define constants: TELEGRAM_BOT_TOKEN, GEMINI_API_KEY, ANTHROPIC_API_KEY
- Implement `validate_config()` function that raises ValueError for missing keys
- Add MODEL constants for Gemini (`gemini-3-pro-image-preview`) and Anthropic (`claude-sonnet-4-20250514`)

### 3. Create Prompt Templates
- Create `src/prompts.py`
- Define FIGHTER_IMAGE_PROMPT template for generating person+rooster images
- Define SCENE_IMAGE_PROMPT template for press conference scene images
- Define TRASH_TALK_PROMPT template for Claude (Ukrainian, aggressive, humorous)
- Define BOT_INTRO_TEXT in Ukrainian with party theme

### 4. Implement Image Generator Module
- Create `src/image_generator.py`
- **Port logic from `generate-image.ts`** to Python using `google-genai` library
- Implement Gemini client singleton pattern
- Create `generate_fighter_portrait(rooster_image: bytes, human_image: bytes, prompt: str) -> bytes` function
  - Використовує РЕАЛЬНІ фото півня та людини як референс
  - Генерує: людина тримає свого півня, готує до бою
- Create `generate_scene_image(prompt: str, aspect_ratio: str = "16:9") -> bytes` function
  - Для сцен пресс-конференції та треш-току
- Use model `gemini-3-pro-image-preview` with `responseModalities: ["Image"]`
- Handle Gemini API responses and base64 image decoding
- Add error handling with fallback behavior

**Reference from generate-image.ts:**
```python
from google import genai

client = genai.Client(api_key=GEMINI_API_KEY)
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=[
        prompt,
        # Can include reference images as bytes
    ],
    config={
        "responseModalities": ["Text", "Image"],
        "imageConfig": {"aspectRatio": aspect_ratio}
    }
)
# Extract image: response.candidates[0].content.parts[i].inline_data.data (base64)
```

### 5. Implement Text Generator Module
- Create `src/text_generator.py`
- Implement Anthropic client singleton pattern
- Create `generate_trash_talk(fighter: dict, opponent: dict, round_number: int) -> str` function
- Use Claude to generate aggressive, humorous Ukrainian trash-talk
- Include context about both fighters in prompt
- Return text ready for Telegram message

### 6. Implement State Manager
- Create `src/state_manager.py`
- Define Fighter dataclass: `name`, `description`, `image_path`
- **Pre-load 6 fighters from `data/images/` at startup:**
  - andrew_3, bohdan, oleg, petro, roma, vadym
- Define GameState class with:
  - `fighters: list[Fighter]` - Pre-loaded 6 fighters
  - `pairings: list[tuple[Fighter, Fighter]]` - 3 pairs after draw
  - `current_conference: int` - Which pair is in conference (0-2)
  - `conference_round: int` - Current round of trash-talk (0-2)
- Implement `load_fighters()`, `draw_pairings()`, `get_current_pair()`, `advance_conference()` methods
- Store state per chat_id in global dict

### 7. Implement Bot Core with /start Command
- Create `src/bot.py`
- Set up logging (same pattern as reference)
- Implement `start_command()` handler:
  - Send intro text from prompts.py
  - Send intro image (from data/ directory or generate one)
- Create Application builder with token
- Add CommandHandler for /start
- Add error handler
- Implement main() with polling

### 8. Implement /fighters Command
- Add `fighters_command()` handler to bot.py
- **Display all 6 pre-generated fighters** (no dynamic addition)
- Load each fighter image from `data/images/{name}/image.png`
- Send all 6 images with fighter names/descriptions
- Optionally show one fighter at a time with pagination

### 9. Implement /draw Command
- Add `draw_command()` handler to bot.py
- Verify 6 fighters exist (or use default count)
- Call state_manager.draw_pairings() to randomly pair fighters
- Send message announcing all 3 pairings
- Store pairings in state for conference command

### 10. Implement /conference Command
- Add `conference_command()` handler to bot.py
- Get current pairing from state manager
- For each round (3 total, **6 messages with scene images**):
  - Generate trash-talk text for current fighter using text_generator
  - Generate scene image depicting the trash-talk using **Gemini image_generator**
  - Send photo with trash-talk as caption
  - Alternate between paired fighters
  - Add dramatic delay between messages (2-3 seconds)
- After 3 rounds, announce winner randomly or based on "audience" vote
- **Note:** All 6 messages get generated scene images (user confirmed)

### 11. Add /help Command
- Implement help_command() with usage instructions in Ukrainian
- List all available commands and their purpose
- Explain the flow: register fighters -> draw pairs -> run conferences

### 12. Add Error Handling and Logging
- Wrap all AI API calls in try-except blocks
- Implement fallback text for failed image generations
- Add logging.info/error throughout all handlers
- Implement graceful degradation (text-only mode if image fails)

### 13. Validate Implementation
- Run `uv run python -m py_compile src/*.py` to verify syntax
- Test /start command manually
- Test /fighters with sample fighter
- Test /draw with 6 fighters
- Test /conference for full trash-talk exchange
- Verify all images generate correctly

## Testing Strategy

### Unit Tests
- Test state_manager.py: fighter addition, pairing logic, round tracking
- Test prompts.py: verify prompt templates have required placeholders
- Test config.py: validation raises correct errors

### Integration Tests
- Test image_generator with mock Gemini responses
- Test text_generator with mock Anthropic responses
- Test full command flow with test Telegram bot

### Manual Testing
1. Start bot with /start - verify intro message and image
2. Run /fighters - verify all 6 pre-generated fighter images display
3. Run /draw - verify 3 pairs announced
4. Run /conference - verify 6 trash-talk messages with generated scene images
5. Test error scenarios: missing API keys, failed image generation

### Edge Cases
- Running /conference before /draw (should prompt to draw first)
- API rate limiting (add retry logic with backoff for Gemini)
- Gemini refusing to generate image (content policy - handle gracefully)

## Acceptance Criteria

- [ ] Bot responds to /start with introduction text and image
- [ ] /fighters command displays all 6 pre-generated fighter images
- [ ] State persists between commands (pairings remembered)
- [ ] /draw randomly pairs 6 fighters into 3 matches
- [ ] /conference generates 6 trash-talk messages (3 per fighter in pair)
- [ ] Each trash-talk message includes a **Gemini-generated scene image**
- [ ] All text is in Ukrainian with party-appropriate tone
- [ ] Bot handles errors gracefully with user-friendly messages
- [ ] Configuration validates required API keys on startup (GEMINI_API_KEY, TELEGRAM_BOT_TOKEN, ANTHROPIC_API_KEY)

## Validation Commands

Execute these commands to validate the task is complete:

- `uv run python -m py_compile src/*.py` - Verify all Python files compile without syntax errors
- `uv run python -c "from src.config import validate_config; validate_config()"` - Verify configuration loads correctly
- `uv run python -c "from src.image_generator import generate_fighter_image; print('Image generator OK')"` - Verify image generator imports
- `uv run python -c "from src.text_generator import generate_trash_talk; print('Text generator OK')"` - Verify text generator imports
- `uv run python -c "from src.state_manager import GameState; print('State manager OK')"` - Verify state manager imports
- `uv run python src/bot.py` - Start the bot for manual testing

## Notes

### Dependencies to Install
```bash
uv add python-telegram-bot google-genai anthropic python-dotenv
```

### Environment Variables Required
```
GEMINI_API_KEY=AIzaSy...  # Already configured in .env
TELEGRAM_BOT_TOKEN=8549606143:AAEYecRFxxoPnVaqDRvujHjvV0-9rUvf7xQ
ANTHROPIC_API_KEY=<your-anthropic-api-key>
```

### Key Design Decisions
1. **Gemini 3 Pro** for image generation - port from existing `generate-image.ts`
2. **Pre-generated fighters** - use 6 existing images from `data/images/` (no dynamic fighter creation)
3. **Claude** chosen for text generation as it excels at creative writing in non-English languages
4. **In-memory state** sufficient since bot is for single event (no persistence needed)
5. **Async architecture** follows python-telegram-bot best practices for concurrent handling

### Tone of Voice (from TokopediaImageInspiration)
- Fun, playful, over-the-top party atmosphere
- Ukrainian language throughout
- Humorous trash-talk (aggressive but not offensive)
- Dramatic announcements and buildup

### Image Generation Prompts Should Include

**Для представлення бійців (fighters command):**
- Людина тримає свого півня
- Тренер готує бійця до бою
- Власник з гордістю показує свого чемпіона
- Драматичне освітлення, атмосфера змагань

**Для пресс-конференції (conference command):**
- Півень "говорить" треш-ток (уособлення)
- Тренер підтримує свого бійця
- Драматичні сцени протистояння
- Партійна, весела атмосфера

**Важливо:**
- Використовувати РЕАЛЬНІ фото півня та людини як референс для генерації
- No explicit violence (Telegram-safe content)
- Комічний, розважальний стиль

### Rate Limiting Considerations
- Gemini image generation: Add 2-3 second delays between scene image generations
- Pre-generated fighter images eliminate need for on-demand fighter image generation
- 6 scene images per conference (one per trash-talk message)

### Fighter Data Structure

**Концепція:**
- Б'ються СПРАВЖНІ ПІВНІ
- Люди - це ВЛАСНИКИ / ТРЕНЕРИ / ПРОТЕЖЕ своїх півнів
- Потрібно генерувати фото: ЛЮДИ ТРИМАЮТЬ СВОЇХ ПІВНІВ, готують до бою

Located in `data/images/`:
```
data/images/
├── andrew_3/
│   ├── image.png                    # СПРАВЖНІЙ півень (фото)
│   ├── telegram-peer-photo-*.jpg    # Фото Андрія (власник/тренер)
│   └── (3 різних Андрія в цій папці!)
├── bohdan/
│   ├── image.png                    # СПРАВЖНІЙ півень (фото)
│   └── telegram-cloud-photo-*.jpg   # Фото Богдана (власник/тренер)
├── oleg/
│   ├── image.png                    # СПРАВЖНІЙ півень (фото)
│   └── telegram-peer-photo-*.jpg    # Фото Олега (власник/тренер)
├── petro/
│   ├── image.png                    # СПРАВЖНІЙ півень (фото)
│   └── telegram-peer-photo-*.jpg    # Фото Петра (власник/тренер)
├── roma/
│   ├── image.png                    # СПРАВЖНІЙ півень (фото)
│   └── ...
├── vadym/
│   ├── image.png                    # СПРАВЖНІЙ півень (фото)
│   └── ...
```

**Що є в кожній папці:**
- `image.png` - Фото СПРАВЖНЬОГО ПІВНЯ (боєць)
- `telegram-*.jpg` - Фото ЛЮДИНИ (власник/тренер/протеже півня)

**Що потрібно ГЕНЕРУВАТИ:**
- Фото де ЛЮДИНА ТРИМАЄ СВОГО ПІВНЯ
- Сцени підготовки півня до бою
- Тренер готує свого бійця

**Примітка:** `andrew_3` містить 3 різних Андрія (3 власники?) і 1 півня
