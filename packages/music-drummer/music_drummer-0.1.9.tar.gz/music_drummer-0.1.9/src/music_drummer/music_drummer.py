from music21 import stream, note, tempo, meter, instrument
from music21 import duration as m21duration

class Drummer:
    STRAIGHT = 50

    def __init__(self, file='Drummer.mid', bpm=120, volume=100, accent=20, signature='4/4', bars=4):
        self.file = file
        self.volume = volume
        self.bars = bars
        self.counter = 0
        self.accent = accent
        self.signature = signature
        self.bpm = bpm
        self.instruments = {
            'kick': { 'num': 35, 'obj': instrument.BassDrum(), 'part': stream.Part() },
            'snare': { 'num': 38, 'obj': instrument.SnareDrum(), 'part': stream.Part() },
            'hihat': { 'num': 42, 'obj': instrument.HiHatCymbal(), 'part': stream.Part() },
        }
        self._init_score()
        self._init_parts()

    def _init_score(self):
        self.score = stream.Score()
        # self.score.append(instrument.Percussion()) # XXX broken?
        self.score.append(instrument.Woodblock())  # <- so this?

    def _init_parts(self):
        for inst in self.instruments.values():
            inst['part'].append(inst['obj'])

    def sync_parts(self):
        for inst in self.instruments.values():
            self.score.insert(0, inst['part'])

    def set_ts(self, ts=None):
        if not ts:
            ts = self.signature
        else:
            self.signature = ts
        ts = meter.TimeSignature(ts)
        self.beats = ts.numerator
        self.divisions = ts.denominator
        for inst in self.instruments.values():
            inst['part'].timeSignature = ts

    def set_bpm(self, bpm=None):
        if not bpm:
            bpm = self.bpm
        else:
            self.bpm = bpm
        self.score.append(tempo.MetronomeMark(number=bpm))

    def set_instrument(self, name, num, obj=None):
        if name in self.instruments:
            self.instruments[name]['num'] = num
        else:
            self.instruments[name] = { 'num': num, 'part': stream.Part() }
            if obj:
                self.instruments[name]['obj'] = obj
            else:
                self.instruments[name]['obj'] = instrument.Woodblock()

    def rest(self, name, duration=1.0):
        n = note.Rest()
        n.duration = m21duration.Duration(duration)
        if name:
            self.instruments[name]['part'].append(n)
        else:
            self.score.append(n)
        if duration:
            self.counter += duration

    def note(self, name, duration=1.0, volume=None, flam=0):
        if volume is None:
            volume = self.volume
        if flam > 0:
            grace = note.Note(self.instruments[name]['num'])
            grace.duration = m21duration.Duration(flam)
            self.instruments[name]['part'].append(grace)
        n = note.Note(self.instruments[name]['num'])
        n.volume.velocity = volume
        n.duration = m21duration.Duration(duration - flam)
        if name:
            self.instruments[name]['part'].append(n)
        else:
            self.score.append(n)
        if duration:
            self.counter += duration

    def accent_note(self, name, duration=1.0, volume=None, accent=None):
        if volume is None:
            volume = self.volume
        if accent is None:
            accent = self.accent
        self.note(name, duration=duration, volume=volume + accent)

    def duck_note(self, name, duration=1.0, volume=None, accent=None):
        if volume is None:
            volume = self.volume
        if accent is None:
            accent = self.accent
        self.note(name, duration=duration, volume=volume - accent)

    def count_in(self, bars=1):
        for _ in range(bars):
            self.accent_note('hihat')
            for i in range(self.beats - 1):
                self.note('hihat')

    def pattern(self, patterns=None, duration=1/4, vary=None):
        if not patterns:
            return

        if vary is None:
            vary = {
                '0': lambda self, **args: self.rest(args['patch'], duration=args['duration']),
                '1': lambda self, **args: self.note(args['patch'], duration=args['duration']),
            }

        if 'kick' in patterns:
            for pattern_str in patterns['kick']:
                for bit in pattern_str:
                    vary[bit](self, patch='kick', duration=duration)
        if 'snare' in patterns:
            for pattern_str in patterns['snare']:
                for bit in pattern_str:
                    vary[bit](self, patch='snare', duration=duration)
        if 'hihat' in patterns:
            for pattern_str in patterns['hihat']:
                for bit in pattern_str:
                    vary[bit](self, patch='hihat', duration=duration)

    def roll(self, name, duration=1, subdivisions=4, crescendo=[]):
        if not crescendo:
            factor = 0
            volume = self.volume
        else:
            factor = round((crescendo[1] - crescendo[0]) / (subdivisions - 1))
            volume = crescendo[0]
        for _ in range(subdivisions):
            self.note(name, duration=duration/subdivisions, volume=int(volume))
            volume += factor
