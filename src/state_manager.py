"""State management for Dana CockFight Telegram Bot.

Manages game state including fighter data, pairings, and conference rounds.
Pre-loads 6 fighters from data/images/ directory and tracks game progression.
"""

import logging
import random
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class Fighter:
    """Represents a fighting rooster and its trainer/owner.

    Attributes:
        name: Fighter name (e.g., "andrew_3", "bohdan")
        description: Brief description of rooster/trainer in Ukrainian
        rooster_image_path: Absolute path to rooster image (image.png)
        human_image_path: Absolute path to human/trainer image
    """

    name: str
    description: str
    rooster_image_path: str
    human_image_path: str


def load_fighters() -> list[Fighter]:
    """Load 6 pre-defined fighters from data/images/ directory.

    Scans the data/images/ directory for fighter subdirectories and loads
    fighter data including image paths and descriptions.

    Fighter directories should contain:
        - image.png: Rooster photo
        - telegram-*.jpg or "image copy.png": Human/trainer photo

    Returns:
        List of 6 Fighter instances with valid paths.
    """
    base_path = Path(__file__).parent.parent / "data" / "images"

    fighter_names = ["andrew_3", "bohdan", "oleg", "petro", "roma", "vadym"]
    fighters: list[Fighter] = []

    # Fighter descriptions (trashy party tone - Ukrainian with emojis)
    descriptions: dict[str, str] = {
        "andrew_3": """Троє — сила! 💪
Один веде блог і знає всі тренди (нарцис, але талановитий).
Другий фотографує кожен момент — навіть твій ганебний програш буде в HD! 📸
Третій напише про це вірш... і він буде жорстокий. ✍️
Що поганого може статися? ВСЕ.
Їхній півень не просто кукурікає — він вайбить на всіх платформах!
Тебе розірвуть на контент ще до початку бою! 😈""",
        "bohdan": """ІМЕНИННИК, СУЧКИ! 🎉
Сьогодні ВСЕ для нього — і цей турнір теж.
Кажуть, що змагання підкуплене... 🤫
Бо у цього півня є зв'язки з організаторами.
Але це не точно... чи точно? 😏
День народження — його суперсила.
Хто наважиться побити іменинника?
Тобі потім жити з цим... 🎂💀""",
        "oleg": """Найвищий. 📏
Найголосніший. 📢
Найрозумніший. 🧠
Три «най» в одному півні — задовбав уже хвалитися!
Прилетів зі Штатів — давно не бачив ципочок. 🐔💕
Тому найагресивніший — сублімація, чули?
Коли ти бачив світ, дрібні місцеві півні здаються... ЖАЛЮГІДНИМИ.
Та чи досвіду вистачить, щоб не обісратися на рідній землі? 😤""",
        "petro": """Спокійний і розсудливий... 🧘
Справжній дзен-майстер серед півнів.
АЛЕ.
Як треба — легко дасть пізди. 👊
Найстарший пєтух турніру.
З віком приходить мудрість... і БЕЗЖАЛЬНІСТЬ.
Не ведись на його спокійний вигляд — це тактика!
Він просто чекає, коли ти облажаєшся. А ти облажаєшся. 💀""",
        "roma": """Шикарні уси — шикарний півень! 🥸
Він на Балі ненадовго. 🐕✈️
Але його півень встигне тебе знищити!
Діджеїть так, що твій півень танцює замість бою. 🎧🔥
Ще й продасть тобі твою поразку з посмішкою. 💼😈""",
        "vadym": """Зараз у Штатах, але навіть на відстані його півень може всім НАВАЛЯТИ! 🇺🇸👊
Власник Buba Tea — чайної в стилі Балі. 🧋🌴
Подає найкращі чаї, поки ти подаєш надії.
Приводить лідів на Upwork — справжній бізнесмен!
Його півень працює remote, але б'є ЛОКАЛЬНО.
Distance is not a barrier — для нього і для болю, який він принесе! 💼💀""",
    }

    for name in fighter_names:
        fighter_dir = base_path / name

        if not fighter_dir.exists():
            logger.warning(f"Fighter directory not found: {fighter_dir}")
            continue

        rooster_path = fighter_dir / "image.png"
        if not rooster_path.exists():
            logger.warning(f"Rooster image not found for {name}: {rooster_path}")
            continue

        # Find human photo: try telegram-*.jpg first, then "image copy.png"
        human_photos = list(fighter_dir.glob("telegram-*.jpg"))
        human_path: Path | None = None

        if human_photos:
            human_path = human_photos[0]  # Use first match
        else:
            # Fallback to "image copy.png" for fighters without telegram photos
            copy_path = fighter_dir / "image copy.png"
            if copy_path.exists():
                human_path = copy_path
            else:
                logger.warning(f"No human photo found for {name}")
                continue

        fighters.append(
            Fighter(
                name=name,
                description=descriptions.get(name, "Mysterious fighter"),
                rooster_image_path=str(rooster_path),
                human_image_path=str(human_path),
            )
        )
        logger.debug(f"Loaded fighter: {name}")

    logger.info(f"Loaded {len(fighters)} fighters")
    return fighters


