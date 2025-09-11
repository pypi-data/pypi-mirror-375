from pyspark.sql import SparkSession
from delta.tables import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
import sys

import importlib.resources

import os
import pandas as pd
from datetime import timedelta
from azure.monitor.query import LogsQueryClient, LogsQueryStatus
from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential

from FabricFramework.FabricLocations import *
from FabricFramework.FabricDataInterface import *
from FabricFramework.FabricConfiguration import *
from FabricFramework.FabricFramework import *

LAKEHOUSE_CONTROL_STAGE_NAME = 'CONTROL'
LAKEHOUSE_PREPROCESSING_STAGE_NAME = 'PREPROCESSING'
LAKEHOUSE_RAW_STAGE_NAME = 'RAW'
LAKEHOUSE_TRUSTED_STAGE_NAME = 'TRUSTED'
LAKEHOUSE_CURATED_STAGE_NAME = 'CURATED'

# Below constants represent the types of validation
IS_NULL = "expect_column_values_to_not_be_null"
IS_OUT_OF_RANGE = "expect_column_values_to_be_between" # The first value is the minimum, whilst the second is the maximum
IS_NOT_MATCHING_REGEX = "expect_column_values_to_match_regex"
IS_NOT_EXPECTED_DATA_TYPE = "expect_column_values_to_be_of_data_type"

# Below constants represent the Data Type validations
INTEGER_TYPE = "Integer"
DOUBLE_TYPE = "Double"
BOOLEAN_TYPE = "Boolean"

EMPLOYEES_DATASET_PATH = "employees.csv"
EMPLOYEES_INSERT_DATASET_PATH = "employees-insert.csv"
EMPLOYEES_UPDATE_DATASET_PATH = "employees-update.csv"
EMPLOYEES_DELETE_DATASET_PATH = "employees-delete.csv"
EMPLOYEES_CDC_INSERT_DATASET_PATH = "employees-cdc-insert.csv"
EMPLOYEES_CDC_UPDATE_DATASET_PATH = "employees-cdc-update.csv"
EMPLOYEES_CDC_DELETE_DATASET_PATH = "employees-cdc-delete.csv"
EMPLOYEES_GX_VALID_DATASET_PATH = "employees-gx-valid-rows.csv"
EMPLOYEES_GX_NULL_INVALID_DATASET_PATH = "employees-gx-null-invalid-rows.csv"
EMPLOYEES_GX_INRANGE_INVALID_DATASET_PATH = "employees-gx-inRange-invalid-rows.csv"
EMPLOYEES_GX_REGEX_INVALID_DATASET_PATH = "employees-gx-regex-invalid-rows.csv"
EMPLOYEES_GX_INTEGER_INVALID_DATASET_PATH = "employees-gx-int-invalid-rows.csv"
EMPLOYEES_GX_DOUBLE_INVALID_DATASET_PATH = "employees-gx-double-invalid-rows.csv"
EMPLOYEES_GX_BOOLEAN_INVALID_DATASET_PATH = "employees-gx-boolean-invalid-rows.csv"

TEST_DATA_DF_COLUMNS = ["employeeId", "firstName", "surName", "age", "dateOfBirth", "position", "salary", "isSenior"]
TEST_RESULT_DF_COLUMNS = ["sourceId", "testModule", "sourceType", "testCase", "success"]

TEST_DATA_SOURCE_SCHEMA = StructType([
            StructField("employeeId", IntegerType(), False)
            , StructField("firstName", StringType(), False)
            , StructField("surName", StringType(), True)
            , StructField("age", IntegerType(), False)
            , StructField("dateOfBirth", DateType(), False)
            , StructField("position", StringType(), False)
            , StructField("salary", DoubleType(), False)
            , StructField("isSenior", BooleanType(), False)
        ])

TEST_RESULT_SCHEMA = StructType([
            StructField("sourceId", StringType(), False)
            , StructField("testModule", StringType(), False)
            , StructField("sourceType", StringType(), False)
            , StructField("testCase", StringType(), False)
            , StructField("success", BooleanType(), True)
        ])


