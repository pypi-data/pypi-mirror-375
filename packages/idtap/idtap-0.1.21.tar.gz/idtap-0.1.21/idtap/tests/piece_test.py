import os
import sys
sys.path.insert(0, os.path.abspath("."))

import json
from pathlib import Path

import pytest
import math

from idtap.classes.piece import (
    Piece,
    init_sec_categorization,
    durations_of_fixed_pitches,
)
from idtap.classes.phrase import Phrase
from idtap.classes.trajectory import Trajectory
from idtap.classes.pitch import Pitch
from idtap.classes.raga import Raga
from idtap.classes.articulation import Articulation
from idtap.classes.group import Group
from idtap.classes.chikari import Chikari
from idtap.classes.meter import Meter
from idtap.classes.assemblage import Assemblage
from idtap.enums import Instrument
from datetime import datetime


# Helper builders

def build_simple_piece():
    raga = Raga()
    t1 = Trajectory({'id': 0, 'pitches': [Pitch()], 'dur_tot': 1})
    t2 = Trajectory({'id': 12, 'pitches': [Pitch()], 'dur_tot': 1})
    p1 = Phrase({'trajectories': [t1], 'dur_tot': 1, 'raga': raga})
    p2 = Phrase({'trajectories': [t2], 'dur_tot': 1, 'raga': raga})
    m1 = Meter([1], start_time=0, tempo=60)
    m2 = Meter([1], start_time=1, tempo=60)
    return Piece({'phrases': [p1, p2], 'raga': raga, 'meters': [m1, m2], 'instrumentation': [Instrument.Sitar]})


def build_simple_piece_full():
    raga = Raga({'fundamental': 240})
    art = {'0.00': Articulation({'stroke_nickname': 'da'})}
    t1 = Trajectory({'num': 0, 'pitches': [Pitch()], 'dur_tot': 0.5, 'articulations': art})
    t2 = Trajectory({'num': 1, 'pitches': [Pitch({'swara': 'r', 'raised': False})], 'dur_tot': 0.5, 'articulations': art})
    group = Group({'trajectories': [t1, t2]})
    p1 = Phrase({'trajectories': [t1, t2], 'raga': raga})
    p1.groups_grid[0].append(group)
    t3 = Trajectory({'num': 0, 'pitches': [Pitch()], 'dur_tot': 1})
    p2 = Phrase({'trajectories': [t3], 'raga': raga})
    piece = Piece({'phrases': [p1, p2], 'raga': raga, 'instrumentation': [Instrument.Sitar]})
    meter = Meter(start_time=0, tempo=60)
    return piece, p1, p2, t1, t2, t3, group, meter


# ---------------------------- tests ----------------------------

def test_realign_and_set_dur_tot():
    piece = build_simple_piece()
    piece.phrases[0].trajectories[0].pitches[0].ratios = [1]
    piece.realign_pitches()
    assert piece.phrases[0].trajectories[0].pitches[0].ratios[0] == piece.raga.stratified_ratios[0]

    piece.set_dur_tot(3)
    assert piece.dur_tot == 3
    assert pytest.approx(piece.dur_array_grid[0][0], rel=1e-6) == 1 / 3
    assert piece.phrases[1].trajectories[0].dur_tot == 2
    assert pytest.approx(piece.phrases[1].start_time, rel=1e-6) == 1


def test_dur_calculations_and_cleanup():
    piece = build_simple_piece()
    piece.phrases[0].trajectories[0].dur_tot = 2
    piece.phrases[0].dur_tot_from_trajectories()
    piece.dur_tot_from_phrases()
    assert piece.dur_tot == 3
    piece.dur_array_from_phrases()
    assert piece.dur_array_grid[0] == pytest.approx([2/3, 1/3])
    piece.phrases[0].dur_tot = None  # type: ignore
    with pytest.raises(Exception):
        piece.dur_array_from_phrases()

    c = init_sec_categorization()
    del c['Improvisation']
    del c['Other']
    del c['Top Level']
    c['Composition Type']['Bandish'] = True
    piece.clean_up_section_categorization(c)
    assert 'Improvisation' in c
    assert 'Other' in c
    assert c['Top Level'] == 'Composition'


def test_piece_serialization_round_trip(tmp_path: Path):
    fixture = Path('idtap/tests/fixtures/serialization_test.json')
    data = json.loads(fixture.read_text())
    piece = Piece.from_json(data)
    json_obj = piece.to_json()
    copy = Piece.from_json(json_obj)
    assert copy.to_json() == json_obj


