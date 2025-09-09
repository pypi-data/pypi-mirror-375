import json
import os

from mplabml.base import utility
from mplabml.datamanager.base import Base, BaseSet


class FoundationModel(Base):
    """Base class for a transform object"""

    _uuid = ""
    _name = None

    _fields = [
        "uuid",
        "name",
        "features_count",
        "model_size",
        "created_at",
        "knowledgepack_description",
        "last_modified",
    ]

    _read_only_fields = [
        "uuid",
        "name",
        "features_count",
        "model_size",
        "created_at",
        "knowledgepack_description",
        "last_modified",
    ]

    _field_map = {"transform_type": "type"}

    def __init__(self, connection, uuid=None):
        self._connection = connection
        if uuid:
            self.uuid = uuid
            self.refresh()

    @property
    def base_url(self):
        return "foundation-model/"

    @property
    def detail_url(self):
        return "foundation-model/{uuid}/".format(uuid=self.uuid)

    @property
    def uuid(self):
        return self._uuid

    @uuid.setter
    def uuid(self, value):
        self._uuid = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def knowledgepack_description(self):
        return self._knowledgepack_description

    @knowledgepack_description.setter
    def knowledgepack_description(self, value):
        self._knowledgepack_description = value


class FoundationModelSet(BaseSet):
    def __init__(self, connection, initialize_set=True):
        """Initialize a custom transform set object.

        Args:
            connection
        """
        self._connection = connection
        self._set = None
        self._objclass = FoundationModel
        self._attr_key = "uuid"

        if initialize_set:
            self.refresh()

    @property
    def foundation_models(self):
        return self.objs

    @property
    def get_set_url(self):
        return "foundation-model/"

    def _new_obj_from_dict(self, data):
        """Creates a new object from the response data from the server.

        Args:
            data (dict): contains properties of the object

        Returns:
            obj of type _objclass

        """
        obj = self._objclass(self._connection)
        obj.initialize_from_dict(data)
        return obj