class DeploymentTesting:

    """
        A wrapper class for initiating the deployment testing.
    """

    def __init__(self, ingestionConfigurationFilePath, ingestionConfigurationTablePath, constants,
                 preProcessFunction=None, layer=None, system_code=None, sourceID=None):
        
        """
        Initialize DeploymentTesting

        Args:
            ingestionConfigurationFilePath: ingestion configuration file path
            ingestionConfigurationTablePath: ingestion configuration table path
            constants: Dictionary containing constant values.
            preProcessFunction: Optional function to be applied during ingestion.
            layer: Optional layers to be applied during ingestion.
            system_code: Optional list of source systems to filter by.
            sourceID: Optional list of source IDs to filter by.
        """

        # Configuration value initialization
        self.ingestionConfigurationFilePath = ingestionConfigurationFilePath
        self.ingestionConfigurationTablePath = ingestionConfigurationTablePath
        self.constants = constants
        self.preProcessFunction = preProcessFunction
        self.ff = FabricFramework(self.ingestionConfigurationFilePath, self.ingestionConfigurationTablePath
                             , self.constants, self.preProcessFunction)
        self.ingestConfiguration = self.ff.ingestConfiguration
        self.fabricConfigInstance = FabricConfiguration(self.ingestConfiguration, self.constants, self.preProcessFunction,
                                            listofSourceSystems=system_code, listofSourceID=sourceID)
        self.sources = self.fabricConfigInstance.sources
        
        # Ingestion value initialization
        self.layer = layer
        self.system_code = system_code
        self.sourceID = sourceID
        
        """ For now, we have paused on Automated Data Source creation """
        # Creation of Custom Datasources for testing
        # self.testDataSources = TestDataSources(self.sources)
        # self.testDataSources.createDataSources()

    def runIngestion(self):

        """
        Executes the runIngestion method of the FabricFramework object
        """

        self.ff.runIngestion(self.layer, self.system_code, self.sourceID)

    def runDeploymentTesting(self):

        """
        Initiates the deployment testing for the executed ingestion flow
        """

        testIngestionFlow = TestIngestionFlow(self.sources, self.constants)
        testIngestionFlow.initiateTesting()

class TestDataSources:

    def __int__(self, sources):
        self.sources = sources
        self.spark = SparkSession.builder.appName("Default_Config").getOrCreate()
        self.df = DataTransformation.createDatasetDF(self.spark, EMPLOYEES_DATASET_PATH)
        self.fabricDataInterface = FabricDataInterface()

    def createDataSources(self):
        
        for source in self.sources:

            sourceType = source["source_type"].upper()

            if sourceType == 'SQL':
                return "TBD"
            elif sourceType == 'FABRIC-TEXT':
                return self.createFabricTextDataSource()
            elif sourceType == 'FABRIC-TABLE':
                return self.createFabricTableDataSource()

    def createSQLTableDataSource(self, source):

        # Create a CSV file in the relevant DB in SQL
        return "TBD"

    def createFabricTextDataSource(self, source):

        # Create a CSV file in the relevant Lakehouse
        fabricLakehouseLocation = FabricLakehouseLocation(self.ingestConfiguration["LAKEHOUSE_PREPROCESSING_STAGE_NAME"]
                                                    , source["prelanding_workspace"], source["lakehouse"])
        fabricFileLocation = FabricFileLocation(source["source_name"], fabricLakehouseLocation)
        self.df.write.mode("overwrite").format('csv').save(fabricFileLocation.abfss_path())
        return "Success"

    def createFabricTableDataSource(self, source):

        # Create the Fabric Location and then save the table
        fabricLakehouseLocation = FabricLakehouseLocation(self.ingestConfiguration["LAKEHOUSE_PREPROCESSING_STAGE_NAME"]
                                                    , source["prelanding_workspace"], source["lakehouse"])
        fabricTableLocation = FabricTableLocation(source["source_name"], fabricLakehouseLocation)
        testDataTableRecordCount = self.fabricDataInterface.saveDeltaTable(self.df, fabricTableLocation, 'overwrite', [])
        return "Success"