def test_durations_and_proportions_each_type():
    raga = Raga()
    t1 = Trajectory({'id': 0, 'pitches': [Pitch({'swara': 0})], 'dur_tot': 1})
    t2 = Trajectory({'id': 0, 'pitches': [Pitch({'swara': 1})], 'dur_tot': 2})
    phrase = Phrase({'trajectories': [t1, t2], 'raga': raga})
    piece = Piece({'phrases': [phrase], 'raga': raga, 'instrumentation': [Instrument.Sitar]})

    np1 = t1.pitches[0].numbered_pitch
    np2 = t2.pitches[0].numbered_pitch

    durPN = piece.durations_of_fixed_pitches()
    assert durPN == {np1: 1, np2: 2}

    propPN = piece.proportions_of_fixed_pitches()
    assert pytest.approx(propPN[np1]) == 1/3
    assert pytest.approx(propPN[np2]) == 2/3

    c1 = Pitch.pitch_number_to_chroma(np1)
    c2 = Pitch.pitch_number_to_chroma(np2)
    assert piece.durations_of_fixed_pitches(output_type='chroma') == {c1: 1, c2: 2}
    assert piece.proportions_of_fixed_pitches(output_type='chroma') == {c1: pytest.approx(1/3), c2: pytest.approx(2/3)}

    sd1 = Pitch.chroma_to_scale_degree(c1)[0]
    sd2 = Pitch.chroma_to_scale_degree(c2)[0]
    assert piece.durations_of_fixed_pitches(output_type='scaleDegree') == {sd1: 1, sd2: 2}
    assert piece.proportions_of_fixed_pitches(output_type='scaleDegree') == {sd1: pytest.approx(1/3), sd2: pytest.approx(2/3)}

    sarg1 = Pitch.from_pitch_number(np1).sargam_letter
    sarg2 = Pitch.from_pitch_number(np2).sargam_letter
    assert piece.durations_of_fixed_pitches(output_type='sargamLetter') == {sarg1: 1, sarg2: 2}
    assert piece.proportions_of_fixed_pitches(output_type='sargamLetter') == {sarg1: pytest.approx(1/3), sarg2: pytest.approx(2/3)}


def test_helper_durations_invalid_and_proportional():
    bad_traj = type('T', (), {'durations_of_fixed_pitches': lambda self, *_: 5})()
    with pytest.raises(SyntaxError):
        durations_of_fixed_pitches([bad_traj])

    t1 = Trajectory({'id':0,'pitches':[Pitch({'swara':0})],'dur_tot':1})
    t2 = Trajectory({'id':0,'pitches':[Pitch({'swara':1})],'dur_tot':2})
    np1 = t1.pitches[0].numbered_pitch
    np2 = t2.pitches[0].numbered_pitch
    result = durations_of_fixed_pitches([t1,t2], count_type='proportional')
    assert pytest.approx(result[np1]) == 1/3
    assert pytest.approx(result[np2]) == 2/3
    total = sum(result.values())
    assert pytest.approx(total) == 1


# -------------------------------------------------------
#  New tests mirroring additional Piece features
# -------------------------------------------------------

def build_multi_track_piece():
    raga = Raga({'fundamental': 200})
    tA1 = Trajectory({'num': 0, 'pitches': [Pitch()], 'dur_tot': 0.5})
    tA2 = Trajectory({'num': 1, 'pitches': [Pitch()], 'dur_tot': 0.5})
    group = Group({'trajectories': [tA1, tA2]})
    pA = Phrase({'trajectories': [tA1, tA2], 'raga': raga})
    pA.groups_grid[0].append(group)

    tB1 = Trajectory({'num': 0, 'pitches': [Pitch()], 'dur_tot': 1})
    pB = Phrase({'trajectories': [tB1], 'raga': raga})

    piece = Piece({
        'phraseGrid': [[pA], [pB]],
        'instrumentation': [Instrument.Sitar, Instrument.Vocal_M],
        'raga': raga,
    })

    return piece


def test_optional_fields_round_trip():
    opts = {
        'title': 'my title',
        'dateCreated': datetime(2020, 1, 1),
        'dateModified': datetime(2020, 1, 2),
        'location': 'home',
        '_id': 'id1',
        'audioID': 'a1',
        'audio_DB_ID': 'db1',
        'userID': 'u1',
        'name': 'name',
        'family_name': 'fam',
        'given_name': 'giv',
        'permissions': 'perm',
        'explicitPermissions': {'edit': ['e'], 'view': ['v'], 'publicView': False},
        'soloist': 'solo',
        'soloInstrument': 'sitar',
        'instrumentation': [Instrument.Sitar],
        'phrases': [],
        'raga': Raga(),
    }
    piece = Piece(opts)
    copy = Piece.from_json(piece.to_json())
    assert copy.title == opts['title']
    assert copy.date_created.isoformat() == opts['dateCreated'].isoformat()
    assert copy.date_modified.isoformat() == opts['dateModified'].isoformat()
    assert copy.location == opts['location']
    assert copy._id == opts['_id']
    assert copy.audio_id == opts['audioID']
    assert copy.user_id == opts['userID']
    assert copy.name == opts['name']
    assert copy.family_name == opts['family_name']
    assert copy.given_name == opts['given_name']
    assert copy.permissions == opts['permissions']
    assert copy.explicit_permissions == opts['explicitPermissions']
    assert copy.soloist == opts['soloist']
    assert copy.solo_instrument == opts['soloInstrument']


def test_getters_and_setters_modify_grids():
    raga = Raga()
    t1 = Trajectory({'num': 0, 'pitches': [Pitch()], 'dur_tot': 1})
    p1 = Phrase({'trajectories': [t1], 'raga': raga})
    piece = Piece({'phrases': [p1], 'raga': raga, 'instrumentation': [Instrument.Sitar]})

    t2 = Trajectory({'num': 0, 'pitches': [Pitch()], 'dur_tot': 1})
    p2 = Phrase({'trajectories': [t2], 'raga': raga})
    piece.phrases = [p2]
    assert piece.phrase_grid[0][0] is p2

    piece.durArray = [1]
    assert piece.dur_array_grid[0] == [1]

    piece.section_starts = [0]
    assert piece.section_starts_grid[0] == [0]

    sc = [init_sec_categorization()]
    piece.section_categorization = sc
    assert piece.section_cat_grid[0] is sc


