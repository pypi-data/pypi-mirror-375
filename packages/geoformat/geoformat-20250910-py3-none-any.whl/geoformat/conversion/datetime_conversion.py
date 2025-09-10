import datetime


def format_datetime_object_to_str_value(
    datetime_value, format=["year", "month", "day"]
):
    """
    Convert a datetime object to a string representation based on specified components.

    This function allows selective formatting of a datetime object into a string by choosing specific components
    such as year, month, day, hour, second, and microsecond. The components are concatenated in the order
    provided in the format list.

    Parameters:
    datetime_value (datetime): The datetime object to be formatted.
    format (list of str, optional): A list of string components to include in the output.
        Default is ["year", "month", "day"]. Valid components are "year", "month", "day", "hour",
        "second", and "microsecond".

    Returns:
    str: A string representation of the datetime object based on the specified format.

    Raises:
    Exception: If an invalid component is specified in the format list.
    """

    if isinstance(format, str):
        format = [format]

    return_value = ""
    for v in format:
        if v == "year":
            return_value += str(datetime_value.year).zfill(4)
        elif v == "month":
            return_value += str(datetime_value.month).zfill(2)
        elif v == "day":
            return_value += str(datetime_value.day).zfill(2)
        elif v == "hour":
            return_value += str(datetime_value.hour).zfill(2)
        elif v == "second":
            return_value += str(datetime_value.second).zfill(2)
        elif v == "microsecond":
            return_value += str(datetime_value.microsecond).zfill(6)
        else:
            raise Exception()

    return return_value


def date_to_int(date_value, epoch=datetime.date(1970, 1, 1)):
    """
    Convert a date object to an integer representing the number of days since a specified epoch.

    This function calculates the number of days from a given epoch (default is 1970-01-01) to the specified date.
    It's useful for converting date values into a consistent numeric format for calculations or storage.

    Parameters:
    date_value (datetime.date): The date value to be converted.
    epoch (datetime.date, optional): The epoch (start date) from which the days are counted.
        Default is 1970-01-01.

    Returns:
    int: The number of days from the epoch to the given date.
    """
    return (date_value - epoch).days


def time_to_int(time_value):
    """
    Convert a time object to an integer representing the time in microseconds.

    This function transforms a time object into an integer representing the total number of microseconds
    since midnight. It's useful for time calculations or storing time values in a compact numeric format.

    Parameters:
    time_value (datetime.time): The time value to be converted.

    Returns:
    int: The number of microseconds since midnight represented by the time object.
    """
    return int(
        time_value.hour * 3600 * 1e6
        + time_value.minute * 60 * 1e6
        + time_value.second * 1e6
        + time_value.microsecond
    )


def int_to_date(int_value, epoch=datetime.date(1970, 1, 1)):
    """
    Convert an integer representing the number of days since a specified epoch to a date object.

    Parameters:
    int_value (int): The number of days since the epoch.
    epoch (datetime.date, optional): The epoch (start date) from which the days are counted.
        Default is 1970-01-01.

    Returns:
    datetime.date: The date corresponding to the given number of days since the epoch.
    """
    return epoch + datetime.timedelta(days=int_value)


def int_to_time(int_value):
    """
    Convert an integer representing time in microseconds since midnight to a time object.

    Parameters:
    int_value (int): The number of microseconds since midnight.

    Returns:
    datetime.time: The time object represented by the given number of microseconds since midnight.
    """
    seconds, int_value = divmod(int_value, 1e6)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return datetime.time(int(hours), int(minutes), int(seconds), int(int_value))


