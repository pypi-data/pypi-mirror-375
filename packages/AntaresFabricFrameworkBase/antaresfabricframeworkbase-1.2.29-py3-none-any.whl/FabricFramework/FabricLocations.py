from pyspark.sql import SparkSession
from FabricFramework.FabricCache import *


# TODO: import this from the constants list defined in an external notebook
# Define a list to hold lakehouse stage names
LAKEHOUSE_STAGE_LIST = []

# Define constants for different lakehouse stages
LAKEHOUSE_CONTROL_STAGE_NAME = 'CONTROL'
LAKEHOUSE_PREPROCESSING_STAGE_NAME = 'PREPROCESSING'
LAKEHOUSE_RAW_STAGE_NAME = 'RAW'
LAKEHOUSE_TRUSTED_STAGE_NAME = 'TRUSTED'
LAKEHOUSE_CURATED_STAGE_NAME = 'CURATED'

# Extend the stage list with the defined stage names
LAKEHOUSE_STAGE_LIST.extend([
    LAKEHOUSE_CONTROL_STAGE_NAME,
    LAKEHOUSE_PREPROCESSING_STAGE_NAME,
    LAKEHOUSE_RAW_STAGE_NAME,
    LAKEHOUSE_TRUSTED_STAGE_NAME,
    LAKEHOUSE_CURATED_STAGE_NAME
])


class FabricLakehouseLocation:
    """
    Class representing a Fabric Lakehouse Location.
    """

    def __init__(self, stage, workspace, lakehouse):
        """
        Initialize a FabricLakehouseLocation object.

        :param stage: Stage of the lakehouse.
        :param workspace: Workspace ID.
        :param lakehouse: Lakehouse ID.
        """
        self._stage = stage
        self.fabricCache = FabricCache()
        self._workspace = self.fabricCache.getWorkspaceId(workspace)
        self._lakehouse = self.fabricCache.getLakehouseId(workspace, lakehouse)
        self.spark = SparkSession.builder.appName("Default_Config").getOrCreate()

    @property
    def stage(self):
        return self._stage

    @property
    def workspace(self):
        return self._workspace

    @property
    def lakehouse(self):
        return self._lakehouse

    def abfss_path(self, path=None):
        """
        Generate an ABFSS path for the lakehouse location.

        :param path: Optional path within the lakehouse.
        :return: ABFSS path as a string.
        """
        if path:
            return f'abfss://{self._workspace}@onelake.dfs.fabric.microsoft.com/{self._lakehouse}/{path}'
        return f'abfss://{self._workspace}@onelake.dfs.fabric.microsoft.com/{self._lakehouse}'

    @stage.setter
    def stage(self, stage):
        """
        Setter for the stage property, with validation against the predefined stage list.

        :param stage: Stage to be set.
        :raises ValueError: If the stage is not in the predefined stage list.
        """
        if stage not in LAKEHOUSE_STAGE_LIST:
            raise ValueError("Stage name must be defined in the LAKEHOUSE_STAGE_LIST")
        self._stage = stage


class FabricLocation:
    """
    Base class for Fabric locations.
    """

    def abfss_path(self):
        pass



class FabricFileLocation(FabricLocation):
    """
    Class representing a file location in the lakehouse.
    """

    def __init__(self, file, lakehouseLocation=None):
        """
        Initialize a FabricFileLocation object.

        :param file: File name.
        :param lakehouseLocation: Optional FabricLakehouseLocation object.
        """
        if lakehouseLocation:
            self.location = lakehouseLocation.abfss_path(f'Files/{file}')
        else:
            self.location = f'Files/{file}'

    def abfss_path(self):
        return self.location


class FabricFolderLocation(FabricLocation):
    """
    Class representing a folder location in the lakehouse.
    """

    def __init__(self, folder, lakehouseLocation=None):
        """
        Initialize a FabricFolderLocation object.

        :param folder: Folder name.
        :param lakehouseLocation: Optional FabricLakehouseLocation object.
        """
        if lakehouseLocation:
            self.location = lakehouseLocation.abfss_path(f'Files/{folder}')
        else:
            self.location = f'Files/{folder}'

    def abfss_path(self):
        return self.location


class FabricTableLocation(FabricLocation):
    """
    Class representing a table location in the lakehouse.
    """

    def __init__(self, table, lakehouseLocation=None):
        """
        Initialize a FabricTableLocation object.

        :param table: Table name.
        :param lakehouseLocation: Optional FabricLakehouseLocation object.
        """
        if lakehouseLocation:
            self.location = lakehouseLocation.abfss_path(f'Tables/{table}')
        else:
            self.location = f'Tables/{table}'

        self.table = table
        self.lakehouseLocation = lakehouseLocation

    def abfss_path(self):
        return self.location

    def changeTableName(self, newTableName):
        if self.lakehouseLocation:
            self.location = self.lakehouseLocation.abfss_path(f'Tables/{newTableName}')
        else:
            self.location = f'Tables/{newTableName}'

    def getTableName(self):
        return self.table


def extract_url(url):
    """
    Extract components from a given ABFSS URL.

    :param url: ABFSS URL as a string.
    :return: Tuple containing workspace ID, lakehouse ID, entity name, and entity type.
    :raises ValueError: If the URL does not contain 'Tables/' or 'Files/'.
    """
    core_part = url.split('://')[1]

    # Extract the workspace_id
    workspace_id, rest = core_part.split('@onelake.dfs.fabric.microsoft.com/')

    # Extract the lakehouse_id and the latter part which could contain Tables or Files
    lakehouse_id, latter_part = rest.split('.Lakehouse/')

    # Check if the latter part contains 'Tables' or 'Files' and extract table_name or file_name
    if 'Tables/' in latter_part:
        entity_type, entity_name = latter_part.split('/')
    elif 'Files/' in latter_part:
        entity_type, entity_name = latter_part.split('/')
    else:
        raise ValueError("URL should contain either 'Tables/' or 'Files/'")

    return workspace_id, lakehouse_id, entity_name, entity_type


def convertURL(url, lakehouseName):
    """
    Convert a given URL to a FabricLocation object.

    :param url: ABFSS URL as a string.
    :param lakehouseName: Name of the lakehouse.
    :return: FabricLocation object representing the converted URL.
    :raises ValueError: If the URL does not contain 'Tables/' or 'Files/'.
    """
    workspace_id, lakehouse_id, entity_name, type = extract_url(url)

    # Create lakehouse location
    lakehouse = FabricLakehouseLocation(lakehouseName, workspace_id, lakehouse_id)

    # Create file or table location
    if type == 'Files':
        location = FabricFileLocation(entity_name, lakehouse)
    elif type == 'Tables':
        location = FabricTableLocation(entity_name, lakehouse)
    else:
        raise ValueError("URL should contain either 'Tables/' or 'Files/'")

    return location
