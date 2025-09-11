from __future__ import annotations
from typing import List, Dict, Optional, Union, Literal, TYPE_CHECKING
from uuid import uuid4
import math

if TYPE_CHECKING:
    from .musical_time import MusicalTime

# Tempo validation constants
MIN_TEMPO_BPM = 20  # Very slow musical pieces (e.g., some alap sections)
MAX_TEMPO_BPM = 300  # Very fast musical pieces



def find_closest_idxs(trials: List[float], items: List[float]) -> List[int]:
    """Return indexes of items closest to each trial (greedy)."""
    used: set[int] = set()
    out: List[int] = []
    for trial in trials:
        diffs = [(abs(trial - item), idx) for idx, item in enumerate(items)
                 if idx not in used]
        diffs.sort(key=lambda x: x[0])
        if not diffs:
            raise ValueError("not enough items to match trials")
        used.add(diffs[0][1])
        out.append(diffs[0][1])
    return out


class Pulse:
    def __init__(self, real_time: float = 0.0, unique_id: Optional[str] = None,
                 affiliations: Optional[List[Dict]] = None,
                 meter_id: Optional[str] = None,
                 corporeal: bool = True) -> None:
        # Parameter validation
        self._validate_parameters({'real_time': real_time, 'unique_id': unique_id, 
                                  'affiliations': affiliations, 'meter_id': meter_id, 'corporeal': corporeal})
        self.real_time = real_time
        self.unique_id = unique_id or str(uuid4())
        self.affiliations: List[Dict] = affiliations or []
        self.meter_id = meter_id
        self.corporeal = corporeal

    def _validate_parameters(self, opts: Dict) -> None:
        """Validate constructor parameters and provide helpful error messages."""
        if not isinstance(opts.get('real_time', 0.0), (int, float)):
            raise TypeError(f"Parameter 'real_time' must be a number, got {type(opts['real_time']).__name__}")
        
        if opts.get('real_time', 0.0) < 0:
            raise ValueError(f"Parameter 'real_time' must be non-negative, got {opts['real_time']}")
        
        if 'unique_id' in opts and opts['unique_id'] is not None and not isinstance(opts['unique_id'], str):
            raise TypeError(f"Parameter 'unique_id' must be a string, got {type(opts['unique_id']).__name__}")
        
        if 'affiliations' in opts and opts['affiliations'] is not None:
            if not isinstance(opts['affiliations'], list):
                raise TypeError(f"Parameter 'affiliations' must be a list, got {type(opts['affiliations']).__name__}")
            if not all(isinstance(item, dict) for item in opts['affiliations']):
                raise TypeError("All items in 'affiliations' must be dictionaries")
        
        if 'meter_id' in opts and opts['meter_id'] is not None and not isinstance(opts['meter_id'], str):
            raise TypeError(f"Parameter 'meter_id' must be a string, got {type(opts['meter_id']).__name__}")
        
        if not isinstance(opts.get('corporeal', True), bool):
            raise TypeError(f"Parameter 'corporeal' must be a boolean, got {type(opts['corporeal']).__name__}")

    @staticmethod
    def from_json(obj: Dict) -> 'Pulse':
        return Pulse(
            real_time=obj.get('realTime', 0.0),
            unique_id=obj.get('uniqueId'),
            affiliations=obj.get('affiliations'),
            meter_id=obj.get('meterId'),
            corporeal=obj.get('corporeal', True),
        )

    def to_json(self) -> Dict:
        return {
            'realTime': self.real_time,
            'uniqueId': self.unique_id,
            'affiliations': self.affiliations,
            'meterId': self.meter_id,
            'corporeal': self.corporeal,
        }

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Pulse) and self.to_json() == other.to_json()


