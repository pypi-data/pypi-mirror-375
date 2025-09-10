import os
import sys

sys.path.insert(0, os.path.abspath('.'))

from idtap.classes.note_view_phrase import NoteViewPhrase
from idtap.classes.pitch import Pitch
from idtap.classes.raga import Raga


def test_note_view_phrase_basic():
    r = Raga()
    nv = NoteViewPhrase({'pitches': [Pitch()], 'dur_tot': 1, 'raga': r, 'start_time': 0})
    assert len(nv.pitches) == 1
    assert nv.dur_tot == 1
    assert isinstance(nv.raga, Raga)
    assert nv.start_time == 0
