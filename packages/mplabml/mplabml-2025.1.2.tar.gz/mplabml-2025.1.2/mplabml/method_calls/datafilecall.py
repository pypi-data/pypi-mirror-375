from mplabml.datamanager.pipeline import PipelineStep


class DataFileCall(PipelineStep):
    """The base class for a featurefile call"""

    def __init__(self, name):
        super(DataFileCall, self).__init__(name=name, step_type="DataFileCall")
        self.name = name
        self._data_columns = None
        self._group_columns = None
        self._label_column = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if not isinstance(name, list):
            name = [name]
        self._name = name

    @property
    def data_columns(self):
        return self._data_columns

    @data_columns.setter
    def data_columns(self, value):
        self._data_columns = value

    @property
    def outputs(self):
        return self._outputs

    @outputs.setter
    def outputs(self, value):
        self._outputs = value

    @property
    def label_column(self):
        return self._label_column

    @label_column.setter
    def label_column(self, value):
        self._label_column = value

    @property
    def group_columns(self):
        return self._group_columns

    @group_columns.setter
    def group_columns(self, value):
        self._group_columns = value

    def _to_dict(self):
        capturefile_dict = {}
        capturefile_dict["name"] = self.name
        capturefile_dict["type"] = "datafile"
        capturefile_dict["data_columns"] = self.data_columns
        capturefile_dict["group_columns"] = self.group_columns
        capturefile_dict["label_column"] = self.label_column
        capturefile_dict["outputs"] = self.outputs
        return capturefile_dict
