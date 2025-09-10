''' Functions to convert data '''


def pressure_to_altitude(
    pressure: float,
    pressure_at_start: float,
    temperature_at_start: float,
    altitude_at_start: float = 0
) -> float:
    ''' Convert pressure to altitude

    Arguments
    ---------
    pressure: float
        Pressure to convert to altitude
    pressure_at_start: float
        Pressure at start of flight
    temp_at_start: float
        Temperature at start of flight
    altitude_at_start: float
        Altitude at start of flight (default 0)

    Returns
    -------
    altitude: float
        Altitude in meters

    Example
    -------
    >>> pressure_to_altitude(101325, 101325, 20)
    0.0
    >>> pressure_to_altitude(101325, 101325, 20, 1000)
    1000.0

    '''

    temperature_at_start += 273.15
    temp = temperature_at_start
    pressure_at_sea_level = (
        pressure_at_start
        * ((1 - ((0.0065 * altitude_at_start)
                 / (temperature_at_start + (0.0065 * altitude_at_start))
                 )) ** -5.257)
    )

    altitude = (
        (((pressure_at_sea_level / pressure) ** (1 / 5.257) - 1) * temp)
        / 0.0065
    )

    return altitude
