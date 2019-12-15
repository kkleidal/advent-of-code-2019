I reverse engineered the solution for part 2.

## Things I tried before getting it working

1. Whenever I "lost" I put the ball back in the top of the board and continued executing. This ended up messing up the score.
2. I started trying to make an RL agent to play the game using deep-Q learning, but abandoned that pretty quickly when I thought up the solution that worked.

## The solution that worked

I wrote a basic disassembler for intcode to make it easier for me to read
the intcode and identify where I needed to make my changes.

Using the disassembler (see [disassembly.txt](./disassembly.txt)), I realized that the initial
board state was being stored by tile codes at memory addresses 639 + 40 * y + x where y was
the y coordinate of the tile and x the x coordinate. So in `hacked_game_factory`, I simply
wrote a row of walls at `y = 24` so that the ball couldn't fall out the bottom.
