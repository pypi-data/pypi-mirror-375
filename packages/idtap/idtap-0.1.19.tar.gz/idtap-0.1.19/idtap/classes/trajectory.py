from __future__ import annotations
import math
import uuid
from typing import List, Dict, Optional, Callable, TypedDict

import humps

from .pitch import Pitch
from .articulation import Articulation
from .automation import Automation, get_starts
from ..enums import Instrument


class VibObjType(TypedDict, total=False):
    periods: int
    vert_offset: float
    init_up: bool
    extent: float


class Trajectory:
    def __init__(self, options: Optional[dict] = None) -> None:
        opts = humps.decamelize(options or {})
        
        # Parameter validation
        self._validate_parameters(opts)
        self.names = [
            'Fixed',
            'Bend: Simple',
            'Bend: Sloped Start',
            'Bend: Sloped End',
            'Bend: Ladle',
            'Bend: Reverse Ladle',
            'Bend: Simple Multiple',
            'Krintin',
            'Krintin Slide',
            'Krintin Slide Hammer',
            'Dense Krintin Slide Hammer',
            'Slide',
            'Silent',
            'Vibrato'
        ]

        id_val = opts.get('id', 0)
        if not isinstance(id_val, int):
            raise SyntaxError(f'invalid id type, must be int: {id_val}')
        self.id: int = id_val

        pitches_in = opts.get('pitches', [Pitch()])
        if not isinstance(pitches_in, list) or not all(isinstance(p, Pitch) for p in pitches_in):
            raise SyntaxError('invalid pitches type, must be array of Pitch: ' + str(pitches_in))
        self.pitches: List[Pitch] = pitches_in

        dur_tot = opts.get('dur_tot', 1.0)
        if not isinstance(dur_tot, (int, float)):
            raise SyntaxError(f'invalid durTot type, must be number: {dur_tot}')
        self.dur_tot: float = float(dur_tot)

        self.dur_array: Optional[List[float]] = opts.get('dur_array')

        slope = opts.get('slope')
        if slope is None:
            self.slope = 2.0
        elif isinstance(slope, (int, float)):
            self.slope = float(slope)
        else:
            raise SyntaxError(f'invalid slope type, must be number: {slope}')

        vib_obj = opts.get('vib_obj')
        if vib_obj is None:
            self.vib_obj: VibObjType = {
                'periods': 8,
                'vert_offset': 0,
                'init_up': True,
                'extent': 0.05,
            }
        else:
            # Normalize and validate vib_obj for flexible inputs (e.g., strings)
            self.vib_obj = self._normalize_vib_obj(vib_obj)  # type: ignore

        instr = opts.get('instrumentation', Instrument.Sitar)
        self.instrumentation: Instrument = instr

        articulations_in = opts.get('articulations')
        if articulations_in is None:
            if self.instrumentation == Instrument.Sitar:
                self.articulations: Dict[str, Articulation] = {
                    '0.00': Articulation({'name': 'pluck', 'stroke': 'd'})
                }
            else:
                self.articulations = {}
        else:
            if not isinstance(articulations_in, dict):
                raise SyntaxError(f'invalid articulations type, must be object: {articulations_in}')
            self.articulations = {}
            for k, v in articulations_in.items():
                if not isinstance(v, Articulation):
                    v = Articulation(v)  # type: ignore
                self.articulations[str(k)] = v

        self.num = opts.get('num')
        self.name = opts.get('name')
        self.name = self.name_
        self.ids: List[Callable[[float], float]] = []
        for i in range(14):
            if i == 11:
                self.ids.append(self.id7)
            else:
                self.ids.append(getattr(self, f'id{i}'))
        self.fund_id12 = opts.get('fund_id12')
        self.structured_names = {
            'fixed': 0,
            'bend': {
                'simple': 1,
                'sloped start': 2,
                'sloped end': 3,
                'ladle': 4,
                'reverse ladle': 5,
                'yoyo': 6,
            },
            'krintin': {
                'krintin': 7,
                'krintin slide': 8,
                'krintin slide hammer': 9,
                'spiffy krintin slide hammer': 10,
            },
            'slide': 11,
            'silent': 12,
            'vibrato': 13,
        }
        self.vowel = opts.get('vowel')
        self.vowel_ipa = opts.get('vowel_ipa')
        self.vowel_hindi = opts.get('vowel_hindi')
        self.vowel_eng_trans = opts.get('vowel_eng_trans')
        self.start_consonant = opts.get('start_consonant')
        self.start_consonant_hindi = opts.get('start_consonant_hindi')
        self.start_consonant_ipa = opts.get('start_consonant_ipa')
        self.start_consonant_eng_trans = opts.get('start_consonant_eng_trans')
        self.end_consonant = opts.get('end_consonant')
        self.end_consonant_hindi = opts.get('end_consonant_hindi')
        self.end_consonant_ipa = opts.get('end_consonant_ipa')
        self.end_consonant_eng_trans = opts.get('end_consonant_eng_trans')
        self.group_id = opts.get('group_id')

        automation_in = opts.get('automation')
        if automation_in is not None:
            if isinstance(automation_in, Automation):
                self.automation = automation_in
            else:
                self.automation = Automation(automation_in)
        elif self.id == 12:
            self.automation = None
        else:
            self.automation = Automation()

        if self.start_consonant is not None:
            self.articulations['0.00'] = Articulation({
                'name': 'consonant',
                'stroke': self.start_consonant,
                'hindi': self.start_consonant_hindi,
                'ipa': self.start_consonant_ipa,
            })
        if self.end_consonant is not None:
            self.articulations['1.00'] = Articulation({
                'name': 'consonant',
                'stroke': self.end_consonant,
                'hindi': self.end_consonant_hindi,
                'ipa': self.end_consonant_ipa,
            })

        if self.id < 4:
            self.dur_array = [1]
        elif self.dur_array is None and self.id == 4:
            self.dur_array = [1/3, 2/3]
        elif self.dur_array is None and self.id == 5:
            self.dur_array = [2/3, 1/3]
        elif self.dur_array is None and self.id == 6:
            if len(self.log_freqs) > 1:
                self.dur_array = [1/(len(self.log_freqs)-1)] * (len(self.log_freqs)-1)
            else:
                self.dur_array = []
        elif self.id == 7:
            if self.dur_array is None:
                self.dur_array = [0.2, 0.8]
            starts = get_starts(self.dur_array)
            cond = len(self.log_freqs) > 1 and self.log_freqs[1] >= self.log_freqs[0]
            self.articulations[str(starts[1])] = Articulation({
                'name': 'hammer-on' if cond else 'hammer-off'
            })
        elif self.id == 8:
            if self.dur_array is None:
                self.dur_array = [1/3,1/3,1/3]
            starts = get_starts(self.dur_array)
            self.articulations[str(starts[1])] = Articulation({'name': 'hammer-off'})
            self.articulations[str(starts[2])] = Articulation({'name': 'slide'})
        elif self.id == 9:
            if self.dur_array is None:
                self.dur_array = [0.25,0.25,0.25,0.25]
            starts = get_starts(self.dur_array)
            self.articulations[str(starts[1])] = Articulation({'name': 'hammer-off'})
            self.articulations[str(starts[2])] = Articulation({'name': 'slide'})
            self.articulations[str(starts[3])] = Articulation({'name': 'hammer-on'})
        elif self.id == 10:
            if self.dur_array is None:
                self.dur_array = [1/6]*6
            starts = get_starts(self.dur_array)
            self.articulations[str(starts[1])] = Articulation({'name': 'slide'})
            self.articulations[str(starts[2])] = Articulation({'name': 'hammer-on'})
            self.articulations[str(starts[3])] = Articulation({'name': 'hammer-off'})
            self.articulations[str(starts[4])] = Articulation({'name': 'slide'})
            self.articulations[str(starts[5])] = Articulation({'name': 'hammer-on'})
        elif self.id == 11:
            if self.dur_array is None or len(self.dur_array) == 1:
                self.dur_array = [0.5,0.5]
            starts = get_starts(self.dur_array)
            self.articulations[str(starts[1])] = Articulation({'name': 'slide'})

        if self.dur_array:
            i = 0
            while i < len(self.dur_array):
                if self.dur_array[i] == 0:
                    print('removing zero dur')
                    self.dur_array.pop(i)
                    if i+1 < len(self.pitches):
                        self.pitches.pop(i+1)
                else:
                    i += 1

        if self.instrumentation in (Instrument.Vocal_M, Instrument.Vocal_F):
            for k in list(self.articulations.keys()):
                if self.articulations[k].name == 'pluck':
                    del self.articulations[k]

        self.c_ipas = ['k', 'kʰ', 'g', 'gʱ', 'ŋ', 'c', 'cʰ', 'ɟ', 'ɟʱ', 'ɲ', 'ʈ',
                       'ʈʰ', 'ɖ', 'ɖʱ', 'n', 't', 'tʰ', 'd', 'dʱ', 'n̪', 'p', 'pʰ', 'b', 'bʱ',
                       'm', 'j', 'r', 'l', 'v', 'ʃ', 'ʂ', 's', 'h']
        self.c_isos = ['ka', 'kha', 'ga', 'gha', 'ṅa', 'ca', 'cha', 'ja', 'jha', 'ña', 'ṭa',
                       'ṭha', 'ḍa', 'ḍha', 'na', 'ta', 'tha', 'da', 'dha', 'na', 'pa', 'pha',
                       'ba', 'bha', 'ma', 'ya', 'ra', 'la', 'va', 'śa', 'ṣa', 'sa', 'ha']
        self.c_hindis = ['क', 'ख', 'ग', 'घ', 'ङ', 'च', 'छ', 'ज', 'झ', 'ञ', 'ट',
                          'ठ', 'ड', 'ढ', 'न', 'त', 'थ', 'द', 'ध', 'न', 'प', 'फ़', 'ब', 'भ', 'म', 'य',
                          'र', 'ल', 'व', 'श', 'ष', 'स', 'ह']
        self.c_eng_trans = ['k', 'kh', 'g', 'gh', 'ṅ', 'c', 'ch', 'j', 'jh', 'ñ', 'ṭ',
                             'ṭh', 'ḍ', 'ḍh', 'n', 't', 'th', 'd', 'dh', 'n', 'p', 'ph', 'b', 'bh',
                             'm', 'y', 'r', 'l', 'v', 'ś', 'ṣ', 's', 'h']
        self.v_ipas = ['ə', 'aː', 'ɪ', 'iː', 'ʊ', 'uː', 'eː', 'ɛː', 'oː', 'ɔː', '_']
        self.v_isos = ['a', 'ā', 'i', 'ī', 'u', 'ū', 'ē', 'ai', 'ō', 'au', '_']
        self.v_hindis = ['अ', 'आ', 'इ', 'ई', 'उ', 'ऊ', 'ए', 'ऐ', 'ओ', 'औ', '_']
        self.v_eng_trans = ['a', 'ā', 'i', 'ī', 'u', 'ū', 'ē', 'ai', 'ō', 'au', '_']

        self.unique_id = opts.get('unique_id') or str(uuid.uuid4())
        self.convert_c_iso_to_hindi_and_ipa()

        for k in list(self.articulations.keys()):
            if k == '0':
                self.articulations['0.00'] = self.articulations[k]
                del self.articulations[k]

        self.tags = opts.get('tags', [])

        self.start_time: Optional[float] = opts.get('start_time')
        self.phrase_idx: Optional[int] = None

    def _validate_parameters(self, opts: dict) -> None:
        """Validate constructor parameters and provide helpful error messages."""
        if not opts:
            return
            
        # Define allowed parameter names
        allowed_keys = {
            'id', 'pitches', 'dur_tot', 'dur_array', 'slope', 'vib_obj', 'instrumentation',
            'articulations', 'num', 'name', 'fund_id12', 'vowel', 'vowel_ipa', 'vowel_hindi',
            'vowel_eng_trans', 'start_consonant', 'start_consonant_hindi', 'start_consonant_ipa',
            'start_consonant_eng_trans', 'end_consonant', 'end_consonant_hindi', 'end_consonant_ipa',
            'end_consonant_eng_trans', 'group_id', 'automation', 'unique_id', 'tags', 'start_time',
            'phrase_idx'
        }
        provided_keys = set(opts.keys())
        invalid_keys = provided_keys - allowed_keys
        
        # Check for invalid parameter names with helpful suggestions
        if invalid_keys:
            error_messages = []
            
            for key in invalid_keys:
                if key == 'type':
                    error_messages.append(f"Parameter '{key}' not supported. Did you mean 'id'?")
                elif key == 'duration':
                    error_messages.append(f"Parameter '{key}' not supported. Did you mean 'dur_tot'?")
                elif key == 'instrument':
                    error_messages.append(f"Parameter '{key}' not supported. Did you mean 'instrumentation'?")
                elif key == 'duration_array':
                    error_messages.append(f"Parameter '{key}' not supported. Did you mean 'dur_array'?")
                elif key == 'vibrato_obj':
                    error_messages.append(f"Parameter '{key}' not supported. Did you mean 'vib_obj'?")
                elif key == 'fundamental_id12':
                    error_messages.append(f"Parameter '{key}' not supported. Did you mean 'fund_id12'?")
                else:
                    error_messages.append(f"Invalid parameter: '{key}'")
            
            error_msg = "; ".join(error_messages)
            error_msg += f". Allowed parameters: {sorted(allowed_keys)}"
            raise ValueError(error_msg)
        
        # Validate parameter types and values
        self._validate_parameter_types(opts)
        self._validate_parameter_values(opts)
    
    def _validate_parameter_types(self, opts: dict) -> None:
        """Validate that all parameters have correct types.
        Note: Some parameters (id, pitches, dur_tot, slope, articulations) are validated 
        by the original constructor logic which throws SyntaxError, so we skip them here."""
        
        # Skip parameters that are already validated by original constructor logic:
        # - id, pitches, dur_tot, slope, articulations (validated with SyntaxError)
        
        if 'dur_array' in opts and opts['dur_array'] is not None:
            if not isinstance(opts['dur_array'], list):
                raise TypeError(f"Parameter 'dur_array' must be a list, got {type(opts['dur_array']).__name__}")
            if not all(isinstance(d, (int, float)) for d in opts['dur_array']):
                raise TypeError("All items in 'dur_array' must be numbers")
        
        if 'vib_obj' in opts and opts['vib_obj'] is not None:
            if not isinstance(opts['vib_obj'], dict):
                raise TypeError(f"Parameter 'vib_obj' must be a dict, got {type(opts['vib_obj']).__name__}")
            self._validate_vib_obj_structure(opts['vib_obj'])
        
        if 'instrumentation' in opts and not isinstance(opts['instrumentation'], Instrument):
            raise TypeError(f"Parameter 'instrumentation' must be an Instrument enum, got {type(opts['instrumentation']).__name__}")
        
        if 'start_time' in opts and opts['start_time'] is not None:
            if not isinstance(opts['start_time'], (int, float)):
                raise TypeError(f"Parameter 'start_time' must be a number, got {type(opts['start_time']).__name__}")
        
        # Validate string parameters
        string_params = ['name', 'vowel', 'vowel_ipa', 'vowel_hindi', 'vowel_eng_trans',
                        'start_consonant', 'start_consonant_hindi', 'start_consonant_ipa',
                        'start_consonant_eng_trans', 'end_consonant', 'end_consonant_hindi',
                        'end_consonant_ipa', 'end_consonant_eng_trans', 'unique_id']
        
        for param in string_params:
            if param in opts and opts[param] is not None and not isinstance(opts[param], str):
                raise TypeError(f"Parameter '{param}' must be a string, got {type(opts[param]).__name__}")
        
        if 'tags' in opts and not isinstance(opts['tags'], list):
            raise TypeError(f"Parameter 'tags' must be a list, got {type(opts['tags']).__name__}")
    
    def _validate_parameter_values(self, opts: dict) -> None:
        """Validate that parameter values are in valid ranges.
        Note: Some parameters (id, dur_tot, slope) are validated by original constructor,
        so we only do additional range checks here."""
        
        # Additional range validation for parameters already type-checked by original constructor
        if 'id' in opts and isinstance(opts['id'], int):
            if not 0 <= opts['id'] <= 13:
                raise ValueError(f"Parameter 'id' must be between 0-13 (trajectory types), got {opts['id']}")
        
        if 'dur_tot' in opts and isinstance(opts['dur_tot'], (int, float)):
            if opts['dur_tot'] <= 0:
                raise ValueError(f"Parameter 'dur_tot' must be positive, got {opts['dur_tot']}")
        
        if 'dur_array' in opts and opts['dur_array'] is not None:
            dur_array = opts['dur_array']
            if any(d < 0 for d in dur_array):
                raise ValueError("All values in 'dur_array' must be non-negative")
            if len(dur_array) > 0 and sum(dur_array) == 0:
                raise ValueError("'dur_array' cannot have all zero values")
        
        if 'slope' in opts and isinstance(opts['slope'], (int, float)):
            if opts['slope'] <= 0:
                raise ValueError(f"Parameter 'slope' must be positive, got {opts['slope']}")
        
        if 'start_time' in opts and opts['start_time'] is not None:
            if opts['start_time'] < 0:
                raise ValueError(f"Parameter 'start_time' must be non-negative, got {opts['start_time']}")
        
        # Validate vocal parameters are only used with vocal instruments
        vocal_params = ['vowel', 'vowel_ipa', 'vowel_hindi', 'vowel_eng_trans',
                       'start_consonant', 'start_consonant_hindi', 'start_consonant_ipa',
                       'start_consonant_eng_trans', 'end_consonant', 'end_consonant_hindi',
                       'end_consonant_ipa', 'end_consonant_eng_trans']
        
        has_vocal_params = any(param in opts and opts[param] is not None for param in vocal_params)
        instrumentation = opts.get('instrumentation', Instrument.Sitar)
        
        if has_vocal_params and instrumentation not in (Instrument.Vocal_M, Instrument.Vocal_F):
            import warnings
            warnings.warn(f"Vocal parameters provided but instrumentation is {instrumentation.name}. "
                         "Vocal parameters are typically used with Vocal_M or Vocal_F instruments.", UserWarning)
    
    def _validate_vib_obj_structure(self, vib_obj: dict) -> None:
        """Validate vib_obj has correct structure, allowing lenient input types.

        Accepts numeric strings and floats that can be coerced to required types,
        but does not mutate the provided dict. Actual coercion happens in
        _normalize_vib_obj.
        """
        allowed_keys = {'periods', 'vert_offset', 'init_up', 'extent'}
        provided_keys = set(vib_obj.keys())
        invalid_keys = provided_keys - allowed_keys

        if invalid_keys:
            raise ValueError(
                f"vib_obj contains invalid keys: {sorted(invalid_keys)}. "
                f"Allowed keys: {sorted(allowed_keys)}"
            )

        # Validate types and values (lenient)
        if 'periods' in vib_obj:
            p = vib_obj['periods']
            if isinstance(p, int):
                if p <= 0:
                    raise ValueError("vib_obj['periods'] must be positive")
            elif isinstance(p, float):
                if p <= 0:
                    raise ValueError("vib_obj['periods'] must be positive")
            elif isinstance(p, str):
                try:
                    pf = float(p.strip())
                except Exception as e:
                    raise TypeError("vib_obj['periods'] must be an integer or numeric string") from e
                if pf <= 0:
                    raise ValueError("vib_obj['periods'] must be positive")
            else:
                raise TypeError("vib_obj['periods'] must be a number")

        for key in ['vert_offset', 'extent']:
            if key in vib_obj:
                v = vib_obj[key]
                if isinstance(v, (int, float)):
                    pass
                elif isinstance(v, str):
                    try:
                        float(v.strip())
                    except Exception as e:
                        raise TypeError(f"vib_obj['{key}'] must be a number or numeric string") from e
                else:
                    raise TypeError(f"vib_obj['{key}'] must be a number")

        if 'extent' in vib_obj:
            try:
                ext_val = float(vib_obj['extent'])
            except Exception:
                # If not coercible, earlier checks will have raised
                ext_val = 0.0
            if ext_val <= 0:
                raise ValueError("vib_obj['extent'] must be positive")

        if 'init_up' in vib_obj:
            iu = vib_obj['init_up']
            if isinstance(iu, bool):
                pass
            elif isinstance(iu, (int, float)):
                if iu not in (0, 1):
                    raise TypeError("vib_obj['init_up'] must be boolean-like (0/1)")
            elif isinstance(iu, str):
                if iu.strip().lower() not in {'true', 'false', '0', '1'}:
                    raise TypeError("vib_obj['init_up'] must be 'true'/'false' or '0'/'1'")
            else:
                raise TypeError("vib_obj['init_up'] must be a boolean or boolean-like string")

    def _normalize_vib_obj(self, vib_obj: dict) -> VibObjType:
        """Return a normalized VibObjType with correct Python types.

        - periods: int (>0)
        - vert_offset: float
        - extent: float (>0)
        - init_up: bool
        """
        # Start from defaults
        norm: VibObjType = {
            'periods': 8,
            'vert_offset': 0.0,
            'init_up': True,
            'extent': 0.05,
        }

        # Validate structure leniently first
        self._validate_vib_obj_structure(vib_obj)

        # Coerce values
        if 'periods' in vib_obj:
            p = vib_obj['periods']
            if isinstance(p, (int, float)):
                norm['periods'] = int(p)
            elif isinstance(p, str):
                norm['periods'] = int(float(p.strip()))

        if 'vert_offset' in vib_obj:
            v = vib_obj['vert_offset']
            if isinstance(v, (int, float)):
                norm['vert_offset'] = float(v)
            elif isinstance(v, str):
                norm['vert_offset'] = float(v.strip())

        if 'extent' in vib_obj:
            e = vib_obj['extent']
            if isinstance(e, (int, float)):
                norm['extent'] = float(e)
            elif isinstance(e, str):
                norm['extent'] = float(e.strip())

        if 'init_up' in vib_obj:
            iu = vib_obj['init_up']
            if isinstance(iu, bool):
                norm['init_up'] = iu
            elif isinstance(iu, (int, float)):
                norm['init_up'] = bool(int(iu))
            elif isinstance(iu, str):
                sval = iu.strip().lower()
                if sval in {'true', '1'}:
                    norm['init_up'] = True
                elif sval in {'false', '0'}:
                    norm['init_up'] = False
                else:
                    # Should not happen due to validation above
                    raise TypeError("vib_obj['init_up'] string must be 'true'/'false' or '0'/'1'")

        # Final sanity checks
        if norm['periods'] <= 0:
            raise ValueError("vib_obj['periods'] must be positive after normalization")
        if norm['extent'] <= 0:
            raise ValueError("vib_obj['extent'] must be positive after normalization")

        return norm

    # ------------------------------- properties -----------------------------
    @property
    def freqs(self) -> List[float]:
        return [p.frequency for p in self.pitches]

    @property
    def log_freqs(self) -> List[float]:
        return [math.log2(p.frequency) for p in self.pitches]

    @property
    def sloped(self) -> bool:
        return self.id in (2,3,4,5)

    @property
    def min_freq(self) -> float:
        return min(self.freqs)

    @property
    def max_freq(self) -> float:
        return max(self.freqs)

    @property
    def min_log_freq(self) -> float:
        return min(self.log_freqs)

    @property
    def max_log_freq(self) -> float:
        return max(self.log_freqs)

    @property
    def end_time(self) -> Optional[float]:
        if self.start_time is None:
            return None
        return self.start_time + self.dur_tot

    @property
    def name_(self) -> str:
        return self.names[self.id]

    # ------------------------------- utils -----------------------------
    def update_fundamental(self, fundamental: float) -> None:
        for p in self.pitches:
            p.fundamental = fundamental

    # ------------------------------- computation -----------------------
    def compute(self, x: float, log_scale: bool = False) -> float:
        val = self.ids[self.id](x)
        return math.log2(val) if log_scale else val

    def id0(self, x: float, lf: Optional[List[float]] = None) -> float:
        log_freqs = lf or self.log_freqs
        return 2 ** log_freqs[0]

    def id1(self, x: float, lf: Optional[List[float]] = None) -> float:
        log_freqs = lf or self.log_freqs
        pi_x = (math.cos(math.pi * (x + 1)) / 2) + 0.5
        diff = log_freqs[1] - log_freqs[0]
        return 2 ** (pi_x * diff + log_freqs[0])

    def id2(self, x: float, lf: Optional[List[float]] = None, sl: Optional[float] = None) -> float:
        log_freqs = lf or self.log_freqs
        slope = sl if sl is not None else self.slope
        a = log_freqs[0]
        b = log_freqs[1]
        log_freq_out = (a - b) * ((1 - x) ** slope) + b
        return 2 ** log_freq_out

    def id3(self, x: float, lf: Optional[List[float]] = None, sl: Optional[float] = None) -> float:
        log_freqs = lf or self.log_freqs
        slope = sl if sl is not None else self.slope
        a = log_freqs[0]
        b = log_freqs[1]
        log_freq_out = (b - a) * (x ** slope) + a
        return 2 ** log_freq_out

    def id4(self, x: float, lf: Optional[List[float]] = None, sl: Optional[float] = None, da: Optional[List[float]] = None) -> float:
        log_freqs = lf or self.log_freqs
        slope = sl if sl is not None else self.slope
        dur_array = da if da is not None else self.dur_array
        if dur_array is None:
            dur_array = [1/3,2/3]
        bend0 = lambda x: self.id2(x, log_freqs[:2], slope)
        bend1 = lambda x: self.id1(x, log_freqs[1:3])
        out0 = lambda x: bend0(x / dur_array[0])
        out1 = lambda x: bend1((x - dur_array[0]) / dur_array[1])
        return out0(x) if x < dur_array[0] else out1(x)

    def id5(self, x: float, lf: Optional[List[float]] = None, sl: Optional[float] = None, da: Optional[List[float]] = None) -> float:
        log_freqs = lf or self.log_freqs
        slope = sl if sl is not None else self.slope
        dur_array = da if da is not None else self.dur_array
        dur_array = dur_array or [1/3,2/3]
        bend0 = lambda x: self.id1(x, log_freqs[:2])
        bend1 = lambda x: self.id3(x, log_freqs[1:3], slope)
        out0 = lambda x: bend0(x / dur_array[0])
        out1 = lambda x: bend1((x - dur_array[0]) / dur_array[1])
        return out0(x) if x < dur_array[0] else out1(x)

    def id6(self, x: float, lf: Optional[List[float]] = None, da: Optional[List[float]] = None) -> float:
        log_freqs = lf or self.log_freqs
        dur_array = da if da is not None else self.dur_array
        if dur_array is None:
            dur_array = [1/(len(log_freqs)-1)] * (len(log_freqs)-1)
        
        # Get segment start points
        starts = get_starts(dur_array)
        
        # Find the correct segment index using proper boundary logic
        # This matches the TypeScript findLastIndex behavior
        index = -1
        for i in range(len(starts)):
            if x >= starts[i]:
                # Check if this is the last segment or if x is before the next segment start
                if i == len(starts) - 1 or x < starts[i + 1]:
                    index = i
                    break
        
        if index == -1:
            # Fallback for edge cases (x < 0)
            index = 0
        
        # Create the interpolation function for this segment
        bend = lambda y: self.id1(y, log_freqs[index:index+2])
        
        # Calculate the relative position within this segment
        dur_sum = sum(dur_array[:index])
        relative_x = (x - dur_sum) / dur_array[index]
        
        # Ensure relative_x is within [0, 1] bounds
        relative_x = max(0.0, min(1.0, relative_x))
        
        return bend(relative_x)

    def id7(self, x: float, lf: Optional[List[float]] = None, da: Optional[List[float]] = None) -> float:
        log_freqs = lf or self.log_freqs
        dur_array = da if da is not None else self.dur_array
        if dur_array is None:
            dur_array = [0.5,0.5]
        out = log_freqs[0] if x < dur_array[0] else log_freqs[1]
        return 2 ** out

    def id8(self, x: float, lf: Optional[List[float]] = None, da: Optional[List[float]] = None) -> float:
        log_freqs = lf or self.log_freqs
        dur_array = da if da is not None else self.dur_array
        if dur_array is None:
            dur_array = [1/3,1/3,1/3]
        starts = get_starts(dur_array)
        index = 0
        for i,s in enumerate(starts):
            if x >= s:
                index = i
        return 2 ** log_freqs[index]

    def id9(self, x: float, lf: Optional[List[float]] = None, da: Optional[List[float]] = None) -> float:
        log_freqs = lf or self.log_freqs
        dur_array = da if da is not None else self.dur_array
        if dur_array is None:
            dur_array = [0.25,0.25,0.25,0.25]
        starts = get_starts(dur_array)
        index = 0
        for i,s in enumerate(starts):
            if x >= s:
                index = i
        return 2 ** log_freqs[index]

    def id10(self, x: float, lf: Optional[List[float]] = None, da: Optional[List[float]] = None) -> float:
        log_freqs = lf or self.log_freqs
        dur_array = da if da is not None else self.dur_array
        if dur_array is None:
            dur_array = [i/6 for i in range(6)]
        starts = get_starts(dur_array)
        index = 0
        for i,s in enumerate(starts):
            if x >= s:
                index = i
        return 2 ** log_freqs[index]

    def id12(self, x: float) -> float:
        return float(self.fund_id12)

    def id13(self, x: float) -> float:
        periods = self.vib_obj['periods']
        vert_offset = self.vib_obj['vert_offset']
        init_up = self.vib_obj['init_up']
        extent = self.vib_obj['extent']
        if abs(vert_offset) > extent / 2:
            vert_offset = math.copysign(extent/2, vert_offset)
        out = math.cos(x * 2 * math.pi * periods + int(init_up) * math.pi)
        if x < 1/(2*periods):
            start = self.log_freqs[0]
            end = math.log2(self.id13(1/(2*periods)))
            middle = (end + start)/2
            ext = abs(end - start)/2
            out = out*ext + middle
            return 2 ** out
        elif x > 1 - 1/(2*periods):
            start = math.log2(self.id13(1 - 1/(2*periods)))
            end = self.log_freqs[0]
            middle = (end + start)/2
            ext = abs(end - start)/2
            out = out*ext + middle
            return 2 ** out
        else:
            return 2 ** (out * extent/2 + vert_offset + self.log_freqs[0])

    # ---------------- consonant/vowel helpers -----------------------
    def remove_consonant(self, start: bool = True) -> None:
        if start:
            self.start_consonant = None
            self.start_consonant_hindi = None
            self.start_consonant_ipa = None
            self.start_consonant_eng_trans = None
            art = self.articulations.get('0.00')
            if art and art.name == 'consonant':
                del self.articulations['0.00']
        else:
            self.end_consonant = None
            self.end_consonant_hindi = None
            self.end_consonant_ipa = None
            self.end_consonant_eng_trans = None
            art = self.articulations.get('1.00')
            if art and art.name == 'consonant':
                del self.articulations['1.00']

    def add_consonant(self, consonant: str, start: bool = True) -> None:
        idx = self.c_isos.index(consonant) if consonant in self.c_isos else -1
        hindi = self.c_hindis[idx] if idx != -1 else None
        ipa = self.c_ipas[idx] if idx != -1 else None
        eng = self.c_eng_trans[idx] if idx != -1 else None
        art = Articulation({'name': 'consonant', 'stroke': consonant, 'hindi': hindi, 'ipa': ipa, 'eng_trans': eng})
        if start:
            self.start_consonant = consonant
            self.start_consonant_hindi = hindi
            self.start_consonant_ipa = ipa
            self.start_consonant_eng_trans = eng
            self.articulations['0.00'] = art
        else:
            self.end_consonant = consonant
            self.end_consonant_hindi = hindi
            self.end_consonant_ipa = ipa
            self.end_consonant_eng_trans = eng
            self.articulations['1.00'] = art

    def change_consonant(self, consonant: str, start: bool = True) -> None:
        idx = self.c_isos.index(consonant) if consonant in self.c_isos else -1
        hindi = self.c_hindis[idx] if idx != -1 else None
        ipa = self.c_ipas[idx] if idx != -1 else None
        eng = self.c_eng_trans[idx] if idx != -1 else None
        if start:
            self.start_consonant = consonant
            self.start_consonant_hindi = hindi
            self.start_consonant_ipa = ipa
            self.start_consonant_eng_trans = eng
            art = self.articulations['0.00']
            art.stroke = consonant
            art.hindi = hindi
            art.ipa = ipa
            art.eng_trans = eng
        else:
            self.end_consonant = consonant
            self.end_consonant_hindi = hindi
            self.end_consonant_ipa = ipa
            self.end_consonant_eng_trans = eng
            art = self.articulations['1.00']
            art.stroke = consonant
            art.hindi = hindi
            art.ipa = ipa
            art.eng_trans = eng

    def durations_of_fixed_pitches(self, opts: Optional[Dict] = None) -> Dict:
        output_type = 'pitchNumber'
        if opts:
            output_type = opts.get('output_type', 'pitchNumber')
        pitch_durs: Dict = {}
        id_str = str(self.id)
        if id_str in ('0','13'):
            pitch_durs[self.pitches[0].numbered_pitch] = self.dur_tot
        elif id_str in ('1','2','3'):
            if self.pitches[0].numbered_pitch == self.pitches[1].numbered_pitch:
                pitch_durs[self.pitches[0].numbered_pitch] = self.dur_tot
        elif id_str in ('4','5'):
            p0 = self.pitches[0].numbered_pitch
            p1 = self.pitches[1].numbered_pitch
            p2 = self.pitches[2].numbered_pitch
            if p0 == p1:
                pitch_durs[p0] = self.dur_tot * self.dur_array[0]
            elif p1 == p2:
                pitch_durs[p1] = pitch_durs.get(p1,0) + self.dur_tot * self.dur_array[1]
        elif id_str == '6':
            last_num = None
            for i,p in enumerate(self.pitches):
                num = p.numbered_pitch
                if num == last_num:
                    pitch_durs[num] = pitch_durs.get(num,0) + self.dur_tot * self.dur_array[i-1]
                last_num = num
        elif id_str in ('7','8','9','10','11'):
            for i,p in enumerate(self.pitches):
                if i < len(self.dur_array) and self.dur_array[i] is not None:
                    num = p.numbered_pitch
                    pitch_durs[num] = pitch_durs.get(num,0) + self.dur_tot * self.dur_array[i]
        if output_type == 'pitchNumber':
            return pitch_durs
        elif output_type == 'chroma':
            alt = {}
            for p,v in pitch_durs.items():
                c = Pitch.pitch_number_to_chroma(int(p))
                alt[c] = v
            return alt
        elif output_type == 'scaleDegree':
            alt = {}
            for p,v in pitch_durs.items():
                c = Pitch.pitch_number_to_chroma(int(p))
                sd = Pitch.chroma_to_scale_degree(c)[0]
                alt[sd] = v
            return alt
        elif output_type == 'sargamLetter':
            alt = {}
            for p,v in pitch_durs.items():
                s = Pitch.from_pitch_number(int(p)).sargam_letter
                alt[s] = v
            return alt
        else:
            raise Exception('outputType not recognized')

    def convert_c_iso_to_hindi_and_ipa(self) -> None:
        for art in self.articulations.values():
            if art.name == 'consonant':
                if not isinstance(art.stroke, str):
                    raise Exception('stroke is not a string')
                c_iso = art.stroke
                if c_iso in self.c_isos:
                    idx = self.c_isos.index(c_iso)
                    art.hindi = getattr(art, 'hindi', None) or self.c_hindis[idx]
                    art.ipa = getattr(art, 'ipa', None) or self.c_ipas[idx]
                    art.eng_trans = getattr(art, 'eng_trans', None) or self.c_eng_trans[idx]
                else:
                    if not hasattr(art, 'hindi'):
                        art.hindi = None
                    if not hasattr(art, 'ipa'):
                        art.ipa = None
                    if not hasattr(art, 'eng_trans'):
                        art.eng_trans = None
        if self.start_consonant is not None:
            c_iso = self.start_consonant
            if c_iso in self.c_isos:
                idx = self.c_isos.index(c_iso)
                self.start_consonant_hindi = getattr(self, 'start_consonant_hindi', None) or self.c_hindis[idx]
                self.start_consonant_ipa = getattr(self, 'start_consonant_ipa', None) or self.c_ipas[idx]
                self.start_consonant_eng_trans = getattr(self, 'start_consonant_eng_trans', None) or self.c_eng_trans[idx]
        if self.end_consonant is not None:
            c_iso = self.end_consonant
            if c_iso in self.c_isos:
                idx = self.c_isos.index(c_iso)
                self.end_consonant_hindi = getattr(self, 'end_consonant_hindi', None) or self.c_hindis[idx]
                self.end_consonant_ipa = getattr(self, 'end_consonant_ipa', None) or self.c_ipas[idx]
                self.end_consonant_eng_trans = getattr(self, 'end_consonant_eng_trans', None) or self.c_eng_trans[idx]
        if self.vowel is not None:
            v_iso = self.vowel
            if v_iso in self.v_isos:
                idx = self.v_isos.index(v_iso)
                self.vowel_hindi = getattr(self, 'vowel_hindi', None) or self.v_hindis[idx]
                self.vowel_ipa = getattr(self, 'vowel_ipa', None) or self.v_ipas[idx]
                self.vowel_eng_trans = getattr(self, 'vowel_eng_trans', None) or self.v_eng_trans[idx]

    def update_vowel(self, v_iso: str) -> None:
        if v_iso in self.v_isos:
            idx = self.v_isos.index(v_iso)
            self.vowel = v_iso
            self.vowel_hindi = self.v_hindis[idx]
            self.vowel_ipa = self.v_ipas[idx]
            self.vowel_eng_trans = self.v_eng_trans[idx]
        else:
            self.vowel = v_iso
            self.vowel_hindi = None
            self.vowel_ipa = None
            self.vowel_eng_trans = None

    def to_json(self) -> Dict:
        data = {
            'id': self.id,
            'pitches': [p.to_json() for p in self.pitches],
            'durTot': self.dur_tot,
            'durArray': self.dur_array,
            'slope': self.slope,
            'articulations': {k: a.to_json() for k, a in self.articulations.items()},
            'startTime': self.start_time,
            'num': self.num,
            'name': self.name,
            'fundID12': self.fund_id12,
            'vibObj': self.vib_obj,
            'instrumentation': self.instrumentation.value if isinstance(self.instrumentation, Instrument) else self.instrumentation,
            'vowel': self.vowel,
            'startConsonant': self.start_consonant,
            'startConsonantHindi': self.start_consonant_hindi,
            'startConsonantIpa': self.start_consonant_ipa,
            'startConsonantEngTrans': self.start_consonant_eng_trans,
            'endConsonant': self.end_consonant,
            'endConsonantHindi': self.end_consonant_hindi,
            'endConsonantIpa': self.end_consonant_ipa,
            'endConsonantEngTrans': self.end_consonant_eng_trans,
            'groupId': self.group_id,
            'automation': self.automation.to_json() if self.automation else None,
            'uniqueId': self.unique_id,
            'tags': self.tags,
        }
        # drop None values so they serialize as undefined (omitted) rather than null
        return {k: v for k, v in data.items() if v is not None}

    @staticmethod
    def from_json(obj: Dict) -> 'Trajectory':
        opts = humps.decamelize(obj)
        pitches = [Pitch.from_json(p) for p in opts.get('pitches', [])]
        arts = {}
        for k,v in opts.get('articulations', {}).items():
            if v is not None:
                arts[k] = Articulation.from_json(v)
        automation = opts.get('automation')
        instr = opts.get('instrumentation')
        if isinstance(instr, str):
            try:
                opts['instrumentation'] = Instrument(instr)
            except ValueError:
                opts['instrumentation'] = Instrument.Sitar
        opts['pitches'] = pitches
        opts['articulations'] = arts
        opts['automation'] = automation
        return Trajectory(opts)

    @staticmethod
    def names() -> List[str]:
        return Trajectory().names
