"""Data models for audio upload functionality."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Literal, Union
from datetime import datetime


@dataclass
class Musician:
    """Represents a musician in a recording."""
    name: str
    role: Literal['Soloist', 'Accompanist', 'Percussionist', 'Drone']
    instrument: str
    gharana: Optional[str] = None

    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON format for API."""
        return {
            'role': self.role,
            'instrument': self.instrument,
            'gharana': self.gharana
        }


@dataclass
class Location:
    """Represents a geographic location."""
    continent: str
    country: str
    city: Optional[str] = None

    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON format for API."""
        result = {
            'continent': self.continent,
            'country': self.country
        }
        if self.city:
            result['city'] = self.city
        return result


@dataclass
class RecordingDate:
    """Represents a recording date."""
    year: Optional[int] = None
    month: Optional[str] = None
    day: Optional[int] = None

    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON format for API."""
        result = {}
        if self.year is not None:
            result['year'] = str(self.year)
        if self.month is not None:
            result['month'] = self.month
        if self.day is not None:
            result['day'] = str(self.day)
        return result


@dataclass
class PerformanceSection:
    """Represents a performance section within a raga."""
    name: str
    start: float = 0.0
    end: float = 0.0

    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON format for API."""
        return {
            'start': self.start,
            'end': self.end
        }


@dataclass
class Raga:
    """Represents a raga with performance sections."""
    name: str
    performance_sections: List[PerformanceSection] = field(default_factory=list)

    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON format for API."""
        sections = {}
        for section in self.performance_sections:
            sections[section.name] = section.to_json()
        return {
            'performance sections': sections
        }


@dataclass
class Permissions:
    """Represents access permissions for a recording."""
    public_view: bool = True
    edit: List[str] = field(default_factory=list)
    view: List[str] = field(default_factory=list)

    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON format for API."""
        return {
            'publicView': self.public_view,
            'edit': self.edit,
            'view': self.view
        }


@dataclass
class AudioMetadata:
    """Complete metadata for an audio recording.
    
    Args:
        title: Optional title for the recording
        musicians: List of Musician objects
        location: Optional Location object
        date: Optional RecordingDate object
        ragas: List of raga specifications. Accepts multiple formats:
            - AudioRaga objects: AudioRaga(name="Rageshree") (recommended)
            - Strings: "Rageshree" (auto-converted to AudioRaga)
            - Name dicts: {"name": "Rageshree"} (auto-converted to AudioRaga)
            - Legacy format: {"Rageshree": {"performance_sections": {}}} (auto-converted)
        sa_estimate: Optional fundamental frequency estimate in Hz
        permissions: Permissions object for access control
    """
    title: Optional[str] = None
    musicians: List[Musician] = field(default_factory=list)
    location: Optional[Location] = None
    date: Optional[RecordingDate] = None
    ragas: List[Union[Raga, str, Dict[str, Any]]] = field(default_factory=list)
    sa_estimate: Optional[float] = None
    permissions: Permissions = field(default_factory=Permissions)

    def _normalize_ragas(self, ragas: List[Union[Raga, str, Dict[str, Any]]]) -> List[Raga]:
        """Convert various raga input formats to AudioRaga objects."""
        normalized = []
        
        for i, raga in enumerate(ragas):
            if isinstance(raga, Raga):
                # Already an AudioRaga object
                normalized.append(raga)
            elif isinstance(raga, str):
                # String format: "Rageshree" -> AudioRaga(name="Rageshree")
                normalized.append(Raga(name=raga))
            elif isinstance(raga, dict):
                if 'name' in raga:
                    # Name dict format: {"name": "Rageshree"} -> AudioRaga(name="Rageshree")
                    normalized.append(Raga(name=raga['name']))
                elif len(raga) == 1:
                    # Legacy format: {"Rageshree": {...}} -> AudioRaga(name="Rageshree")
                    raga_name = list(raga.keys())[0]
                    normalized.append(Raga(name=raga_name))
                else:
                    raise ValueError(f"Raga at index {i}: Invalid dict format. "
                                   f"Use {{'name': 'RagaName'}} or AudioRaga(name='RagaName') instead.")
            else:
                # Check for wrong Raga class (musical analysis Raga)
                if hasattr(raga, 'name') and hasattr(raga, 'rule_set'):
                    raise ValueError(f"Raga at index {i}: Musical analysis Raga class not supported for uploads. "
                                   f"Use AudioRaga(name='{raga.name}') instead.")
                else:
                    raise ValueError(f"Raga at index {i}: Invalid raga format. "
                                   f"Expected AudioRaga object, string, or dict with 'name' key. "
                                   f"Got {type(raga).__name__}: {raga}")
        
        return normalized

    def _validate_ragas(self, ragas: List[Raga]) -> None:
        """Validate that all ragas are AudioRaga objects with to_json method."""
        for i, raga in enumerate(ragas):
            if not hasattr(raga, 'to_json'):
                raise ValueError(f"Raga at index {i}: Object missing to_json method. "
                               f"Expected AudioRaga object, got {type(raga).__name__}")
            if not hasattr(raga, 'name'):
                raise ValueError(f"Raga at index {i}: Object missing name attribute. "
                               f"Expected AudioRaga object, got {type(raga).__name__}")

    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON format for API."""
        # Convert musicians to dict format expected by API
        musicians_dict = {}
        for musician in self.musicians:
            musicians_dict[musician.name] = musician.to_json()

        # Normalize and validate ragas, then convert to dict format expected by API
        normalized_ragas = self._normalize_ragas(self.ragas)
        self._validate_ragas(normalized_ragas)
        
        ragas_dict = {}
        for raga in normalized_ragas:
            ragas_dict[raga.name] = raga.to_json()

        result = {
            'musicians': musicians_dict,
            'ragas': ragas_dict,
            'permissions': self.permissions.to_json()
        }

        if self.title:
            result['title'] = self.title
        if self.location:
            result['location'] = self.location.to_json()
        if self.date:
            result['date'] = self.date.to_json()
        if self.sa_estimate is not None:
            result['sa_estimate'] = self.sa_estimate

        return result


