#!/usr/bin/env python3
import json
import sys

data = json.load(sys.stdin)

for month, games in data.items():
    for game in games:
        if (not game.get("genres") or 
            game.get("image") is None or 
            game.get("link") is None):
            print(json.dumps(game, indent=2))