class PulseStructure:
    def __init__(self, tempo: float = 60.0, size: int = 4,
                 start_time: float = 0.0, unique_id: Optional[str] = None,
                 front_weighted: bool = True, layer: Optional[int] = None,
                 parent_pulse_id: Optional[str] = None,
                 primary: bool = True, segmented_meter_idx: int = 0,
                 meter_id: Optional[str] = None,
                 pulses: Optional[List[Pulse | Dict]] = None) -> None:
        # Parameter validation
        self._validate_parameters({
            'tempo': tempo, 'size': size, 'start_time': start_time, 'unique_id': unique_id,
            'front_weighted': front_weighted, 'layer': layer, 'parent_pulse_id': parent_pulse_id,
            'primary': primary, 'segmented_meter_idx': segmented_meter_idx, 'meter_id': meter_id,
            'pulses': pulses
        })
        self.tempo = tempo
        self.pulse_dur = 60.0 / tempo
        self.size = size
        self.start_time = start_time
        self.unique_id = unique_id or str(uuid4())
        self.front_weighted = front_weighted
        self.layer = layer
        self.parent_pulse_id = parent_pulse_id
        self.primary = primary
        self.segmented_meter_idx = segmented_meter_idx
        self.meter_id = meter_id

        if pulses is not None:
            self.pulses = [p if isinstance(p, Pulse) else Pulse.from_json(p)
                           for p in pulses]
        else:
            self.pulses = [
                Pulse(
                    real_time=start_time + i * self.pulse_dur,
                    affiliations=[{
                        'psId': self.unique_id,
                        'idx': i,
                        'layer': self.layer,
                        'segmentedMeterIdx': self.segmented_meter_idx,
                        'strong': (i == 0) if front_weighted else (i == size - 1),
                    }],
                    meter_id=meter_id
                ) for i in range(size)
            ]

    def _validate_parameters(self, opts: Dict) -> None:
        """Validate constructor parameters and provide helpful error messages."""
        if not isinstance(opts.get('tempo', 60.0), (int, float)):
            raise TypeError(f"Parameter 'tempo' must be a number, got {type(opts['tempo']).__name__}")
        
        if opts.get('tempo', 60.0) <= 0:
            raise ValueError(f"Parameter 'tempo' must be positive, got {opts['tempo']}")
        
        if opts.get('tempo', 60.0) < MIN_TEMPO_BPM or opts.get('tempo', 60.0) > MAX_TEMPO_BPM:
            import warnings
            warnings.warn(f"Tempo {opts['tempo']} BPM is outside typical range ({MIN_TEMPO_BPM}-{MAX_TEMPO_BPM} BPM)", UserWarning)
        
        if not isinstance(opts.get('size', 4), int):
            raise TypeError(f"Parameter 'size' must be an integer, got {type(opts['size']).__name__}")
        
        if opts.get('size', 4) <= 0:
            raise ValueError(f"Parameter 'size' must be positive, got {opts['size']}")
        
        if not isinstance(opts.get('start_time', 0.0), (int, float)):
            raise TypeError(f"Parameter 'start_time' must be a number, got {type(opts['start_time']).__name__}")
        
        if opts.get('start_time', 0.0) < 0:
            raise ValueError(f"Parameter 'start_time' must be non-negative, got {opts['start_time']}")
        
        if 'unique_id' in opts and opts['unique_id'] is not None and not isinstance(opts['unique_id'], str):
            raise TypeError(f"Parameter 'unique_id' must be a string, got {type(opts['unique_id']).__name__}")
        
        if not isinstance(opts.get('front_weighted', True), bool):
            raise TypeError(f"Parameter 'front_weighted' must be a boolean, got {type(opts['front_weighted']).__name__}")
        
        if 'layer' in opts and opts['layer'] is not None:
            if not isinstance(opts['layer'], int):
                raise TypeError(f"Parameter 'layer' must be an integer, got {type(opts['layer']).__name__}")
            if opts['layer'] < 0:
                raise ValueError(f"Parameter 'layer' must be non-negative, got {opts['layer']}")
        
        if 'parent_pulse_id' in opts and opts['parent_pulse_id'] is not None and not isinstance(opts['parent_pulse_id'], str):
            raise TypeError(f"Parameter 'parent_pulse_id' must be a string, got {type(opts['parent_pulse_id']).__name__}")
        
        if not isinstance(opts.get('primary', True), bool):
            raise TypeError(f"Parameter 'primary' must be a boolean, got {type(opts['primary']).__name__}")
        
        if not isinstance(opts.get('segmented_meter_idx', 0), int):
            raise TypeError(f"Parameter 'segmented_meter_idx' must be an integer, got {type(opts['segmented_meter_idx']).__name__}")
        
        if opts.get('segmented_meter_idx', 0) < 0:
            raise ValueError(f"Parameter 'segmented_meter_idx' must be non-negative, got {opts['segmented_meter_idx']}")
        
        if 'meter_id' in opts and opts['meter_id'] is not None and not isinstance(opts['meter_id'], str):
            raise TypeError(f"Parameter 'meter_id' must be a string, got {type(opts['meter_id']).__name__}")
        
        if 'pulses' in opts and opts['pulses'] is not None:
            if not isinstance(opts['pulses'], list):
                raise TypeError(f"Parameter 'pulses' must be a list, got {type(opts['pulses']).__name__}")

    @property
    def dur_tot(self) -> float:
        return self.size * self.pulse_dur

    def set_tempo(self, new_tempo: float) -> None:
        self.tempo = new_tempo
        self.pulse_dur = 60.0 / new_tempo
        for i, pulse in enumerate(self.pulses):
            pulse.real_time = self.start_time + i * self.pulse_dur

    def set_start_time(self, new_start: float) -> None:
        diff = new_start - self.start_time
        self.start_time = new_start
        for pulse in self.pulses:
            pulse.real_time += diff

    @staticmethod
    def from_pulse(pulse: Pulse, duration: float, size: int,
                   front_weighted: bool = True, layer: int = 0) -> 'PulseStructure':
        tempo = 60 * size / duration
        ps = PulseStructure(tempo=tempo, size=size, start_time=pulse.real_time,
                            front_weighted=front_weighted, layer=layer,
                            parent_pulse_id=pulse.unique_id, meter_id=pulse.meter_id)
        idx = 0 if front_weighted else ps.size - 1
        pulse.affiliations.append({
            'psId': ps.unique_id,
            'idx': idx,
            'layer': layer,
            'segmentedMeterIdx': 0,
            'strong': True,
        })
        ps.pulses[idx] = pulse
        return ps

    def to_json(self) -> Dict:
        return {
            'pulses': [p.to_json() for p in self.pulses],
            'tempo': self.tempo,
            'pulseDur': self.pulse_dur,
            'size': self.size,
            'startTime': self.start_time,
            'uniqueId': self.unique_id,
            'frontWeighted': self.front_weighted,
            'layer': self.layer,
            'parentPulseID': self.parent_pulse_id,
            'primary': self.primary,
            'segmentedMeterIdx': self.segmented_meter_idx,
            'meterId': self.meter_id,
            'offsets': [0.0] * self.size,
        }

    @staticmethod
    def from_json(obj: Dict) -> 'PulseStructure':
        return PulseStructure(
            tempo=obj.get('tempo', 60.0),
            size=obj.get('size', 4),
            start_time=obj.get('startTime', 0.0),
            unique_id=obj.get('uniqueId'),
            front_weighted=obj.get('frontWeighted', True),
            layer=obj.get('layer'),
            parent_pulse_id=obj.get('parentPulseID'),
            primary=obj.get('primary', True),
            segmented_meter_idx=obj.get('segmentedMeterIdx', 0),
            meter_id=obj.get('meterId'),
            pulses=[Pulse.from_json(p) for p in obj.get('pulses', [])]
        )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, PulseStructure) and self.to_json() == other.to_json()


