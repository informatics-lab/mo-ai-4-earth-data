from __app__.vendor import data_filter


def test_data_filter():

    required = [
        'mo-atmospheric-mogreps-uk/20191213T1000Z/20191215T1000Z-PT0048H00M-temperature_at_surface.nc'

    ]

    not_required = [
        'mo-atmospheric-mogreps-uk/20191213T1000Z/20191215T1000Z-PT0048H00M-wind_gust_at_10m-PT01H.nc'
    ]

    for diagnostic in not_required:
        assert data_filter.required_diagnostic(diagnostic) == False

    for diagnostic in required:
        assert data_filter.required_diagnostic(diagnostic) == True