def test_assemblages_getter():
    raga = Raga()
    traj = Trajectory({'num': 0, 'pitches': [Pitch()], 'dur_tot': 1})
    phrase = Phrase({'trajectories': [traj], 'raga': raga})
    asm = Assemblage(Instrument.Sitar, 'a')
    asm.add_phrase(phrase)
    piece = Piece({'phrases': [phrase], 'raga': raga, 'instrumentation': [Instrument.Sitar]})
    piece.assemblage_descriptors = [asm.descriptor]
    aggs = piece.assemblages
    assert len(aggs) == 1
    assert isinstance(aggs[0], Assemblage)
    assert aggs[0].phrases[0] is phrase


def test_update_start_times_recalc():
    raga = Raga()
    p1 = Phrase({'trajectories': [Trajectory({'dur_tot': 1})], 'raga': raga})
    p2 = Phrase({'trajectories': [Trajectory({'dur_tot': 1})], 'raga': raga})
    piece = Piece({'phrases': [p1, p2], 'raga': raga, 'instrumentation': [Instrument.Sitar]})
    piece.dur_array_grid[0] = [0.25, 0.75]
    piece.dur_tot = 2
    piece.update_start_times()
    assert pytest.approx(p2.start_time, rel=1e-6) == piece.dur_starts()[1]
    assert p2.piece_idx == 1


def test_track_specific_helpers():
    piece = build_multi_track_piece()
    assert piece.dur_starts(1) == [0]
    assert piece.traj_start_times(1) == [0]
    assert len(piece.all_pitches(track=1)) == 1
    traj = piece.phrase_grid[1][0].trajectories[0]
    assert piece.most_recent_traj(1.2, 1) is traj


def test_ad_hoc_grid_expansion():
    raga = Raga()
    traj = Trajectory({'dur_tot': 1})
    phrase = Phrase({'trajectories': [traj], 'raga': raga})
    piece = Piece({
        'phraseGrid': [[phrase]],
        'instrumentation': [Instrument.Sitar, Instrument.Vocal_M],
        'raga': raga,
        'adHocSectionCatGrid': [[]],
    })
    assert len(piece.ad_hoc_section_cat_grid) == 2


def test_section_cat_grid_expansion():
    raga = Raga()
    phrase = Phrase({'trajectories': [Trajectory({'dur_tot': 1})], 'raga': raga})
    piece = Piece({
        'phrases': [phrase],
        'raga': raga,
        'instrumentation': [Instrument.Sitar],
        'sectionStarts': [0, 1],
        'sectionCatGrid': [[init_sec_categorization()]],
    })
    assert len(piece.section_cat_grid[0]) == 2


def test_add_trajectory_validation_basic():
    """Test basic input validation for add_trajectory."""
    piece = build_simple_piece()
    
    # Invalid track index
    assert not piece.add_trajectory({'id': 0, 'dur_tot': 0.5}, -1, 0.5)
    assert not piece.add_trajectory({'id': 0, 'dur_tot': 0.5}, 999, 0.5)
    
    # Invalid start time
    assert not piece.add_trajectory({'id': 0, 'dur_tot': 0.5}, 0, -1)
    
    # Invalid trajectory exceeding piece duration
    assert not piece.add_trajectory({'id': 0, 'dur_tot': 10}, 0, 0.5)


def test_add_trajectory_replace_entire_silent():
    """Test replacing an entire silent trajectory."""
    raga = Raga({'fundamental': 240})
    silent_traj = Trajectory({'id': 12, 'dur_tot': 2.0, 'fundID12': 240})
    phrase = Phrase({'trajectories': [silent_traj], 'raga': raga})
    piece = Piece({'phrases': [phrase], 'raga': raga, 'instrumentation': [Instrument.Sitar]})
    
    # Create new trajectory to add 
    new_traj_data = {
        'id': 0,
        'dur_tot': 2.0,
        'pitches': [Pitch({'swara': 's', 'fundamental': 240})]
    }
    
    # Add trajectory that replaces entire silent trajectory
    success = piece.add_trajectory(new_traj_data, 0, 0.0)
    assert success
    
    # Verify replacement
    phrase = piece.phrase_grid[0][0]
    assert len(phrase.trajectories) == 1
    assert phrase.trajectories[0].id == 0
    assert phrase.trajectories[0].dur_tot == 2.0


