import sys

from pydantic import BaseModel, ConfigDict

ALLOW_EXTRA = "allow" if "--allow-extra" in sys.argv else "forbid"


class BaseValidation(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra=ALLOW_EXTRA,
        use_enum_values=False,
        json_schema_mode_override="serialization",
        validate_assignment=True,
        protected_namespaces=(),
    )

    def __format__(self, format_spec: str) -> str:
        return f"{self!s:{format_spec}}"

    def model_dump_json(self, *, indent: int = 4) -> str:  # type: ignore[override]
        # alias is required for models since the PBIX format uses the alias version of attribute names
        # exclude_unset is required to avoid writing default values that are not present in the original PBIX.
        #  This can cause issues otherwise with visual configs
        # round_trip is required to return JSON types back to strings when 
        return super().model_dump_json(by_alias=True, exclude_unset=True, indent=indent, round_trip=True)
