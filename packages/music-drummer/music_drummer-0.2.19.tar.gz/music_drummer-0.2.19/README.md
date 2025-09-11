# Music Drummer
Glorified Metronome

The methods of this package depend upon `music21`.

For this package (and `music21` too), a `duration` of `1` is a quarter-note. So, `1/2` would be an eighth-note, etc.

The (general MIDI) kit is made up of the following instrument types (and defaults):
```
'kick' (default: 'kick1')
'snare' (default: 'snare1')
'hihat' (default: 'hihat1')
'toms' (default 'tom3')
'cymbals' (default: 'crash1')
'percussion' (default: 'woodblock1')
```

Each above type includes a `music21` `Part` and a `counter` (that starts at `0` of course).

The known instruments and their names, MIDI numbers, and types can be seen by printing the return of `instrument_map()`.

You can change default instruments with the `set_instrument()` method. This is most useful for the `kick` and `snare` types, because there are two variations for each: acoustic and electric.

## SYNOPSIS
```python
from music_drummer import Drummer

# Ex 1 - basic 4/4 metronome groove:
d = Drummer()
d.set_bpm(60) # set the beats per minute
d.set_ts() # set the default time signature of 4/4
# add a 16-beat phrase for 64 measures
for _ in range(64):
    d.pattern(
        patterns={
            'kick':  '1000000010000000',
            'snare': '0000100000001000',
            'hihat': '1010101010101010',
        },
    )
d.sync_parts() # make the parts play simultaneously
d.show(format='midi') # or nothing, ='text', etc. see music21 docs

# Ex 2 - 5/8 groove with intro:
d = Drummer()

d.set_instrument('kick', 'kick2') # change to the electric kick
d.set_instrument('snare', 'snare2') # change to the electric snare
# print(d.instrument_map()) # full list of known instruments

d.set_bpm(99) # change the beats per minute from 120
d.set_ts('5/8') # change the time signature from 4/4

d.count_in(2) # count-in on the hi-hats for 2 measures
d.rest('kick', duration=10)
d.rest('snare', duration=10)
d.rest('cymbals', duration=10)
d.rest('toms', duration=10)

# 3 known hi-hat states: closed, open, pedal
d.note('closed', duration=1/2)
d.note('open', duration=1/2)
d.note('pedal', duration=1/2)
d.note('closed', duration=1/2)
d.rest(['snare', 'kick', 'cymbals', 'toms'], duration=2)

# 7 known cymbals:
d.note('crash1')
d.note('crash2')
d.note('china')
d.note('splash')
d.note('ride1')
d.note('ride2')
d.note('ridebell')
d.rest(['kick', 'snare', 'hihat', 'toms'], duration=7)

# 6 known toms:
d.note('tom1', duration=1/3)
d.note('tom2', duration=1/3)
d.note('tom3', duration=1/3)
d.note('tom4', duration=1/3)
d.note('tom5', duration=1/3)
d.note('tom6', duration=1/3)
d.rest(['kick', 'snare', 'hihat', 'cymbals'], duration=2)

# add a eighth-note snare flam to the score
d.note('snare', duration=1/2, flam=1/16)
d.rest(['kick', 'hihat', 'cymbals', 'toms'], duration=1/2)

# add a 5-note snare roll for an eighth-note, increasing in volume
d.roll('snare', duration=1/2, subdivisions=5, crescendo=[100, 127])
d.rest(['kick', 'hihat', 'cymbals', 'toms'], duration=1/2)

# crash and kick!
d.note('kick', duration=1/2)
d.note('crash1', duration=1/2)
d.rest(['snare', 'hihat', 'toms'], duration=1/2)

# add a 4-part, 8-bar, eighth-note phrase to the score
for _ in range(8):
    d.pattern(
        patterns={
            'kick':   '1000000010',
            'snare':  '0000001000',
            'hihat':  '0111111111',
            'crash1': '1000000000',
        },
        duration=1/2
    )

d.sync_parts() # make the parts play simultaneously

d.show() # or format='text', format='midi', etc. see music21 docs
# or
d.write() # or filename='groove.mid' for example
```