def test_add_trajectory_replace_left_side():
    """Test replacing left side of silent trajectory."""
    raga = Raga({'fundamental': 240})
    silent_traj = Trajectory({'id': 12, 'dur_tot': 3.0, 'fundID12': 240})
    phrase = Phrase({'trajectories': [silent_traj], 'raga': raga})
    piece = Piece({'phrases': [phrase], 'raga': raga, 'instrumentation': [Instrument.Sitar]})
    
    new_traj_data = {
        'id': 0,
        'dur_tot': 1.0,
        'pitches': [Pitch({'swara': 's', 'fundamental': 240})]
    }
    
    # Add trajectory at beginning of silent trajectory
    success = piece.add_trajectory(new_traj_data, 0, 0.0)
    assert success
    
    # Verify replacement
    phrase = piece.phrase_grid[0][0]
    assert len(phrase.trajectories) == 2
    assert phrase.trajectories[0].id == 0
    assert phrase.trajectories[0].dur_tot == 1.0
    assert phrase.trajectories[1].id == 12
    assert phrase.trajectories[1].dur_tot == 2.0


def test_add_trajectory_replace_right_side():
    """Test replacing right side of silent trajectory."""
    raga = Raga({'fundamental': 240})
    silent_traj = Trajectory({'id': 12, 'dur_tot': 3.0, 'fundID12': 240})
    phrase = Phrase({'trajectories': [silent_traj], 'raga': raga})
    piece = Piece({'phrases': [phrase], 'raga': raga, 'instrumentation': [Instrument.Sitar]})
    
    new_traj_data = {
        'id': 0,
        'dur_tot': 1.0,
        'pitches': [Pitch({'swara': 's', 'fundamental': 240})]
    }
    
    # Add trajectory at end of silent trajectory
    success = piece.add_trajectory(new_traj_data, 0, 2.0)
    assert success
    
    # Verify replacement
    phrase = piece.phrase_grid[0][0]
    assert len(phrase.trajectories) == 2
    assert phrase.trajectories[0].id == 12
    assert phrase.trajectories[0].dur_tot == 2.0
    assert phrase.trajectories[1].id == 0
    assert phrase.trajectories[1].dur_tot == 1.0


def test_add_trajectory_replace_internal():
    """Test replacing internal portion of silent trajectory."""
    raga = Raga({'fundamental': 240})
    silent_traj = Trajectory({'id': 12, 'dur_tot': 5.0, 'fundID12': 240})
    phrase = Phrase({'trajectories': [silent_traj], 'raga': raga})
    piece = Piece({'phrases': [phrase], 'raga': raga, 'instrumentation': [Instrument.Sitar]})
    
    new_traj_data = {
        'id': 0,
        'dur_tot': 2.0,
        'pitches': [Pitch({'swara': 's', 'fundamental': 240})]
    }
    
    # Add trajectory in middle of silent trajectory
    success = piece.add_trajectory(new_traj_data, 0, 1.5)
    assert success
    
    # Verify replacement - should create 3 trajectories: first silent, new, last silent
    phrase = piece.phrase_grid[0][0]
    assert len(phrase.trajectories) == 3
    assert phrase.trajectories[0].id == 12
    assert phrase.trajectories[0].dur_tot == 1.5
    assert phrase.trajectories[1].id == 0
    assert phrase.trajectories[1].dur_tot == 2.0
    assert phrase.trajectories[2].id == 12
    assert phrase.trajectories[2].dur_tot == 1.5


def test_add_trajectory_with_existing_trajectory_object():
    """Test adding pre-instantiated Trajectory object with different raga."""
    piece_raga = Raga({'fundamental': 240})
    different_raga = Raga({'fundamental': 220})
    
    silent_traj = Trajectory({'id': 12, 'dur_tot': 2.0, 'fundID12': 240})
    phrase = Phrase({'trajectories': [silent_traj], 'raga': piece_raga})
    piece = Piece({'phrases': [phrase], 'raga': piece_raga, 'instrumentation': [Instrument.Sitar]})
    
    # Create trajectory with different raga
    wrong_pitch = Pitch({'swara': 's', 'fundamental': 220, 'raga': different_raga})
    existing_traj = Trajectory({
        'id': 0,
        'dur_tot': 1.0,
        'pitches': [wrong_pitch],
        'instrumentation': Instrument.Vocal_M  # Also wrong instrumentation
    })
    
    # Add the pre-existing trajectory
    success = piece.add_trajectory(existing_traj, 0, 0.0)
    assert success
    
    # Verify the trajectory was recreated with piece's context
    added_traj = piece.phrase_grid[0][0].trajectories[0]
    assert added_traj.instrumentation == Instrument.Sitar  # Should match piece instrumentation
    # Verify pitches were updated with piece's raga fundamental
    for pitch in added_traj.pitches:
        assert pitch.fundamental == 240  # Should match piece's raga


def test_add_trajectory_validation_requirements():
    """Test the 5 validation requirements."""
    raga = Raga({'fundamental': 240})
    
    # Create piece with non-silent trajectory
    non_silent_traj = Trajectory({'id': 0, 'dur_tot': 2.0})
    phrase = Phrase({'trajectories': [non_silent_traj], 'raga': raga})
    piece = Piece({'phrases': [phrase], 'raga': raga, 'instrumentation': [Instrument.Sitar]})
    
    new_traj_data = {'id': 1, 'dur_tot': 1.0}
    
    # Should fail - target trajectory is not silent (id != 12)
    assert not piece.add_trajectory(new_traj_data, 0, 0.0)
    
    # Create piece with silent trajectory for remaining tests
    silent_traj = Trajectory({'id': 12, 'dur_tot': 2.0, 'fundID12': 240})
    phrase2 = Phrase({'trajectories': [silent_traj], 'raga': raga})
    piece2 = Piece({'phrases': [phrase2], 'raga': raga, 'instrumentation': [Instrument.Sitar]})
    
    # Should fail - trajectory extends beyond piece duration
    long_traj = {'id': 0, 'dur_tot': 5.0}
    assert not piece2.add_trajectory(long_traj, 0, 0.0)
    
    # Should pass - valid trajectory within silent trajectory
    valid_traj = {'id': 0, 'dur_tot': 1.0}
    assert piece2.add_trajectory(valid_traj, 0, 0.5)


