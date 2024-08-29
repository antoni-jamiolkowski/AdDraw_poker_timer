# poker_timer

Poker Level Timer


Summary:

Poker Timer should allow anybody to run a tournament game with:

- timed rounds that change automatically
- autoincremented blinds
- ability to change the blinds, number of levels etc easily
- ability to reset the state of the game
- ability to move up/down in levels
- ability to pause the tournament at any time(in case of a problem/in case of a PAUSE required)

If I would like to run a game:

- Ideally:
  - I should just choose the config/setup of the tournament
  - hit play and just be notified of round changes
  - If I need a pause I can make it any time I want
    - either have them embedded into the config or have them be done manually)
  - If there is a problem or I have messed something up I want to be able to reset the app without having to close it(should be repeatable since you might like to play X tournaments in one sitting)

Display(what is the most important information):

- Blind values(this should be visible enough so that anybody can look at it and easily remember)
- Time left for the round
  - This might be checked more often than blind values since in theory at least one person will remember them after checking on round start
  - Should be big enough so that looking at it does not make the game halt etc(one glance and has to be checked often, or it might be that a bell sound might be what players will prefer to wait for to indicate the round end)
- Controls: Should be big enough to make it easy to use with a simple mouse/controller combo


## Game state

- `current level`, this should be enough to tell you:
  - current `blinds`
  - current `round period`
- round timer
  - tracks the round, and at the end of the round level is changed
- timer state:
  - has the current round been paused
- global timer:
  - how long has the app been open

## State Machine

1. **IDLE** - game has not been started, config can be chosen, game can be started on `PLAY`, global timer ticks
2. **NORMAL** -
   1. round timer ticks, on round_timer end event go to `STATE_UPDATE with direction up`
   2. when `PAUSE` has been hit go to `PAUSED`
   3. when `NEXT/PREV LVL` hit, go to `STATE_UPDATE` with a direction of `either down or up`
   4. on `RESET`, go to `RESET_STATE`
3. **STATE_UPDATE**: based on config and current state change the state for next/prev level
   1. exit naturally to `NORMAL/PAUSED` if the tournament should still play
   2. if there are no further levels end the tournament
   3. if there are no `down` levels, keep the level at `0/1`
4. **RESET_STATE** - in this state, go back to level `0/1`
5. **PAUSED** - in this state, keep the config as is, initialize the `PAUSED timer`, on `PLAY` go back to `NORMAL`

>  at any point config can be chosen/updated using a `Settings` button

>  should I make this some form of a FSM? maybe just operating at Timer/Button events is better?
>
> How do I then make it most easy to write the code, keep the state, keep the config, update the config etc
