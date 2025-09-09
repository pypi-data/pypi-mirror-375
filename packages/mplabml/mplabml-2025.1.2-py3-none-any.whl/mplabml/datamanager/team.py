import os
import json
from mplabml.base import utility


class Team(object):
    """Base class for a transform object"""

    _uuid = ""
    _name = None

    def __init__(self, connection):
        self._connection = connection

    def get_user(self):
        """Get Information about the users on your team."""

        url = "user/"
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)

        return response_data

    def team_subscription(self):
        """Get Information about your teams subscription."""
        url = "team-subscription/"
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)

        return response_data

    def team_info(self):
        """Get information about your specific team."""
        url = "team-info/"
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)

        return response_data