def test_add_trajectory_multi_track():
    """Test adding trajectories to different instrument tracks."""
    raga = Raga({'fundamental': 240})
    
    # Create piece with two tracks
    silent1 = Trajectory({'id': 12, 'dur_tot': 2.0, 'fundID12': 240})
    silent2 = Trajectory({'id': 12, 'dur_tot': 2.0, 'fundID12': 240})
    phrase1 = Phrase({'trajectories': [silent1], 'raga': raga})
    phrase2 = Phrase({'trajectories': [silent2], 'raga': raga})
    
    piece = Piece({
        'phraseGrid': [[phrase1], [phrase2]], 
        'raga': raga, 
        'instrumentation': [Instrument.Sitar, Instrument.Vocal_M]
    })
    
    # Add trajectory to first track
    traj1_data = {'id': 0, 'dur_tot': 1.0}
    success1 = piece.add_trajectory(traj1_data, 0, 0.0)
    assert success1
    
    # Add trajectory to second track
    traj2_data = {'id': 1, 'dur_tot': 1.0}  
    success2 = piece.add_trajectory(traj2_data, 1, 0.5)
    assert success2
    
    # Verify both tracks were modified correctly
    assert piece.phrase_grid[0][0].trajectories[0].id == 0
    assert piece.phrase_grid[0][0].trajectories[0].instrumentation == Instrument.Sitar
    
    assert piece.phrase_grid[1][0].trajectories[0].id == 12
    assert piece.phrase_grid[1][0].trajectories[1].id == 1
    assert piece.phrase_grid[1][0].trajectories[1].instrumentation == Instrument.Vocal_M


def test_all_pitches_no_repetition():
    raga = Raga()
    p1 = Pitch({'swara': 'sa'})
    t1 = Trajectory({'num': 0, 'phrase_idx': 0, 'pitches': [p1]})
    t2 = Trajectory({'num': 1, 'phrase_idx': 0, 'pitches': [Pitch({'swara': 'sa'})]})
    t3 = Trajectory({'num': 2, 'phrase_idx': 0, 'pitches': [Pitch({'swara': 're'})]})
    phrase = Phrase({'trajectories': [t1, t2, t3], 'raga': raga})
    piece = Piece({'phrases': [phrase], 'raga': raga, 'instrumentation': [Instrument.Sitar]})
    assert len(piece.all_pitches()) == 3
    assert piece.all_pitches(repetition=False) == [p1, t3.pitches[0]]


def test_all_pitches_pitch_number_option():
    piece = build_simple_piece()
    nums = piece.all_pitches(pitch_number=True)
    assert all(isinstance(n, (int, float)) for n in nums)
    assert len(nums) > 0


def test_update_fundamental_and_chikari_freqs():
    piece, p1, *_ = build_simple_piece_full()
    base = piece.raga.fundamental
    assert piece.chikari_freqs(0) == [base * 2, base * 4]
    piece.update_fundamental(300)
    assert piece.raga.fundamental == 300
    assert p1.trajectories[0].pitches[0].fundamental == 300
    piece.put_raga_in_phrase()
    assert p1.raga is piece.raga
    chikari = Chikari({'fundamental': piece.raga.fundamental})
    p1.chikaris['0.00'] = chikari
    assert piece.chikari_freqs(0) == [c.frequency for c in chikari.pitches[:2]]
    nums = [p.numbered_pitch for p in piece.all_pitches()]
    assert piece.highest_pitch_number == max(nums)
    assert piece.lowest_pitch_number == min(nums)


def test_dur_starts_errors():
    piece = build_simple_piece()
    saved = piece.dur_array_grid
    piece.dur_array_grid = None
    with pytest.raises(Exception):
        piece.dur_starts()
    piece.dur_array_grid = saved
    piece.dur_tot = None
    with pytest.raises(Exception):
        piece.dur_starts()


def test_excerpt_range_and_assemblage_serialization():
    p = Phrase({'trajectories': [Trajectory()]})
    piece = Piece({'phrases': [p], 'raga': Raga()})
    piece.excerpt_range = {'start': 1, 'end': 2}
    asm = Assemblage(Instrument.Sitar, 'a')
    asm.add_phrase(p)
    piece.assemblage_descriptors = [asm.descriptor]
    copy = Piece.from_json(piece.to_json())
    assert copy.excerpt_range == piece.excerpt_range
    assert copy.assemblage_descriptors == piece.assemblage_descriptors


