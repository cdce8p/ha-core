from enum import IntEnum
from typing import Union


class AirFlowScale(IntEnum):
    CUBIC_FEET_PER_MINUTE = 1
    CUBIC_METER_PER_HOUR = 0

class AnglePositionScale(IntEnum):
    DEGREES_RELATIVE_TO_NORTH_POLE_OF_STANDING_EYE_VIEW = 1
    DEGREES_RELATIVE_TO_SOUTH_POLE_OF_STANDING_EYE_VIEW = 2
    PERCENTAGE_VALUE = 0

class AppliedForceOnTheSensorScale(IntEnum):
    NEWTON = 0

class AccelerationScale(IntEnum):
    METER_PER_SQUARE_SECOND = 0

class AcidityScale(IntEnum):
    ACIDITY = 0

class AirPressureScale(IntEnum):
    INCHES_OF_MERCURY = 1
    KILOPASCAL = 0

class BasisMetabolicRateScale(IntEnum):
    JOULE = 0

class BloodPressureScale(IntEnum):
    DIASTOLIC = 1
    SYSTOLIC = 0

class BodyMassIndexScale(IntEnum):
    BODY_MASS_INDEX = 0

class CarbonDioxideLevelScale(IntEnum):
    PARTS_MILLION = 0

class CarbonMonoxideLevelScale(IntEnum):
    MOLE_PER_CUBIC_METER = 0
    PARTS_MILLION = 1

class CurrentScale(IntEnum):
    AMPERE = 0
    MILLIAMPERE = 1

class DistanceScale(IntEnum):
    CENTIMETER = 1
    FEET = 2
    METER = 0

class DensityScale(IntEnum):
    DENSITY = 0

class DirectionScale(IntEnum):
    DEGREES = 0

class ElectricalConductivityScale(IntEnum):
    SIEMENS_PER_METER = 0

class ElectricalResistivityScale(IntEnum):
    OHM_METER = 0

class FormaldehydeLevelScale(IntEnum):
    MOLE_PER_CUBIC_METER = 0

class FrequencyScale(IntEnum):
    HERTZ = 0
    KILOHERTZ = 1

class GeneralPurposeScale(IntEnum):
    DIMENSIONLESS_VALUE = 1
    PERCENTAGE_VALUE = 0

class HeartRateScale(IntEnum):
    BEATS_PER_MINUTE = 0

class HumidityScale(IntEnum):
    ABSOLUTE_HUMIDITY = 1
    PERCENTAGE_VALUE = 0

class IlluminanceScale(IntEnum):
    LUX = 1
    PERCENTAGE_VALUE = 0

class LoudnessScale(IntEnum):
    A_WEIGHTED_DECIBELS = 1
    DECIBEL = 0

class MethaneDensityScale(IntEnum):
    MOLE_PER_CUBIC_METER = 0

class MoistureScale(IntEnum):
    IMPEDANCE = 2
    PERCENTAGE_VALUE = 0
    VOLUME_WATER_CONTENT = 1
    WATER_ACTIVITY = 3

class MassScale(IntEnum):
    KILOGRAM = 0

class ParticulateMatter10Scale(IntEnum):
    MICROGRAM_PER_CUBIC_METER = 1
    MOLE_PER_CUBIC_METER = 0

class ParticulateMatter25Scale(IntEnum):
    MICROGRAM_PER_CUBIC_METER = 1
    MOLE_PER_CUBIC_METER = 0

class PowerScale(IntEnum):
    BTU_H = 1
    WATT = 0

class PercentageScale(IntEnum):
    PERCENTAGE_VALUE = 0

class PressureScale(IntEnum):
    KILOPASCAL = 0
    POUND_PER_SQUARE_INCH = 1

class RadonConcentrationScale(IntEnum):
    BECQUEREL_PER_CUBIC_METER = 0
    PICOCURIES_PER_LITER = 1

class RainRateScale(IntEnum):
    INCHES_PER_HOUR = 1
    MILLIMETER_HOUR = 0

class RespiratoryRateScale(IntEnum):
    BREATHS_PER_MINUTE = 0

class RfSignalStrengthScale(IntEnum):
    POWER_LEVEL = 1
    RSSI = 0

class RotationScale(IntEnum):
    HERTZ = 1
    REVOLUTIONS_PER_MINUTE = 0

class SeismicIntensityScale(IntEnum):
    EUROPEAN_MACROSEISMIC = 1
    LIEDU = 2
    MERCALLI = 0
    SHINDO = 3

