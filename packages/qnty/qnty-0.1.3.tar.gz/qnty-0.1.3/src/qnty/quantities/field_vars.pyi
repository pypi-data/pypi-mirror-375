"""
Type stubs for quantities module - Complete Edition.

Provides complete type hints for IDE autocomplete and type checking
for quantity classes and their setter relationships.
Contains 107 quantity types with 871 total units.

Auto-generated from unit_data.json.
"""

from typing import TYPE_CHECKING, Self, overload

if TYPE_CHECKING:
    from . import field_setter

from ..dimensions import field_dims as dim
from .base_qnty import TypeSafeSetter
from .field_qnty import FieldQnty

# ===== CONVERTER TYPE STUBS =====
# Unit conversion handled by base ToUnitConverter and AsUnitConverter classes
# with dynamic __getattr__ for unit method type hints


# ===== QUANTITY CLASSES =====
# Type stubs for quantity classes with setter relationships

class AbsorbedDose(FieldQnty):
    """
    Type-safe absorbed radiation dose quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - AbsorbedDose("variable_name") -> Create unknown absorbed radiation dose
    - AbsorbedDose(value, "unit", "variable_name") -> Create known absorbed radiation dose
    
    Examples:
    ---------
    >>> unknown = AbsorbedDose("pressure")  # Unknown absorbed radiation dose
    >>> known = AbsorbedDose(100, "erg_per_gram", "inlet_pressure")  # Known absorbed radiation dose
    
    Available units: "erg_per_gram", "gram_rad", "gray"
    """

    __slots__ = ()
    _setter_class = field_setter.AbsorbedDoseSetter
    _dimension = dim.ABSORBED_DOSE

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.AbsorbedDoseSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.AbsorbedDoseSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class Acceleration(FieldQnty):
    """
    Type-safe acceleration quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - Acceleration("variable_name") -> Create unknown acceleration
    - Acceleration(value, "unit", "variable_name") -> Create known acceleration
    
    Examples:
    ---------
    >>> unknown = Acceleration("pressure")  # Unknown acceleration
    >>> known = Acceleration(100, "meter_per_second_squared", "inlet_pressure")  # Known acceleration
    
    Available units: "meter_per_second_squared", "foot_per_second_squared"
    """

    __slots__ = ()
    _setter_class = field_setter.AccelerationSetter
    _dimension = dim.ACCELERATION

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.AccelerationSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.AccelerationSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class ActivationEnergy(FieldQnty):
    """
    Type-safe activation energy quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - ActivationEnergy("variable_name") -> Create unknown activation energy
    - ActivationEnergy(value, "unit", "variable_name") -> Create known activation energy
    
    Examples:
    ---------
    >>> unknown = ActivationEnergy("pressure")  # Unknown activation energy
    >>> known = ActivationEnergy(100, "btu_per_pound_mole", "inlet_pressure")  # Known activation energy
    
    Available units: "btu_per_pound_mole", "calorie_mean_per_gram_mole", "joule_per_gram_mole"
    """

    __slots__ = ()
    _setter_class = field_setter.ActivationEnergySetter
    _dimension = dim.ACTIVATION_ENERGY

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.ActivationEnergySetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.ActivationEnergySetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class AmountOfSubstance(FieldQnty):
    """
    Type-safe amount of substance quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - AmountOfSubstance("variable_name") -> Create unknown amount of substance
    - AmountOfSubstance(value, "unit", "variable_name") -> Create known amount of substance
    
    Examples:
    ---------
    >>> unknown = AmountOfSubstance("pressure")  # Unknown amount of substance
    >>> known = AmountOfSubstance(100, "kilogram_mol", "inlet_pressure")  # Known amount of substance
    
    Available units: "kilogram_mol", "mole", "pound_mole"
    """

    __slots__ = ()
    _setter_class = field_setter.AmountOfSubstanceSetter
    _dimension = dim.AMOUNT_OF_SUBSTANCE

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.AmountOfSubstanceSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.AmountOfSubstanceSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class AnglePlane(FieldQnty):
    """
    Type-safe angle, plane quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - AnglePlane("variable_name") -> Create unknown angle, plane
    - AnglePlane(value, "unit", "variable_name") -> Create known angle, plane
    
    Examples:
    ---------
    >>> unknown = AnglePlane("pressure")  # Unknown angle, plane
    >>> known = AnglePlane(100, "degree", "inlet_pressure")  # Known angle, plane
    
    Available units: "degree", "gon", "grade"
    """

    __slots__ = ()
    _setter_class = field_setter.AnglePlaneSetter
    _dimension = dim.ANGLE_PLANE

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.AnglePlaneSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.AnglePlaneSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class AngleSolid(FieldQnty):
    """
    Type-safe angle, solid quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - AngleSolid("variable_name") -> Create unknown angle, solid
    - AngleSolid(value, "unit", "variable_name") -> Create known angle, solid
    
    Examples:
    ---------
    >>> unknown = AngleSolid("pressure")  # Unknown angle, solid
    >>> known = AngleSolid(100, "spat", "inlet_pressure")  # Known angle, solid
    
    Available units: "spat", "square_degree", "square_gon"
    """

    __slots__ = ()
    _setter_class = field_setter.AngleSolidSetter
    _dimension = dim.ANGLE_SOLID

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.AngleSolidSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.AngleSolidSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class AngularAcceleration(FieldQnty):
    """
    Type-safe angular acceleration quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - AngularAcceleration("variable_name") -> Create unknown angular acceleration
    - AngularAcceleration(value, "unit", "variable_name") -> Create known angular acceleration
    
    Examples:
    ---------
    >>> unknown = AngularAcceleration("pressure")  # Unknown angular acceleration
    >>> known = AngularAcceleration(100, "radian_per_second_squared", "inlet_pressure")  # Known angular acceleration
    
    Available units: "radian_per_second_squared", "revolution_per_second_squared", "rpm_or_revolution_per_minute"
    """

    __slots__ = ()
    _setter_class = field_setter.AngularAccelerationSetter
    _dimension = dim.ANGULAR_ACCELERATION

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.AngularAccelerationSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.AngularAccelerationSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class AngularMomentum(FieldQnty):
    """
    Type-safe angular momentum quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - AngularMomentum("variable_name") -> Create unknown angular momentum
    - AngularMomentum(value, "unit", "variable_name") -> Create known angular momentum
    
    Examples:
    ---------
    >>> unknown = AngularMomentum("pressure")  # Unknown angular momentum
    >>> known = AngularMomentum(100, "gram_centimeter_squared_per_second", "inlet_pressure")  # Known angular momentum
    
    Available units: "gram_centimeter_squared_per_second", "kilogram_meter_squared_per_second", "pound_force_square_foot_per_second"
    """

    __slots__ = ()
    _setter_class = field_setter.AngularMomentumSetter
    _dimension = dim.ANGULAR_MOMENTUM

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.AngularMomentumSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.AngularMomentumSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class Area(FieldQnty):
    """
    Type-safe area quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - Area("variable_name") -> Create unknown area
    - Area(value, "unit", "variable_name") -> Create known area
    
    Examples:
    ---------
    >>> unknown = Area("pressure")  # Unknown area
    >>> known = Area(100, "acre_general", "inlet_pressure")  # Known area
    
    Available units: "acre_general", "are", "arpent_quebec"
    """

    __slots__ = ()
    _setter_class = field_setter.AreaSetter
    _dimension = dim.AREA

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.AreaSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.AreaSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class AreaPerUnitVolume(FieldQnty):
    """
    Type-safe area per unit volume quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - AreaPerUnitVolume("variable_name") -> Create unknown area per unit volume
    - AreaPerUnitVolume(value, "unit", "variable_name") -> Create known area per unit volume
    
    Examples:
    ---------
    >>> unknown = AreaPerUnitVolume("pressure")  # Unknown area per unit volume
    >>> known = AreaPerUnitVolume(100, "square_centimeter_per_cubic_centimeter", "inlet_pressure")  # Known area per unit volume
    
    Available units: "square_centimeter_per_cubic_centimeter", "square_foot_per_cubic_foot", "square_inch_per_cubic_inch"
    """

    __slots__ = ()
    _setter_class = field_setter.AreaPerUnitVolumeSetter
    _dimension = dim.AREA_PER_UNIT_VOLUME

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.AreaPerUnitVolumeSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.AreaPerUnitVolumeSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class AtomicWeight(FieldQnty):
    """
    Type-safe atomic weight quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - AtomicWeight("variable_name") -> Create unknown atomic weight
    - AtomicWeight(value, "unit", "variable_name") -> Create known atomic weight
    
    Examples:
    ---------
    >>> unknown = AtomicWeight("pressure")  # Unknown atomic weight
    >>> known = AtomicWeight(100, "atomic_mass_unit_12c", "inlet_pressure")  # Known atomic weight
    
    Available units: "atomic_mass_unit_12c", "grams_per_mole", "kilograms_per_kilomole"
    """

    __slots__ = ()
    _setter_class = field_setter.AtomicWeightSetter
    _dimension = dim.ATOMIC_WEIGHT

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.AtomicWeightSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.AtomicWeightSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class Concentration(FieldQnty):
    """
    Type-safe concentration quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - Concentration("variable_name") -> Create unknown concentration
    - Concentration(value, "unit", "variable_name") -> Create known concentration
    
    Examples:
    ---------
    >>> unknown = Concentration("pressure")  # Unknown concentration
    >>> known = Concentration(100, "grains_of_i_per_cubic_foot", "inlet_pressure")  # Known concentration
    
    Available units: "grains_of_i_per_cubic_foot", "grains_of_i_per_gallon_us"
    """

    __slots__ = ()
    _setter_class = field_setter.ConcentrationSetter
    _dimension = dim.CONCENTRATION

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.ConcentrationSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.ConcentrationSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class Dimensionless(FieldQnty):
    """
    Type-safe dimensionless quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - Dimensionless("variable_name") -> Create unknown dimensionless
    - Dimensionless(value, "variable_name") -> Create known dimensionless
    
    Examples:
    ---------
    >>> unknown = Dimensionless("efficiency")  # Unknown dimensionless
    >>> known = Dimensionless(0.85, "thermal_efficiency")  # Known dimensionless
    """

    __slots__ = ()
    _setter_class = field_setter.DimensionlessSetter
    _dimension = dim.DIMENSIONLESS

    def __init__(self, name_or_value: str | int | float, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.DimensionlessSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.DimensionlessSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class DynamicFluidity(FieldQnty):
    """
    Type-safe dynamic fluidity quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - DynamicFluidity("variable_name") -> Create unknown dynamic fluidity
    - DynamicFluidity(value, "unit", "variable_name") -> Create known dynamic fluidity
    
    Examples:
    ---------
    >>> unknown = DynamicFluidity("pressure")  # Unknown dynamic fluidity
    >>> known = DynamicFluidity(100, "meter_seconds_per_kilogram", "inlet_pressure")  # Known dynamic fluidity
    
    Available units: "meter_seconds_per_kilogram", "rhe", "square_foot_per_pound_second"
    """

    __slots__ = ()
    _setter_class = field_setter.DynamicFluiditySetter
    _dimension = dim.DYNAMIC_FLUIDITY

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.DynamicFluiditySetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.DynamicFluiditySetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class ElectricCapacitance(FieldQnty):
    """
    Type-safe electric capacitance quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - ElectricCapacitance("variable_name") -> Create unknown electric capacitance
    - ElectricCapacitance(value, "unit", "variable_name") -> Create known electric capacitance
    
    Examples:
    ---------
    >>> unknown = ElectricCapacitance("pressure")  # Unknown electric capacitance
    >>> known = ElectricCapacitance(100, "cm", "inlet_pressure")  # Known electric capacitance
    
    Available units: "cm", "abfarad", "farad"
    """

    __slots__ = ()
    _setter_class = field_setter.ElectricCapacitanceSetter
    _dimension = dim.ELECTRIC_CAPACITANCE

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.ElectricCapacitanceSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.ElectricCapacitanceSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class ElectricCharge(FieldQnty):
    """
    Type-safe electric charge quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - ElectricCharge("variable_name") -> Create unknown electric charge
    - ElectricCharge(value, "unit", "variable_name") -> Create known electric charge
    
    Examples:
    ---------
    >>> unknown = ElectricCharge("pressure")  # Unknown electric charge
    >>> known = ElectricCharge(100, "abcoulomb", "inlet_pressure")  # Known electric charge
    
    Available units: "abcoulomb", "ampere_hour", "coulomb"
    """

    __slots__ = ()
    _setter_class = field_setter.ElectricChargeSetter
    _dimension = dim.ELECTRIC_CHARGE

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.ElectricChargeSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.ElectricChargeSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class ElectricCurrentIntensity(FieldQnty):
    """
    Type-safe electric current intensity quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - ElectricCurrentIntensity("variable_name") -> Create unknown electric current intensity
    - ElectricCurrentIntensity(value, "unit", "variable_name") -> Create known electric current intensity
    
    Examples:
    ---------
    >>> unknown = ElectricCurrentIntensity("pressure")  # Unknown electric current intensity
    >>> known = ElectricCurrentIntensity(100, "abampere", "inlet_pressure")  # Known electric current intensity
    
    Available units: "abampere", "ampere_intl_mean", "ampere_intl_us"
    """

    __slots__ = ()
    _setter_class = field_setter.ElectricCurrentIntensitySetter
    _dimension = dim.ELECTRIC_CURRENT_INTENSITY

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.ElectricCurrentIntensitySetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.ElectricCurrentIntensitySetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class ElectricDipoleMoment(FieldQnty):
    """
    Type-safe electric dipole moment quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - ElectricDipoleMoment("variable_name") -> Create unknown electric dipole moment
    - ElectricDipoleMoment(value, "unit", "variable_name") -> Create known electric dipole moment
    
    Examples:
    ---------
    >>> unknown = ElectricDipoleMoment("pressure")  # Unknown electric dipole moment
    >>> known = ElectricDipoleMoment(100, "ampere_meter_second", "inlet_pressure")  # Known electric dipole moment
    
    Available units: "ampere_meter_second", "coulomb_meter", "debye"
    """

    __slots__ = ()
    _setter_class = field_setter.ElectricDipoleMomentSetter
    _dimension = dim.ELECTRIC_DIPOLE_MOMENT

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.ElectricDipoleMomentSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.ElectricDipoleMomentSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class ElectricFieldStrength(FieldQnty):
    """
    Type-safe electric field strength quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - ElectricFieldStrength("variable_name") -> Create unknown electric field strength
    - ElectricFieldStrength(value, "unit", "variable_name") -> Create known electric field strength
    
    Examples:
    ---------
    >>> unknown = ElectricFieldStrength("pressure")  # Unknown electric field strength
    >>> known = ElectricFieldStrength(100, "volt_per_centimeter", "inlet_pressure")  # Known electric field strength
    
    Available units: "volt_per_centimeter", "volt_per_meter"
    """

    __slots__ = ()
    _setter_class = field_setter.ElectricFieldStrengthSetter
    _dimension = dim.ELECTRIC_FIELD_STRENGTH

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.ElectricFieldStrengthSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.ElectricFieldStrengthSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class ElectricInductance(FieldQnty):
    """
    Type-safe electric inductance quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - ElectricInductance("variable_name") -> Create unknown electric inductance
    - ElectricInductance(value, "unit", "variable_name") -> Create known electric inductance
    
    Examples:
    ---------
    >>> unknown = ElectricInductance("pressure")  # Unknown electric inductance
    >>> known = ElectricInductance(100, "abhenry", "inlet_pressure")  # Known electric inductance
    
    Available units: "abhenry", "cm", "henry"
    """

    __slots__ = ()
    _setter_class = field_setter.ElectricInductanceSetter
    _dimension = dim.ELECTRIC_INDUCTANCE

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.ElectricInductanceSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.ElectricInductanceSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class ElectricPotential(FieldQnty):
    """
    Type-safe electric potential quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - ElectricPotential("variable_name") -> Create unknown electric potential
    - ElectricPotential(value, "unit", "variable_name") -> Create known electric potential
    
    Examples:
    ---------
    >>> unknown = ElectricPotential("pressure")  # Unknown electric potential
    >>> known = ElectricPotential(100, "abvolt", "inlet_pressure")  # Known electric potential
    
    Available units: "abvolt", "statvolt", "u_a_potential"
    """

    __slots__ = ()
    _setter_class = field_setter.ElectricPotentialSetter
    _dimension = dim.ELECTRIC_POTENTIAL

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.ElectricPotentialSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.ElectricPotentialSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class ElectricResistance(FieldQnty):
    """
    Type-safe electric resistance quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - ElectricResistance("variable_name") -> Create unknown electric resistance
    - ElectricResistance(value, "unit", "variable_name") -> Create known electric resistance
    
    Examples:
    ---------
    >>> unknown = ElectricResistance("pressure")  # Unknown electric resistance
    >>> known = ElectricResistance(100, "abohm", "inlet_pressure")  # Known electric resistance
    
    Available units: "abohm", "jacobi", "lenz"
    """

    __slots__ = ()
    _setter_class = field_setter.ElectricResistanceSetter
    _dimension = dim.ELECTRIC_RESISTANCE

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.ElectricResistanceSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.ElectricResistanceSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class ElectricalConductance(FieldQnty):
    """
    Type-safe electrical conductance quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - ElectricalConductance("variable_name") -> Create unknown electrical conductance
    - ElectricalConductance(value, "unit", "variable_name") -> Create known electrical conductance
    
    Examples:
    ---------
    >>> unknown = ElectricalConductance("pressure")  # Unknown electrical conductance
    >>> known = ElectricalConductance(100, "emu_cgs", "inlet_pressure")  # Known electrical conductance
    
    Available units: "emu_cgs", "esu_cgs", "mho"
    """

    __slots__ = ()
    _setter_class = field_setter.ElectricalConductanceSetter
    _dimension = dim.ELECTRICAL_CONDUCTANCE

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.ElectricalConductanceSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.ElectricalConductanceSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class ElectricalPermittivity(FieldQnty):
    """
    Type-safe electrical permittivity quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - ElectricalPermittivity("variable_name") -> Create unknown electrical permittivity
    - ElectricalPermittivity(value, "unit", "variable_name") -> Create known electrical permittivity
    
    Examples:
    ---------
    >>> unknown = ElectricalPermittivity("pressure")  # Unknown electrical permittivity
    >>> known = ElectricalPermittivity(100, "farad_per_meter", "inlet_pressure")  # Known electrical permittivity
    
    Available units: "farad_per_meter"
    """

    __slots__ = ()
    _setter_class = field_setter.ElectricalPermittivitySetter
    _dimension = dim.ELECTRICAL_PERMITTIVITY

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.ElectricalPermittivitySetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.ElectricalPermittivitySetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class ElectricalResistivity(FieldQnty):
    """
    Type-safe electrical resistivity quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - ElectricalResistivity("variable_name") -> Create unknown electrical resistivity
    - ElectricalResistivity(value, "unit", "variable_name") -> Create known electrical resistivity
    
    Examples:
    ---------
    >>> unknown = ElectricalResistivity("pressure")  # Unknown electrical resistivity
    >>> known = ElectricalResistivity(100, "circular_mil_ohm_per_foot", "inlet_pressure")  # Known electrical resistivity
    
    Available units: "circular_mil_ohm_per_foot", "emu_cgs", "microhm_inch"
    """

    __slots__ = ()
    _setter_class = field_setter.ElectricalResistivitySetter
    _dimension = dim.ELECTRICAL_RESISTIVITY

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.ElectricalResistivitySetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.ElectricalResistivitySetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class EnergyFlux(FieldQnty):
    """
    Type-safe energy flux quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - EnergyFlux("variable_name") -> Create unknown energy flux
    - EnergyFlux(value, "unit", "variable_name") -> Create known energy flux
    
    Examples:
    ---------
    >>> unknown = EnergyFlux("pressure")  # Unknown energy flux
    >>> known = EnergyFlux(100, "btu_per_square_foot_per_hour", "inlet_pressure")  # Known energy flux
    
    Available units: "btu_per_square_foot_per_hour", "calorie_per_square_centimeter_per_second", "celsius_heat_units_chu"
    """

    __slots__ = ()
    _setter_class = field_setter.EnergyFluxSetter
    _dimension = dim.ENERGY_FLUX

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.EnergyFluxSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.EnergyFluxSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class EnergyHeatWork(FieldQnty):
    """
    Type-safe energy, heat, work quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - EnergyHeatWork("variable_name") -> Create unknown energy, heat, work
    - EnergyHeatWork(value, "unit", "variable_name") -> Create known energy, heat, work
    
    Examples:
    ---------
    >>> unknown = EnergyHeatWork("pressure")  # Unknown energy, heat, work
    >>> known = EnergyHeatWork(100, "barrel_oil_equivalent_or_equivalent_barrel", "inlet_pressure")  # Known energy, heat, work
    
    Available units: "barrel_oil_equivalent_or_equivalent_barrel", "billion_electronvolt", "british_thermal_unit_4circ_mathrmc"
    """

    __slots__ = ()
    _setter_class = field_setter.EnergyHeatWorkSetter
    _dimension = dim.ENERGY_HEAT_WORK

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.EnergyHeatWorkSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.EnergyHeatWorkSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class EnergyPerUnitArea(FieldQnty):
    """
    Type-safe energy per unit area quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - EnergyPerUnitArea("variable_name") -> Create unknown energy per unit area
    - EnergyPerUnitArea(value, "unit", "variable_name") -> Create known energy per unit area
    
    Examples:
    ---------
    >>> unknown = EnergyPerUnitArea("pressure")  # Unknown energy per unit area
    >>> known = EnergyPerUnitArea(100, "british_thermal_unit_per_square_foot", "inlet_pressure")  # Known energy per unit area
    
    Available units: "british_thermal_unit_per_square_foot", "joule_per_square_meter", "langley"
    """

    __slots__ = ()
    _setter_class = field_setter.EnergyPerUnitAreaSetter
    _dimension = dim.ENERGY_PER_UNIT_AREA

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.EnergyPerUnitAreaSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.EnergyPerUnitAreaSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class Force(FieldQnty):
    """
    Type-safe force quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - Force("variable_name") -> Create unknown force
    - Force(value, "unit", "variable_name") -> Create known force
    
    Examples:
    ---------
    >>> unknown = Force("pressure")  # Unknown force
    >>> known = Force(100, "crinal", "inlet_pressure")  # Known force
    
    Available units: "crinal", "dyne", "funal"
    """

    __slots__ = ()
    _setter_class = field_setter.ForceSetter
    _dimension = dim.FORCE

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.ForceSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.ForceSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class ForceBody(FieldQnty):
    """
    Type-safe force (body) quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - ForceBody("variable_name") -> Create unknown force (body)
    - ForceBody(value, "unit", "variable_name") -> Create known force (body)
    
    Examples:
    ---------
    >>> unknown = ForceBody("pressure")  # Unknown force (body)
    >>> known = ForceBody(100, "dyne_per_cubic_centimeter", "inlet_pressure")  # Known force (body)
    
    Available units: "dyne_per_cubic_centimeter", "kilogram_force_per_cubic_centimeter", "kilogram_force_per_cubic_meter"
    """

    __slots__ = ()
    _setter_class = field_setter.ForceBodySetter
    _dimension = dim.FORCE_BODY

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.ForceBodySetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.ForceBodySetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class ForcePerUnitMass(FieldQnty):
    """
    Type-safe force per unit mass quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - ForcePerUnitMass("variable_name") -> Create unknown force per unit mass
    - ForcePerUnitMass(value, "unit", "variable_name") -> Create known force per unit mass
    
    Examples:
    ---------
    >>> unknown = ForcePerUnitMass("pressure")  # Unknown force per unit mass
    >>> known = ForcePerUnitMass(100, "dyne_per_gram", "inlet_pressure")  # Known force per unit mass
    
    Available units: "dyne_per_gram", "kilogram_force_per_kilogram", "newton_per_kilogram"
    """

    __slots__ = ()
    _setter_class = field_setter.ForcePerUnitMassSetter
    _dimension = dim.FORCE_PER_UNIT_MASS

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.ForcePerUnitMassSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.ForcePerUnitMassSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class FrequencyVoltageRatio(FieldQnty):
    """
    Type-safe frequency voltage ratio quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - FrequencyVoltageRatio("variable_name") -> Create unknown frequency voltage ratio
    - FrequencyVoltageRatio(value, "unit", "variable_name") -> Create known frequency voltage ratio
    
    Examples:
    ---------
    >>> unknown = FrequencyVoltageRatio("pressure")  # Unknown frequency voltage ratio
    >>> known = FrequencyVoltageRatio(100, "cycles_per_second_per_volt", "inlet_pressure")  # Known frequency voltage ratio
    
    Available units: "cycles_per_second_per_volt", "hertz_per_volt", "terahertz_per_volt"
    """

    __slots__ = ()
    _setter_class = field_setter.FrequencyVoltageRatioSetter
    _dimension = dim.FREQUENCY_VOLTAGE_RATIO

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.FrequencyVoltageRatioSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.FrequencyVoltageRatioSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class FuelConsumption(FieldQnty):
    """
    Type-safe fuel consumption quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - FuelConsumption("variable_name") -> Create unknown fuel consumption
    - FuelConsumption(value, "unit", "variable_name") -> Create known fuel consumption
    
    Examples:
    ---------
    >>> unknown = FuelConsumption("pressure")  # Unknown fuel consumption
    >>> known = FuelConsumption(100, "unit_100_km_per_liter", "inlet_pressure")  # Known fuel consumption
    
    Available units: "unit_100_km_per_liter", "gallons_uk", "gallons_us"
    """

    __slots__ = ()
    _setter_class = field_setter.FuelConsumptionSetter
    _dimension = dim.FUEL_CONSUMPTION

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.FuelConsumptionSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.FuelConsumptionSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class HeatOfCombustion(FieldQnty):
    """
    Type-safe heat of combustion quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - HeatOfCombustion("variable_name") -> Create unknown heat of combustion
    - HeatOfCombustion(value, "unit", "variable_name") -> Create known heat of combustion
    
    Examples:
    ---------
    >>> unknown = HeatOfCombustion("pressure")  # Unknown heat of combustion
    >>> known = HeatOfCombustion(100, "british_thermal_unit_per_pound", "inlet_pressure")  # Known heat of combustion
    
    Available units: "british_thermal_unit_per_pound", "calorie_per_gram", "chu_per_pound"
    """

    __slots__ = ()
    _setter_class = field_setter.HeatOfCombustionSetter
    _dimension = dim.HEAT_OF_COMBUSTION

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.HeatOfCombustionSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.HeatOfCombustionSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class HeatOfFusion(FieldQnty):
    """
    Type-safe heat of fusion quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - HeatOfFusion("variable_name") -> Create unknown heat of fusion
    - HeatOfFusion(value, "unit", "variable_name") -> Create known heat of fusion
    
    Examples:
    ---------
    >>> unknown = HeatOfFusion("pressure")  # Unknown heat of fusion
    >>> known = HeatOfFusion(100, "british_thermal_unit_mean", "inlet_pressure")  # Known heat of fusion
    
    Available units: "british_thermal_unit_mean", "british_thermal_unit_per_pound", "calorie_per_gram"
    """

    __slots__ = ()
    _setter_class = field_setter.HeatOfFusionSetter
    _dimension = dim.HEAT_OF_FUSION

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.HeatOfFusionSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.HeatOfFusionSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class HeatOfVaporization(FieldQnty):
    """
    Type-safe heat of vaporization quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - HeatOfVaporization("variable_name") -> Create unknown heat of vaporization
    - HeatOfVaporization(value, "unit", "variable_name") -> Create known heat of vaporization
    
    Examples:
    ---------
    >>> unknown = HeatOfVaporization("pressure")  # Unknown heat of vaporization
    >>> known = HeatOfVaporization(100, "british_thermal_unit_per_pound", "inlet_pressure")  # Known heat of vaporization
    
    Available units: "british_thermal_unit_per_pound", "calorie_per_gram", "chu_per_pound"
    """

    __slots__ = ()
    _setter_class = field_setter.HeatOfVaporizationSetter
    _dimension = dim.HEAT_OF_VAPORIZATION

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.HeatOfVaporizationSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.HeatOfVaporizationSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class HeatTransferCoefficient(FieldQnty):
    """
    Type-safe heat transfer coefficient quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - HeatTransferCoefficient("variable_name") -> Create unknown heat transfer coefficient
    - HeatTransferCoefficient(value, "unit", "variable_name") -> Create known heat transfer coefficient
    
    Examples:
    ---------
    >>> unknown = HeatTransferCoefficient("pressure")  # Unknown heat transfer coefficient
    >>> known = HeatTransferCoefficient(100, "btu_per_square_foot_per_hour_per_degree_fahrenheit_or_rankine", "inlet_pressure")  # Known heat transfer coefficient
    
    Available units: "btu_per_square_foot_per_hour_per_degree_fahrenheit_or_rankine", "watt_per_square_meter_per_degree_celsius_or_kelvin"
    """

    __slots__ = ()
    _setter_class = field_setter.HeatTransferCoefficientSetter
    _dimension = dim.HEAT_TRANSFER_COEFFICIENT

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.HeatTransferCoefficientSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.HeatTransferCoefficientSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class Illuminance(FieldQnty):
    """
    Type-safe illuminance quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - Illuminance("variable_name") -> Create unknown illuminance
    - Illuminance(value, "unit", "variable_name") -> Create known illuminance
    
    Examples:
    ---------
    >>> unknown = Illuminance("pressure")  # Unknown illuminance
    >>> known = Illuminance(100, "foot_candle", "inlet_pressure")  # Known illuminance
    
    Available units: "foot_candle", "lux", "nox"
    """

    __slots__ = ()
    _setter_class = field_setter.IlluminanceSetter
    _dimension = dim.ILLUMINANCE

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.IlluminanceSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.IlluminanceSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class KineticEnergyOfTurbulence(FieldQnty):
    """
    Type-safe kinetic energy of turbulence quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - KineticEnergyOfTurbulence("variable_name") -> Create unknown kinetic energy of turbulence
    - KineticEnergyOfTurbulence(value, "unit", "variable_name") -> Create known kinetic energy of turbulence
    
    Examples:
    ---------
    >>> unknown = KineticEnergyOfTurbulence("pressure")  # Unknown kinetic energy of turbulence
    >>> known = KineticEnergyOfTurbulence(100, "square_foot_per_second_squared", "inlet_pressure")  # Known kinetic energy of turbulence
    
    Available units: "square_foot_per_second_squared", "square_meters_per_second_squared"
    """

    __slots__ = ()
    _setter_class = field_setter.KineticEnergyOfTurbulenceSetter
    _dimension = dim.KINETIC_ENERGY_OF_TURBULENCE

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.KineticEnergyOfTurbulenceSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.KineticEnergyOfTurbulenceSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class Length(FieldQnty):
    """
    Type-safe length quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - Length("variable_name") -> Create unknown length
    - Length(value, "unit", "variable_name") -> Create known length
    
    Examples:
    ---------
    >>> unknown = Length("pressure")  # Unknown length
    >>> known = Length(100, "ngstr_m", "inlet_pressure")  # Known length
    
    Available units: "ngstr_m", "arpent_quebec", "astronomic_unit"
    """

    __slots__ = ()
    _setter_class = field_setter.LengthSetter
    _dimension = dim.LENGTH

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.LengthSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.LengthSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class LinearMassDensity(FieldQnty):
    """
    Type-safe linear mass density quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - LinearMassDensity("variable_name") -> Create unknown linear mass density
    - LinearMassDensity(value, "unit", "variable_name") -> Create known linear mass density
    
    Examples:
    ---------
    >>> unknown = LinearMassDensity("pressure")  # Unknown linear mass density
    >>> known = LinearMassDensity(100, "denier", "inlet_pressure")  # Known linear mass density
    
    Available units: "denier", "kilogram_per_centimeter", "kilogram_per_meter"
    """

    __slots__ = ()
    _setter_class = field_setter.LinearMassDensitySetter
    _dimension = dim.LINEAR_MASS_DENSITY

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.LinearMassDensitySetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.LinearMassDensitySetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class LinearMomentum(FieldQnty):
    """
    Type-safe linear momentum quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - LinearMomentum("variable_name") -> Create unknown linear momentum
    - LinearMomentum(value, "unit", "variable_name") -> Create known linear momentum
    
    Examples:
    ---------
    >>> unknown = LinearMomentum("pressure")  # Unknown linear momentum
    >>> known = LinearMomentum(100, "foot_pounds_force_per_hour", "inlet_pressure")  # Known linear momentum
    
    Available units: "foot_pounds_force_per_hour", "foot_pounds_force_per_minute", "foot_pounds_force_per_second"
    """

    __slots__ = ()
    _setter_class = field_setter.LinearMomentumSetter
    _dimension = dim.LINEAR_MOMENTUM

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.LinearMomentumSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.LinearMomentumSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class LuminanceSelf(FieldQnty):
    """
    Type-safe luminance (self) quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - LuminanceSelf("variable_name") -> Create unknown luminance (self)
    - LuminanceSelf(value, "unit", "variable_name") -> Create known luminance (self)
    
    Examples:
    ---------
    >>> unknown = LuminanceSelf("pressure")  # Unknown luminance (self)
    >>> known = LuminanceSelf(100, "apostilb", "inlet_pressure")  # Known luminance (self)
    
    Available units: "apostilb", "blondel", "candela_per_square_meter"
    """

    __slots__ = ()
    _setter_class = field_setter.LuminanceSelfSetter
    _dimension = dim.LUMINANCE_SELF

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.LuminanceSelfSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.LuminanceSelfSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class LuminousFlux(FieldQnty):
    """
    Type-safe luminous flux quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - LuminousFlux("variable_name") -> Create unknown luminous flux
    - LuminousFlux(value, "unit", "variable_name") -> Create known luminous flux
    
    Examples:
    ---------
    >>> unknown = LuminousFlux("pressure")  # Unknown luminous flux
    >>> known = LuminousFlux(100, "candela_steradian", "inlet_pressure")  # Known luminous flux
    
    Available units: "candela_steradian", "lumen"
    """

    __slots__ = ()
    _setter_class = field_setter.LuminousFluxSetter
    _dimension = dim.LUMINOUS_FLUX

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.LuminousFluxSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.LuminousFluxSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class LuminousIntensity(FieldQnty):
    """
    Type-safe luminous intensity quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - LuminousIntensity("variable_name") -> Create unknown luminous intensity
    - LuminousIntensity(value, "unit", "variable_name") -> Create known luminous intensity
    
    Examples:
    ---------
    >>> unknown = LuminousIntensity("pressure")  # Unknown luminous intensity
    >>> known = LuminousIntensity(100, "candela", "inlet_pressure")  # Known luminous intensity
    
    Available units: "candela", "candle_international", "carcel"
    """

    __slots__ = ()
    _setter_class = field_setter.LuminousIntensitySetter
    _dimension = dim.LUMINOUS_INTENSITY

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.LuminousIntensitySetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.LuminousIntensitySetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class MagneticField(FieldQnty):
    """
    Type-safe magnetic field quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MagneticField("variable_name") -> Create unknown magnetic field
    - MagneticField(value, "unit", "variable_name") -> Create known magnetic field
    
    Examples:
    ---------
    >>> unknown = MagneticField("pressure")  # Unknown magnetic field
    >>> known = MagneticField(100, "ampere_per_meter", "inlet_pressure")  # Known magnetic field
    
    Available units: "ampere_per_meter", "lenz", "oersted"
    """

    __slots__ = ()
    _setter_class = field_setter.MagneticFieldSetter
    _dimension = dim.MAGNETIC_FIELD

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.MagneticFieldSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.MagneticFieldSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class MagneticFlux(FieldQnty):
    """
    Type-safe magnetic flux quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MagneticFlux("variable_name") -> Create unknown magnetic flux
    - MagneticFlux(value, "unit", "variable_name") -> Create known magnetic flux
    
    Examples:
    ---------
    >>> unknown = MagneticFlux("pressure")  # Unknown magnetic flux
    >>> known = MagneticFlux(100, "kapp_line", "inlet_pressure")  # Known magnetic flux
    
    Available units: "kapp_line", "line", "maxwell"
    """

    __slots__ = ()
    _setter_class = field_setter.MagneticFluxSetter
    _dimension = dim.MAGNETIC_FLUX

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.MagneticFluxSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.MagneticFluxSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class MagneticInductionFieldStrength(FieldQnty):
    """
    Type-safe magnetic induction field strength quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MagneticInductionFieldStrength("variable_name") -> Create unknown magnetic induction field strength
    - MagneticInductionFieldStrength(value, "unit", "variable_name") -> Create known magnetic induction field strength
    
    Examples:
    ---------
    >>> unknown = MagneticInductionFieldStrength("pressure")  # Unknown magnetic induction field strength
    >>> known = MagneticInductionFieldStrength(100, "gamma", "inlet_pressure")  # Known magnetic induction field strength
    
    Available units: "gamma", "gauss", "line_per_square_centimeter"
    """

    __slots__ = ()
    _setter_class = field_setter.MagneticInductionFieldStrengthSetter
    _dimension = dim.MAGNETIC_INDUCTION_FIELD_STRENGTH

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.MagneticInductionFieldStrengthSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.MagneticInductionFieldStrengthSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class MagneticMoment(FieldQnty):
    """
    Type-safe magnetic moment quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MagneticMoment("variable_name") -> Create unknown magnetic moment
    - MagneticMoment(value, "unit", "variable_name") -> Create known magnetic moment
    
    Examples:
    ---------
    >>> unknown = MagneticMoment("pressure")  # Unknown magnetic moment
    >>> known = MagneticMoment(100, "bohr_magneton", "inlet_pressure")  # Known magnetic moment
    
    Available units: "bohr_magneton", "joule_per_tesla", "nuclear_magneton"
    """

    __slots__ = ()
    _setter_class = field_setter.MagneticMomentSetter
    _dimension = dim.MAGNETIC_MOMENT

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.MagneticMomentSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.MagneticMomentSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class MagneticPermeability(FieldQnty):
    """
    Type-safe magnetic permeability quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MagneticPermeability("variable_name") -> Create unknown magnetic permeability
    - MagneticPermeability(value, "unit", "variable_name") -> Create known magnetic permeability
    
    Examples:
    ---------
    >>> unknown = MagneticPermeability("pressure")  # Unknown magnetic permeability
    >>> known = MagneticPermeability(100, "henrys_per_meter", "inlet_pressure")  # Known magnetic permeability
    
    Available units: "henrys_per_meter", "newton_per_square_ampere"
    """

    __slots__ = ()
    _setter_class = field_setter.MagneticPermeabilitySetter
    _dimension = dim.MAGNETIC_PERMEABILITY

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.MagneticPermeabilitySetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.MagneticPermeabilitySetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class MagnetomotiveForce(FieldQnty):
    """
    Type-safe magnetomotive force quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MagnetomotiveForce("variable_name") -> Create unknown magnetomotive force
    - MagnetomotiveForce(value, "unit", "variable_name") -> Create known magnetomotive force
    
    Examples:
    ---------
    >>> unknown = MagnetomotiveForce("pressure")  # Unknown magnetomotive force
    >>> known = MagnetomotiveForce(100, "abampere_turn", "inlet_pressure")  # Known magnetomotive force
    
    Available units: "abampere_turn", "ampere", "ampere_turn"
    """

    __slots__ = ()
    _setter_class = field_setter.MagnetomotiveForceSetter
    _dimension = dim.MAGNETOMOTIVE_FORCE

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.MagnetomotiveForceSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.MagnetomotiveForceSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class Mass(FieldQnty):
    """
    Type-safe mass quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - Mass("variable_name") -> Create unknown mass
    - Mass(value, "unit", "variable_name") -> Create known mass
    
    Examples:
    ---------
    >>> unknown = Mass("pressure")  # Unknown mass
    >>> known = Mass(100, "slug", "inlet_pressure")  # Known mass
    
    Available units: "slug", "atomic_mass_unit_12_mathrmc", "carat_metric"
    """

    __slots__ = ()
    _setter_class = field_setter.MassSetter
    _dimension = dim.MASS

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.MassSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.MassSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class MassDensity(FieldQnty):
    """
    Type-safe mass density quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MassDensity("variable_name") -> Create unknown mass density
    - MassDensity(value, "unit", "variable_name") -> Create known mass density
    
    Examples:
    ---------
    >>> unknown = MassDensity("pressure")  # Unknown mass density
    >>> known = MassDensity(100, "gram_per_cubic_centimeter", "inlet_pressure")  # Known mass density
    
    Available units: "gram_per_cubic_centimeter", "gram_per_cubic_decimeter", "gram_per_cubic_meter"
    """

    __slots__ = ()
    _setter_class = field_setter.MassDensitySetter
    _dimension = dim.MASS_DENSITY

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.MassDensitySetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.MassDensitySetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class MassFlowRate(FieldQnty):
    """
    Type-safe mass flow rate quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MassFlowRate("variable_name") -> Create unknown mass flow rate
    - MassFlowRate(value, "unit", "variable_name") -> Create known mass flow rate
    
    Examples:
    ---------
    >>> unknown = MassFlowRate("pressure")  # Unknown mass flow rate
    >>> known = MassFlowRate(100, "kilograms_per_day", "inlet_pressure")  # Known mass flow rate
    
    Available units: "kilograms_per_day", "kilograms_per_hour", "kilograms_per_minute"
    """

    __slots__ = ()
    _setter_class = field_setter.MassFlowRateSetter
    _dimension = dim.MASS_FLOW_RATE

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.MassFlowRateSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.MassFlowRateSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class MassFlux(FieldQnty):
    """
    Type-safe mass flux quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MassFlux("variable_name") -> Create unknown mass flux
    - MassFlux(value, "unit", "variable_name") -> Create known mass flux
    
    Examples:
    ---------
    >>> unknown = MassFlux("pressure")  # Unknown mass flux
    >>> known = MassFlux(100, "kilogram_per_square_meter_per_day", "inlet_pressure")  # Known mass flux
    
    Available units: "kilogram_per_square_meter_per_day", "kilogram_per_square_meter_per_hour", "kilogram_per_square_meter_per_minute"
    """

    __slots__ = ()
    _setter_class = field_setter.MassFluxSetter
    _dimension = dim.MASS_FLUX

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.MassFluxSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.MassFluxSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class MassFractionOfI(FieldQnty):
    """
    Type-safe mass fraction of "i" quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MassFractionOfI("variable_name") -> Create unknown mass fraction of "i"
    - MassFractionOfI(value, "unit", "variable_name") -> Create known mass fraction of "i"
    
    Examples:
    ---------
    >>> unknown = MassFractionOfI("pressure")  # Unknown mass fraction of "i"
    >>> known = MassFractionOfI(100, "grains_of_i_per_pound_total", "inlet_pressure")  # Known mass fraction of "i"
    
    Available units: "grains_of_i_per_pound_total", "gram_of_i_per_kilogram_total", "kilogram_of_i_per_kilogram_total"
    """

    __slots__ = ()
    _setter_class = field_setter.MassFractionOfISetter
    _dimension = dim.MASS_FRACTION_OF_I

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.MassFractionOfISetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.MassFractionOfISetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class MassTransferCoefficient(FieldQnty):
    """
    Type-safe mass transfer coefficient quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MassTransferCoefficient("variable_name") -> Create unknown mass transfer coefficient
    - MassTransferCoefficient(value, "unit", "variable_name") -> Create known mass transfer coefficient
    
    Examples:
    ---------
    >>> unknown = MassTransferCoefficient("pressure")  # Unknown mass transfer coefficient
    >>> known = MassTransferCoefficient(100, "gram_per_square_centimeter_per_second", "inlet_pressure")  # Known mass transfer coefficient
    
    Available units: "gram_per_square_centimeter_per_second", "kilogram_per_square_meter_per_second", "pounds_force_per_cubic_foot_per_hour"
    """

    __slots__ = ()
    _setter_class = field_setter.MassTransferCoefficientSetter
    _dimension = dim.MASS_TRANSFER_COEFFICIENT

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.MassTransferCoefficientSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.MassTransferCoefficientSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class MolalityOfSoluteI(FieldQnty):
    """
    Type-safe molality of solute "i" quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MolalityOfSoluteI("variable_name") -> Create unknown molality of solute "i"
    - MolalityOfSoluteI(value, "unit", "variable_name") -> Create known molality of solute "i"
    
    Examples:
    ---------
    >>> unknown = MolalityOfSoluteI("pressure")  # Unknown molality of solute "i"
    >>> known = MolalityOfSoluteI(100, "gram_moles_of_i_per_kilogram", "inlet_pressure")  # Known molality of solute "i"
    
    Available units: "gram_moles_of_i_per_kilogram", "kilogram_mols_of_i_per_kilogram", "kmols_of_i_per_kilogram"
    """

    __slots__ = ()
    _setter_class = field_setter.MolalityOfSoluteISetter
    _dimension = dim.MOLALITY_OF_SOLUTE_I

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.MolalityOfSoluteISetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.MolalityOfSoluteISetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class MolarConcentrationByMass(FieldQnty):
    """
    Type-safe molar concentration by mass quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MolarConcentrationByMass("variable_name") -> Create unknown molar concentration by mass
    - MolarConcentrationByMass(value, "unit", "variable_name") -> Create known molar concentration by mass
    
    Examples:
    ---------
    >>> unknown = MolarConcentrationByMass("pressure")  # Unknown molar concentration by mass
    >>> known = MolarConcentrationByMass(100, "gram_mole_or_mole_per_gram", "inlet_pressure")  # Known molar concentration by mass
    
    Available units: "gram_mole_or_mole_per_gram", "gram_mole_or_mole_per_kilogram", "kilogram_mole_or_kmol_per_kilogram"
    """

    __slots__ = ()
    _setter_class = field_setter.MolarConcentrationByMassSetter
    _dimension = dim.MOLAR_CONCENTRATION_BY_MASS

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.MolarConcentrationByMassSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.MolarConcentrationByMassSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class MolarFlowRate(FieldQnty):
    """
    Type-safe molar flow rate quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MolarFlowRate("variable_name") -> Create unknown molar flow rate
    - MolarFlowRate(value, "unit", "variable_name") -> Create known molar flow rate
    
    Examples:
    ---------
    >>> unknown = MolarFlowRate("pressure")  # Unknown molar flow rate
    >>> known = MolarFlowRate(100, "gram_mole_per_day", "inlet_pressure")  # Known molar flow rate
    
    Available units: "gram_mole_per_day", "gram_mole_per_hour", "gram_mole_per_minute"
    """

    __slots__ = ()
    _setter_class = field_setter.MolarFlowRateSetter
    _dimension = dim.MOLAR_FLOW_RATE

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.MolarFlowRateSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.MolarFlowRateSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class MolarFlux(FieldQnty):
    """
    Type-safe molar flux quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MolarFlux("variable_name") -> Create unknown molar flux
    - MolarFlux(value, "unit", "variable_name") -> Create known molar flux
    
    Examples:
    ---------
    >>> unknown = MolarFlux("pressure")  # Unknown molar flux
    >>> known = MolarFlux(100, "kmol_per_square_meter_per_day", "inlet_pressure")  # Known molar flux
    
    Available units: "kmol_per_square_meter_per_day", "kmol_per_square_meter_per_hour", "kmol_per_square_meter_per_minute"
    """

    __slots__ = ()
    _setter_class = field_setter.MolarFluxSetter
    _dimension = dim.MOLAR_FLUX

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.MolarFluxSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.MolarFluxSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class MolarHeatCapacity(FieldQnty):
    """
    Type-safe molar heat capacity quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MolarHeatCapacity("variable_name") -> Create unknown molar heat capacity
    - MolarHeatCapacity(value, "unit", "variable_name") -> Create known molar heat capacity
    
    Examples:
    ---------
    >>> unknown = MolarHeatCapacity("pressure")  # Unknown molar heat capacity
    >>> known = MolarHeatCapacity(100, "btu_per_pound_mole_per_degree_fahrenheit_or_degree_rankine", "inlet_pressure")  # Known molar heat capacity
    
    Available units: "btu_per_pound_mole_per_degree_fahrenheit_or_degree_rankine", "calories_per_gram_mole_per_kelvin_or_degree_celsius", "joule_per_gram_mole_per_kelvin_or_degree_celsius"
    """

    __slots__ = ()
    _setter_class = field_setter.MolarHeatCapacitySetter
    _dimension = dim.MOLAR_HEAT_CAPACITY

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.MolarHeatCapacitySetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.MolarHeatCapacitySetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class MolarityOfI(FieldQnty):
    """
    Type-safe molarity of "i" quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MolarityOfI("variable_name") -> Create unknown molarity of "i"
    - MolarityOfI(value, "unit", "variable_name") -> Create known molarity of "i"
    
    Examples:
    ---------
    >>> unknown = MolarityOfI("pressure")  # Unknown molarity of "i"
    >>> known = MolarityOfI(100, "gram_moles_of_i_per_cubic_meter", "inlet_pressure")  # Known molarity of "i"
    
    Available units: "gram_moles_of_i_per_cubic_meter", "gram_moles_of_i_per_liter", "kilogram_moles_of_i_per_cubic_meter"
    """

    __slots__ = ()
    _setter_class = field_setter.MolarityOfISetter
    _dimension = dim.MOLARITY_OF_I

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.MolarityOfISetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.MolarityOfISetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class MoleFractionOfI(FieldQnty):
    """
    Type-safe mole fraction of "i" quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MoleFractionOfI("variable_name") -> Create unknown mole fraction of "i"
    - MoleFractionOfI(value, "unit", "variable_name") -> Create known mole fraction of "i"
    
    Examples:
    ---------
    >>> unknown = MoleFractionOfI("pressure")  # Unknown mole fraction of "i"
    >>> known = MoleFractionOfI(100, "gram_mole_of_i_per_gram_mole_total", "inlet_pressure")  # Known mole fraction of "i"
    
    Available units: "gram_mole_of_i_per_gram_mole_total", "kilogram_mole_of_i_per_kilogram_mole_total", "kilomole_of_i_per_kilomole_total"
    """

    __slots__ = ()
    _setter_class = field_setter.MoleFractionOfISetter
    _dimension = dim.MOLE_FRACTION_OF_I

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.MoleFractionOfISetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.MoleFractionOfISetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class MomentOfInertia(FieldQnty):
    """
    Type-safe moment of inertia quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MomentOfInertia("variable_name") -> Create unknown moment of inertia
    - MomentOfInertia(value, "unit", "variable_name") -> Create known moment of inertia
    
    Examples:
    ---------
    >>> unknown = MomentOfInertia("pressure")  # Unknown moment of inertia
    >>> known = MomentOfInertia(100, "gram_force_centimeter_square_second", "inlet_pressure")  # Known moment of inertia
    
    Available units: "gram_force_centimeter_square_second", "gram_square_centimeter", "kilogram_force_centimeter_square_second"
    """

    __slots__ = ()
    _setter_class = field_setter.MomentOfInertiaSetter
    _dimension = dim.MOMENT_OF_INERTIA

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.MomentOfInertiaSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.MomentOfInertiaSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class MomentumFlowRate(FieldQnty):
    """
    Type-safe momentum flow rate quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MomentumFlowRate("variable_name") -> Create unknown momentum flow rate
    - MomentumFlowRate(value, "unit", "variable_name") -> Create known momentum flow rate
    
    Examples:
    ---------
    >>> unknown = MomentumFlowRate("pressure")  # Unknown momentum flow rate
    >>> known = MomentumFlowRate(100, "foot_pounds_per_square_hour", "inlet_pressure")  # Known momentum flow rate
    
    Available units: "foot_pounds_per_square_hour", "foot_pounds_per_square_minute", "foot_pounds_per_square_second"
    """

    __slots__ = ()
    _setter_class = field_setter.MomentumFlowRateSetter
    _dimension = dim.MOMENTUM_FLOW_RATE

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.MomentumFlowRateSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.MomentumFlowRateSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class MomentumFlux(FieldQnty):
    """
    Type-safe momentum flux quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MomentumFlux("variable_name") -> Create unknown momentum flux
    - MomentumFlux(value, "unit", "variable_name") -> Create known momentum flux
    
    Examples:
    ---------
    >>> unknown = MomentumFlux("pressure")  # Unknown momentum flux
    >>> known = MomentumFlux(100, "dyne_per_square_centimeter", "inlet_pressure")  # Known momentum flux
    
    Available units: "dyne_per_square_centimeter", "gram_per_centimeter_per_square_second", "newton_per_square_meter"
    """

    __slots__ = ()
    _setter_class = field_setter.MomentumFluxSetter
    _dimension = dim.MOMENTUM_FLUX

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.MomentumFluxSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.MomentumFluxSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class NormalityOfSolution(FieldQnty):
    """
    Type-safe normality of solution quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - NormalityOfSolution("variable_name") -> Create unknown normality of solution
    - NormalityOfSolution(value, "unit", "variable_name") -> Create known normality of solution
    
    Examples:
    ---------
    >>> unknown = NormalityOfSolution("pressure")  # Unknown normality of solution
    >>> known = NormalityOfSolution(100, "gram_equivalents_per_cubic_meter", "inlet_pressure")  # Known normality of solution
    
    Available units: "gram_equivalents_per_cubic_meter", "gram_equivalents_per_liter", "pound_equivalents_per_cubic_foot"
    """

    __slots__ = ()
    _setter_class = field_setter.NormalityOfSolutionSetter
    _dimension = dim.NORMALITY_OF_SOLUTION

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.NormalityOfSolutionSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.NormalityOfSolutionSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class ParticleDensity(FieldQnty):
    """
    Type-safe particle density quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - ParticleDensity("variable_name") -> Create unknown particle density
    - ParticleDensity(value, "unit", "variable_name") -> Create known particle density
    
    Examples:
    ---------
    >>> unknown = ParticleDensity("pressure")  # Unknown particle density
    >>> known = ParticleDensity(100, "particles_per_cubic_centimeter", "inlet_pressure")  # Known particle density
    
    Available units: "particles_per_cubic_centimeter", "particles_per_cubic_foot", "particles_per_cubic_meter"
    """

    __slots__ = ()
    _setter_class = field_setter.ParticleDensitySetter
    _dimension = dim.PARTICLE_DENSITY

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.ParticleDensitySetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.ParticleDensitySetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class Percent(FieldQnty):
    """
    Type-safe percent quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - Percent("variable_name") -> Create unknown percent
    - Percent(value, "unit", "variable_name") -> Create known percent
    
    Examples:
    ---------
    >>> unknown = Percent("pressure")  # Unknown percent
    >>> known = Percent(100, "percent", "inlet_pressure")  # Known percent
    
    Available units: "percent", "per_mille", "basis_point"
    """

    __slots__ = ()
    _setter_class = field_setter.PercentSetter
    _dimension = dim.PERCENT

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.PercentSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.PercentSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class Permeability(FieldQnty):
    """
    Type-safe permeability quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - Permeability("variable_name") -> Create unknown permeability
    - Permeability(value, "unit", "variable_name") -> Create known permeability
    
    Examples:
    ---------
    >>> unknown = Permeability("pressure")  # Unknown permeability
    >>> known = Permeability(100, "darcy", "inlet_pressure")  # Known permeability
    
    Available units: "darcy", "square_feet", "square_meters"
    """

    __slots__ = ()
    _setter_class = field_setter.PermeabilitySetter
    _dimension = dim.PERMEABILITY

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.PermeabilitySetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.PermeabilitySetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class PhotonEmissionRate(FieldQnty):
    """
    Type-safe photon emission rate quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - PhotonEmissionRate("variable_name") -> Create unknown photon emission rate
    - PhotonEmissionRate(value, "unit", "variable_name") -> Create known photon emission rate
    
    Examples:
    ---------
    >>> unknown = PhotonEmissionRate("pressure")  # Unknown photon emission rate
    >>> known = PhotonEmissionRate(100, "rayleigh", "inlet_pressure")  # Known photon emission rate
    
    Available units: "rayleigh", "reciprocal_square_meter_second"
    """

    __slots__ = ()
    _setter_class = field_setter.PhotonEmissionRateSetter
    _dimension = dim.PHOTON_EMISSION_RATE

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.PhotonEmissionRateSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.PhotonEmissionRateSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class PowerPerUnitMass(FieldQnty):
    """
    Type-safe power per unit mass or specific power quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - PowerPerUnitMass("variable_name") -> Create unknown power per unit mass or specific power
    - PowerPerUnitMass(value, "unit", "variable_name") -> Create known power per unit mass or specific power
    
    Examples:
    ---------
    >>> unknown = PowerPerUnitMass("pressure")  # Unknown power per unit mass or specific power
    >>> known = PowerPerUnitMass(100, "british_thermal_unit_per_hour_per_pound_mass", "inlet_pressure")  # Known power per unit mass or specific power
    
    Available units: "british_thermal_unit_per_hour_per_pound_mass", "calorie_per_second_per_gram", "kilocalorie_per_hour_per_kilogram"
    """

    __slots__ = ()
    _setter_class = field_setter.PowerPerUnitMassSetter
    _dimension = dim.POWER_PER_UNIT_MASS

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.PowerPerUnitMassSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.PowerPerUnitMassSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class PowerPerUnitVolume(FieldQnty):
    """
    Type-safe power per unit volume or power density quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - PowerPerUnitVolume("variable_name") -> Create unknown power per unit volume or power density
    - PowerPerUnitVolume(value, "unit", "variable_name") -> Create known power per unit volume or power density
    
    Examples:
    ---------
    >>> unknown = PowerPerUnitVolume("pressure")  # Unknown power per unit volume or power density
    >>> known = PowerPerUnitVolume(100, "british_thermal_unit_per_hour_per_cubic_foot", "inlet_pressure")  # Known power per unit volume or power density
    
    Available units: "british_thermal_unit_per_hour_per_cubic_foot", "calorie_per_second_per_cubic_centimeter", "chu_per_hour_per_cubic_foot"
    """

    __slots__ = ()
    _setter_class = field_setter.PowerPerUnitVolumeSetter
    _dimension = dim.POWER_PER_UNIT_VOLUME

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.PowerPerUnitVolumeSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.PowerPerUnitVolumeSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class PowerThermalDuty(FieldQnty):
    """
    Type-safe power, thermal duty quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - PowerThermalDuty("variable_name") -> Create unknown power, thermal duty
    - PowerThermalDuty(value, "unit", "variable_name") -> Create known power, thermal duty
    
    Examples:
    ---------
    >>> unknown = PowerThermalDuty("pressure")  # Unknown power, thermal duty
    >>> known = PowerThermalDuty(100, "abwatt_emu_of_power", "inlet_pressure")  # Known power, thermal duty
    
    Available units: "abwatt_emu_of_power", "boiler_horsepower", "british_thermal_unit_mean"
    """

    __slots__ = ()
    _setter_class = field_setter.PowerThermalDutySetter
    _dimension = dim.POWER_THERMAL_DUTY

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.PowerThermalDutySetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.PowerThermalDutySetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class Pressure(FieldQnty):
    """
    Type-safe pressure quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - Pressure("variable_name") -> Create unknown pressure
    - Pressure(value, "unit", "variable_name") -> Create known pressure
    
    Examples:
    ---------
    >>> unknown = Pressure("pressure")  # Unknown pressure
    >>> known = Pressure(100, "atmosphere_standard", "inlet_pressure")  # Known pressure
    
    Available units: "atmosphere_standard", "bar", "barye"
    """

    __slots__ = ()
    _setter_class = field_setter.PressureSetter
    _dimension = dim.PRESSURE

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.PressureSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.PressureSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class RadiationDoseEquivalent(FieldQnty):
    """
    Type-safe radiation dose equivalent quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - RadiationDoseEquivalent("variable_name") -> Create unknown radiation dose equivalent
    - RadiationDoseEquivalent(value, "unit", "variable_name") -> Create known radiation dose equivalent
    
    Examples:
    ---------
    >>> unknown = RadiationDoseEquivalent("pressure")  # Unknown radiation dose equivalent
    >>> known = RadiationDoseEquivalent(100, "rem", "inlet_pressure")  # Known radiation dose equivalent
    
    Available units: "rem", "sievert", "millisievert"
    """

    __slots__ = ()
    _setter_class = field_setter.RadiationDoseEquivalentSetter
    _dimension = dim.RADIATION_DOSE_EQUIVALENT

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.RadiationDoseEquivalentSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.RadiationDoseEquivalentSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class RadiationExposure(FieldQnty):
    """
    Type-safe radiation exposure quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - RadiationExposure("variable_name") -> Create unknown radiation exposure
    - RadiationExposure(value, "unit", "variable_name") -> Create known radiation exposure
    
    Examples:
    ---------
    >>> unknown = RadiationExposure("pressure")  # Unknown radiation exposure
    >>> known = RadiationExposure(100, "coulomb_per_kilogram", "inlet_pressure")  # Known radiation exposure
    
    Available units: "coulomb_per_kilogram", "d_unit", "pastille_dose_b_unit"
    """

    __slots__ = ()
    _setter_class = field_setter.RadiationExposureSetter
    _dimension = dim.RADIATION_EXPOSURE

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.RadiationExposureSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.RadiationExposureSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class Radioactivity(FieldQnty):
    """
    Type-safe radioactivity quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - Radioactivity("variable_name") -> Create unknown radioactivity
    - Radioactivity(value, "unit", "variable_name") -> Create known radioactivity
    
    Examples:
    ---------
    >>> unknown = Radioactivity("pressure")  # Unknown radioactivity
    >>> known = Radioactivity(100, "becquerel", "inlet_pressure")  # Known radioactivity
    
    Available units: "becquerel", "curie", "mache_unit"
    """

    __slots__ = ()
    _setter_class = field_setter.RadioactivitySetter
    _dimension = dim.RADIOACTIVITY

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.RadioactivitySetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.RadioactivitySetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class SecondMomentOfArea(FieldQnty):
    """
    Type-safe second moment of area quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - SecondMomentOfArea("variable_name") -> Create unknown second moment of area
    - SecondMomentOfArea(value, "unit", "variable_name") -> Create known second moment of area
    
    Examples:
    ---------
    >>> unknown = SecondMomentOfArea("pressure")  # Unknown second moment of area
    >>> known = SecondMomentOfArea(100, "inch_quadrupled", "inlet_pressure")  # Known second moment of area
    
    Available units: "inch_quadrupled", "centimeter_quadrupled", "foot_quadrupled"
    """

    __slots__ = ()
    _setter_class = field_setter.SecondMomentOfAreaSetter
    _dimension = dim.SECOND_MOMENT_OF_AREA

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.SecondMomentOfAreaSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.SecondMomentOfAreaSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class SecondRadiationConstantPlanck(FieldQnty):
    """
    Type-safe second radiation constant (planck) quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - SecondRadiationConstantPlanck("variable_name") -> Create unknown second radiation constant (planck)
    - SecondRadiationConstantPlanck(value, "unit", "variable_name") -> Create known second radiation constant (planck)
    
    Examples:
    ---------
    >>> unknown = SecondRadiationConstantPlanck("pressure")  # Unknown second radiation constant (planck)
    >>> known = SecondRadiationConstantPlanck(100, "meter_kelvin", "inlet_pressure")  # Known second radiation constant (planck)
    
    Available units: "meter_kelvin"
    """

    __slots__ = ()
    _setter_class = field_setter.SecondRadiationConstantPlanckSetter
    _dimension = dim.SECOND_RADIATION_CONSTANT_PLANCK

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.SecondRadiationConstantPlanckSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.SecondRadiationConstantPlanckSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class SpecificEnthalpy(FieldQnty):
    """
    Type-safe specific enthalpy quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - SpecificEnthalpy("variable_name") -> Create unknown specific enthalpy
    - SpecificEnthalpy(value, "unit", "variable_name") -> Create known specific enthalpy
    
    Examples:
    ---------
    >>> unknown = SpecificEnthalpy("pressure")  # Unknown specific enthalpy
    >>> known = SpecificEnthalpy(100, "british_thermal_unit_mean", "inlet_pressure")  # Known specific enthalpy
    
    Available units: "british_thermal_unit_mean", "british_thermal_unit_per_pound", "calorie_per_gram"
    """

    __slots__ = ()
    _setter_class = field_setter.SpecificEnthalpySetter
    _dimension = dim.SPECIFIC_ENTHALPY

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.SpecificEnthalpySetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.SpecificEnthalpySetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class SpecificGravity(FieldQnty):
    """
    Type-safe specific gravity quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - SpecificGravity("variable_name") -> Create unknown specific gravity
    - SpecificGravity(value, "unit", "variable_name") -> Create known specific gravity
    
    Examples:
    ---------
    >>> unknown = SpecificGravity("pressure")  # Unknown specific gravity
    >>> known = SpecificGravity(100, "dimensionless", "inlet_pressure")  # Known specific gravity
    
    Available units: "dimensionless"
    """

    __slots__ = ()
    _setter_class = field_setter.SpecificGravitySetter
    _dimension = dim.SPECIFIC_GRAVITY

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.SpecificGravitySetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.SpecificGravitySetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class SpecificHeatCapacityConstantPressure(FieldQnty):
    """
    Type-safe specific heat capacity (constant pressure) quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - SpecificHeatCapacityConstantPressure("variable_name") -> Create unknown specific heat capacity (constant pressure)
    - SpecificHeatCapacityConstantPressure(value, "unit", "variable_name") -> Create known specific heat capacity (constant pressure)
    
    Examples:
    ---------
    >>> unknown = SpecificHeatCapacityConstantPressure("pressure")  # Unknown specific heat capacity (constant pressure)
    >>> known = SpecificHeatCapacityConstantPressure(100, "btu_per_pound_per_degree_fahrenheit_or_degree_rankine", "inlet_pressure")  # Known specific heat capacity (constant pressure)
    
    Available units: "btu_per_pound_per_degree_fahrenheit_or_degree_rankine", "calories_per_gram_per_kelvin_or_degree_celsius", "joules_per_kilogram_per_kelvin_or_degree_celsius"
    """

    __slots__ = ()
    _setter_class = field_setter.SpecificHeatCapacityConstantPressureSetter
    _dimension = dim.SPECIFIC_HEAT_CAPACITY_CONSTANT_PRESSURE

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.SpecificHeatCapacityConstantPressureSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.SpecificHeatCapacityConstantPressureSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class SpecificLength(FieldQnty):
    """
    Type-safe specific length quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - SpecificLength("variable_name") -> Create unknown specific length
    - SpecificLength(value, "unit", "variable_name") -> Create known specific length
    
    Examples:
    ---------
    >>> unknown = SpecificLength("pressure")  # Unknown specific length
    >>> known = SpecificLength(100, "centimeter_per_gram", "inlet_pressure")  # Known specific length
    
    Available units: "centimeter_per_gram", "cotton_count", "ft_per_pound"
    """

    __slots__ = ()
    _setter_class = field_setter.SpecificLengthSetter
    _dimension = dim.SPECIFIC_LENGTH

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.SpecificLengthSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.SpecificLengthSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class SpecificSurface(FieldQnty):
    """
    Type-safe specific surface quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - SpecificSurface("variable_name") -> Create unknown specific surface
    - SpecificSurface(value, "unit", "variable_name") -> Create known specific surface
    
    Examples:
    ---------
    >>> unknown = SpecificSurface("pressure")  # Unknown specific surface
    >>> known = SpecificSurface(100, "square_centimeter_per_gram", "inlet_pressure")  # Known specific surface
    
    Available units: "square_centimeter_per_gram", "square_foot_per_kilogram", "square_foot_per_pound"
    """

    __slots__ = ()
    _setter_class = field_setter.SpecificSurfaceSetter
    _dimension = dim.SPECIFIC_SURFACE

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.SpecificSurfaceSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.SpecificSurfaceSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class SpecificVolume(FieldQnty):
    """
    Type-safe specific volume quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - SpecificVolume("variable_name") -> Create unknown specific volume
    - SpecificVolume(value, "unit", "variable_name") -> Create known specific volume
    
    Examples:
    ---------
    >>> unknown = SpecificVolume("pressure")  # Unknown specific volume
    >>> known = SpecificVolume(100, "cubic_centimeter_per_gram", "inlet_pressure")  # Known specific volume
    
    Available units: "cubic_centimeter_per_gram", "cubic_foot_per_kilogram", "cubic_foot_per_pound"
    """

    __slots__ = ()
    _setter_class = field_setter.SpecificVolumeSetter
    _dimension = dim.SPECIFIC_VOLUME

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.SpecificVolumeSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.SpecificVolumeSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class Stress(FieldQnty):
    """
    Type-safe stress quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - Stress("variable_name") -> Create unknown stress
    - Stress(value, "unit", "variable_name") -> Create known stress
    
    Examples:
    ---------
    >>> unknown = Stress("pressure")  # Unknown stress
    >>> known = Stress(100, "dyne_per_square_centimeter", "inlet_pressure")  # Known stress
    
    Available units: "dyne_per_square_centimeter", "gigapascal", "hectopascal"
    """

    __slots__ = ()
    _setter_class = field_setter.StressSetter
    _dimension = dim.STRESS

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.StressSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.StressSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class SurfaceMassDensity(FieldQnty):
    """
    Type-safe surface mass density quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - SurfaceMassDensity("variable_name") -> Create unknown surface mass density
    - SurfaceMassDensity(value, "unit", "variable_name") -> Create known surface mass density
    
    Examples:
    ---------
    >>> unknown = SurfaceMassDensity("pressure")  # Unknown surface mass density
    >>> known = SurfaceMassDensity(100, "gram_per_square_centimeter", "inlet_pressure")  # Known surface mass density
    
    Available units: "gram_per_square_centimeter", "gram_per_square_meter", "kilogram_per_square_meter"
    """

    __slots__ = ()
    _setter_class = field_setter.SurfaceMassDensitySetter
    _dimension = dim.SURFACE_MASS_DENSITY

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.SurfaceMassDensitySetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.SurfaceMassDensitySetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class SurfaceTension(FieldQnty):
    """
    Type-safe surface tension quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - SurfaceTension("variable_name") -> Create unknown surface tension
    - SurfaceTension(value, "unit", "variable_name") -> Create known surface tension
    
    Examples:
    ---------
    >>> unknown = SurfaceTension("pressure")  # Unknown surface tension
    >>> known = SurfaceTension(100, "dyne_per_centimeter", "inlet_pressure")  # Known surface tension
    
    Available units: "dyne_per_centimeter", "gram_force_per_centimeter", "newton_per_meter"
    """

    __slots__ = ()
    _setter_class = field_setter.SurfaceTensionSetter
    _dimension = dim.SURFACE_TENSION

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.SurfaceTensionSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.SurfaceTensionSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class Temperature(FieldQnty):
    """
    Type-safe temperature quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - Temperature("variable_name") -> Create unknown temperature
    - Temperature(value, "unit", "variable_name") -> Create known temperature
    
    Examples:
    ---------
    >>> unknown = Temperature("pressure")  # Unknown temperature
    >>> known = Temperature(100, "degree_celsius_unit_size", "inlet_pressure")  # Known temperature
    
    Available units: "degree_celsius_unit_size", "degree_fahrenheit_unit_size", "degree_r_aumur_unit_size"
    """

    __slots__ = ()
    _setter_class = field_setter.TemperatureSetter
    _dimension = dim.TEMPERATURE

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.TemperatureSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.TemperatureSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class ThermalConductivity(FieldQnty):
    """
    Type-safe thermal conductivity quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - ThermalConductivity("variable_name") -> Create unknown thermal conductivity
    - ThermalConductivity(value, "unit", "variable_name") -> Create known thermal conductivity
    
    Examples:
    ---------
    >>> unknown = ThermalConductivity("pressure")  # Unknown thermal conductivity
    >>> known = ThermalConductivity(100, "btu_it", "inlet_pressure")  # Known thermal conductivity
    
    Available units: "btu_it", "btu_therm", "btu_therm"
    """

    __slots__ = ()
    _setter_class = field_setter.ThermalConductivitySetter
    _dimension = dim.THERMAL_CONDUCTIVITY

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.ThermalConductivitySetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.ThermalConductivitySetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class Time(FieldQnty):
    """
    Type-safe time quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - Time("variable_name") -> Create unknown time
    - Time(value, "unit", "variable_name") -> Create known time
    
    Examples:
    ---------
    >>> unknown = Time("pressure")  # Unknown time
    >>> known = Time(100, "blink", "inlet_pressure")  # Known time
    
    Available units: "blink", "century", "chronon_or_tempon"
    """

    __slots__ = ()
    _setter_class = field_setter.TimeSetter
    _dimension = dim.TIME

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.TimeSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.TimeSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class Torque(FieldQnty):
    """
    Type-safe torque quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - Torque("variable_name") -> Create unknown torque
    - Torque(value, "unit", "variable_name") -> Create known torque
    
    Examples:
    ---------
    >>> unknown = Torque("pressure")  # Unknown torque
    >>> known = Torque(100, "centimeter_kilogram_force", "inlet_pressure")  # Known torque
    
    Available units: "centimeter_kilogram_force", "dyne_centimeter", "foot_kilogram_force"
    """

    __slots__ = ()
    _setter_class = field_setter.TorqueSetter
    _dimension = dim.TORQUE

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.TorqueSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.TorqueSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class TurbulenceEnergyDissipationRate(FieldQnty):
    """
    Type-safe turbulence energy dissipation rate quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - TurbulenceEnergyDissipationRate("variable_name") -> Create unknown turbulence energy dissipation rate
    - TurbulenceEnergyDissipationRate(value, "unit", "variable_name") -> Create known turbulence energy dissipation rate
    
    Examples:
    ---------
    >>> unknown = TurbulenceEnergyDissipationRate("pressure")  # Unknown turbulence energy dissipation rate
    >>> known = TurbulenceEnergyDissipationRate(100, "square_foot_per_cubic_second", "inlet_pressure")  # Known turbulence energy dissipation rate
    
    Available units: "square_foot_per_cubic_second", "square_meter_per_cubic_second"
    """

    __slots__ = ()
    _setter_class = field_setter.TurbulenceEnergyDissipationRateSetter
    _dimension = dim.TURBULENCE_ENERGY_DISSIPATION_RATE

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.TurbulenceEnergyDissipationRateSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.TurbulenceEnergyDissipationRateSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class VelocityAngular(FieldQnty):
    """
    Type-safe velocity, angular quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - VelocityAngular("variable_name") -> Create unknown velocity, angular
    - VelocityAngular(value, "unit", "variable_name") -> Create known velocity, angular
    
    Examples:
    ---------
    >>> unknown = VelocityAngular("pressure")  # Unknown velocity, angular
    >>> known = VelocityAngular(100, "degree_per_minute", "inlet_pressure")  # Known velocity, angular
    
    Available units: "degree_per_minute", "degree_per_second", "grade_per_minute"
    """

    __slots__ = ()
    _setter_class = field_setter.VelocityAngularSetter
    _dimension = dim.VELOCITY_ANGULAR

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.VelocityAngularSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.VelocityAngularSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class VelocityLinear(FieldQnty):
    """
    Type-safe velocity, linear quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - VelocityLinear("variable_name") -> Create unknown velocity, linear
    - VelocityLinear(value, "unit", "variable_name") -> Create known velocity, linear
    
    Examples:
    ---------
    >>> unknown = VelocityLinear("pressure")  # Unknown velocity, linear
    >>> known = VelocityLinear(100, "foot_per_hour", "inlet_pressure")  # Known velocity, linear
    
    Available units: "foot_per_hour", "foot_per_minute", "foot_per_second"
    """

    __slots__ = ()
    _setter_class = field_setter.VelocityLinearSetter
    _dimension = dim.VELOCITY_LINEAR

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.VelocityLinearSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.VelocityLinearSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class ViscosityDynamic(FieldQnty):
    """
    Type-safe viscosity, dynamic quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - ViscosityDynamic("variable_name") -> Create unknown viscosity, dynamic
    - ViscosityDynamic(value, "unit", "variable_name") -> Create known viscosity, dynamic
    
    Examples:
    ---------
    >>> unknown = ViscosityDynamic("pressure")  # Unknown viscosity, dynamic
    >>> known = ViscosityDynamic(100, "centipoise", "inlet_pressure")  # Known viscosity, dynamic
    
    Available units: "centipoise", "dyne_second_per_square_centimeter", "kilopound_second_per_square_meter"
    """

    __slots__ = ()
    _setter_class = field_setter.ViscosityDynamicSetter
    _dimension = dim.VISCOSITY_DYNAMIC

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.ViscosityDynamicSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.ViscosityDynamicSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class ViscosityKinematic(FieldQnty):
    """
    Type-safe viscosity, kinematic quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - ViscosityKinematic("variable_name") -> Create unknown viscosity, kinematic
    - ViscosityKinematic(value, "unit", "variable_name") -> Create known viscosity, kinematic
    
    Examples:
    ---------
    >>> unknown = ViscosityKinematic("pressure")  # Unknown viscosity, kinematic
    >>> known = ViscosityKinematic(100, "centistokes", "inlet_pressure")  # Known viscosity, kinematic
    
    Available units: "centistokes", "millistokes", "square_centimeter_per_second"
    """

    __slots__ = ()
    _setter_class = field_setter.ViscosityKinematicSetter
    _dimension = dim.VISCOSITY_KINEMATIC

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.ViscosityKinematicSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.ViscosityKinematicSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class Volume(FieldQnty):
    """
    Type-safe volume quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - Volume("variable_name") -> Create unknown volume
    - Volume(value, "unit", "variable_name") -> Create known volume
    
    Examples:
    ---------
    >>> unknown = Volume("pressure")  # Unknown volume
    >>> known = Volume(100, "acre_foot", "inlet_pressure")  # Known volume
    
    Available units: "acre_foot", "acre_inch", "barrel_us_liquid"
    """

    __slots__ = ()
    _setter_class = field_setter.VolumeSetter
    _dimension = dim.VOLUME

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.VolumeSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.VolumeSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class VolumeFractionOfI(FieldQnty):
    """
    Type-safe volume fraction of "i" quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - VolumeFractionOfI("variable_name") -> Create unknown volume fraction of "i"
    - VolumeFractionOfI(value, "unit", "variable_name") -> Create known volume fraction of "i"
    
    Examples:
    ---------
    >>> unknown = VolumeFractionOfI("pressure")  # Unknown volume fraction of "i"
    >>> known = VolumeFractionOfI(100, "cubic_centimeters_of_i_per_cubic_meter_total", "inlet_pressure")  # Known volume fraction of "i"
    
    Available units: "cubic_centimeters_of_i_per_cubic_meter_total", "cubic_foot_of_i_per_cubic_foot_total", "cubic_meters_of_i_per_cubic_meter_total"
    """

    __slots__ = ()
    _setter_class = field_setter.VolumeFractionOfISetter
    _dimension = dim.VOLUME_FRACTION_OF_I

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.VolumeFractionOfISetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.VolumeFractionOfISetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class VolumetricCalorificHeatingValue(FieldQnty):
    """
    Type-safe volumetric calorific (heating) value quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - VolumetricCalorificHeatingValue("variable_name") -> Create unknown volumetric calorific (heating) value
    - VolumetricCalorificHeatingValue(value, "unit", "variable_name") -> Create known volumetric calorific (heating) value
    
    Examples:
    ---------
    >>> unknown = VolumetricCalorificHeatingValue("pressure")  # Unknown volumetric calorific (heating) value
    >>> known = VolumetricCalorificHeatingValue(100, "british_thermal_unit_per_cubic_foot", "inlet_pressure")  # Known volumetric calorific (heating) value
    
    Available units: "british_thermal_unit_per_cubic_foot", "british_thermal_unit_per_gallon_uk", "british_thermal_unit_per_gallon_us"
    """

    __slots__ = ()
    _setter_class = field_setter.VolumetricCalorificHeatingValueSetter
    _dimension = dim.VOLUMETRIC_CALORIFIC_HEATING_VALUE

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.VolumetricCalorificHeatingValueSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.VolumetricCalorificHeatingValueSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class VolumetricCoefficientOfExpansion(FieldQnty):
    """
    Type-safe volumetric coefficient of expansion quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - VolumetricCoefficientOfExpansion("variable_name") -> Create unknown volumetric coefficient of expansion
    - VolumetricCoefficientOfExpansion(value, "unit", "variable_name") -> Create known volumetric coefficient of expansion
    
    Examples:
    ---------
    >>> unknown = VolumetricCoefficientOfExpansion("pressure")  # Unknown volumetric coefficient of expansion
    >>> known = VolumetricCoefficientOfExpansion(100, "gram_per_cubic_centimeter_per_kelvin_or_degree_celsius", "inlet_pressure")  # Known volumetric coefficient of expansion
    
    Available units: "gram_per_cubic_centimeter_per_kelvin_or_degree_celsius", "kilogram_per_cubic_meter_per_kelvin_or_degree_celsius", "pound_per_cubic_foot_per_degree_fahrenheit_or_degree_rankine"
    """

    __slots__ = ()
    _setter_class = field_setter.VolumetricCoefficientOfExpansionSetter
    _dimension = dim.VOLUMETRIC_COEFFICIENT_OF_EXPANSION

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.VolumetricCoefficientOfExpansionSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.VolumetricCoefficientOfExpansionSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class VolumetricFlowRate(FieldQnty):
    """
    Type-safe volumetric flow rate quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - VolumetricFlowRate("variable_name") -> Create unknown volumetric flow rate
    - VolumetricFlowRate(value, "unit", "variable_name") -> Create known volumetric flow rate
    
    Examples:
    ---------
    >>> unknown = VolumetricFlowRate("pressure")  # Unknown volumetric flow rate
    >>> known = VolumetricFlowRate(100, "cubic_feet_per_day", "inlet_pressure")  # Known volumetric flow rate
    
    Available units: "cubic_feet_per_day", "cubic_feet_per_hour", "cubic_feet_per_minute"
    """

    __slots__ = ()
    _setter_class = field_setter.VolumetricFlowRateSetter
    _dimension = dim.VOLUMETRIC_FLOW_RATE

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.VolumetricFlowRateSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.VolumetricFlowRateSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class VolumetricFlux(FieldQnty):
    """
    Type-safe volumetric flux quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - VolumetricFlux("variable_name") -> Create unknown volumetric flux
    - VolumetricFlux(value, "unit", "variable_name") -> Create known volumetric flux
    
    Examples:
    ---------
    >>> unknown = VolumetricFlux("pressure")  # Unknown volumetric flux
    >>> known = VolumetricFlux(100, "cubic_feet_per_square_foot_per_day", "inlet_pressure")  # Known volumetric flux
    
    Available units: "cubic_feet_per_square_foot_per_day", "cubic_feet_per_square_foot_per_hour", "cubic_feet_per_square_foot_per_minute"
    """

    __slots__ = ()
    _setter_class = field_setter.VolumetricFluxSetter
    _dimension = dim.VOLUMETRIC_FLUX

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.VolumetricFluxSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.VolumetricFluxSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class VolumetricMassFlowRate(FieldQnty):
    """
    Type-safe volumetric mass flow rate quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - VolumetricMassFlowRate("variable_name") -> Create unknown volumetric mass flow rate
    - VolumetricMassFlowRate(value, "unit", "variable_name") -> Create known volumetric mass flow rate
    
    Examples:
    ---------
    >>> unknown = VolumetricMassFlowRate("pressure")  # Unknown volumetric mass flow rate
    >>> known = VolumetricMassFlowRate(100, "gram_per_second_per_cubic_centimeter", "inlet_pressure")  # Known volumetric mass flow rate
    
    Available units: "gram_per_second_per_cubic_centimeter", "kilogram_per_hour_per_cubic_foot", "kilogram_per_hour_per_cubic_meter"
    """

    __slots__ = ()
    _setter_class = field_setter.VolumetricMassFlowRateSetter
    _dimension = dim.VOLUMETRIC_MASS_FLOW_RATE

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.VolumetricMassFlowRateSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.VolumetricMassFlowRateSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

class Wavenumber(FieldQnty):
    """
    Type-safe wavenumber quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - Wavenumber("variable_name") -> Create unknown wavenumber
    - Wavenumber(value, "unit", "variable_name") -> Create known wavenumber
    
    Examples:
    ---------
    >>> unknown = Wavenumber("pressure")  # Unknown wavenumber
    >>> known = Wavenumber(100, "diopter", "inlet_pressure")  # Known wavenumber
    
    Available units: "diopter", "kayser", "reciprocal_meter"
    """

    __slots__ = ()
    _setter_class = field_setter.WavenumberSetter
    _dimension = dim.WAVENUMBER

    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):
        ...
    
    @overload
    def set(self, value: float, unit: str) -> Self: ...
    @overload
    def set(self, value: float, unit: None = None) -> field_setter.WavenumberSetter: ...
    def set(self, value: float, unit: str | None = None) -> Self | field_setter.WavenumberSetter:
        ...
    
    @property
    def value(self) -> float | None:
        ...

    @property
    def unit(self) -> str | None:
        ...
    
    

