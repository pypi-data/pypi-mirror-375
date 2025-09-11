from pyspark.sql import SparkSession
from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient
from datetime import datetime
from pyspark.sql.functions import lit, when, col, current_timestamp, monotonically_increasing_id, from_json, explode
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType, BooleanType, ArrayType
import json

from FabricFramework.FabricLocations import *
from FabricFramework.FabricDataInterface import *
from FabricFramework.DataSource import *
from FabricFramework.LogMonitor import *
from FabricFramework.DataValidation import *


class FabricConfiguration:
    """
    Configuration class for managing fabric data ingestion and validation processes.
    """

    def __init__(self, ingestConfiguration, constants, function=None, listofSourceSystems=None, listofSourceID=None):
        """
        Initialize the FabricConfiguration.

        Args:
            ingestConfiguration: Configuration for ingestion.
            constants: Dictionary containing constant values.
            function: Optional function to be applied during ingestion.
            listofSourceSystems: Optional list of source systems to filter by.
            listofSourceID: Optional list of source IDs to filter by.
        """
        self.spark = SparkSession.builder.appName("Default_Config").getOrCreate()
        self.fabricInterface = FabricDataInterface()
        self.ingestConfiguration = ingestConfiguration
        self.function = function
        self.constants = constants
        self.sources = self._filterSources(listofSourceSystems, listofSourceID)
        self.logger = Logger.getInstance(
            constants['LOGS_AZURE_TENANT_ID'], constants['LOGS_AZURE_CLIENT_ID'],
            constants['LOGS_AZURE_CLIENT_SECRET'], constants['DCE_ENDPOINT'],
            constants['DRC_ID'], constants['LOG_BUFFER_SIZE']
        )
        self.entity_log_stream = constants['LOG_STREAM']

    def flushLogs(self):
        """
        Flush the logs to the log stream.
        """
        self.logger.flushLogs(self.entity_log_stream)

    def _filterSources(self, listofSourceSystems=None, listofSourceID=None):
        """
        Filter the sources based on the provided source systems and source IDs.

        Args:
            listofSourceSystems: List of source systems to filter by.
            listofSourceID: List of source IDs to filter by.

        Returns:
            Filtered list of sources.
        """
        sources = self.ingestConfiguration.collect()

        if not listofSourceSystems and not listofSourceID:
            return sources

        if listofSourceSystems:
            systems_set = set(listofSourceSystems)
            sources = [source for source in sources if source.system_code in systems_set]

        if listofSourceID:
            sourceid_set = set(listofSourceID)
            sources = [source for source in sources if source.SourceID in sourceid_set]

        return sources

    def validateTables(self, rawDF=None, sourceParams=None):
        """
        Validate tables by processing raw dataframes and saving them to the trusted stage.

        Args:
            rawDF: Raw dataframe to be validated.
            sourceParams: Additional parameters for source.
        """

        # TODO: add the ability to pass in a single raw datagrame and process that into trusted
        if not rawDF:
            for source in self.sources:
                
                # Check if ingestion is enabled
                if source["ingestion_enabled"]:

                    # if the validation is not enabled then write table directly to Trusted
                    if not source["validation_enabled"]:
                        lakehouse_raw = FabricLakehouseLocation(
                            self.constants['LAKEHOUSE_RAW_STAGE_NAME'],
                            source["raw_workspace"],
                            source["raw_lakehouse"]
                        )
                        raw_destination_table = FabricTableLocation(source["destination_name"], lakehouse_raw)
                        df = self.fabricInterface.loadLatestDeltaTable(raw_destination_table)

                        lakehouse_trusted = FabricLakehouseLocation(
                            self.constants['LAKEHOUSE_TRUSTED_STAGE_NAME'],
                            source["trusted_workspace"],
                            source["trusted_lakehouse"]
                        )
                        trusted_destination_table = FabricTableLocation(source["destination_name"], lakehouse_trusted)

                        if self.constants['LOGGING_LEVEL'] != 'NONE':
                            # creates the first initial log in this section
                            assembler = LogAssembler(self.entity_log_stream, self.constants, source, "Processing",
                                                    self.constants['LAKEHOUSE_TRUSTED_STAGE_NAME'])
                            newLog = assembler.createLog()
                            self.logger.updateAndQueueLog(newLog, None, self.entity_log_stream)

                        # check the save type (CDC or not)
                        if "cdc" not in source["trusted_savetype"].lower():
                            targetCount = self.fabricInterface.saveDeltaTable(
                                sourceDataFrame=df,
                                fabricTableLocation=trusted_destination_table,
                                savetype=source["trusted_savetype"],
                                primarykey=source["primary_key"]
                            )
                        else:  # TODO: create a CDC function call
                            targetCount = self.fabricInterface.saveCDCTable(
                                df=df,
                                fabricTableLocation=trusted_destination_table,
                                savetype=source["trusted_savetype"],
                                primarykey=source["primary_key"],
                                rowhash_columns = source["rowhash_columns"],
                                transactional_watermark_column = source["watermark"]
                            )

                        # now log the save event.
                        if self.constants['LOGGING_LEVEL'] != 'NONE':
                            updated_log = {
                                "EndDateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "LogDateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "Status": "Completed", "SourceRows": df.count(), "TargetRows": targetCount
                            }
                            log = Log(self.entity_log_stream, updated_log)
                            self.logger.updateAndQueueLog(newLog, log, self.entity_log_stream)

                    else:  # if the validation is enabled for the SourceID

                        print("Starting Data Validation Process...")

                        if self.constants['LOGGING_LEVEL'] != 'NONE':
                            # creates the first initial log in this section
                            assembler = LogAssembler(self.entity_log_stream, self.constants, source,
                                                    "Data Validation Started",
                                                    self.constants['LAKEHOUSE_TRUSTED_STAGE_NAME'])
                            newLog = assembler.createLog()
                            self.logger.updateAndQueueLog(newLog, None, self.entity_log_stream)

                        lakehouse_raw = FabricLakehouseLocation(
                            self.constants['LAKEHOUSE_RAW_STAGE_NAME'],
                            source["raw_workspace"],
                            source["raw_lakehouse"]
                        )
                        raw_destination_table = FabricTableLocation(source["destination_name"], lakehouse_raw)
                        df = self.fabricInterface.loadLatestDeltaTable(raw_destination_table)

                        lakehouse_trusted = FabricLakehouseLocation(
                            self.constants['LAKEHOUSE_TRUSTED_STAGE_NAME'],
                            source["trusted_workspace"],
                            source["trusted_lakehouse"]
                        )
                        trusted_destination_table = FabricTableLocation(source["destination_name"], lakehouse_trusted)

                        list_validation = []

                        source_df = self.ingestConfiguration.filter(col("SourceID") == source["SourceID"])

                        df_exploded = source_df.withColumn("json_obj", explode("data_validation"))

                        # Process each JSON object
                        collected_data = df_exploded.select("json_obj").collect()

                        for row in collected_data:
                            json_obj = row["json_obj"]

                            options = []
                            if json_obj["Validation_Type"] == "expect_column_values_to_be_between":
                                options.append(int(json_obj["Options"][0]))
                                options.append(int(json_obj["Options"][1]))
                            elif json_obj["Validation_Type"] == "expect_column_values_to_match_regex" or json_obj[
                                "Validation_Type"] == "expect_column_values_to_be_of_data_type":
                                options.append(str(json_obj["Options"][0]))

                            expectation = Expectation(json_obj["Validation_Type"], json_obj["Column"], json_obj["Pass"],
                                                    options)
                            list_validation.append(expectation)

                        # sk = source["primary_key"] if (
                        #             source["primary_key"] != "" and source["primary_key"] is not None) else None

                        # TODO - merge composite key into a single column of values

                        sk = source["primary_key"][0]

                        gxv = GreatExpectationsValidation(df, trusted_destination_table, list_validation, sk=sk)
                        result = gxv.validateData()

                        if self.constants['LOGGING_LEVEL'] in ['INFO', 'DEBUG']:
                            updated_log = {
                                "EndDateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "LogDateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "Status": "Completed"
                            }
                            log = Log(self.entity_log_stream, updated_log)
                            self.logger.updateAndQueueLog(newLog, log, self.entity_log_stream)
                else:


                    if self.constants['LOGGING_LEVEL'] != 'NONE':
                        # creates the first initial log in this section
                        assembler = LogAssembler(self.entity_log_stream, self.constants, source,
                                                "Processing",
                                                self.constants['LAKEHOUSE_TRUSTED_STAGE_NAME'])
                        newLog = assembler.createLog()
                        self.logger.updateAndQueueLog(newLog, None, self.entity_log_stream)

                    print(f'Skipping SourceID: {source["SourceID"]} as it is disabled in the ingestion configuration.')
                    if self.constants['LOGGING_LEVEL'] in ['INFO', 'DEBUG']:
                        updated_log = {
                            "EndDateTime": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                            "LogDateTime": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                            "Status": "Skipped"
                        }
                        log = Log(self.entity_log_stream, updated_log)
                        self.logger.updateAndQueueLog(newLog, log, self.entity_log_stream)


    # TODO: Option to load only a single table or multiple (provided as a list)
    def loadTables(self):
        """
        Load tables from the sources, preprocess and save them to the raw stage.
        """
        for source in self.sources:
            print(f'Evaluating SourceID: {source["SourceID"]}')

            if source["ingestion_enabled"]:
                print(f'Ingestion enabled for SourceID: {source["SourceID"]} and ingestion started.')

                if source["source_type"] == 'FABRIC-TEXT':
                    connection = source["prelanding_workspace"] + ";" + source["prelanding_lakehouse"]
                elif source["source_type"] == 'FABRIC-TABLE':
                    connection = source["prelanding_workspace"] + ";" + source["prelanding_lakehouse"]
                else:
                    keyvaultConnection = KeyVault(
                        source["key_vault_name"], source["tenant_id"], source["client_id"],
                        source["client_secret"], source["secret_name"]
                    )
                    connection = keyvaultConnection.secretValue

                newDataSource = DataSource.getDataSourceType(connection, source, self.function, self.constants)
                loaded_data = newDataSource.loadTable()

                lakehouse_raw = FabricLakehouseLocation(
                    self.constants['LAKEHOUSE_RAW_STAGE_NAME'],
                    source["raw_workspace"],
                    source["raw_lakehouse"]
                )
                raw_destination_table = FabricTableLocation(source["destination_name"], lakehouse_raw)

                if self.constants['LOGGING_LEVEL'] != 'NONE':
                    # creates the first initial log
                    assembler = LogAssembler(self.entity_log_stream, self.constants, source, "Processing", self.constants['LAKEHOUSE_RAW_STAGE_NAME'])
                    newLog = assembler.createLog()
                    self.logger.updateAndQueueLog(newLog, None, self.entity_log_stream)

                targetCount = self.fabricInterface.saveDeltaTable(
                    loaded_data,
                    raw_destination_table,
                    savetype=source["raw_savetype"],
                    primarykey=source["primary_key"]
                )

                if self.constants['LOGGING_LEVEL'] != 'NONE':
                    updated_log = {
                        "EndDateTime": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                        "LogDateTime": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                        "Status": "Completed", "SourceRows": loaded_data.count(), "TargetRows": targetCount
                    }
                    log = Log(self.entity_log_stream, updated_log)
                    self.logger.updateAndQueueLog(newLog, log, self.entity_log_stream)

            else:

                if self.constants['LOGGING_LEVEL'] != 'NONE':
                    # creates the first initial log
                    assembler = LogAssembler(self.entity_log_stream, self.constants, source, "Processing", self.constants['LAKEHOUSE_RAW_STAGE_NAME'])
                    newLog = assembler.createLog()
                    self.logger.updateAndQueueLog(newLog, None, self.entity_log_stream)

                print(f'Skipping SourceID: {source["SourceID"]} as it is disabled in the ingestion configuration.')
                if self.constants['LOGGING_LEVEL'] in ['INFO', 'DEBUG']:
                    updated_log = {
                        "EndDateTime": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                        "LogDateTime": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                        "Status": "Skipped"
                    }
                    log = Log(self.entity_log_stream, updated_log)
                    self.logger.updateAndQueueLog(newLog, log, self.entity_log_stream)


class KeyVault:
    """
    Class for interacting with Azure Key Vault to retrieve secrets.
    """

    def __init__(self, keyvaultname, tenantid, clientid, clientsecret, secretName):
        """
        Initialize the KeyVault client.

        Args:
            keyvaultname: Name of the Key Vault.
            tenantid: Azure Tenant ID.
            clientid: Azure Client ID.
            clientsecret: Azure Client Secret.
            secretName: Name of the secret to retrieve.
        """
        credential = ClientSecretCredential(tenantid, clientid, clientsecret)
        vaultURL = f"https://{keyvaultname}.vault.azure.net"
        secretClient = SecretClient(vault_url=vaultURL, credential=credential)
        self.secretVal = secretClient.get_secret(secretName).value

    @property
    def secretValue(self):
        """
        Retrieve the secret value.

        Returns:
            Secret value from the Key Vault.
        """
        return self.secretVal
