from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class Config:
    """
    This is a fasade for the simulation configuration dictionary. and provides a getter for eatch seting that must be there. gives a error if somting critical is not set and a warning if somthing non critical is missing, and gives standard values for those. 
    """

    geometry: Dict[str, Any]
    settings: Dict[str, Any]
    IO: Dict[str, Any] = field(default_factory=dict)
    video: Dict[str, Any] = field(default_factory=dict)
    other: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Create a Config from a plain dict and validate it.

        Raises:
          - TypeError: when `data` is not a mapping/dict
          - ValueError: when required keys are missing
        """
        if not isinstance(data, dict):
            raise TypeError("Config data must be a dict-like mapping")

        geometry = data.get("geometry") or {}
        settings = data.get("settings") or {}
        io = data.get("IO") or {}
        video = data.get("video") or {}
        other = {k: v for k, v in data.items() if k not in ("geometry", "settings", "IO", "video")}

        cfg = cls(geometry=geometry, settings=settings, IO=io, video=video, other=other)
        cfg.validate()
        return cfg

    def validate(self) -> None:
        """Ensure minimal required configuration keys are present.

        This method raises a ValueError with a human-readable message
        when a required entry is missing.
        """
        if "meshName" not in self.geometry:
            raise ValueError("Missing required setting: geometry.meshName")

        for key in ("tStart", "tEnd", "nSteps"):
            if key not in self.settings:
                raise ValueError(f"Missing required setting: settings.{key}")

        # Set small, sensible defaults for optional entries
        self.IO.setdefault("writeFrequency", 0)
        self.video.setdefault("videoFPS", 30)

    # Convenience accessors with readable names
    def images_dir(self) -> str:
        """Return the images output directory (safe default provided)."""
        return str(self.IO.get("imagesDir", "Output/images/"))

    def mesh_name(self) -> str:
        """Return the mesh filename configured for this simulation."""
        return str(self.geometry.get("meshName"))

    def to_dict(self) -> Dict[str, Any]:
        """Return a plain dictionary representation compatible with older code."""
        base = {"geometry": self.geometry, "settings": self.settings, "IO": self.IO, "video": self.video}
        base.update(self.other or {})
        return base
