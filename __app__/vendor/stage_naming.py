#!/usr/bin/env python
import os

CF_NAME_CONFIG_KEY_MAP = {
    # cf_name: stage_config_key
    "air_pressure_at_sea_level": "pressure_at_mean_sea_level",
    "atmosphere_boundary_layer_thickness": "boundary_layer_depth",
    "cloud_area_fraction": "cloud_amount_of_total_cloud",
    "cloud_area_fraction_assuming_only_consider_surface_to_1000_feet_asl": "cloud_amount_below_1000ft_ASL",
    "cloud_base_altitude_assuming_only_consider_cloud_area_fraction_greater_than_2p5_oktas": "height_ASL_at_cloud_base_where_cloud_cover_2p5_oktas",
    "cloud_base_altitude_assuming_only_consider_cloud_area_fraction_greater_than_4p5_oktas": "height_ASL_at_cloud_base_where_cloud_cover_4p5_oktas",
    "fog_area_fraction": "fog_fraction_at_screen_level",
    "freezing_level_altitude": "height_ASL_at_freezing_level",
    "high_type_cloud_area_fraction": "cloud_amount_of_high_cloud",
    "land_binary_mask": "landsea_mask",
    "low_type_cloud_area_fraction": "cloud_amount_of_low_cloud",
    "lwe_thickness_of_surface_snow_amount": "snow_depth_water_equivalent",
    "medium_type_cloud_area_fraction": "cloud_amount_of_medium_cloud",
    "surface_air_pressure": "pressure_at_surface",
    "surface_altitude": "height_of_orography",
    "surface_diffusive_downwelling_shortwave_flux_in_air": "radiation_flux_in_shortwave_diffuse_downward_at_surface",
    "surface_direct_downwelling_shortwave_flux_in_air": "radiation_flux_in_shortwave_direct_downward_at_surface",
    "surface_downwelling_longwave_flux_in_air": "radiation_flux_in_longwave_downward_at_surface",
    "surface_downwelling_shortwave_flux_in_air": "radiation_flux_in_shortwave_total_downward_at_surface",
    "surface_downwelling_ultraviolet_flux_in_air": "radiation_flux_in_uv_downward_at_surface",
    "surface_temperature": "temperature_at_surface",
    "surface_upward_sensible_heat_flux": "sensible_heat_flux_at_surface",
    "surface_upwelling_ultraviolet_flux_in_air": "radiation_flux_in_uv_upward_at_surface",
    "total_radar_reflectivity_max_in_column": "total_radar_reflectivity_max_in_column",
    "water_evaporation_flux_from_soil": "evaporation_flux_at_surface",
    "wet_bulb_freezing_level_altitude": "height_ASL_at_wet_bulb_freezing_level",
}

CF_NAME_STAT_VERTICAL_CONFIG_KEY_MAP = {
    # cf names where the config key can also contain statistical or vertical level info
    "air_pressure": "pressure",
    "air_temperature": "temperature",
    "cloud_volume_fraction_in_atmosphere_layer": "cloud_amount",
    "dew_point_temperature": "temperature_of_dew_point",
    "lwe_graupel_and_hail_fall_rate": "hail_fall_rate",
    "lwe_snowfall_rate": "snowfall_rate",
    "lwe_thickness_of_graupel_and_hail_fall_amount": "hail_fall_accumulation",
    "lwe_thickness_of_snowfall_amount": "snowfall_accumulation",
    "number_of_lightning_flashes_per_unit_area": "lightning_flash_accumulation",
    "rainfall_rate": "rainfall_rate",
    "relative_humidity": "relative_humidity",
    "soil_temperature": "soil_temperature",
    "total_radar_reflectivity": "total_radar_reflectivity",
    "thickness_of_rainfall_amount": "rainfall_accumulation",
    "upward_air_velocity": "wind_vertical_velocity",
    "visibility_in_air": "visibility",
    "wet_bulb_potential_temperature": "wet_bulb_potential_temperature",
    "wind_from_direction": "wind_direction",
    "wind_speed": "wind_speed",
    "wind_speed_of_gust": "wind_gust",
}


def secs_to_hrs_mins(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    # assume whole number of minutes
    assert seconds == 0
    return hours, minutes


def reformat_datetime_str(dtstr):
    # reformat string in the form:
    # YYYY-MM-DDThh:mm:ssZ to YYYYMMDDThhmmZ
    date, time = dtstr.split("T")
    # remove hyphens from date
    date = date.replace("-", "")
    # remove trailing Z
    time = time[:-1]
    # remove seconds
    time = time.split(":")[:-1]
    # rejoin
    time = "".join(time)
    return f"{date}T{time}Z"


def fp_to_duration_str(fp_secs):
    hours, mins = secs_to_hrs_mins(fp_secs)
    return f"PT{hours:04}H{mins:02}M"


def determine_config_key(metadata):
    def vertical_coord_str(metadata):
        # look for.. height, pressure, depth
        for coord_name in ("height", "pressure", "depth"):
            coord = metadata.get(coord_name)
            if not coord:
                continue
            coord = coord.split()
            if len(coord) != 1:
                coord_name = "soil" if coord_name == "depth" else coord_name
                return f"_on_{coord_name}_levels"
            elif len(coord) == 1 and coord_name == "height":
                # check for scalar height coord
                level_names = {"1.5m": "screen_level", "10.0m": "10m"}
                coord_units = metadata[f"{coord_name}_units"]
                vertical_level = level_names[f"{coord[0]}{coord_units}"]
                return f"_at_{vertical_level}"
        return ""

    def statistical_str(metadata):
        # if cube has statistical information (e.g: max/min)
        # need to expose in name
        # (NB: accumulations/rates are treated via the dictionaries..)
        bnds = metadata.get("forecast_period_bounds")
        if not bnds:
            return ""
        bnds = [int(x) for x in bnds.split()]
        period = bnds[1] - bnds[0]
        hours, minutes = secs_to_hrs_mins(period)
        hours = f"{hours:02}H" if hours != 0 else ""
        minutes = f"{minutes:02}M" if minutes != 0 else ""
        period = f"-PT{hours}{minutes}"

        cell_methods = metadata.get("cell_methods")
        if cell_methods:
            method = [method for method in cell_methods.split(",") if "time" in method]
            if len(method) == 1:
                method = method[0]
                method = method.split(": ")[1]
                method = f"_{method[:3]}" if method in ("minimum", "maximum") else ""
            else:
                method = ""
        else:
            method = ""
        return f"{method}{period}"

    name = metadata["name"]
    try:
        diag = CF_NAME_CONFIG_KEY_MAP[name]
        return diag
    except KeyError:
        diag = CF_NAME_STAT_VERTICAL_CONFIG_KEY_MAP[name]
        vertical_level_str = vertical_coord_str(metadata)
        stat_str = statistical_str(metadata)
        # expect to find vertical level or statistical substring
        return f"{diag}{vertical_level_str}{stat_str}"


def generate_stage_name(metadata):
    config_key = determine_config_key(metadata)
    validity_time = reformat_datetime_str(metadata["time"])
    lead_time = fp_to_duration_str(int(metadata["forecast_period"]))
    return f"{validity_time}-{lead_time}-{config_key}"


def diagnostic_from_fpath(fpath):
    # /some/path/validtime-leadtime-diag.nc
    diag = os.path.basename(fpath)
    diag, _ = os.path.splitext(diag)
    diag = "-".join(diag.split("-")[2:])
    return diag if diag else None