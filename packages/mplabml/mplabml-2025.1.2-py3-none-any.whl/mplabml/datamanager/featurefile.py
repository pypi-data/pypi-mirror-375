import datetime
import os

import mplabml.base.utility as utility
from mplabml.datamanager.base import Base


class FeatureFile(Base):
    """Base class for a featurefile object."""

    _fields = [
        "uuid",
        "name",
        "created_at",
        "last_modified",
        "is_features",
        "label_column",
        "number_rows",
    ]

    def __init__(
        self,
        connection,
        project,
        name="",
        path="",
        is_features=True,
        uuid=None,
        label_column="",
        number_rows=None,
    ):
        self._connection = connection
        self._project = project
        self.uuid = uuid
        self._created_at = None
        self._is_features = is_features
        self.name = name
        self.path = path
        self.label_column = label_column
        self.number_rows = number_rows

    # Maintain campatibility with old filename attr
    @property
    def filename(self):
        """The name of the file as stored on the server

        Note:
            Filename must contain a .csv or .arff extension
        """
        return self.name

    @filename.setter
    def filename(self, value):
        self.name = value

    @property
    def is_features(self):
        """If this is a DataFile or FeatureFile"""
        return self._is_features

    @is_features.setter
    def is_features(self, value):
        self._is_features = value

    @property
    def created_at(self):
        """Date of the Pipeline creation"""
        return self._created_at

    @created_at.setter
    def created_at(self, value):
        self._created_at = datetime.datetime.strptime(
            value[:-6], "%Y-%m-%dT%H:%M:%S.%f"
        )

    def insert(self):
        """Calls the REST API to insert a new featurefile."""
        url = "project/{0}/featurefile/".format(self._project.uuid)
        featurefile_info = {"name": self.name, "is_features": self.is_features}

        if not os.path.exists(self.path):
            raise OSError(
                "Cannot update featurefile because the system cannot find the file path: '{0}'. "
                "Please update the file's path attribute.".format(self.path)
            )

        response = self._connection.file_request(url, self.path, featurefile_info, "rb")
        response_data, err = utility.check_server_response(response)
        if err is False:
            self.uuid = response_data["uuid"]

        return response

    def update(self):
        """Calls the REST API to update the featurefile's properties on the server."""
        url = "project/{0}/featurefile/{1}/".format(self._project.uuid, self.uuid)
        featurefile_info = {"name": self.name, "is_features": self.is_features}

        if not os.path.exists(self.path):
            raise OSError(
                "Cannot update featurefile because the system cannot find the file path: '{0}'. "
                "Please update the file's path attribute.".format(self.path)
            )

        response = self._connection.file_request(
            url, self.path, featurefile_info, "rb", method="put"
        )
        response_data, err = utility.check_server_response(response)

        return response

    def delete(self):
        """Calls the REST API and deletes the featurefile from the server."""
        url = "project/{0}/featurefile/{1}/".format(self._project.uuid, self.uuid)
        response = self._connection.request("delete", url)
        response_data, err = utility.check_server_response(response)

        return response

    def refresh(self):
        """Calls the REST API and populate the featurefile's properties from the server."""
        url = "project/{0}/featurefile/{1}/".format(self._project.uuid, self.uuid)
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            self.name = response_data["name"]
            self.is_features = response_data["is_features"]

        return response

    def download(self):
        """Calls the REST API and retrieves the featurefile's binary data.

        Returns:
            featurefile contents
        """

        url = "project/{0}/featurefile/{1}/data/".format(self._project.uuid, self.uuid)

        response = self._connection.request("get", url)

        return response

    def download_json(self):
        """Calls the REST API and retrieves the featurefile's json data.

        Returns:
            featurefile contents as json
        """

        url = "project/{0}/featurefile/{1}/json/".format(self._project.uuid, self.uuid)

        response = self._connection.request("get", url)

        return response

    def compute_analysis(self, analysis_type="UMAP", **kwargs):
        """Calls the REST API to compute the analysis for the feature file.

        Args:
            analysis_type (str): the type of clustering analysis, ie "UMAP" (default), "TSNE" and "PCA".

        Kwargs:
            shuffle_seed (int): random seed to shuffle and resample feature vector
            analysis_seed (int): random state of the analysis (default is 0)
            n_neighbor (int): The size of local neighborhood (in terms of number of neighboring sample points) used for manifold approximation. If not specified, default is the number of unique labels.
            n_components (int): The dimension of the output result. Default is 2. 'n_components' is adjusted based on the method, dimension of the feature vector and number of samples
            n_sample (int): Maximum number of output samples. Default is 1000.

        Returns:
            A JSON response containing the metadata of the generated analysis.

        Example:
            >>> feature_file = client.get_featurefile(<feature-file uuid>)
            >>> response = feature_file.compute_analysis(analysis_type="PCA", shuffle_seed=13, n_components=5)
            >>> response.json()

        """

        url = "project/{0}/featurefile-analysis/{1}/".format(
            self._project.uuid, self.uuid
        )

        json_payload = dict({"analysis_type": analysis_type}, **kwargs)

        response = self._connection.request("post", url, json=json_payload)

        return response

    def list_analysis(self):
        """Calls the REST API and retrieve list of computed analysis for featurefile

        Returns:
            JSON response holding the list of all computed analysis
        """

        url = "project/{0}/featurefile-analysis/{1}/".format(
            self._project.uuid, self.uuid
        )

        response = self._connection.request("get", url)

        response_data, err = utility.check_server_response(response)

        if err is True:
            print(err)
            return response

        return response_data