@dataclass
class AudioEventConfig:
    """Configuration for audio event association."""
    mode: Literal['add', 'create', 'none'] = 'none'
    event_id: Optional[str] = None  # For 'add' mode
    name: Optional[str] = None      # For 'create' mode
    event_type: Optional[str] = None # For 'create' mode

    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON format for API."""
        result = {'mode': self.mode}
        if self.event_id:
            result['event_id'] = self.event_id
        if self.name:
            result['name'] = self.name
        if self.event_type:
            result['event_type'] = self.event_type
        return result


@dataclass
class FileInfo:
    """Information about an uploaded file."""
    name: str
    mimetype: str
    size: int


@dataclass
class ProcessingStatus:
    """Status of audio processing operations."""
    audio_processed: bool = False
    melograph_generated: bool = False
    spectrogram_generated: bool = False


@dataclass
class AudioUploadResult:
    """Result of an audio upload operation."""
    audio_id: str
    success: bool
    file_info: FileInfo
    processing_status: ProcessingStatus

    @classmethod
    def from_api_response(cls, response_data: Dict[str, Any]) -> 'AudioUploadResult':
        """Create from API response."""
        file_info_data = response_data.get('file_info', {})
        file_info = FileInfo(
            name=file_info_data.get('name', ''),
            mimetype=file_info_data.get('mimetype', ''),
            size=file_info_data.get('size', 0)
        )
        
        processing_data = response_data.get('processing_status', {})
        processing_status = ProcessingStatus(
            audio_processed=processing_data.get('audio_processed', False),
            melograph_generated=processing_data.get('melograph_generated', False),
            spectrogram_generated=processing_data.get('spectrogram_generated', False)
        )
        
        return cls(
            audio_id=response_data.get('audio_id', ''),
            success=response_data.get('success', False),
            file_info=file_info,
            processing_status=processing_status
        )


@dataclass
class ValidationResult:
    """Result of metadata validation."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class LocationHierarchy:
    """Geographic location hierarchy."""
    data: Dict[str, Dict[str, List[str]]]  # continent -> country -> cities

    def get_continents(self) -> List[str]:
        """Get available continents."""
        return list(self.data.keys())

    def get_countries(self, continent: str) -> List[str]:
        """Get countries for a continent."""
        return list(self.data.get(continent, {}).keys())

    def get_cities(self, continent: str, country: str) -> List[str]:
        """Get cities for a country."""
        return self.data.get(continent, {}).get(country, [])

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'LocationHierarchy':
        """Create from API response."""
        return cls(data=data)