class GameState:
    """Manages game state for a single chat.

    Tracks fighters, pairings from draw, and conference progression.
    Each chat_id gets its own GameState instance.

    Attributes:
        fighters: List of all 6 pre-loaded Fighter instances
        pairings: List of 3 fighter pairs after /draw command
        current_conference: Index of current pair in conference (0-2)
        conference_round: Current round of trash-talk within a conference (0-2)
    """

    def __init__(self) -> None:
        """Initialize game state with pre-loaded fighters."""
        self.fighters: list[Fighter] = load_fighters()
        self.pairings: list[tuple[Fighter, Fighter]] = []
        self.current_conference: int = 0
        self.conference_round: int = 0

    def draw_pairings(self) -> list[tuple[Fighter, Fighter]]:
        """Randomly pair 6 fighters into 3 matches.

        Shuffles fighters and creates 3 pairs for battles.
        Resets conference state for new draw.

        Returns:
            List of 3 tuples, each containing 2 Fighter instances.

        Raises:
            ValueError: If there are not exactly 6 fighters available.
        """
        if len(self.fighters) != 6:
            raise ValueError(
                f"Expected 6 fighters for draw, got {len(self.fighters)}"
            )

        shuffled = self.fighters.copy()
        random.shuffle(shuffled)

        self.pairings = [
            (shuffled[0], shuffled[1]),
            (shuffled[2], shuffled[3]),
            (shuffled[4], shuffled[5]),
        ]
        self.current_conference = 0
        self.conference_round = 0

        logger.info(
            f"Drew pairings: "
            f"{[(p[0].name, p[1].name) for p in self.pairings]}"
        )
        return self.pairings

    def get_current_pair(self) -> tuple[Fighter, Fighter] | None:
        """Get the current conference pair.

        Returns:
            Tuple of 2 Fighter instances for current conference,
            or None if no pairings exist or all conferences are complete.
        """
        if not self.pairings:
            return None
        if self.current_conference >= len(self.pairings):
            return None
        return self.pairings[self.current_conference]

    def advance_round(self) -> bool:
        """Advance to the next trash-talk round within current conference.

        Returns:
            True if there are more rounds in current conference,
            False if the conference is complete.
        """
        self.conference_round += 1
        if self.conference_round >= 3:
            return False
        return True

    def advance_conference(self) -> bool:
        """Move to the next conference pair.

        Resets conference_round to 0 and increments current_conference.

        Returns:
            True if there are more conferences remaining,
            False if all conferences are complete.
        """
        self.current_conference += 1
        self.conference_round = 0

        has_more = self.current_conference < len(self.pairings)
        logger.info(
            f"Advanced to conference {self.current_conference}, "
            f"more remaining: {has_more}"
        )
        return has_more

    def reset(self) -> None:
        """Reset game state for a new game.

        Clears pairings and resets conference tracking.
        Fighters remain loaded.
        """
        self.pairings = []
        self.current_conference = 0
        self.conference_round = 0
        logger.info("Game state reset")

    def is_conference_active(self) -> bool:
        """Check if a conference is currently in progress.

        Returns:
            True if pairings exist and not all conferences are complete.
        """
        return bool(self.pairings) and self.current_conference < len(self.pairings)

    def get_conference_progress(self) -> tuple[int, int, int, int]:
        """Get current conference progress.

        Returns:
            Tuple of (current_conference, total_conferences,
                     current_round, total_rounds).
            All values are 1-indexed for display purposes.
        """
        return (
            self.current_conference + 1,
            len(self.pairings) if self.pairings else 3,
            self.conference_round + 1,
            3,  # Total rounds per conference
        )


# Global state storage - keyed by chat_id
_game_states: dict[int, GameState] = {}


def get_game_state(chat_id: int) -> GameState:
    """Get or create game state for a specific chat.

    Thread-safe access to per-chat game state.
    Automatically initializes a new GameState if one doesn't exist.

    Args:
        chat_id: Telegram chat ID

    Returns:
        GameState instance for the specified chat.
    """
    if chat_id not in _game_states:
        logger.info(f"Creating new game state for chat {chat_id}")
        _game_states[chat_id] = GameState()
    return _game_states[chat_id]


def reset_game_state(chat_id: int) -> None:
    """Reset game state for a specific chat.

    Removes the existing state, causing a fresh state to be created
    on next access.

    Args:
        chat_id: Telegram chat ID
    """
    if chat_id in _game_states:
        del _game_states[chat_id]
        logger.info(f"Removed game state for chat {chat_id}")
