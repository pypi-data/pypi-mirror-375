from pyspark.sql import SparkSession
from delta.tables import *
import sys

from FabricFramework.FabricCache import *
from FabricFramework.FabricLocations import *
from FabricFramework.FabricDataInterface import *
from FabricFramework.FabricConfiguration import *


class FabricFramework:
    """
    Class representing the Fabric Framework for data ingestion.
    """

    def __init__(self, ingestionConfigurationFilePath, ingestionConfigurationTablePath, constants,
                 preProcessFunction=None):
        """
        Initialize a FabricFramework object.

        :param ingestionConfigurationFilePath: Path to the ingestion configuration file.
        :param ingestionConfigurationTablePath: Path to the ingestion configuration table.
        :param constants: Dictionary containing constant values.
        :param preProcessFunction: Optional pre-processing function.
        """
        # Check if the required constants are provided
        self._constantsListChecker(constants)

        #Create the WS and LH cache
        cache = FabricCache()
        cache.load_workspace_lakehouses()

        self.ingestConfigurationFileLocation = convertURL(ingestionConfigurationFilePath,
                                                          constants['LAKEHOUSE_CONTROL_STAGE_NAME'])
        self.ingestConfigurationTableLocation = convertURL(ingestionConfigurationTablePath,
                                                           constants['LAKEHOUSE_CONTROL_STAGE_NAME'])
        self.preprocess = preProcessFunction
        self.constants = constants
        self.spark = SparkSession.builder.appName("Default_Config").getOrCreate()
        self.fabricInterface = FabricDataInterface()
        self.ingestConfiguration = self.fabricInterface.loadIngestionConfiguration(
            self.ingestConfigurationFileLocation, self.ingestConfigurationTableLocation
        )

    def _constantsListChecker(self, constants):
        """
        Check if the required constants are provided in the constants dictionary.

        :param constants: Dictionary containing constant values.
        :raises SystemExit: If required constants are missing.
        """
        # Ensure constants are provided
        if not constants:
            print("Must supply a constants list that include: workspace, lakehouse and log details.")
            sys.exit(1)
        elif not constants['LAKEHOUSE_CONTROL_STAGE_NAME'] or \
                not constants['LAKEHOUSE_RAW_STAGE_NAME'] or \
                not constants['LAKEHOUSE_TRUSTED_STAGE_NAME'] or \
                not constants['LAKEHOUSE_CURATED_STAGE_NAME']:
            print("Missing Lakehouse details from constants.")
            print("Must supply a constants list that include: workspace, lakehouse and log details.")
            sys.exit(1)

        # Ensure logging level is provided
        if not constants['LOGGING_LEVEL']:
            print("Missing Logging Level from constants.")
            print("Must supply a constants list that include: workspace, lakehouse and log details.")
            sys.exit(1)
        elif constants['LOGGING_LEVEL'] != 'NONE' and \
                (not constants['LOGS_AZURE_TENANT_ID'] or \
                 not constants['LOGS_AZURE_CLIENT_ID'] or \
                 not constants['LOGS_AZURE_CLIENT_SECRET'] or \
                 not constants['DCE_ENDPOINT'] or \
                 not constants['DRC_ID'] or \
                 not constants['LOG_STREAM'] or \
                 not constants['LOG_BUFFER_SIZE']):
            print("Missing Log details from constants.")
            print("Must supply a constants list that include: workspace, lakehouse and log details.")
            sys.exit(1)

    def runIngestion(self, layer=None, system_code=None, sourceID=None):
        """
        Run the ingestion process for the specified layer, system code, and source ID.

        :param layer: Optional layer to ingest (e.g., RAW, TRUSTED).
        :param system_code: Optional system code for the source system.
        :param sourceID: Optional source ID for the source system.
        """
        fabricConfigInstance = FabricConfiguration(
            self.ingestConfiguration, self.constants, self.preprocess,
            listofSourceSystems=system_code, listofSourceID=sourceID
        )

        # Ingest to RAW layer
        if layer is None or self.constants["LAKEHOUSE_RAW_STAGE_NAME"] in layer:
            print(f'Ingesting to {self.constants["LAKEHOUSE_RAW_STAGE_NAME"]}.')
            fabricConfigInstance.loadTables()
            print(f'Ingestion to {self.constants["LAKEHOUSE_RAW_STAGE_NAME"]} Complete.')

        # Load to TRUSTED layer
        if layer is None or self.constants["LAKEHOUSE_TRUSTED_STAGE_NAME"] in layer:
            print(f'Ingesting to {self.constants["LAKEHOUSE_TRUSTED_STAGE_NAME"]}.')
            fabricConfigInstance.validateTables()
            print(f'Ingestion to {self.constants["LAKEHOUSE_TRUSTED_STAGE_NAME"]} Complete.')

        # Flush any remaining logs to the Azure log service
        if self.constants['LOGGING_LEVEL'] != 'NONE':
            print("Saving Logs...", end='')
            fabricConfigInstance.flushLogs()
            print("Logs saved.")
            print("Ingestion Complete.")
