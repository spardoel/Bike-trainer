# Workout Template class


class WorkoutTemplate:
    """The basic template for each workout.
    Accepts a name string, id integer, difficulty string, duration integer in minutes, and a power profile in a list.
    The length of the list must match the duration (in minutes) x 60.
    This is because the system updates every second and the power profile must be equal to the workout length in seconds

    Args:
        name (string): Unique workout name
        id (int): unique workout identifier
        difficulty (string): workout difficulty (easy, medium, hard, all-out)
        duration (int): workout duration in minutes
        profile (int list): list of power values over time. Length must be duration * 60
    """

    def __init__(self, name, id, difficulty, duration, profile):
        """The basic workout template class.
        Accepts a name string,
        id integer, difficulty string, duration integer in minutes, and a power profile in a list.
        The length of the list must match the duration (in minutes) x 60.
        This is because the system updates every second and the power profile must be equal to the workout length in seconds

        Args:
            name (string): Unique workout name
            id (int): unique workout identifier
            difficulty (string): workout difficulty (easy, medium, hard, all-out)
            duration (int): workout duration in minutes
            profile (int list): list of power values over time as fraction of FTP. Length must be duration * 60
        """
        self.name = name
        self.id = id
        self.difficulty = difficulty
        self.duration = duration
        self.power_profile = profile

    def get_details(self):
        """Returns the workout name, id, difficulty, and duration"""
        return self.name, self.id, self.difficulty, self.duration

    def get_power(self, timestamp, ftp):
        """Accepts a timestamp and returns the corresponding power in the workout profile"""

        # Check if the timestamp is within range
        if timestamp >= 0 and timestamp < self.duration * 60:
            # return the power value associated with the input timestamp.
            # The power profile is stored as fraction of ftp. Convert to int then return
            return int(self.power_profile[timestamp] * ftp)

        else:
            # if not within range return error code -1
            return -1
