from music21 import stream, note, tempo, meter, duration, instrument

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
            'kick': { 'num': 35, 'obj': instrument.BassDrum() },
            'snare': { 'num': 38, 'obj': instrument.SnareDrum() },
            'hihat': { 'num': 42, 'obj': instrument.HiHatCymbal() },
        }
        self._init_score()
        self._init_parts()
        self.set_ts(self.signature)

    def _init_score(self):
        self.score = stream.Score()
        self.set_bpm(self.bpm)
        # self.score.append(instrument.Percussion()) # XXX broken?
        self.score.append(instrument.Woodblock())  # <- so this?

    def _init_parts(self):
        self.kick = stream.Part()
        self.kick.append(self.instruments['kick']['obj'])
        self.snare = stream.Part()
        self.snare.append(self.instruments['snare']['obj'])
        self.hihat = stream.Part()
        self.hihat.append(self.instruments['hihat']['obj'])

    def sync_parts(self):
        self.score.insert(0, self.kick)
        self.score.insert(0, self.snare)
        self.score.insert(0, self.hihat)
        
    def set_ts(self, ts):
        ts = meter.TimeSignature(ts)
        self.beats = ts.numerator
        self.divisions = ts.denominator
        self.kick.timeSignature = ts
        self.snare.timeSignature = ts
        self.hihat.timeSignature = ts

    def set_bpm(self, bpm):
        self.bpm = bpm
        self.score.append(tempo.MetronomeMark(number=bpm))

    def rest(self, dur=1.0, part=None):
        n = note.Rest()
        n.duration = duration.Duration(dur)
        if part:
            part.append(n)
        else:
            self.score.append(n)
        if dur:
            self.counter += dur

    def note(self, num, dur=1.0, volume=None, flam=0, part=None):
        if volume is None:
            volume = self.volume
        if flam > 0:
            grace = note.Note(num)
            grace.duration = duration.Duration(flam)
            part.append(grace)
        n = note.Note(num)
        n.volume.velocity = volume
        n.duration = duration.Duration(dur - flam)
        if part:
            part.append(n)
        else:
            self.score.append(n)
        if dur:
            self.counter += dur
    
    def accent_note(self, num, dur=1.0, volume=None, accent=None, part=None):
        if volume is None:
            volume = self.volume
        if accent is None:
            accent = self.accent
        self.note(num, dur=dur, volume=volume + accent, part=part)

    def duck_note(self, num, dur=1.0, volume=None, accent=None, part=None):
        if volume is None:
            volume = self.volume
        if accent is None:
            accent = self.accent
        self.note(num, dur=dur, volume=volume - accent, part=part)

    def count_in(self, bars=1, part=None):
        if part is None:
            part = self.hihat
        for _ in range(bars):
            self.accent_note(self.instruments['hihat']['num'], part=part)
            self.rest(part=self.kick)
            self.rest(part=self.snare)
            for i in range(self.beats - 1):
                self.note(self.instruments['hihat']['num'], part=part)
                self.rest(part=self.kick)
                self.rest(part=self.snare)

    def pattern(self, patterns=None, duration=1/4, vary=None):
        if not patterns:
            return

        if vary is None:
            vary = {
                '0': lambda self, **args: self.rest(dur=args['dur'], part=args['part']),
                '1': lambda self, **args: self.note(args['patch'], dur=args['dur'], part=args['part']),
            }

        if 'kick' in patterns:
            for pattern_str in patterns['kick']:
                for bit in pattern_str:
                    vary[bit](self, patch=self.instruments['kick']['num'], dur=duration, part=self.kick)
        if 'snare' in patterns:
            for pattern_str in patterns['snare']:
                for bit in pattern_str:
                    vary[bit](self, patch=self.instruments['snare']['num'], dur=duration, part=self.snare)
        if 'hihat' in patterns:
            for pattern_str in patterns['hihat']:
                for bit in pattern_str:
                    vary[bit](self, patch=self.instruments['hihat']['num'], dur=duration, part=self.hihat)

    def roll(self, duration=1, subdivisions=4, crescendo=[]):
        patch = self.instruments['snare']['num']
        if not crescendo:
            factor = 0
            volume = self.volume
        else:
            factor = round((crescendo[1] - crescendo[0]) / (subdivisions - 1))
            volume = crescendo[0]
        for _ in range(subdivisions):
            self.note(patch, dur=duration/subdivisions, volume=int(volume), part=self.snare)
            volume += factor