def test_dur_tot_and_permissions_persist():
    perms = {'edit': ['a'], 'view': ['b'], 'publicView': False}
    piece = Piece({'phrases': [], 'durTot': 5, 'instrumentation': [Instrument.Sitar], 'raga': Raga(), 'explicitPermissions': perms})
    # durTot is recalculated from phrases and becomes 0
    assert piece.dur_tot == 0
    assert piece.dur_array == []
    assert piece.explicit_permissions == perms
    assert piece.assemblage_descriptors == []


def test_clean_up_section_cat_defaults_multi_inst():
    sc = [init_sec_categorization()]
    del sc[0]['Improvisation']
    del sc[0]['Other']
    del sc[0]['Top Level']
    piece = Piece({'sectionStarts': [0], 'sectionCategorization': sc, 'instrumentation': [Instrument.Sitar, Instrument.Vocal_M], 'raga': Raga(), 'phrases': []})
    assert 'Improvisation' in sc[0]
    assert 'Other' in sc[0]
    assert 'Top Level' in sc[0]
    assert len(piece.ad_hoc_section_cat_grid) == 2
    assert piece.dur_tot == 0


# ----------------------------------------------------------------------
# Additional tests ported from the TypeScript suite
# ----------------------------------------------------------------------

def build_vocal_piece():
    raga = Raga({'fundamental': 240})
    art = {'0.00': Articulation({'stroke_nickname': 'da'})}
    t1 = Trajectory({'num': 0, 'pitches': [Pitch()], 'dur_tot': 0.5, 'articulations': art})
    t1.add_consonant('ka')
    t1.update_vowel('a')
    t1.add_consonant('ga', start=False)
    t2 = Trajectory({'num': 1, 'pitches': [Pitch({'swara': 'r', 'raised': False})], 'dur_tot': 0.5, 'articulations': art})
    t2.update_vowel('i')
    p1 = Phrase({'trajectories': [t1, t2], 'raga': raga})
    p1.chikaris['0.25'] = Chikari({})
    p2 = Phrase({'trajectories': [Trajectory({'num': 0, 'pitches': [Pitch()], 'dur_tot': 1})], 'raga': raga})
    piece = Piece({'phrases': [p1, p2], 'raga': raga, 'instrumentation': [Instrument.Vocal_M], 'sectionStarts': [0,1]})
    meter = Meter(start_time=0, tempo=60)
    piece.add_meter(meter)
    return piece, meter


def test_track_from_traj_uid_error():
    piece, *_ = build_simple_piece_full()
    with pytest.raises(ValueError):
        piece.track_from_traj_uid('missing')


def test_p_idx_from_group_across_phrases():
    raga = Raga()
    t1 = Trajectory({'num': 0, 'pitches': [Pitch()], 'dur_tot': 0.5})
    t2 = Trajectory({'num': 1, 'pitches': [Pitch()], 'dur_tot': 0.5})
    g1 = Group({'trajectories': [t1, t2]})
    p1 = Phrase({'trajectories': [t1, t2], 'raga': raga})
    p1.groups_grid[0].append(g1)
    t3 = Trajectory({'num': 0, 'pitches': [Pitch()], 'dur_tot': 0.5})
    t4 = Trajectory({'num': 1, 'pitches': [Pitch()], 'dur_tot': 0.5})
    g2 = Group({'trajectories': [t3, t4]})
    p2 = Phrase({'trajectories': [t3, t4], 'raga': raga})
    p2.groups_grid[0].append(g2)
    piece = Piece({'phrases': [p1, p2], 'raga': raga, 'instrumentation': [Instrument.Sitar]})
    assert piece.p_idx_from_group(g1) == 0
    assert piece.p_idx_from_group(g2) == 1


def test_most_recent_traj_and_chikari_freqs():
    piece, _ = build_vocal_piece()
    first_traj = piece.phrase_grid[0][0].trajectories[0]
    chikari = piece.phrase_grid[0][0].chikaris['0.25']
    assert piece.most_recent_traj(0.6, 0) is first_traj
    assert piece.chikari_freqs(0) == [c.frequency for c in chikari.pitches[:2]]


def test_add_meter_overlap_and_remove():
    raga = Raga()
    traj = Trajectory({'num': 0, 'pitches': [Pitch()], 'dur_tot': 1})
    phrase = Phrase({'trajectories': [traj], 'raga': raga})
    piece = Piece({'phrases': [phrase], 'raga': raga, 'instrumentation': [Instrument.Sitar]})
    m1 = Meter(start_time=0, tempo=60)
    m2 = Meter(start_time=5, tempo=60)
    piece.add_meter(m1)
    piece.add_meter(m2)
    with pytest.raises(ValueError):
        piece.add_meter(Meter(start_time=3, tempo=60))
    piece.remove_meter(m1)
    assert piece.meters == [m2]


def test_comp_section_tempo_fallback():
    piece = build_simple_piece()
    c = init_sec_categorization()
    del c['Comp.-section/Tempo']
    c['Composition-section/Tempo'] = {'Madhya': True}
    del c['Top Level']
    piece.clean_up_section_categorization(c)
    assert c['Comp.-section/Tempo']['Madhya']
    assert 'Composition-section/Tempo' not in c
    assert c['Top Level'] == 'Composition'