def datetime_to_timestamp(
    datetime_value, epoch=datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
):
    """
    Converts a datetime object to a UNIX timestamp (float) representing seconds since a specified epoch.

    This function takes a datetime object and calculates the number of seconds elapsed from the specified epoch
    to the datetime value. It provides support for both timezone-aware and naive (without timezone information)
    datetime objects. When handling naive datetime objects, they are assumed to be in the local timezone.
    Additionally, the function aligns the timezone of the epoch with that of the datetime_value before performing
    the calculation to ensure accuracy.

    Parameters:
    - datetime_value (datetime.datetime): The datetime value to be converted to a timestamp.
    - epoch (datetime.datetime, optional): The reference epoch time. Defaults to January 1, 1970, 00:00:00 UTC.

    Returns:
    - float: The UNIX timestamp representing the number of seconds from the epoch to the given datetime.

    Notes:
    - This function handles timezone alignment by standardizing the timezones of both the datetime_value and the epoch.
    - Naive datetime objects are treated as being in the local timezone for conversion.
    - Timezone-aware datetime objects are used as is, with the epoch being converted to their timezone for accurate calculation.

    Internal Functions:
    - format_timezones: Aligns the timezones of datetime_value and epoch for consistent calculation.
    - format_timezone: Sets or replaces the timezone information for a given datetime object.
    """

    def format_timezones(datetime_value, epoch_value):
        """
        Aligns the timezones of two datetime objects, either by setting a naive datetime object to a specific timezone
        or ensuring both datetime objects share the same timezone.

        This function checks the timezone information of both the datetime_value and the epoch_value. If one of them is
        timezone-aware and the other is naive (without timezone information), it assigns the timezone of the aware object
        to the naive one. If both are naive, no timezone is assigned. The function ensures that both datetime objects
        are either timezone-aware and aligned, or both remain naive.

        Parameters:
        - datetime_value (datetime.datetime): The primary datetime object to be aligned with the epoch.
        - epoch_value (datetime.datetime): The reference epoch datetime object for alignment.

        Returns:
        - tuple: A tuple containing two datetime.datetime objects with aligned timezones.

        Note:
        - If both datetime_value and epoch_value are timezone-aware but with different timezones, no conversion is done.
        - This function is typically used in timestamp calculation to ensure consistency in timezone handling.
        """
        datetime_value_timezone = datetime_value.tzinfo
        epoch_timezone = epoch_value.tzinfo
        if datetime_value_timezone is not None and epoch_timezone is None:
            timezone = datetime_value_timezone
        elif datetime_value_timezone is None and epoch_timezone is not None:
            timezone = epoch_timezone
        else:
            timezone = None

        datetime_value = format_timezone(
            datetime_value=datetime_value, timezone=timezone
        )
        epoch_value = format_timezone(datetime_value=epoch_value, timezone=timezone)

        return datetime_value, epoch_value

    def format_timezone(datetime_value, timezone):
        """
        Sets or replaces the timezone information of a datetime object.

        This function takes a datetime object and a timezone object. If the datetime object is naive (without timezone
        information), it assigns the provided timezone to it. If the datetime object is already timezone-aware, it
        replaces its existing timezone with the provided one. This function is used to standardize the timezone of
        a datetime object for consistent time-based calculations.

        Parameters:
        - datetime_value (datetime.datetime): The datetime object to which the timezone information will be applied.
        - timezone (datetime.timezone or None): The timezone to be set for the datetime object. If None, the function
          leaves the datetime object unchanged.

        Returns:
        - datetime.datetime: The datetime object with updated timezone information.

        Note:
        - This function does not perform any timezone conversion. It only sets or replaces the timezone information.
        """
        if timezone is not None:
            datetime_value = datetime_value.replace(tzinfo=timezone)

        return datetime_value

    datetime_value, epoch = format_timezones(
        datetime_value=datetime_value, epoch_value=epoch
    )

    # Calculate the difference in seconds
    delta = datetime_value - epoch
    timestamp = delta.total_seconds()

    return timestamp


def _determine_timestamp_unit(timestamp):
    """
    Determine if the given timestamp is in seconds or milliseconds.

    Args:
        timestamp (int or float): The timestamp to evaluate.

    Returns:
        str: 'seconds' if the timestamp is determined to be in seconds,
             'milliseconds' if the timestamp is determined to be in milliseconds.
    """
    # Define a threshold year, beyond which we consider the timestamp to be in milliseconds.
    # This is based on a rough estimate; timestamps representing dates beyond this year in seconds
    # are unlikely, thus considered to be in milliseconds.
    threshold_year = 3000

    try:
        # Try to convert the timestamp to datetime assuming it's in seconds.
        date_in_seconds = datetime.datetime.fromtimestamp(timestamp)
        if date_in_seconds.year > threshold_year:
            # If the year is beyond the threshold, it's likely the input was in milliseconds.
            return "milliseconds"
        else:
            return "seconds"
    except ValueError:
        # If conversion assuming seconds fails (e.g., value is too large), assume milliseconds.
        # This block also handles cases where the timestamp is negative and far in the past.
        return "milliseconds"
    except OverflowError:
        # If the timestamp value is too large even for milliseconds representation,
        # this block catches the overflow error.
        return "milliseconds"


def timestamp_to_datetime(timestamp, epoch=datetime.datetime(1970, 1, 1)):
    """
    Converts a numeric timestamp to a datetime object, automatically determining
    whether the timestamp is in seconds or milliseconds, and adjusting the conversion accordingly.

    This function leverages the _determine_timestamp_unit helper to decide if the given
    timestamp is measured in seconds or milliseconds. It then calculates the datetime
    corresponding to the timestamp, taking into account the unit of measurement and the
    specified epoch. The conversion accounts for timezone information of the epoch.

    Args:
        timestamp (int or float): The timestamp to be converted, which can be in seconds or milliseconds.
        epoch (datetime.datetime, optional): The reference epoch from which time is counted.
                                             Defaults to January 1, 1970, 00:00:00 UTC.

    Returns:
        datetime.datetime: The datetime object corresponding to the given timestamp, in the same timezone as the epoch.

    Notes:
        - The function automatically adjusts for the unit of the input timestamp (seconds or milliseconds).
        - The resulting datetime object will be in the same timezone as the provided epoch.
    """
    # Determine if timestamp is in seconds or milliseconds
    unit = _determine_timestamp_unit(timestamp)
    if unit == "milliseconds":
        # Convert milliseconds to seconds
        timestamp = timestamp / 1000.0

    # Ensure the epoch has timezone information
    if epoch.tzinfo is None:
        epoch = epoch.replace(tzinfo=datetime.timezone.utc)

    # Calculate the datetime corresponding to the timestamp
    return epoch + datetime.timedelta(seconds=timestamp)