class TestIngestionFlow:

    """
    Initiations for the required deployment tests
    """

    def __init__(self, sources, constants):


        """
        Initialize TestIngestionFlow

        Args:

            sources: Source object definitions from the ingestion configuration table.
            constants: Dictionary containing constant values.
        """

        self.spark = SparkSession.builder.appName("Default_Config").getOrCreate()
        self.fabricDataInterface = FabricDataInterface()
        self.sources = sources
        self.constants = constants
        self.df = DataTransformation.createDatasetDF(self.spark, EMPLOYEES_DATASET_PATH)
        self.testResultsWorkspace = sources[0]["prelanding_workspace"]
        self.testResultsLakehouse = sources[0]["prelanding_lakehouse"]
        self.testResultTableName = "DeploymentTestResults"
        self.testResultDF = self.spark.createDataFrame([], TEST_RESULT_SCHEMA)

    def initiateTesting(self):

        """
        Initiates the deployment testing. For the testing to proceed, ingestion_enabled should be True.
        
        General deployment tests goes as follows:
            - Ingestion Deployment Test
            - Raw Ingestion Test
            - Trusted Ingestion Test
            - Log Analytics Test - ** LOGGING_LEVEL should not be NONE for this to wrok

        If validation_enabled is True
            - GX Validation Test
        """

        for source in self.sources:

            if(source["ingestion_enabled"] == 1):
                if(source["validation_enabled"] == 1): # If validation is enabled, we only proceed with GX Test
                    self.testResultDF = self.testResultDF.union(self.initateGXValidationTest(source))
                else:
                    self.testResultDF = self.testResultDF.union(self.initiateIngestionDeploymentTest(source))
                    self.testResultDF = self.testResultDF.union(self.initiateRawIngestionTest(source))
                    self.testResultDF = self.testResultDF.union(self.initiateTrustedIngestionTest(source))
                    if self.constants['LOGGING_LEVEL'] != 'NONE':
                        self.testResultDF = self.testResultDF.union(self.initiateLogAnalyticsTest(source))

        resultTableRowCount = self.createDeploymentTestResultTable()

        return self.testResultDF

    def initiateIngestionDeploymentTest(self, source):

        testModule = TestModule("INGESTION Test", "INGESTION"
                                , source
                                , targetStageName=LAKEHOUSE_RAW_STAGE_NAME
                                , targetWorkspace=source["raw_workspace"]
                                , targetLakehouse=source["raw_lakehouse"]
                                , targetDestinationName=source["destination_name"] 
                                )
        testResult = testModule.ingestionTest()
        testResultRows = []

        for key,value in testResult.items():

            testResultRow = Row(source["SourceID"]
                            , "Ingestion Test"
                            , "Ingestion Deployment"
                            , key
                            , value)
            testResultRows.append(testResultRow)

        
        return self.spark.createDataFrame(testResultRows, schema=TEST_RESULT_SCHEMA)

    def initiateRawIngestionTest(self, source):

        currentDF = DataTransformation.createDatasetDF(self.spark, EMPLOYEES_DATASET_PATH)
        testModule = TestModule("RAW Test"
                                , "RAW"
                                , source
                                , targetStageName=LAKEHOUSE_RAW_STAGE_NAME
                                , targetWorkspace=source["raw_workspace"]
                                , targetLakehouse=source["raw_lakehouse"]
                                , targetDestinationName=source["destination_name"]
                                , df=currentDF)
        testResult = testModule.rawIngestionTest()
        testResultRows = []

        for key,value in testResult.items():

            testResultRow = Row(source["SourceID"]
                            , "RAW Test"
                            , ("RAW - " + source["raw_savetype"])
                            , key
                            , value)
            testResultRows.append(testResultRow)
    
        return self.spark.createDataFrame(testResultRows, schema=TEST_RESULT_SCHEMA)

    def initiateTrustedIngestionTest(self, source):

        currentDF = DataTransformation.createDatasetDF(self.spark, EMPLOYEES_DATASET_PATH)
        testModule = TestModule("TRUSTED Test"
                                , "TRUSTED"
                                , source
                                , targetStageName=LAKEHOUSE_TRUSTED_STAGE_NAME
                                , targetWorkspace=source["trusted_workspace"]
                                , targetLakehouse=source["trusted_lakehouse"]
                                , targetDestinationName=source["destination_name"]
                                , df=currentDF
                                )
        testResult = testModule.trustedIngestionTest()
        testResultRows = []

        for key,value in testResult.items():

            testResultRow = Row(source["SourceID"]
                            , "TRUSTED Test"
                            , ("TRUSTED - " + source["trusted_savetype"])
                            , key
                            , value)
            testResultRows.append(testResultRow)

        
        return self.spark.createDataFrame(testResultRows, schema=TEST_RESULT_SCHEMA)

    def initateGXValidationTest(self, source):

        currentDF = DataTransformation.createDatasetDF(self.spark, EMPLOYEES_DATASET_PATH)
        testModule = TestModule("TRUSTED Validation Test"
                                , "GX"
                                , source
                                , targetStageName=LAKEHOUSE_TRUSTED_STAGE_NAME
                                , targetWorkspace=source["trusted_workspace"]
                                , targetLakehouse=source["trusted_lakehouse"]
                                , targetDestinationName=source["destination_name"]
                                , df=currentDF
                                )
        testResult = testModule.gxIngestionTest()
        testResultRows = []

        for key,value in testResult.items():

            testResultRow = Row(source["SourceID"]
                            , "TRUSTED Validation Test"
                            , "GX"
                            , key
                            , value)
            testResultRows.append(testResultRow)

        
        return self.spark.createDataFrame(testResultRows, schema=TEST_RESULT_SCHEMA)

    def initiateLogAnalyticsTest(self, source):

        testModule = TestModule("LOG Test"
                                , "LOG"
                                , source=source
                                , constants=self.constants)
        testResult = testModule.logAnalyticsTest()
        testResultRows = []

        for key,value in testResult.items():

            testResultRow = Row(source["SourceID"]
                            , "LOG Test"
                            , "LOG"
                            , key
                            , value)
            testResultRows.append(testResultRow)

        
        return self.spark.createDataFrame(testResultRows, schema=TEST_RESULT_SCHEMA)

    def createDeploymentTestResultTable(self):

        testResultLakehouseLocation = FabricLakehouseLocation(LAKEHOUSE_PREPROCESSING_STAGE_NAME
                                                    , self.testResultsWorkspace, self.testResultsLakehouse)
        testResultTableLocation = FabricTableLocation(self.testResultTableName, testResultLakehouseLocation)

        self.testResultDF = self.testResultDF.withColumn("testRunSK", monotonically_increasing_id())
        self.testResultDF = self.testResultDF.select("testRunSK", *TEST_RESULT_DF_COLUMNS)
        return self.fabricDataInterface.saveDeltaTable(self.testResultDF, testResultTableLocation, 'overwrite', ["testRunSK"])

