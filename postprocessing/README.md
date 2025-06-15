# Postprocessing

Humble choice games generally have all the information on the choice page,
but monthly games are missing information (like genre and thumbnails).

Scripts here search for genre and image information on the steam page for every
game. Genres are limited to genres listed in humble choice games:

 - Action
 - Adventure
 - Fps
 - Indie
 - Mmo
 - Multiplayer
 - Puzzle
 - Racing
 - Retro
 - Rpg
 - Simulation
 - Sports
 - Strategy
 - Virtual Reality

## Usage

1. Use convert-games.js to convert the list of humble monthly games to the
   same format as the humble choice games.
2. Use `populate_monthly_games.py` to search all monthly games on steam
   for genre and thumbnails.