@pytest.mark.parametrize('modify,expected', [
    (lambda c: c['Pre-Chiz Alap'].__setitem__('Pre-Chiz Alap', True), 'Pre-Chiz Alap'),
    (lambda c: c['Alap'].__setitem__('Alap', True), 'Alap'),
    (lambda c: c['Composition Type'].__setitem__('Bandish', True), 'Composition'),
    (lambda c: c['Comp.-section/Tempo'].__setitem__('Vilambit', True), 'Composition'),
    (lambda c: c['Improvisation'].__setitem__('Improvisation', True), 'Improvisation'),
    (lambda c: c['Other'].__setitem__('Other', True), 'Other'),
    (lambda c: None, 'None'),
])
def test_top_level_classification(modify, expected):
    piece = build_simple_piece()
    c = init_sec_categorization()
    del c['Top Level']
    modify(c)
    piece.clean_up_section_categorization(c)
    assert c['Top Level'] == expected


def test_all_display_vowels_non_vocal():
    raga = Raga()
    traj = Trajectory({'num': 0, 'pitches': [Pitch()], 'dur_tot': 1})
    phrase = Phrase({'trajectories': [traj], 'raga': raga})
    piece = Piece({'phrases': [phrase], 'raga': raga, 'instrumentation': [Instrument.Sitar]})
    with pytest.raises(Exception, match='instrumentation is not vocal'):
        piece.all_display_vowels()


def test_all_pitches_number_error():
    raga = Raga()
    traj = Trajectory({'num': 0, 'pitches': [Pitch()], 'dur_tot': 1})
    traj.pitches.append(0)  # type: ignore
    phrase = Phrase({'trajectories': [traj], 'raga': raga})
    piece = Piece({'phrases': [phrase], 'raga': raga, 'instrumentation': [Instrument.Sitar]})
    with pytest.raises(ValueError):
        piece.all_pitches(repetition=False)


def test_traj_from_time_after_last():
    piece = build_simple_piece()
    after = (piece.dur_tot or 0) + 1
    assert piece.traj_from_time(after, 0) is None


def test_traj_from_uid_error():
    piece = build_simple_piece()
    with pytest.raises(ValueError):
        piece.traj_from_uid('missing', 0)


def test_track_from_traj_error():
    piece, *_ = build_simple_piece_full()
    missing = Trajectory({'num': 99, 'pitches': [Pitch()], 'dur_tot': 1})
    with pytest.raises(ValueError):
        piece.track_from_traj(missing)


def test_phrase_from_uid_and_track_from_phrase_uid_error():
    piece, *_ = build_simple_piece_full()
    with pytest.raises(ValueError):
        piece.phrase_from_uid('missing')
    with pytest.raises(ValueError):
        piece.track_from_phrase_uid('missing')


def test_add_meter_enclosing_rejects():
    raga = Raga()
    traj = Trajectory({'num': 0, 'pitches': [Pitch()], 'dur_tot': 1})
    phrase = Phrase({'trajectories': [traj], 'raga': raga})
    piece = Piece({'phrases': [phrase], 'raga': raga, 'instrumentation': [Instrument.Sitar]})
    base = Meter(start_time=0, tempo=60)
    piece.add_meter(base)
    with pytest.raises(ValueError):
        piece.add_meter(Meter(start_time=-1, hierarchy=[8], tempo=60))
    later = Meter(start_time=5, tempo=60)
    piece.add_meter(later)
    assert piece.meters == [base, later]


def test_dur_array_branch_empty_section_cat_grid():
    raga = Raga()
    traj = Trajectory({'num': 0, 'pitches': [Pitch()], 'dur_tot': 1})
    phrase = Phrase({'trajectories': [traj], 'raga': raga})
    piece = Piece({'phrases': [phrase], 'durTot': 1, 'durArray': [1], 'instrumentation': [Instrument.Sitar], 'raga': raga, 'sectionStarts': [0], 'sectionCatGrid': []})
    assert piece.dur_array_grid == [[1]]
    assert len(piece.section_cat_grid) == 1
    assert len(piece.section_cat_grid[0]) == len(piece.section_starts_grid[0])


def test_dur_tot_from_phrases_adds_silent_phrase():
    raga = Raga()
    t1 = Trajectory({'dur_tot': 1})
    p1 = Phrase({'trajectories': [t1], 'raga': raga})
    piece = Piece({'phraseGrid': [[p1], []], 'instrumentation': [Instrument.Sitar, Instrument.Sitar], 'raga': raga})
    piece.dur_tot_from_phrases()
    assert len(piece.phrase_grid[1]) == 1
    silent = piece.phrase_grid[1][0].trajectories[0]
    assert silent.id == 12
    assert pytest.approx(silent.dur_tot) == 1


def test_dur_array_from_phrases_removes_nan():
    raga = Raga()
    piece = Piece({'raga': raga, 'instrumentation': [Instrument.Sitar]})
    good = Trajectory({'dur_tot': 1})
    bad = Trajectory({'dur_tot': float('nan')})
    phrase = Phrase({'trajectories': [good, bad], 'raga': raga})
    phrase.dur_tot_from_trajectories()
    piece.phrase_grid[0].append(phrase)
    assert math.isnan(phrase.dur_tot)
    piece.dur_array_from_phrases()
    assert len(phrase.trajectories) == 1
    assert pytest.approx(phrase.dur_tot) == 1


