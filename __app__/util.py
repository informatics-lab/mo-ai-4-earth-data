from __app__.vendor.stage_naming import generate_stage_name, reformat_datetime_str

def determine_blob_name(metadata):
    # reverse engineer StaGE filename
 
    name = generate_stage_name(metadata)
    cycle_time = reformat_datetime_str(metadata["forecast_reference_time"])
    name = f"{cycle_time}/{name}.nc"
    
    model = metadata.get("model")
    name = f"{model}/{name}"
    return name