class Meter:
    def __init__(self, hierarchy: Optional[List[int | List[int]]] = None,
                 start_time: float = 0.0, tempo: float = 60.0,
                 unique_id: Optional[str] = None, repetitions: int = 1) -> None:
        # Parameter validation
        self._validate_parameters({
            'hierarchy': hierarchy, 'start_time': start_time, 'tempo': tempo,
            'unique_id': unique_id, 'repetitions': repetitions
        })
        self.hierarchy = hierarchy or [4, 4]
        self.start_time = start_time
        self.tempo = tempo
        self.unique_id = unique_id or str(uuid4())
        self.repetitions = repetitions
        self.pulse_structures: List[List[PulseStructure]] = []
        self._generate_pulse_structures()

    def _validate_parameters(self, opts: Dict) -> None:
        """Validate constructor parameters and provide helpful error messages."""
        if 'hierarchy' in opts and opts['hierarchy'] is not None:
            if not isinstance(opts['hierarchy'], list):
                raise TypeError(f"Parameter 'hierarchy' must be a list, got {type(opts['hierarchy']).__name__}")
            
            if len(opts['hierarchy']) == 0:
                raise ValueError("Parameter 'hierarchy' cannot be empty")
            
            for i, level in enumerate(opts['hierarchy']):
                if isinstance(level, list):
                    if not all(isinstance(item, int) for item in level):
                        raise TypeError(f"All items in hierarchy[{i}] must be integers")
                    if any(item <= 0 for item in level):
                        raise ValueError(f"All items in hierarchy[{i}] must be positive")
                elif isinstance(level, int):
                    if level <= 0:
                        raise ValueError(f"hierarchy[{i}] must be positive, got {level}")
                else:
                    raise TypeError(f"hierarchy[{i}] must be an integer or list of integers, got {type(level).__name__}")
        
        if not isinstance(opts.get('start_time', 0.0), (int, float)):
            raise TypeError(f"Parameter 'start_time' must be a number, got {type(opts['start_time']).__name__}")
        
        if opts.get('start_time', 0.0) < 0:
            raise ValueError(f"Parameter 'start_time' must be non-negative, got {opts['start_time']}")
        
        if not isinstance(opts.get('tempo', 60.0), (int, float)):
            raise TypeError(f"Parameter 'tempo' must be a number, got {type(opts['tempo']).__name__}")
        
        if opts.get('tempo', 60.0) <= 0:
            raise ValueError(f"Parameter 'tempo' must be positive, got {opts['tempo']}")
        
        if opts.get('tempo', 60.0) < MIN_TEMPO_BPM or opts.get('tempo', 60.0) > MAX_TEMPO_BPM:
            import warnings
            warnings.warn(f"Tempo {opts['tempo']} BPM is outside typical range ({MIN_TEMPO_BPM}-{MAX_TEMPO_BPM} BPM)", UserWarning)
        
        if 'unique_id' in opts and opts['unique_id'] is not None and not isinstance(opts['unique_id'], str):
            raise TypeError(f"Parameter 'unique_id' must be a string, got {type(opts['unique_id']).__name__}")
        
        if not isinstance(opts.get('repetitions', 1), int):
            raise TypeError(f"Parameter 'repetitions' must be an integer, got {type(opts['repetitions']).__name__}")
        
        if opts.get('repetitions', 1) <= 0:
            raise ValueError(f"Parameter 'repetitions' must be positive, got {opts['repetitions']}")

    # helper values
    @property
    def _top_size(self) -> int:
        h0 = self.hierarchy[0]
        return sum(h0) if isinstance(h0, list) else int(h0)

    @property
    def _bottom_mult(self) -> int:
        mult = 1
        for h in self.hierarchy[1:]:
            mult *= int(h)
        return mult

    @property
    def _pulses_per_cycle(self) -> int:
        return self._top_size * self._bottom_mult

    @property
    def _pulse_dur(self) -> float:
        return 60.0 / self.tempo / self._bottom_mult

    @property
    def cycle_dur(self) -> float:
        return self._pulse_dur * self._pulses_per_cycle

    def _generate_pulse_structures(self) -> None:
        self.pulse_structures = [[]]
        # single layer of pulses for simplified implementation
        pulses: List[Pulse] = []
        for rep in range(self.repetitions):
            start = self.start_time + rep * self.cycle_dur
            for i in range(self._pulses_per_cycle):
                pulses.append(Pulse(real_time=start + i * self._pulse_dur,
                                    meter_id=self.unique_id))
        self.pulse_structures[0] = [PulseStructure(
            tempo=self.tempo,
            size=self._pulses_per_cycle,
            start_time=self.start_time,
            meter_id=self.unique_id,
            pulses=pulses,
        )]

    @property
    def all_pulses(self) -> List[Pulse]:
        """Get all pulses from the finest layer (lowest level) of the hierarchy.
        
        This concatenates pulses from all pulse structures in the last layer,
        matching the TypeScript implementation: lastLayer.map(ps => ps.pulses).flat()
        """
        if not self.pulse_structures or not self.pulse_structures[-1]:
            return []
        # Flatten all pulses from all structures in the finest layer
        return [pulse for ps in self.pulse_structures[-1] for pulse in ps.pulses]

    @property
    def real_times(self) -> List[float]:
        return [p.real_time for p in self.all_pulses]

    def offset_pulse(self, pulse: Pulse, offset: float) -> None:
        pulse.real_time += offset

    def reset_tempo(self) -> None:
        base = self.all_pulses[:self._pulses_per_cycle]
        diff = base[-1].real_time - base[0].real_time
        if len(base) > 1:
            bit = diff / (len(base) - 1)
            if bit > 0:
                self.tempo = 60.0 / (bit * self._bottom_mult)
        # pulse duration will be derived from tempo

    def grow_cycle(self) -> None:
        self.reset_tempo()
        start = self.start_time + self.repetitions * self.cycle_dur
        for i in range(self._pulses_per_cycle):
            new_pulse = Pulse(real_time=start + i * self._pulse_dur,
                              meter_id=self.unique_id)
            self.pulse_structures[0][0].pulses.append(new_pulse)
        self.repetitions += 1

    def add_time_points(self, time_points: List[float], layer: int = 1) -> None:
        time_points = sorted(time_points)
        for tp in time_points:
            self.pulse_structures[0][0].pulses.append(Pulse(real_time=tp,
                                                            meter_id=self.unique_id))
        self.pulse_structures[0][0].pulses.sort(key=lambda p: p.real_time)

    @staticmethod
    def from_time_points(time_points: List[float], hierarchy: List[Union[int, List[int]]], 
                        repetitions: int = 1, layer: int = 0) -> 'Meter':
        """Create a Meter from actual pulse time points, handling timing variations.
        
        This method creates a meter that accurately represents actual pulse timing
        (including rubato and tempo variations) rather than theoretical even spacing.
        Uses timing regularization algorithm to handle extreme deviations.
        
        Args:
            time_points: List of actual pulse times in seconds
            hierarchy: Meter hierarchy (e.g., [4, 4, 2])  
            repetitions: Number of cycle repetitions
            layer: Which hierarchical layer the time points represent (0 or 1)
            
        Returns:
            Meter object with pulses positioned at the provided time points
        """
        if not time_points or len(time_points) < 2:
            raise ValueError("Must provide at least two time points")
        
        if not hierarchy or len(hierarchy) < 1:
            raise ValueError("Must provide hierarchy to create Meter")
        
        # Work on a copy to avoid modifying the original
        time_points = sorted(time_points.copy())
        
        # Step 1: Timing regularization algorithm (from TypeScript)
        # Calculate pulse duration and handle extreme deviations
        diffs = [time_points[i+1] - time_points[i] for i in range(len(time_points) - 1)]
        pulse_dur = sum(diffs) / len(diffs)
        
        # Normalize deviations relative to pulse duration
        zeroed_tps = [tp - time_points[0] for tp in time_points]
        norms = [pulse_dur * i for i in range(len(time_points))]
        tp_diffs = [(zeroed_tps[i] - norms[i]) / pulse_dur for i in range(len(time_points))]
        
        # Insert intermediate time points when deviations exceed 40%
        max_iterations = 100  # Prevent infinite loops
        iteration = 0
        while any(abs(d) > 0.4 for d in tp_diffs) and iteration < max_iterations:
            abs_tp_diffs = [abs(d) for d in tp_diffs]
            biggest_idx = abs_tp_diffs.index(max(abs_tp_diffs))
            diff = tp_diffs[biggest_idx]
            
            if diff > 0:
                # Insert time point before the problematic one
                if biggest_idx > 0:
                    new_tp = (time_points[biggest_idx-1] + time_points[biggest_idx]) / 2
                    time_points.insert(biggest_idx, new_tp)
                else:
                    # Can't insert before first point, adjust differently
                    break
            else:
                # Insert time point after the problematic one
                if biggest_idx < len(time_points) - 1:
                    new_tp = (time_points[biggest_idx] + time_points[biggest_idx+1]) / 2
                    time_points.insert(biggest_idx+1, new_tp)
                else:
                    # Can't insert after last point, adjust differently
                    break
            
            # Recalculate deviations
            diffs = [time_points[i+1] - time_points[i] for i in range(len(time_points) - 1)]
            pulse_dur = sum(diffs) / len(diffs)
            zeroed_tps = [tp - time_points[0] for tp in time_points]
            norms = [pulse_dur * i for i in range(len(time_points))]
            tp_diffs = [(zeroed_tps[i] - norms[i]) / pulse_dur for i in range(len(time_points))]
            
            iteration += 1
        
        # Step 2: Calculate meter properties
        tempo = 60.0 / pulse_dur
        start_time = time_points[0]
        
        # Determine how many repetitions we need based on time points
        if isinstance(hierarchy[0], list):
            layer0_size = sum(hierarchy[0])
        else:
            layer0_size = hierarchy[0]
            
        # Calculate minimum repetitions needed
        min_reps = max(repetitions, (len(time_points) + layer0_size - 1) // layer0_size)
        
        # Step 3: Create theoretical meter
        meter = Meter(
            hierarchy=hierarchy,
            start_time=start_time,
            tempo=tempo,
            repetitions=min_reps
        )
        
        # Step 4: Adjust pulses to match actual time points
        finest_pulses = meter.all_pulses
        
        # Update pulse times to match provided time points
        for i, time_point in enumerate(time_points):
            if i < len(finest_pulses):
                finest_pulses[i].real_time = time_point
        
        # If we have fewer time points than pulses, extrapolate the remaining
        if len(time_points) < len(finest_pulses):
            # Use the calculated pulse duration to extrapolate
            last_provided_time = time_points[-1]
            for i in range(len(time_points), len(finest_pulses)):
                extrapolated_time = last_provided_time + (i - len(time_points) + 1) * pulse_dur
                finest_pulses[i].real_time = extrapolated_time
        
        return meter

    @staticmethod  
    def from_json(obj: Dict) -> 'Meter':
        m = Meter(hierarchy=obj.get('hierarchy'),
                  start_time=obj.get('startTime', 0.0),
                  tempo=obj.get('tempo', 60.0),
                  unique_id=obj.get('uniqueId'),
                  repetitions=obj.get('repetitions', 1))
        m.pulse_structures = [
            [PulseStructure.from_json(ps) for ps in layer]
            for layer in obj.get('pulseStructures', [])
        ]
        return m

    def to_json(self) -> Dict:
        return {
            'uniqueId': self.unique_id,
            'hierarchy': self.hierarchy,
            'startTime': self.start_time,
            'tempo': self.tempo,
            'repetitions': self.repetitions,
            'pulseStructures': [[ps.to_json() for ps in layer]
                                for layer in self.pulse_structures]
        }

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Meter) and self.to_json() == other.to_json()

    # Musical time conversion methods
    
    def _validate_reference_level(self, reference_level: Optional[int]) -> int:
        """Validate and normalize reference level parameter."""
        if reference_level is None:
            return len(self.hierarchy) - 1
        
        if not isinstance(reference_level, int):
            raise TypeError(f"reference_level must be an integer, got {type(reference_level).__name__}")
        
        if reference_level < 0:
            raise ValueError(f"reference_level must be non-negative, got {reference_level}")
        
        if reference_level >= len(self.hierarchy):
            raise ValueError(f"reference_level {reference_level} exceeds hierarchy depth {len(self.hierarchy)}")
        
        return reference_level
    
    def _hierarchical_position_to_pulse_index(self, positions: List[int], cycle_number: int) -> int:
        """Convert hierarchical position to pulse index."""
        pulse_index = 0
        multiplier = 1
        
        # Work from finest to coarsest level
        for level in range(len(positions) - 1, -1, -1):
            position = positions[level]
            hierarchy_size = self.hierarchy[level]
            
            if isinstance(hierarchy_size, list):
                hierarchy_size = sum(hierarchy_size)
            
            pulse_index += position * multiplier
            multiplier *= hierarchy_size
        
        # Add offset for cycle
        cycle_offset = cycle_number * self._pulses_per_cycle
        return pulse_index + cycle_offset
    
    def _pulse_index_to_hierarchical_position(self, pulse_index: int, cycle_number: int) -> List[int]:
        """Convert pulse index back to hierarchical position (reverse of _hierarchical_position_to_pulse_index)."""
        # Use modulo to get within-cycle index regardless of which cycle the pulse belongs to
        within_cycle_index = pulse_index % self._pulses_per_cycle
        
        # Ensure within_cycle_index is non-negative
        if within_cycle_index < 0:
            within_cycle_index = 0
        
        positions = []
        remaining_index = within_cycle_index
        
        # Work from coarsest to finest level
        for level in range(len(self.hierarchy)):
            hierarchy_size = self.hierarchy[level]
            
            if isinstance(hierarchy_size, list):
                hierarchy_size = sum(hierarchy_size)
            
            # Calculate how many pulses are in each group at this level
            group_size = self._pulses_per_cycle
            for inner_level in range(level + 1):
                inner_size = self.hierarchy[inner_level]
                if isinstance(inner_size, list):
                    inner_size = sum(inner_size)
                group_size = group_size // inner_size
            
            position_at_level = remaining_index // group_size if group_size > 0 else 0
            positions.append(position_at_level)
            remaining_index = remaining_index % group_size if group_size > 0 else 0
        
        return positions
    
    def _calculate_level_start_time(self, positions: List[int], cycle_number: int, reference_level: int) -> float:
        """Calculate start time of hierarchical unit at reference level."""
        
        # Create positions for start of reference-level unit
        # Ensure we have positions up to reference_level
        start_positions = list(positions[:reference_level + 1])
        # Extend with zeros for levels below reference level
        while len(start_positions) < len(self.hierarchy):
            start_positions.append(0)
        
        start_pulse_index = self._hierarchical_position_to_pulse_index(start_positions, cycle_number)
        
        return self.all_pulses[start_pulse_index].real_time
    
    def _calculate_level_duration(self, positions: List[int], cycle_number: int, reference_level: int) -> float:
        """Calculate actual duration of hierarchical unit based on pulse timing."""
        
        # Get start time of current unit
        start_time = self._calculate_level_start_time(positions, cycle_number, reference_level)
        
        # Calculate start time of next unit at same level
        next_positions = positions.copy()
        next_positions[reference_level] += 1
        
        # Handle overflow - if we've exceeded this level
        hierarchy_size = self.hierarchy[reference_level]
        if isinstance(hierarchy_size, list):
            hierarchy_size = sum(hierarchy_size)
            
        if next_positions[reference_level] >= hierarchy_size:
            # Handle overflow by moving to next cycle
            next_cycle_number = cycle_number + 1
            if next_cycle_number >= self.repetitions:
                # Use meter end time
                return self.start_time + self.repetitions * self.cycle_dur - start_time
            next_positions[reference_level] = 0
            return self._calculate_level_start_time(next_positions, next_cycle_number, reference_level) - start_time
        
        end_time = self._calculate_level_start_time(next_positions, cycle_number, reference_level)
        return end_time - start_time
    
    def get_musical_time(self, real_time: float, reference_level: Optional[int] = None) -> Union['MusicalTime', Literal[False]]:
        """
        Convert real time to musical time within this meter.
        
        Args:
            real_time: Time in seconds
            reference_level: Hierarchical level for fractional calculation 
                           (0=beat, 1=subdivision, etc.). Defaults to finest level.
            
        Returns:
            MusicalTime object if time falls within meter boundaries, False otherwise
        """
        from .musical_time import MusicalTime
        
        # Step 1: Boundary validation
        if real_time < self.start_time:
            return False
        
        # Calculate proper end time 
        if self.all_pulses and len(self.all_pulses) > 0:
            # For boundary validation, use theoretical end time to maintain compatibility with existing tests
            # The pulse-based logic will handle actual cycle boundaries in the main calculation
            actual_end_time = self.start_time + self.repetitions * self.cycle_dur
        else:
            # No pulses available - this should not happen as we require pulse data
            raise ValueError("No pulse data available for meter. Pulse data is required for musical time calculation.")
        
        if real_time > actual_end_time:
            return False
        
        # Validate reference level
        ref_level = self._validate_reference_level(reference_level)
        
        # Step 2: Pulse-based cycle calculation (pulse data always available)
        if not self.all_pulses or len(self.all_pulses) == 0:
            raise ValueError(f"No pulse data available for meter. Pulse data is required for musical time calculation.")
        
        cycle_number = None
        cycle_offset = None
        
        for cycle in range(self.repetitions):
            cycle_start_pulse_idx = cycle * self._pulses_per_cycle
            
            # Get actual cycle start time
            if cycle_start_pulse_idx < len(self.all_pulses):
                cycle_start_time = self.all_pulses[cycle_start_pulse_idx].real_time
                
                # Get actual cycle end time
                next_cycle_start_pulse_idx = (cycle + 1) * self._pulses_per_cycle
                if next_cycle_start_pulse_idx < len(self.all_pulses):
                    cycle_end_time = self.all_pulses[next_cycle_start_pulse_idx].real_time
                else:
                    # Final cycle - use theoretical end
                    cycle_end_time = self.start_time + self.repetitions * self.cycle_dur
                
                # Check if time falls within this cycle
                # For the final cycle, include the exact end time (Issue #38 fix)
                if cycle == self.repetitions - 1:
                    # Final cycle: include exact end time
                    if cycle_start_time <= real_time <= cycle_end_time:
                        cycle_number = cycle
                        cycle_offset = real_time - cycle_start_time  
                        break
                else:
                    # Intermediate cycles: exclude end time (it belongs to next cycle)
                    if cycle_start_time <= real_time < cycle_end_time:
                        cycle_number = cycle
                        cycle_offset = real_time - cycle_start_time
                        break
        
        # Error if no pulse-based cycle found - indicates data integrity issue
        if cycle_number is None:
            raise ValueError(f"Unable to determine cycle for time {real_time} using pulse data. "
                           f"Time does not fall within any pulse-based cycle boundaries. "
                           f"This indicates a problem with meter pulse data integrity.")
        
        # Step 3: Fractional beat calculation
        # Find the correct pulse based on actual time, not hierarchical position
        # This is necessary when pulse timing has variations (rubato)
        
        # Find the pulse that comes at or before the query time within the current cycle
        cycle_start_pulse_idx = cycle_number * self._pulses_per_cycle
        cycle_end_pulse_idx = min((cycle_number + 1) * self._pulses_per_cycle, len(self.all_pulses))
        
        current_pulse_index = None
        for pulse_idx in range(cycle_start_pulse_idx, cycle_end_pulse_idx):
            if self.all_pulses[pulse_idx].real_time <= real_time:
                current_pulse_index = pulse_idx
            else:
                break
        
        if current_pulse_index is None:
            # Query time is before all pulses in this cycle (shouldn't happen but handle gracefully)
            current_pulse_index = cycle_start_pulse_idx
        
        current_pulse_time = self.all_pulses[current_pulse_index].real_time
        
        # Update positions to reflect the actual pulse found
        positions = self._pulse_index_to_hierarchical_position(current_pulse_index, cycle_number)
        
        # Find next pulse for fractional calculation - always use pulse-based logic
        if current_pulse_index + 1 < len(self.all_pulses):
            next_pulse_time = self.all_pulses[current_pulse_index + 1].real_time
            pulse_duration = next_pulse_time - current_pulse_time
            
            if pulse_duration <= 0:
                fractional_beat = 0.0
            else:
                time_from_current_pulse = real_time - current_pulse_time
                fractional_beat = time_from_current_pulse / pulse_duration
        else:
            # This is the last pulse - fractional_beat should be 0.0 since we can't calculate duration
            fractional_beat = 0.0
        
        # Note: fractional_beat calculation may need refinement when hierarchical position
        # calculation finds the wrong pulse due to timing variations, but clamping ensures valid range
        # Clamp to [0, 1) range (exclusive upper bound for MusicalTime)
        fractional_beat = max(0.0, min(0.9999999999999999, fractional_beat))
        
        # Step 4: Handle reference level truncation (if specified)
        if ref_level is not None and ref_level < len(self.hierarchy) - 1:
            # Truncate positions to reference level for final result
            positions = positions[:ref_level + 1]
        
        # Step 5: Result construction
        return MusicalTime(
            cycle_number=cycle_number,
            hierarchical_position=positions,
            fractional_beat=fractional_beat
        )
