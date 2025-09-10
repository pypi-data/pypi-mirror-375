import math
from collections import defaultdict

class MidiDrummerTiny:
    STRAIGHT = 50

    def __init__(self, file='MIDI-Drummer.mid', bpm=120, volume=100, signature='4/4', bars=4, reverb=15, soundfont=None, kick=35, snare=38, setup=True, verbose=False):
        self.file = file
        self.bpm = bpm
        self.volume = volume
        self.signature = signature
        self.bars = bars
        self.reverb = reverb
        self.soundfont = soundfont
        self.kick = kick
        self.snare = snare
        self.setup = setup
        self.verbose = verbose
        self.channel = 9
        self.counter = 0
        self.beats, self.divisions = map(int, self.signature.split('/'))
        self.score = []
        self._init_percussion()
        self._init_durations()
        if self.setup:
            self._build()

    def _init_percussion(self):
        percussion_names = [
            'click', 'bell', 'acoustic_bass', 'electric_bass', 'side_stick', 'acoustic_snare', 'clap', 'electric_snare',
            'low_floor_tom', 'closed_hh', 'hi_floor_tom', 'pedal_hh', 'low_tom', 'open_hh', 'low_mid_tom', 'hi_mid_tom',
            'crash1', 'hi_tom', 'ride1', 'china', 'ride_bell', 'tambourine', 'splash', 'cowbell', 'crash2', 'vibraslap',
            'ride2', 'hi_bongo', 'low_bongo', 'mute_hi_conga', 'open_hi_conga', 'low_conga', 'high_timbale', 'low_timbale',
            'high_agogo', 'low_agogo', 'cabasa', 'maracas', 'short_whistle', 'long_whistle', 'short_guiro', 'long_guiro',
            'claves', 'hi_wood_block', 'low_wood_block', 'mute_cuica', 'open_cuica', 'mute_triangle', 'open_triangle'
        ]
        start = 33
        for i, name in enumerate(percussion_names):
            setattr(self, name, start + i)
        self.kick = 35
        self.snare = 38

    def _init_durations(self):
        self.whole = 'wn'
        self.half = 'hn'
        self.quarter = 'qn'
        self.eighth = 'en'
        self.sixteenth = 'sn'
        self.thirtysecond = 'xn'
        self.sixtyfourth = 'yn'
        self.onetwentyeighth = 'zn'
        self.triplet_whole = 'twn'
        self.dotted_whole = 'dwn'
        self.double_dotted_whole = 'ddwn'
        self.triplet_half = 'thn'
        self.dotted_half = 'dhn'
        self.double_dotted_half = 'ddhn'
        self.triplet_quarter = 'tqn'
        self.dotted_quarter = 'dqn'
        self.double_dotted_quarter = 'ddqn'
        self.triplet_eighth = 'ten'
        self.dotted_eighth = 'den'
        self.double_dotted_eighth = 'dden'
        self.triplet_sixteenth = 'tsn'
        self.dotted_sixteenth = 'dsn'
        self.double_dotted_sixteenth = 'ddsn'
        self.triplet_thirtysecond = 'txn'
        self.dotted_thirtysecond = 'dxn'
        self.double_dotted_thirtysecond = 'ddxn'
        self.triplet_sixtyfourth = 'tyn'
        self.dotted_sixtyfourth = 'dyn'
        self.double_dotted_sixtyfourth = 'ddyn'
        self.triplet_onetwentyeighth = 'tzn'
        self.dotted_onetwentyeighth = 'dzn'
        self.double_dotted_onetwentyeighth = 'ddzn'

    def _build(self):
        # Placeholder for MIDI setup logic
        pass

    def set_channel(self, channel=9):
        self.channel = channel

    def set_volume(self, volume=0):
        self.volume = volume

    def set_bpm(self, bpm):
        self.bpm = bpm

    def set_time_sig(self, time_signature=None, set_beats=True):
        if time_signature:
            self.signature = time_signature
        if set_beats:
            self.beats, self.divisions = map(int, self.signature.split('/'))

    def note(self, duration, *patches):
        self.counter += self._dura_size(duration)
        self.score.append(('note', duration, *patches))

    def accent_note(self, accent, duration, *patches):
        self.score.append(('accent_note', accent, duration, *patches))

    def rest(self, duration):
        self.counter += self._dura_size(duration)
        self.score.append(('rest', duration))

    def count_in(self, bars=None, patch=None, accent=None):
        bars = bars if bars is not None else self.bars
        patch = patch if patch is not None else getattr(self, 'pedal_hh', self.closed_hh)
        accent = accent if accent is not None else self.closed_hh
        for i in range(1, self.beats * bars + 1):
            if i % self.beats == 1:
                self.accent_note(127, self.quarter, accent)
            else:
                self.note(self.quarter, patch)

    def metronome3(self, bars=None, cymbal=None, tempo=None, swing=None):
        bars = bars if bars is not None else self.bars
        cymbal = cymbal if cymbal is not None else self.closed_hh
        tempo = tempo if tempo is not None else self.quarter
        swing = swing if swing is not None else 50
        for _ in range(bars):
            self.note(tempo, cymbal, self.kick)
            if swing > self.STRAIGHT:
                self.note(tempo, cymbal)
                self.note(tempo, cymbal)
            else:
                self.note(tempo, cymbal)
            self.note(tempo, cymbal, self.snare)

    def metronome4(self, bars=None, cymbal=None, tempo=None, swing=None):
        bars = bars if bars is not None else self.bars
        cymbal = cymbal if cymbal is not None else self.closed_hh
        tempo = tempo if tempo is not None else self.quarter
        swing = swing if swing is not None else 50
        for _ in range(bars):
            self.note(tempo, cymbal, self.kick)
            if swing > self.STRAIGHT:
                self.note(tempo, cymbal)
                self.note(tempo, cymbal)
            else:
                self.note(tempo, cymbal)
            self.note(tempo, cymbal, self.snare)
            if swing > self.STRAIGHT:
                self.note(tempo, cymbal)
                self.note(tempo, cymbal)
            else:
                self.note(tempo, cymbal)

    def metronome5(self, bars=None, cymbal=None, tempo=None, swing=None):
        bars = bars if bars is not None else self.bars
        cymbal = cymbal if cymbal is not None else self.closed_hh
        tempo = tempo if tempo is not None else self.quarter
        swing = swing if swing is not None else 50
        for n in range(1, bars + 1):
            self.note(tempo, cymbal, self.kick)
            if swing > self.STRAIGHT:
                self.note(tempo, cymbal)
                self.note(tempo, cymbal)
            else:
                self.note(tempo, cymbal)
            self.note(tempo, cymbal, self.snare)
            if swing > self.STRAIGHT:
                self.note(tempo, cymbal)
                self.note(tempo, cymbal)
            else:
                self.note(tempo, cymbal)
            if n % 2:
                self.note(tempo, cymbal)
            else:
                self.note(self.half, cymbal)
                self.note(self.half, self.kick)

    def metronome6(self, bars=None, cymbal=None, tempo=None, swing=None):
        bars = bars if bars is not None else self.bars
        cymbal = cymbal if cymbal is not None else self.closed_hh
        tempo = tempo if tempo is not None else self.quarter
        swing = swing if swing is not None else 50
        for _ in range(bars):
            self.note(tempo, cymbal, self.kick)
            if swing > self.STRAIGHT:
                self.note(tempo, cymbal)
                self.note(tempo, cymbal)
            else:
                self.note(tempo, cymbal)
            self.note(tempo, cymbal)
            self.note(tempo, cymbal, self.snare)
            if swing > self.STRAIGHT:
                self.note(tempo, cymbal)
                self.note(tempo, cymbal)
            else:
                self.note(tempo, cymbal)
            self.note(tempo, cymbal)

    def metronome7(self, bars=None, cymbal=None, tempo=None, swing=None):
        bars = bars if bars is not None else self.bars
        cymbal = cymbal if cymbal is not None else self.closed_hh
        tempo = tempo if tempo is not None else self.quarter
        swing = swing if swing is not None else 50
        for _ in range(bars):
            self.note(tempo, cymbal, self.kick)
            if swing > self.STRAIGHT:
                self.note(tempo, cymbal)
                self.note(tempo, cymbal)
            else:
                self.note(tempo, cymbal)
            self.note(tempo, cymbal)
            if swing > self.STRAIGHT:
                self.note(tempo, cymbal, self.kick)
                self.note(tempo, cymbal)
            else:
                self.note(tempo, cymbal, self.kick)
            self.note(tempo, cymbal, self.snare)
            if swing > self.STRAIGHT:
                self.note(tempo, cymbal)
                self.note(tempo, cymbal)
            else:
                self.note(tempo, cymbal)
            self.note(tempo, cymbal)

    def metronome44(self, bars=None, flag=0, cymbal=None):
        bars = bars if bars is not None else self.bars
        cymbal = cymbal if cymbal is not None else self.closed_hh
        i = 0
        for n in range(1, self.beats * bars + 1):
            if n % 2 == 0:
                self.note(self.quarter, cymbal, self.snare)
            else:
                if flag == 0:
                    self.note(self.quarter, cymbal, self.kick)
                else:
                    if i % 2 == 0:
                        self.note(self.quarter, cymbal, self.kick)
                    else:
                        self.note(self.eighth, cymbal, self.kick)
                        self.note(self.eighth, self.kick)
                i += 1

    def flam(self, spec, grace=None, patch=None, accent=None):
        grace = grace if grace is not None else self.snare
        patch = patch if patch is not None else self.snare
        accent = accent if accent is not None else self.volume // 2
        if grace == 'r':
            self.rest(self.sixtyfourth)
        else:
            self.accent_note(accent, self.sixtyfourth, grace)
        self.note(spec, patch)

    def roll(self, length, spec, patch=None):
        patch = patch if patch is not None else self.snare
        count = int(self._dura_size(length) / self._dura_size(spec))
        for _ in range(count):
            self.note(spec, patch)

    def crescendo_roll(self, span, length, spec, patch=None):
        patch = patch if patch is not None else self.snare
        start, end, bezier = span
        count = int(self._dura_size(length) / self._dura_size(spec))
        if bezier:
            for n in range(count):
                t = n / (count - 1) if count > 1 else 0
                v = int(start + (end - start) * t * t * (3 - 2 * t))  # simple bezier
                self.accent_note(v, spec, patch)
        else:
            step = (end - start) / (count - 1) if count > 1 else 0
            for n in range(count):
                v = int(start + step * n)
                self.accent_note(v, spec, patch)

    def pattern(self, patterns=None, instrument=None, duration=None, beats=None, repeat=1, negate=False, vary=None):
        instrument = instrument if instrument is not None else self.snare
        patterns = patterns if patterns is not None else []
        beats = beats if beats is not None else self.beats
        if not patterns:
            return
        if duration is None:
            duration = self.quarter
        if vary is None:
            vary = {
                '0': lambda self, **args: self.rest(duration),
                '1': lambda self, **args: self.note(duration, instrument)
            }
        for pattern in patterns:
            if negate:
                pattern = ''.join('1' if c == '0' else '0' for c in pattern)
            if set(pattern) == {'0'}:
                continue
            for _ in range(repeat):
                for bit in pattern:
                    vary[bit](self)

    def sync_patterns(self, **patterns):
        master_duration = patterns.pop('duration', None)
        for instrument, pats in patterns.items():
            self.pattern(patterns=pats, instrument=instrument, duration=master_duration)

    def add_fill(self, fill=None, **patterns):
        if fill is None:
            fill = lambda self: {
                'duration': 8,
                self.open_hh: '000',
                self.snare: '111',
                self.kick: '000'
            }
        fill_patterns = fill(self)
        fill_duration = fill_patterns.pop('duration', 8)
        fill_length = len(next(iter(fill_patterns.values())))
        lengths = {inst: sum(len(p) for p in pats) for inst, pats in patterns.items()}
        lcm = self._multilcm(fill_duration, *lengths.values())
        size = 4 / lcm
        master_duration = self.eighth
        fill_chop = fill_length if fill_duration == lcm else int(lcm / fill_length) + 1
        fresh_patterns = {}
        for inst, pats in patterns.items():
            pattern = ''.join(''.join(p) for p in pats)
            fresh_patterns[inst] = [pattern.ljust(lcm, '0')]
        replacement = {}
        for inst, pat in fill_patterns.items():
            pattern = pat.rjust(fill_duration, '0')
            fresh = pattern.ljust(lcm, '0')
            replacement[inst] = fresh[-fill_chop:]
        replaced = {}
        for inst, pats in fresh_patterns.items():
            string = pats[0]
            pos = len(replacement.get(inst, ''))
            string = string[:-pos] + replacement.get(inst, '') if pos else string
            replaced[inst] = [string]
        self.sync_patterns(**replaced, duration=master_duration)
        return replaced

    def write(self):
        # Placeholder for MIDI file writing
        pass

    def timidity_cfg(self, config=None):
        if not self.soundfont:
            raise ValueError('No soundfont defined')
        # Placeholder for timidity config generation
        return f"soundfont {self.soundfont}"

    def play_with_timidity(self, config=None):
        # Placeholder for playing with timidity
        pass

    def play_with_fluidsynth(self, config=None):
        # Placeholder for playing with fluidsynth
        pass

    def _dura_size(self, duration):
        # Placeholder for duration size calculation
        # For now, treat all durations as 1
        return 1

    def _gcf(self, x, y):
        while y:
            x, y = y, x % y
        return x

    def _lcm(self, x, y):
        return x * y // self._gcf(x, y)

    def _multilcm(self, *args):
        x = args[0]
        for y in args[1:]:
            x = self._lcm(x, y)
        return x