# For a raw test, you crate e raw testmodule, for trusted you create a trusted test module
class TestModule:

    """
    Categories or Modules for the Deplyoment Testing.
    """

    def __init__(self, name, type, source, targetStageName=None, targetWorkspace=None, targetLakehouse=None
                , targetDestinationName=None, df=None, constants=None):
    
        """
        Initialize TestModule

        Args:

            name: Test Module name
            type: Test Module type. Values should be one of these: RAW, TRUSTED, GX, LOG
            source: ingestion object defintion
            targetStageName: Target Stage Name. Values should be one of these : CONTROL, PREPROCESSING, RAW, TRUSTED
            targetWorkspace: Target Table's workspace name
            targetLakehouse: Target Table's Lakehouse name
            targetDestinationName: Target Table's Destination name
            df: Current dataframe representing the expected values, which is used to  validate with the Target Table values
            constants: Dictionary containing constant values
        """

        self.spark = SparkSession.builder.appName("Default").getOrCreate() 
        self.name = name # module name
        self.type = type # module test type : RAW,TRUSTED,GX,LOG
        self.source = source
        self.constants = constants
        self.fabricDataInterface = FabricDataInterface()

        # We dont utilize the target values for the LOG scenario since the LOG Table is outside of Fabric
        if(self.type != "LOG"):
            self.targetStageName = targetStageName
            self.targetWorkspace = targetWorkspace
            self.targetLakehouse = targetLakehouse
            self.targetDestinationName = targetDestinationName
            self.targetFabricLakehouseLocation = FabricLakehouseLocation(self.targetStageName
                                                        , self.targetWorkspace, self.targetLakehouse)
            self.targetFabricTableLocation = FabricTableLocation(self.targetDestinationName
                                                                    , self.targetFabricLakehouseLocation)
            self.targetDF = self.spark.read.format('delta').load(self.targetFabricTableLocation.abfss_path()).select(*TEST_DATA_DF_COLUMNS)
        
        self.df = df # This is not used for the GX Validation test

        if(self.type == "RAW"):

            self.insertDF = DataTransformation.createDatasetDF(self.spark, EMPLOYEES_INSERT_DATASET_PATH)
            self.updateDF = DataTransformation.createDatasetDF(self.spark, EMPLOYEES_UPDATE_DATASET_PATH)
            self.deleteDF = DataTransformation.createDatasetDF(self.spark, EMPLOYEES_DELETE_DATASET_PATH)

        elif(self.type == "TRUSTED"):

            self.insertDF = DataTransformation.createDatasetDF(self.spark, EMPLOYEES_INSERT_DATASET_PATH)
            if(source["trusted_savetype"] == "cdc-transactions" 
                or source["trusted_savetype"] == "cdc-incremental"):
                    self.updateDF = DataTransformation.createDatasetDF(self.spark, EMPLOYEES_CDC_UPDATE_DATASET_PATH)
                    self.deleteDF = DataTransformation.createDatasetDF(self.spark, EMPLOYEES_CDC_DELETE_DATASET_PATH)
            else:
                    self.updateDF = DataTransformation.createDatasetDF(self.spark, EMPLOYEES_UPDATE_DATASET_PATH)
                    self.deleteDF = DataTransformation.createDatasetDF(self.spark, EMPLOYEES_DELETE_DATASET_PATH)

        elif (self.type == "GX"):
            self.validRowsDF = DataTransformation.createDatasetDF(self.spark, EMPLOYEES_GX_VALID_DATASET_PATH)
            self.inValidRowsDF = ""
            self.invalidRowsLakehouseLocation = FabricLakehouseLocation(self.targetStageName
                                                    , self.targetWorkspace, self.targetLakehouse)
            self.invalidRowsTableLocation = FabricTableLocation(f"{self.targetDestinationName}_invalid_rows"
                                                                , self.invalidRowsLakehouseLocation)

    def ingestionTest(self):

        tableExistanceTest = TestCase.tableExistanceTest(self.spark, self.targetFabricTableLocation)

        return {"Table Existance Test": tableExistanceTest}

    def rawIngestionTest(self):

        tableExistanceTest = TestCase.tableExistanceTest(self.spark, self.targetFabricTableLocation)
        rowCountTest = TestCase.rowCountTest(self.df, self.targetDF)
        columnCountTest = TestCase.columnCountTest(self.df, self.targetDF)

        # Insert 10 new rows test case
        insertRowCount = self.updateTargetTable(self.insertDF, "overwrite")
        insertRowExistanceTest = TestCase.rowExistanceTest(self.insertDF, self.targetDF)

        # Update 10 rows test case
        updateRowCount = self.updateTargetTable(self.updateDF, "overwrite")
        updateRowExistanceTest = TestCase.rowExistanceTest(self.updateDF, self.targetDF)

        # Delete 10 rows test case
        deleteRowCount = self.updateTargetTable(self.deleteDF, "overwrite")
        deleteRowExistanceTest = TestCase.rowExistanceTest(self.deleteDF, self.targetDF)

        # Rever back the RAW table to the original
        originalRowCount = self.updateTargetTable(self.df, "overwrite")

        return {
            "Table Existance Test": tableExistanceTest
            , "Row Count Test": rowCountTest
            , "Column Count Test": columnCountTest
            , "Inserted Rows Existance Test": insertRowExistanceTest
            , "Updated Rows Existance Test": updateRowExistanceTest
            , "Deleted Rows Existance Test": deleteRowExistanceTest
        }

    def trustedIngestionTest(self):

        tableExistanceTest = TestCase.tableExistanceTest(self.spark, self.targetFabricTableLocation)
        rowCountTest = TestCase.rowCountTest(self.df, self.targetDF)
        columnCountTest = TestCase.columnCountTest(self.df, self.targetDF)

        insertRowExistanceTest = None
        updateRowExistanceTest = None
        deleteRowExistanceTest = None

        if "overwrite" == self.source["trusted_savetype"].lower():

            # Insert 10 new rows test case
            insertRowCount = self.updateTargetTable(self.insertDF, "overwrite")
            insertRowExistanceTest = TestCase.rowExistanceTest(self.insertDF, self.targetDF)

            # Update 10 rows test case
            updateRowCount = self.updateTargetTable(self.updateDF, "overwrite")
            updateRowExistanceTest = TestCase.rowExistanceTest(self.updateDF, self.targetDF)

            # Delete 10 rows test case
            deleteRowCount = self.updateTargetTable(self.deleteDF, "overwrite")
            deleteRowExistanceTest = TestCase.rowExistanceTest(self.deleteDF, self.targetDF)

            # Rever back the TRUSTED table to the original
            originalRowCount = self.updateTargetTable(self.df, "overwrite")

        elif "incremental" == self.source["trusted_savetype"].lower():

            # Insert 10 new rows test case
            insertRowCount = self.updateTargetTable(self.insertDF, "incremental")
            insertRowExistanceTest = TestCase.rowExistanceTest(self.insertDF, self.targetDF)
            originalRowCount = self.updateTargetTable(self.df, "overwrite")

            # Update 10 rows test case
            updateRowCount = self.updateTargetTable(self.updateDF, "incremental")
            updateRowExistanceTest = TestCase.rowExistanceTest(self.updateDF, self.targetDF)
            originalRowCount = self.updateTargetTable(self.df, "overwrite")

            # Do we need to test Deletes for Incremental?

            # Rever back the TRUSTED table to the original
            originalRowCount = self.updateTargetTable(self.df, "overwrite")

        elif "merge" == self.source["trusted_savetype"].lower():

            # Insert 10 new rows test case
            insertRowCount = self.updateTargetTable(self.insertDF, "merge")
            insertRowExistanceTest = TestCase.rowExistanceTest(self.insertDF, self.targetDF)
            originalRowCount = self.updateTargetTable(self.df, "overwrite")

            # Update 10 rows test case
            updateRowCount = self.updateTargetTable(self.updateDF, "merge")
            updateRowExistanceTest = TestCase.rowExistanceTest(self.updateDF, self.targetDF)
            originalRowCount = self.updateTargetTable(self.df, "overwrite")

            # Rever back the TRUSTED table to the original
            originalRowCount = self.updateTargetTable(self.df, "overwrite")

        elif "delta" == self.source["trusted_savetype"].lower():

            # Insert 10 new rows test case
            insertRowCount = self.updateTargetTable(self.insertDF, "delta")
            insertRowExistanceTest = TestCase.rowExistanceTest(self.insertDF, self.targetDF)
            originalRowCount = self.updateTargetTable(self.df, "overwrite")

            # Update 10 rows test case
            updateRowCount = self.updateTargetTable(self.updateDF, "delta")
            updateRowExistanceTest = TestCase.rowExistanceTest(self.updateDF, self.targetDF)
            originalRowCount = self.updateTargetTable(self.df, "overwrite")

            # Delete 10 rows test case
            deleteRowCount = self.updateTargetTable(self.deleteDF, "delta")
            deleteRowExistanceTest = TestCase.rowExistanceTest(self.deleteDF, self.targetDF)

            # Rever back the TRUSTED table to the original
            originalRowCount = self.updateTargetTable(self.df, "overwrite")

        elif "cdc-overwrite" == self.source["trusted_savetype"].lower():

            # Insert 10 new rows test case
            insertRowCount = self.updateTargetTable(self.insertDF, "cdc-overwrite")
            insertRowExistanceTest = TestCase.rowExistanceTest(self.insertDF, self.targetDF)
            originalRowCount = self.updateTargetTable(self.df, "cdc-overwrite")

            # Update 10 rows test case
            updateRowCount = self.updateTargetTable(self.updateDF, "cdc-overwrite")
            updateRowExistanceTest = TestCase.rowExistanceTest(self.updateDF, self.targetDF)
            originalRowCount = self.updateTargetTable(self.df, "cdc-overwrite")

            # Delete 10 rows test case
            deleteRowCount = self.updateTargetTable(self.deleteDF, "cdc-overwrite")
            deleteRowExistanceTest = TestCase.rowExistanceTest(self.deleteDF, self.targetDF)

            # Rever back the TRUSTED table to the original
            originalRowCount = self.updateTargetTable(self.df, "cdc-overwrite")

        elif "cdc-transactions" == self.source["trusted_savetype"].lower():

            # Insert 10 new rows test case
            insertRowCount = self.updateTargetTable(self.insertDF, "cdc-transactions")
            insertRowExistanceTest = TestCase.rowExistanceTest(self.insertDF, self.targetDF)
            originalRowCount = self.updateTargetTable(self.df, "cdc-overwrite")

            # Update 10 rows test case
            # updateRowCount = self.updateTargetTable(self.updateDF, "cdc-transactions")
            # updateRowExistanceTest = TestCase.rowExistanceTest(self.updateDF, self.targetDF)
            # originalRowCount = self.updateTargetTable(self.df, "cdc-overwrite")

            # # Delete 10 rows test case
            # deleteRowCount = self.updateTargetTable(self.deleteDF, "cdc-transactions")
            # deleteRowExistanceTest = TestCase.rowExistanceTest(self.deleteDF, self.targetDF)

            # Rever back the TRUSTED table to the original
            # originalRowCount = self.updateTargetTable(self.df, "cdc-overwrite")

        elif "cdc-incremental" == self.source["trusted_savetype"].lower():

            # Insert 10 new rows test case
            insertRowCount = self.updateTargetTable(self.insertDF, "cdc-incremental")
            insertRowExistanceTest = TestCase.rowExistanceTest(self.insertDF, self.targetDF)
            originalRowCount = self.updateTargetTable(self.df, "cdc-overwrite")

            # Update 10 rows test case
            updateRowCount = self.updateTargetTable(self.updateDF, "cdc-incremental")
            updateRowExistanceTest = TestCase.rowExistanceTest(self.updateDF, self.targetDF)
            originalRowCount = self.updateTargetTable(self.df, "cdc-overwrite")

            # Delete 10 rows test case
            deleteRowCount = self.updateTargetTable(self.deleteDF, "cdc-incremental")
            deleteRowExistanceTest = TestCase.rowExistanceTest(self.deleteDF, self.targetDF)

            # Rever back the TRUSTED table to the original
            originalRowCount = self.updateTargetTable(self.df, "cdc-overwrite")

        return {
            "Table Existance Test": tableExistanceTest
            , "Row Count Test": rowCountTest
            , "Column Count Test": columnCountTest
            , "Inserted Rows Existance Test": insertRowExistanceTest
            , "Updated Rows Existance Test": updateRowExistanceTest
            , "Deleted Rows Existance Test": deleteRowExistanceTest
        }

    def gxIngestionTest(self):

        validationName = ""
        validationColumn = ""

        for validation in self.source["data_validation"]:

            validationColumn = validation["Column"] 

            if(validation["Validation_Type"] == IS_NULL):
                validationName = "Null Validation"
                self.inValidRowsDF = DataTransformation.createDatasetDF(self.spark, EMPLOYEES_GX_NULL_INVALID_DATASET_PATH)

            elif(validation["Validation_Type"] == IS_OUT_OF_RANGE):
                validationName = "In Range Validation"
                self.inValidRowsDF = DataTransformation.createDatasetDF(self.spark, EMPLOYEES_GX_INRANGE_INVALID_DATASET_PATH)

            elif(validation["Validation_Type"] == IS_NOT_MATCHING_REGEX):
                validationName = "Regex Validation"
                self.inValidRowsDF = DataTransformation.createDatasetDF(self.spark, EMPLOYEES_GX_REGEX_INVALID_DATASET_PATH)

            elif(validation["Validation_Type"] == IS_NOT_EXPECTED_DATA_TYPE 
                    and validation["Options"][0] == INTEGER_TYPE):
                validationName = "Integer Data Type Validation"
                self.inValidRowsDF = DataTransformation.createDatasetDF(self.spark, EMPLOYEES_GX_INTEGER_INVALID_DATASET_PATH)

            elif(validation["Validation_Type"] == IS_NOT_EXPECTED_DATA_TYPE
                    and validation["Options"][0] == DOUBLE_TYPE):
                validationName = "Double Data Type Validation"
                self.inValidRowsDF = DataTransformation.createDatasetDF(self.spark, EMPLOYEES_GX_DOUBLE_INVALID_DATASET_PATH)

            elif(validation["Validation_Type"] == IS_NOT_EXPECTED_DATA_TYPE
                 and validation["Options"][0] == BOOLEAN_TYPE):
                validationName = "Boolean Validation"
                self.inValidRowsDF = DataTransformation.createDatasetDF(self.spark, EMPLOYEES_GX_BOOLEAN_INVALID_DATASET_PATH)

        gxValidRowsExistanceTest = TestCase.rowExistanceTest(self.validRowsDF, self.targetDF)
        gxInvalidRowsTableExistanceTest = TestCase.tableExistanceTest(self.spark, self.invalidRowsTableLocation)
        targetInvalidRowsDF = self.spark.read.format('delta').load(self.invalidRowsTableLocation.abfss_path()).select(*TEST_DATA_DF_COLUMNS)
        gxInvalidRowsExistanceTest = TestCase.rowExistanceTest(self.inValidRowsDF, targetInvalidRowsDF)

        return {
            f"{validationName} Test on column {validationColumn}: Valid Rows Test": gxValidRowsExistanceTest
            , f"{validationName} Test on column {validationColumn}: Invalid Rows Table Existance Test": gxInvalidRowsTableExistanceTest
            , f"{validationName} Test on column {validationColumn}: Invalid Rows Existance Test": gxInvalidRowsExistanceTest
        }

    def logAnalyticsTest(self):

        tableExistanceTest = self.logTableExistanceTest()

        if(tableExistanceTest):
            logRowExistanceTest = self.logRowExistanceTest()
        else:
            logRowExistanceTest = False
        
        return {
            "Table Existance Test": tableExistanceTest
            , "Logged Row Existance Test": logRowExistanceTest
        }

    def updateTargetTable(self, df, savetype):

        df = (
            df
            .withColumn("employeeId", df["employeeId"].cast(IntegerType()))
            .withColumn("firstName", df["firstName"].cast(StringType()))
            .withColumn("surName", df["surName"].cast(StringType()))
            .withColumn("age", df["age"].cast(IntegerType()))
            .withColumn("dateOfBirth", df["dateOfBirth"].cast(DateType()))
            .withColumn("position", df["position"].cast(StringType()))
            .withColumn("salary", df["salary"].cast(DoubleType()))
            .withColumn("isSenior", df["isSenior"].cast(BooleanType()))
        )

        if ("cdc" not in savetype.lower()):
            targetCount = self.fabricDataInterface.saveDeltaTable(
                            sourceDataFrame=df,
                            fabricTableLocation=self.targetFabricTableLocation,
                            savetype=savetype,
                            primarykey=self.source["primary_key"]
                        )
        else:
            targetCount = self.fabricDataInterface.saveCDCTable(
                df=df,
                fabricTableLocation=self.targetFabricTableLocation,
                savetype=savetype,
                primarykey=self.source["primary_key"],
                rowhash_columns=self.source["rowhash_columns"],
                transactional_watermark_column = self.source["watermark"]
            )

        return targetCount

    def logTableExistanceTest(self):

        # Set Azure credentials as environment variables
        os.environ["AZURE_TENANT_ID"] = self.constants["LOGS_AZURE_TENANT_ID"]
        os.environ["AZURE_CLIENT_ID"] = self.constants["LOGS_AZURE_CLIENT_ID"]
        os.environ["AZURE_CLIENT_SECRET"] = self.constants["LOGS_AZURE_CLIENT_SECRET"]

        # Set workspace Id
        os.environ['LOG_WORKSPACE_ID'] = self.constants["LOGS_AZURE_ANALYTICS_WORKSPACE_ID"]

        credential  = DefaultAzureCredential()
        client = LogsQueryClient(credential)
        query = f"""{self.constants["LOGS_AZURE_ANALYTICS_WORKSPACE_TABLE"]}
                    | take 1"""

        try:
            response = client.query_workspace(workspace_id=os.environ['LOG_WORKSPACE_ID'], query=query, timespan=timedelta(days=1))
            
            if response.status == LogsQueryStatus.SUCCESS:
                return True
            else:
                print("Error:")
                error = response.partial_error
                print(error)
                return False
            
        except HttpResponseError as err:
            print("Error:")
            print(err)

            return False

    def logRowExistanceTest(self):

        # Set Azure credentials as environment variables
        os.environ["AZURE_TENANT_ID"] = self.constants["LOGS_AZURE_TENANT_ID"]
        os.environ["AZURE_CLIENT_ID"] = self.constants["LOGS_AZURE_CLIENT_ID"]
        os.environ["AZURE_CLIENT_SECRET"] = self.constants["LOGS_AZURE_CLIENT_SECRET"]

        # Set workspace Id
        os.environ['LOG_WORKSPACE_ID'] = self.constants["LOGS_AZURE_ANALYTICS_WORKSPACE_ID"]

        credential  = DefaultAzureCredential()
        client = LogsQueryClient(credential)
        targetLogDF = self.spark.createDataFrame([], StructType([]))

        query = f"""{self.constants["LOGS_AZURE_ANALYTICS_WORKSPACE_TABLE"]}
                    | where SourceID == {self.source["SourceID"]} and Status == "Processing"
                    | take 1"""

        try:
            response = client.query_workspace(workspace_id=os.environ['LOG_WORKSPACE_ID'], query=query, timespan=timedelta(days=1))
            if response.status == LogsQueryStatus.SUCCESS:
                data = response.tables
            else:
                # LogsQueryPartialResult
                error = response.partial_error
                data = response.partial_data
                print(error)
                return False

            for table in data:
                df = pd.DataFrame(data=table.rows, columns=table.columns)
                targetLogDF = self.spark.createDataFrame(df)
                if(targetLogDF.count()>0):
                    return True
                else:
                    return False
        except HttpResponseError as err:
            print("Throwing Error:")
            print(err)
            return False


