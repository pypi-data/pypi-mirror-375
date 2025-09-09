import json

import mplabml.base.utility as utility
from mplabml.datamanager.capture import Capture, BackgroundCapture


class CaptureExistsError(Exception):
    """Base class for a Capture exists error"""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Captures:
    """Base class for a collection of Captures."""

    def __init__(self, connection, project):
        self._connection = connection
        self._project = project
        self._reserved_metadata_names = ["capture_uuid", "segment_uuid"]
        self._capture_list = {}

    def create_capture(self, filename, filepath, asynchronous=True, capture_info=None):
        """Creates a capture object from the given filename and filepath.

        Args:
            filename (str): desired name of the file on the server
            filepath (str): local path to the file to be uploaded
            asynchronous (bool): Whether to process asynchronously

        Returns:
            capture object

        Raises:
            CaptureExistsError, if the Capture already exists on the server
        """
        capture_dict = {
            "connection": self._connection,
            "project": self._project,
            "filename": filename,
        }

        if self.get_capture_by_filename(filename) is not None:
            raise CaptureExistsError("capture {0} already exists.".format(filename))
        else:
            capture = Capture.initialize_from_dict(capture_dict)
            capture.path = filepath
            capture.capture_info = (
                capture_info if isinstance(capture_info, dict) else {}
            )
            capture.insert(asynchronous=asynchronous)

        return capture

    def get_or_create(self, filename, filepath, asynchronous=True, capture_info=None):
        """Creates a capture object from the given filename and filepath.

        Args:
            filename (str): desired name of the file on the server
            filepath (str): local path to the file to be uploaded
            asynchronous (bool): Whether to process asynchronously

        Returns:
            capture object

        Raises:
            CaptureExistsError, if the Capture already exists on the server
        """
        capture_dict = {
            "connection": self._connection,
            "project": self._project,
            "filename": filename,
        }

        if self.get_capture_by_filename(filename) is not None:
            return self.get_capture_by_filename(filename)
        else:
            capture = Capture.initialize_from_dict(capture_dict)
            capture.path = filepath
            capture.capture_info = (
                capture_info if isinstance(capture_info, dict) else {}
            )
            capture.insert(asynchronous=asynchronous)

        return capture

    def build_capture_list(self, force: bool = True):
        """Populates the function_list property from the server."""

        if not force and self._capture_list:
            return self._capture_list

        capture_response = self.get_captures()
        for capture in capture_response:
            self._capture_list[capture.filename] = capture

        return self._capture_list

    def get_capture_by_filename(self, filename, force=False):
        """Gets a capture object from the server using its filename property.

        Args:
            filename (str): the capture's name
            force (bool): rebuild the cached list of files

        Returns:
            capture object or None if it does not exist
        """
        capture_list = self.build_capture_list(force=force)

        return capture_list.get(filename)

    def get_capture_by_uuid(self, uuid):
        """Gets a capture object from the server using its filename property.

        Args:
            filename (str): the capture's name

        Returns:
            capture object or None if it does not exist
        """
        """Calls the REST API to update the capture."""
        url = "project/{0}/capture/{1}/".format(self._project.uuid, uuid)

        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)

        return self._new_capture_from_dict(response_data)

    def get_capture_urls_by_uuid(self, capture_uuids, expires_in=100):

        url = f"project/{self._project.uuid}/capture-files/"
        data = {"capture_uuids": capture_uuids, "expires_in": expires_in}

        response = self._connection.request("post", url, json=data)
        response_data, err = utility.check_server_response(response)

        return response_data

    def get_capture_urls_by_name(self, capture_list, expires_in=100):

        capture_uuids = [
            x.uuid
            for key, x in self.build_capture_list().items()
            if key in capture_list
        ]

        return self.get_capture_urls_by_uuid(capture_uuids, expires_in=expires_in)

    def __getitem__(self, key):
        if type(key) == str:
            return self.get_capture_by_filename(key)
        else:
            return self.get_captures()[key]

    def get_statistics(self):
        """Gets all capture statistics for the project.

        Returns:
            DataFrame of capture statistics
        """
        url = "project/{0}/statistics/".format(self._project.uuid)
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            data, error_report = utility.make_statistics_table(response_data)
            return data, error_report
        else:
            return None

    def get_metadata_names_and_values(self):
        """Gets all the metadata names and possible values for a project.

        Returns:
            list(dict) containing metadata names and values
        """
        url = "project/{0}/metadata/".format(self._project.uuid)
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            metadata_values = [
                {
                    "name": item["name"],
                    "values": [i["value"] for i in item["label_values"]],
                }
                for item in response_data
            ]
            return metadata_values

    def get_metadata_names(self):
        """Gets all the metadata names within a project.

        Returns:
            list of metadata names
        """
        url = "project/{0}/metadata/".format(self._project.uuid)
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            return [
                item["name"] for item in response_data
            ] + self._reserved_metadata_names

    def get_captures_by_metadata(self, key, value):
        """Gets captures by existing metadata key-values.

        Args:
            key (str): the name of the metadata item
            value (str, int, or float): the value to search for

        Returns:
            list of captures that have the desired metadata key-value pair
        """
        url = "project/{0}/capture/metadata/[{1}]=[{2}]/".format(
            self._project.uuid, key, value
        )
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            captures = []
            for capture_params in response_data:
                captures.append(self._new_capture_from_dict(capture_params))
            return captures

    def get_label_names_and_values(self):
        """Gets all the label names and possible values for a project.

        Returns:
            list(dict) containing metadata names and values
        """
        url = "project/{0}/label/".format(self._project.uuid)
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            metadata_values = [
                {
                    "name": item["name"],
                    "values": [i["value"] for i in item["label_values"]],
                }
                for item in response_data
            ]
            return metadata_values

    def get_label_names(self):
        """Gets all the label names within a project.

        Returns:
            list of label names
        """
        url = "project/{0}/label/".format(self._project.uuid)
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            return [item["name"] for item in response_data]

    def _new_capture_from_dict(self, capture_dict):
        """Creates a new capture using the dictionary.

        Args:
            capture_dict (dict): dictionary of capture properties

        Returns:
            capture object
        """
        capture_dict.update({"connection": self._connection, "project": self._project})
        return Capture.initialize_from_dict(capture_dict)

    def get_captures(self):
        """Gets all captures from the server.

        Returns:
            list of captures for the project
        """
        # Query the server and get the json
        url = "project/{0}/capture/".format(self._project.uuid)
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)

        # Populate each capture from the server
        captures = []
        if err is False:
            for capture_params in response_data:
                captures.append(self._new_capture_from_dict(capture_params))

        return captures


################################################
class BackgroundCaptures:
    """Base class for a collection of Background Captures."""

    def __init__(self, connection):
        self._connection = connection

    def get_background_captures(self, return_dict=False):
        """Gets all captures from the server.

        Returns:
        list of all available background captures
        """

        # Query the server and get the json
        url = "background-capture/"
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)

        # Populate each capture from the server
        captures = []
        if err is False:
            for capture_params in response_data:
                capture_params["filename"] = capture_params["name"]
                captures.append(
                    BackgroundCapture(
                        self._connection,
                        **capture_params,
                    )
                )

        return captures

    def get_background_capture_urls_by_uuid(self, capture_uuids, expires_in=100):

        url = f"background-capture-files/"
        data = {"background_capture_uuids": capture_uuids, "expires_in": expires_in}

        response = self._connection.request("post", url, json=data)
        response_data, err = utility.check_server_response(response)

        return response_data

    ################################################