def test_display_helpers_and_meters():
    piece = build_simple_piece()

    divs = piece.all_phrase_divs()
    assert len(divs) == 1
    assert pytest.approx(divs[0]['time'], rel=1e-6) == 1

    div_chunks = piece.chunked_phrase_divs(0, 1)
    assert len(div_chunks) == 2
    assert len(div_chunks[0]) == 0
    assert len(div_chunks[1]) == 1

    sargam = piece.all_display_sargam()
    assert sargam[0]['sargam'] is not None
    sargam_chunks = piece.chunked_display_sargam(0, 1)
    assert len(sargam_chunks) == 2
    assert sum(len(c) for c in sargam_chunks) == len(sargam)

    meter_chunks = piece.chunked_meters(1)
    assert len(meter_chunks) == 2
    assert meter_chunks[0][0].start_time == 0
    assert meter_chunks[1][0].start_time == 1

    with pytest.raises(ValueError):
        piece.add_meter(Meter([1], tempo=60, start_time=0.5))


def test_piece_method_helpers():
    piece, p1, p2, t1, t2, t3, group, meter = build_simple_piece_full()

    chunks = piece.chunked_trajs(0, 1)
    assert len(chunks[0]) == 2
    assert len(chunks[1]) == 1

    chunks_small = piece.chunked_trajs(0, 0.75)
    assert len(chunks_small) == 3
    assert len(chunks_small[0]) == 2
    assert len(chunks_small[1]) == 2
    assert len(chunks_small[2]) == 1

    bols = piece.all_display_bols()
    assert len(bols) > 0
    assert len(piece.chunked_display_bols(0, 1)[0]) == len([b for b in bols if b['time'] < 1])

    piece.add_meter(meter)
    pid = meter.all_pulses[0].unique_id
    assert piece.pulse_from_id(pid) == meter.all_pulses[0]


def test_vocal_display_helpers():
    piece, meter = build_vocal_piece()

    assert len(piece.sections) == 2
    assert len(piece.sections_grid[0]) == 2

    vowels = piece.all_display_vowels()
    assert len(vowels) > 0
    assert len(piece.chunked_display_vowels(0, 1)[0]) == len([v for v in vowels if v['time'] < 1])

    cons = piece.all_display_ending_consonants()
    assert len(cons) > 0
    assert len(piece.chunked_display_consonants(0, 1)[0]) == len([c for c in cons if c['time'] < 1])

    chiks = piece.all_display_chikaris()
    assert len(chiks) > 0
    assert len(piece.chunked_display_chikaris(0, 1)[0]) == len([c for c in chiks if c['time'] < 1])

    pid = meter.all_pulses[0].unique_id
    assert piece.pulse_from_id(pid) == meter.all_pulses[0]


def test_meters_and_instrumentation_update_duration_arrays():
    piece = build_simple_piece()
    original = json.dumps(piece.dur_array_grid)

    m = Meter([1], start_time=2.1, tempo=60)
    piece.add_meter(m)
    piece.remove_meter(m)
    assert json.dumps(piece.dur_array_grid) == original

    piece.instrumentation.append(Instrument.Vocal_M)
    new_phrase = Phrase({
        'trajectories': [Trajectory({'num': 0, 'pitches': [Pitch()], 'dur_tot': 2})],
        'raga': piece.raga,
    })
    piece.phrase_grid.append([new_phrase])
    piece.dur_array_grid.append([])
    piece.section_starts_grid.append([0])
    piece.section_cat_grid.append([init_sec_categorization() for _ in piece.section_cat_grid[0]])
    piece.ad_hoc_section_cat_grid.append([[] for _ in piece.ad_hoc_section_cat_grid[0]])
    piece.dur_array_from_phrases()
    assert len(piece.dur_array_grid) == 2

    piece.instrumentation.pop()
    piece.phrase_grid.pop()
    piece.dur_array_grid.pop()
    piece.section_starts_grid.pop()
    piece.section_cat_grid.pop()
    piece.ad_hoc_section_cat_grid.pop()
    piece.dur_array_from_phrases()
    assert json.dumps(piece.dur_array_grid) == original


def test_piece_serialization_reconnects_groups_and_fixes_slide():
    raga = Raga()
    artics = {'0.00': Articulation({'name': 'slide'})}
    t1 = Trajectory({'num': 0, 'pitches': [Pitch()], 'dur_tot': 0.5, 'articulations': artics})
    t2 = Trajectory({'num': 1, 'pitches': [Pitch()], 'dur_tot': 0.5})
    phrase = Phrase({'trajectories': [t1, t2], 'raga': raga})
    group = Group({'trajectories': [t1, t2]})
    phrase.groups_grid[0].append(group)

    piece = Piece({'phrases': [phrase], 'raga': raga, 'instrumentation': [Instrument.Sitar]})
    clone = Piece.from_json(piece.to_json())

    reconstructed = clone.phrases[0].groups_grid[0][0]
    assert isinstance(reconstructed, Group)
    assert reconstructed.trajectories[0] is clone.phrases[0].trajectory_grid[0][0]
    assert reconstructed.trajectories[1] is clone.phrases[0].trajectory_grid[0][1]
    assert clone.phrases[0].trajectory_grid[0][0].articulations['0.00'].name == 'pluck'