class DataTransformation:

    """
    Represents the generic class for holding data transformation methods
    """

    @staticmethod
    def createDatasetDF(spark, filename):

        """
        This method is used to read the csv files on the ExpectedData sub package

        """

        file_path = str(importlib.resources.files("FabricFramework.ExpectedResults").joinpath(filename))
        pandasDF = pd.read_csv(str(file_path))
        sparkDF = spark.createDataFrame(pandasDF)
        return sparkDF

class TestCase:

    """
    Represents the generic Test Cases used within a TestModule
    """

    @staticmethod
    def tableExistanceTest(spark, targetFabricTableLocation):

        """
        Checks is a given target table exists or not

        Args:
            spark: the current spark context
            targetFabricTableLocation: FabricTableLocation object representing the target table
        """

        if(DeltaTable.isDeltaTable(spark, targetFabricTableLocation.abfss_path())):
            return True
        else:
            return False
    
    @staticmethod
    def rowCountTest(currentDF, targetDF):


        """
        Checks if the target table's row count is valid using the expected row count (aka currentDF row count)

        Args:
            currentDF: Dataframe representing the expected results
            targetDF: Dataframe representing the target table
        """

        if(currentDF.count() == targetDF.count()):
            return True
        else:
            return False
        
    @staticmethod
    def columnCountTest(currentDF, targetDF):

        """
        Checks if the target table's column count is valid using the expected row count (aka currentDF row count)

        Args:
            currentDF: Dataframe representing the expected results
            targetDF: Dataframe representing the target table
        """

        if(len(currentDF.columns) == len(targetDF.columns)):
            return True
        else:
            return False
        
    @staticmethod
    def rowExistanceTest(currentDF, targetDF):

        """
        Checks if the target table's row existance using the expected row count (aka currentDF row count)

        Args:
            currentDF: Dataframe representing the expected results
            targetDF: Dataframe representing the target table
        """

        if(currentDF.count() == targetDF.count()):

            return True
        else:
            return False
        










        

