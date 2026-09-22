from __future__ import annotations

CHARACTERS = {
    "chintu": {
        "name": "चिंटू",
        "role": "curious hero",
        "age": 7,
        "species": "human",
        "visual": "Indian boy, short black hair, yellow hoodie, blue shorts, red sneakers, expressive friendly face",
        "personality": ["curious", "brave", "kind", "playful"],
    },
    "mini": {
        "name": "मिन्नी",
        "role": "clever problem-solver",
        "age": 7,
        "species": "human",
        "visual": "Indian girl, black hair in two ponytails with colorful clips, turquoise top, purple skirt, white sneakers",
        "personality": ["clever", "calm", "creative", "helpful"],
    },
    "golu": {
        "name": "गोलू",
        "role": "funny animal companion",
        "age": None,
        "species": "squirrel",
        "visual": "cute brown squirrel with cream belly, large expressive eyes, tiny green backpack",
        "personality": ["funny", "energetic", "kind", "mischievous"],
    },
    "tinku": {
        "name": "टिंकू",
        "role": "friendly helper robot",
        "age": None,
        "species": "robot",
        "visual": "rounded white and sky-blue robot, friendly glowing eyes, small antenna, orange accent lights",
        "personality": ["helpful", "curious", "logical", "gentle"],
    },
}

def get_character(key: str) -> dict:
    return CHARACTERS[key]
