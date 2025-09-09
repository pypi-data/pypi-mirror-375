import logging

import mplabml.base.utility as utility
from mplabml.datamanager.base import Base, BaseSet
from mplabml.datamanager.label import Label
from mplabml.datamanager.labelvalue import LabelValue
from mplabml.datamanager.segmenter import Segmenter

logger = logging.getLogger(__name__)


class Segment(Base):
    """Base class for a label object."""

    _fields = [
        "uuid",
        "sample_start",
        "sample_end",
        "segmenter",
        "label",
        "label_value",
    ]

    _field_map = {
        "sample_start": "capture_sample_sequence_start",
        "sample_end": "capture_sample_sequence_end",
    }

    def __init__(
        self, connection, project, capture, segmenter=None, label=None, label_value=None
    ):
        """Initialize a metadata object.

        Args:
            connection
            project
            capture
        """
        super().__init__(connection)

        self._uuid = ""
        self._sample_start = 0
        self._sample_end = 0
        self._connection = connection
        self._project = project
        self._capture = capture
        self._segmenter = segmenter
        self._label = label
        self._label_value = label_value

    @property
    def uuid(self):
        """Auto generated unique identifier for the metadata object"""
        return self._uuid

    @uuid.setter
    def uuid(self, value):
        self._uuid = value

    @property
    def sample_start(self):
        """The index of the first sample of the label"""
        return self._sample_start

    @sample_start.setter
    def sample_start(self, value):
        self._sample_start = value

    @property
    def sample_end(self):
        """The index of the last sample of the label"""
        return self._sample_end

    @sample_end.setter
    def sample_end(self, value):
        self._sample_end = value

    @property
    def segmenter(self):
        """The index of the last sample of the label"""
        if isinstance(self._segmenter, Segmenter):
            return self._segmenter.uuid

        return self._segmenter

    @segmenter.setter
    def segmenter(self, value):
        self._segmenter = value

    @property
    def label(self):
        if isinstance(self._label, Label):
            return self._label.uuid
        else:
            return self._label

    @label.setter
    def label(self, value):
        self._label = value

    @property
    def label_value(self):
        if isinstance(self._label_value, LabelValue):
            return self._label_value.uuid
        else:
            return self._label_value

    @label_value.setter
    def label_value(self, value):
        self._label_value = value

    def insert(self):
        """Calls the REST API and inserts a metadata object onto the server using the local object's properties."""
        url = "project/{0}/capture/{1}/label-relationship/".format(
            self._project.uuid, self._capture.uuid
        )

        data = self._to_representation()

        response = self._connection.request("post", url, data)
        response_data, err = utility.check_server_response(response)
        if err is False:
            self.uuid = response_data["uuid"]

        return response

    def update(self):
        """Calls the REST API and updates the object on the server."""
        self._capture.await_ready()
        url = "project/{0}/capture/{1}/label-relationship/{2}/".format(
            self._project.uuid, self._capture.uuid, self.uuid
        )
        data = self._to_representation()

        response = self._connection.request("put", url, data)
        response_data, err = utility.check_server_response(response)

        return response

    def delete(self):
        """Calls the REST API and deletes the object from the server."""
        url = "project/{0}/capture/{1}/label-relationship/{2}/".format(
            self._project.uuid, self._capture.uuid, self.uuid
        )
        response = self._connection.request("delete", url)
        response_data, err = utility.check_server_response(response)

        return response

    def refresh(self):
        """Calls the REST API and populates the local object's properties from the server."""
        url = "project/{0}/capture/{1}/label-relationship/{2}/".format(
            self._project.uuid, self._capture.uuid, self.uuid
        )
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            self.initialize_from_dict(response_data)

        return response


class SegmentSet(BaseSet):
    """Base class for a collection of segments"""

    def __init__(self, connection, project, capture, initialize_set=True):
        self._connection = connection
        self._project = project
        self._capture = capture
        self._set = None
        self._objclass = Segment

        if initialize_set:
            self.refresh()

    @property
    def get_set_url(self):
        return "project/{0}/capture/{1}/label-relationship/".format(
            self._project.uuid, self._capture.uuid
        )

    @property
    def segments(self):
        return self.objs

    def _new_obj_from_dict(self, data):
        """Creates a new label from data in the dictionary.

        Args:
            dict (dict): contains label properties uuid, name, type, value, capture_sample_sequence_start, and
            capture_sample_sequence_end

        Returns:
            label object

        """
        segment = self._objclass(self._connection, self._project, self._capture)
        segment.initialize_from_dict(data)
        return segment
