# Mapping from luminarycloud vis enums to LCVis equivalent values

import logging
from luminarycloud.enum import Representation, FieldComponent, ColorMapPreset

logger = logging.getLogger(__name__)


def representation_to_lcvis(representation: Representation) -> int:
    if representation == Representation.SURFACE:
        return 0
    if representation == Representation.SURFACE_WITH_EDGES:
        return 1
    if representation == Representation.WIREFRAME:
        return 2
    logger.error(f"{representation} is not supported by LCVis")
    return 0


def field_component_to_lcvis(comp: FieldComponent) -> int:
    if comp == FieldComponent.X:
        return 0
    if comp == FieldComponent.Y:
        return 1
    if comp == FieldComponent.Z:
        return 2
    if comp == FieldComponent.MAGNITUDE:
        return 3
    logger.error(f"Invalid FieldComponent {comp}")
    return 0


def color_map_preset_to_lcvis(preset: ColorMapPreset) -> str:
    if preset == ColorMapPreset.VIRIDIS:
        return "Viridis"
    if preset == ColorMapPreset.TURBO:
        return "Turbo"
    if preset == ColorMapPreset.JET:
        return "Jet"
    if preset == ColorMapPreset.PLASMA:
        return "Plasma (matplotlib)"
    if preset == ColorMapPreset.WAVE:
        return "Wave"
    if preset == ColorMapPreset.XRAY:
        return "X Ray"
    if preset == ColorMapPreset.COOL_TO_WARM:
        return "Cool to Warm"
    logger.error(f"Invalid ColorMapPreset {preset}")
    return "Turbo"