class SeismicMagnitudeScale(IntEnum):
    BODY_WAVE = 3
    LOCAL = 0
    MOMENT = 1
    SURFACE_WAVE = 2

class SoilSalinityScale(IntEnum):
    MOLE_PER_CUBIC_METER = 0

class SolarRadiationScale(IntEnum):
    WATT_PER_SQUARE_METER = 0

class TankCapacityScale(IntEnum):
    CUBIC_METER = 1
    GALLONS = 2
    LITER = 0

class TideLevelScale(IntEnum):
    FEET = 1
    METER = 0

class TimeScale(IntEnum):
    SECOND = 0

class TemperatureScale(IntEnum):
    CELSIUS = 0
    FAHRENHEIT = 1

class UltravioletScale(IntEnum):
    UV_INDEX = 0

class UnitlessScale(IntEnum):
    UNITLESS = 0

class VelocityScale(IntEnum):
    MPH = 1
    M_S = 0

class VolatileOrganicCompoundLevelScale(IntEnum):
    MOLE_PER_CUBIC_METER = 0
    PARTS_MILLION = 1

class VoltageScale(IntEnum):
    MILLIVOLT = 1
    VOLT = 0

class WaterChlorineLevelScale(IntEnum):
    MILLIGRAM_PER_LITER = 0

class WaterFlowScale(IntEnum):
    LITER_PER_HOUR = 0

class WaterOxidationReductionPotentialScale(IntEnum):
    MILLIVOLT = 0

class WaterPressureScale(IntEnum):
    KILOPASCAL = 0

class WeightScale(IntEnum):
    KILOGRAM = 0
    POUNDS = 1


MultilevelSensorScaleType = Union[
    AccelerationScale,
    AcidityScale,
    AirFlowScale,
    AirPressureScale,
    AnglePositionScale,
    AppliedForceOnTheSensorScale,
    BasisMetabolicRateScale,
    BloodPressureScale,
    BodyMassIndexScale,
    CarbonDioxideLevelScale,
    CarbonMonoxideLevelScale,
    CurrentScale,
    DensityScale,
    DirectionScale,
    DistanceScale,
    ElectricalConductivityScale,
    ElectricalResistivityScale,
    FormaldehydeLevelScale,
    FrequencyScale,
    GeneralPurposeScale,
    HeartRateScale,
    HumidityScale,
    IlluminanceScale,
    LoudnessScale,
    MassScale,
    MethaneDensityScale,
    MoistureScale,
    ParticulateMatter10Scale,
    ParticulateMatter25Scale,
    PercentageScale,
    PowerScale,
    PressureScale,
    RadonConcentrationScale,
    RainRateScale,
    RespiratoryRateScale,
    RfSignalStrengthScale,
    RotationScale,
    SeismicIntensityScale,
    SeismicMagnitudeScale,
    SoilSalinityScale,
    SolarRadiationScale,
    TankCapacityScale,
    TemperatureScale,
    TideLevelScale,
    TimeScale,
    UltravioletScale,
    UnitlessScale,
    VelocityScale,
    VolatileOrganicCompoundLevelScale,
    VoltageScale,
    WaterChlorineLevelScale,
    WaterFlowScale,
    WaterOxidationReductionPotentialScale,
    WaterPressureScale,
    WeightScale,
]


