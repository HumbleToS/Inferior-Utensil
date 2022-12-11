from __future__ import annotations

import random

import discord

__all__ = [
    'randpastel_color',
]

def randpastel_color() -> discord.Color:
    return discord.Color.from_hsv(random.random(), 0.28, 0.97)
