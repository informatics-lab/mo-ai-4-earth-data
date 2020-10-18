from .stage_naming import diagnostic_from_fpath


DIAG_WHITELIST = [
    "cloud_amount_of_low_cloud",
    "cloud_amount_of_medium_cloud",
    "cloud_amount_of_total_cloud",
    "fog_fraction_at_screen_level",
    "hail_fall_accumulation-PT01H",
    "height_ASL_at_freezing_level",
    "lightning_flash_accumulation-PT01H",
#    "pressure_at_mean_sea_level",
#    "pressure_at_surface",
#    "pressure_on_height_levels",
    "radiation_flux_in_longwave_downward_at_surface",
    "radiation_flux_in_shortwave_diffuse_downward_at_surface",
    "radiation_flux_in_shortwave_direct_downward_at_surface",
    "radiation_flux_in_shortwave_total_downward_at_surface",
#    "radiation_flux_in_uv_downward_at_surface",
#    "radiation_flux_in_uv_upward_at_surface",
    "rainfall_accumulation-PT01H",
    "relative_humidity_at_screen_level",
#    "relative_humidity_on_height_levels",
    "sensible_heat_flux_at_surface",
    "snow_depth_water_equivalent",
    "snowfall_accumulation-PT01H",
    "soil_temperature_on_soil_levels",
    "temperature_at_screen_level",
    "temperature_at_screen_level_max-PT01H",
    "temperature_at_screen_level_min-PT01H",
    "temperature_at_surface",
    "temperature_on_height_levels",
    "visibility_at_screen_level",
    "wet_bulb_potential_temperature_on_pressure_levels",
    "wind_direction_at_10m",
    "wind_direction_on_height_levels",
    "wind_gust_at_10m",
#    "wind_gust_at_10m_max-PT01H",
    "wind_speed_at_10m",
    "wind_speed_at_10m_max-PT01H",
#    "wind_speed_on_height_levels",
]


def required_diagnostic(blob_name):
    diag = diagnostic_from_fpath(blob_name)
    if diag in DIAG_WHITELIST:
        return True
    return False