UNIT_AMPERE: set[MultilevelSensorScaleType] = {CurrentScale.AMPERE}
UNIT_BTU_H: set[MultilevelSensorScaleType] = {PowerScale.BTU_H}
UNIT_CELSIUS: set[MultilevelSensorScaleType] = {TemperatureScale.CELSIUS}
UNIT_CENTIMETER: set[MultilevelSensorScaleType] = {DistanceScale.CENTIMETER}
UNIT_CUBIC_FEET_PER_MINUTE: set[MultilevelSensorScaleType] = {
    AirFlowScale.CUBIC_FEET_PER_MINUTE
}
UNIT_CUBIC_METER: set[MultilevelSensorScaleType] = {TankCapacityScale.CUBIC_METER}
UNIT_CUBIC_METER_PER_HOUR: set[MultilevelSensorScaleType] = {
    AirFlowScale.CUBIC_METER_PER_HOUR
}
UNIT_DECIBEL: set[MultilevelSensorScaleType] = {LoudnessScale.DECIBEL}
UNIT_DEGREES: set[MultilevelSensorScaleType] = {DirectionScale.DEGREES}
UNIT_DENSITY: set[MultilevelSensorScaleType] = {DensityScale.DENSITY}
UNIT_FAHRENHEIT: set[MultilevelSensorScaleType] = {TemperatureScale.FAHRENHEIT}
UNIT_FEET: set[MultilevelSensorScaleType] = {DistanceScale.FEET, TideLevelScale.FEET}
UNIT_GALLONS: set[MultilevelSensorScaleType] = {TankCapacityScale.GALLONS}
UNIT_HERTZ: set[MultilevelSensorScaleType] = {FrequencyScale.HERTZ, RotationScale.HERTZ}
UNIT_INCHES_OF_MERCURY: set[MultilevelSensorScaleType] = {
    AirPressureScale.INCHES_OF_MERCURY
}
UNIT_INCHES_PER_HOUR: set[MultilevelSensorScaleType] = {RainRateScale.INCHES_PER_HOUR}
UNIT_KILOGRAM: set[MultilevelSensorScaleType] = {
    MassScale.KILOGRAM,
    WeightScale.KILOGRAM,
}
UNIT_KILOHERTZ: set[MultilevelSensorScaleType] = {FrequencyScale.KILOHERTZ}
UNIT_LITER: set[MultilevelSensorScaleType] = {TankCapacityScale.LITER}
UNIT_LUX: set[MultilevelSensorScaleType] = {IlluminanceScale.LUX}
UNIT_METER: set[MultilevelSensorScaleType] = {DistanceScale.METER, TideLevelScale.METER}
UNIT_MICROGRAM_PER_CUBIC_METER: set[MultilevelSensorScaleType] = {
    ParticulateMatter10Scale.MICROGRAM_PER_CUBIC_METER,
    ParticulateMatter25Scale.MICROGRAM_PER_CUBIC_METER,
}
UNIT_MILLIAMPERE: set[MultilevelSensorScaleType] = {CurrentScale.MILLIAMPERE}
UNIT_MILLIMETER_HOUR: set[MultilevelSensorScaleType] = {RainRateScale.MILLIMETER_HOUR}
UNIT_MILLIVOLT: set[MultilevelSensorScaleType] = {
    VoltageScale.MILLIVOLT,
    WaterOxidationReductionPotentialScale.MILLIVOLT,
}
UNIT_MPH: set[MultilevelSensorScaleType] = {VelocityScale.MPH}
UNIT_M_S: set[MultilevelSensorScaleType] = {VelocityScale.M_S}
UNIT_PARTS_MILLION: set[MultilevelSensorScaleType] = {
    CarbonDioxideLevelScale.PARTS_MILLION,
    CarbonMonoxideLevelScale.PARTS_MILLION,
    VolatileOrganicCompoundLevelScale.PARTS_MILLION,
}
UNIT_PERCENTAGE_VALUE: set[MultilevelSensorScaleType] = {
    AnglePositionScale.PERCENTAGE_VALUE,
    GeneralPurposeScale.PERCENTAGE_VALUE,
    HumidityScale.PERCENTAGE_VALUE,
    IlluminanceScale.PERCENTAGE_VALUE,
    MoistureScale.PERCENTAGE_VALUE,
    PercentageScale.PERCENTAGE_VALUE,
}
UNIT_POUNDS: set[MultilevelSensorScaleType] = {WeightScale.POUNDS}
UNIT_POUND_PER_SQUARE_INCH: set[MultilevelSensorScaleType] = {
    PressureScale.POUND_PER_SQUARE_INCH
}
UNIT_POWER_LEVEL: set[MultilevelSensorScaleType] = {RfSignalStrengthScale.POWER_LEVEL}
UNIT_RSSI: set[MultilevelSensorScaleType] = {RfSignalStrengthScale.RSSI}
UNIT_SECOND: set[MultilevelSensorScaleType] = {TimeScale.SECOND}
UNIT_SYSTOLIC: set[MultilevelSensorScaleType] = {BloodPressureScale.SYSTOLIC}
UNIT_VOLT: set[MultilevelSensorScaleType] = {VoltageScale.VOLT}
UNIT_WATT: set[MultilevelSensorScaleType] = {PowerScale.WATT}
UNIT_WATT_PER_SQUARE_METER: set[MultilevelSensorScaleType] = {
    SolarRadiationScale.WATT_PER_SQUARE_METER
}
