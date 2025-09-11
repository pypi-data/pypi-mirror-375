# libraries
from pyspark.sql import SparkSession, Row
from pyspark.sql.connect.functions import concat_ws
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType, BooleanType, ArrayType
from pyspark.sql.functions import lit, when, col, current_timestamp, monotonically_increasing_id, from_json, explode
import pyspark.sql.functions as F
import json
import re
import great_expectations as gx
from great_expectations.checkpoint import Checkpoint
from delta.tables import *
import time
import copy

from concurrent.futures import ThreadPoolExecutor
from multiprocessing.pool import ThreadPool

from FabricFramework.FabricDataInterface import *
from FabricFramework.FabricLocations import *

""" Constants that would be utilized within the Great Expectation Implementation """

# Below constants represent the types of validation
IS_NULL = "expect_column_values_to_not_be_null"
IS_OUT_OF_RANGE = "expect_column_values_to_be_between" # The first value is the minimum, whilst the second is the maximum
IS_NOT_MATCHING_REGEX = "expect_column_values_to_match_regex"
IS_NOT_EXPECTED_DATA_TYPE = "expect_column_values_to_be_of_data_type"

# Below constants represent the Data Type validations
INTEGER_TYPE = "Integer"
DOUBLE_TYPE = "Double"
BOOLEAN_TYPE = "Boolean"


class Expectation:
    """ The Expectation class represent the information provided for by the user for a validation that needs to be applied to a column. """

    def __init__(self, name, column, _pass, options=[]):
        self.name = name
        self.column = column
        self._pass = _pass
        self.options = options if name != IS_NOT_EXPECTED_DATA_TYPE else self.generateDataTypeValidationRegex(options)

    def generateDataTypeValidationRegex(self, options):
        """ When it comes to a Data Type validation, this method is used to create a Regex to validate if the values match the provided Data Type for the validation. """
        if (options[0] == INTEGER_TYPE):
            options.append("^\\s*-?[0-9]+\\s*$")
        elif (options[0] == DOUBLE_TYPE):
            options.append("^\s*-?[0-9]+(\.[0-9]+)?\s*$")
        elif (options[0] == BOOLEAN_TYPE):
            options.append("^(0|1|true|false|True|False|TRUE|FALSE)$")
        return options


class GreatExpectationsValidation:

    def __init__(self, df, targetTableLocation, list_validation, sk=None, datasource_name="my_datasource_name",
                 data_asset_name="my_data_asset_name", expectation_suite_name="my_expectation_suite_name",
                 checkpoint_name="my_checkpoint"):

        self.spark = SparkSession.builder.appName("Default_Config").getOrCreate()
        self.df = df
        # self.sk = sk if sk is not None else self.generateIndexColumn() # if this is null -> Generate a Index column to the df
        self.source_table_name = targetTableLocation.getTableName()
        self.targetTableLocation = targetTableLocation
        self.list_validation = list_validation
        self.datasource_name = datasource_name
        self.data_asset_name = data_asset_name
        self.expectation_suite_name = expectation_suite_name
        self.checkpoint_name = checkpoint_name
        self.context = gx.get_context()
        self.fabricInterface = FabricDataInterface()

        self.checkpoint_result = None
        self.invalid_row_information_df = None

        self.df = self.df.withColumn("is_valid", lit(True))
        self.df = self.df.withColumn("pass", lit(True))

        if sk is None or (isinstance(sk, list) and len(sk) == 0):
            self.sk = self.generateIndexColumn()
        elif isinstance(sk, list) and len(sk) == 1:
            self.sk = sk[0]
        elif isinstance(sk, list):
            self.sk = self.generateCompositeKeyColumn(sk)
        else:
            self.sk = sk

    def generateIndexColumn(self):
        """ This method is used to add an Index/SK column if the dataset doesnt have a SK column """
        self.df = self.df.withColumn("Index_SK", monotonically_increasing_id() + 1)
        return "Index_SK"

    def generateCompositeKeyColumn(self, column_list):
        # Check if all columns in column_list exist in the DataFrame
        existing_columns = [col for col in column_list if col in self.df.columns]

        # Merge values of existing columns into a new column 'Index_SK'
        self.df = self.df.withColumn('Index_SK', concat_ws('_', *existing_columns))
        return "Index_SK"

    def validateData(self):
        """ This method utilizes the infromation initialized wthin the _init_ and helps to validate the data whilst returning the result in a Dictionary format  """
        datasource = self.context.sources.add_spark(self.datasource_name)
        data_asset = datasource.add_dataframe_asset(name=self.data_asset_name)
        my_batch_request = data_asset.build_batch_request(dataframe=self.df)

        # Creates an Expecation suite, which is a collection of verifiable assertions about data
        self.context.add_or_update_expectation_suite(self.expectation_suite_name)
        validator = self.context.get_validator(batch_request=my_batch_request,
                                               expectation_suite_name=self.expectation_suite_name)
        validator = self.setExpectations(validator)
        validator.save_expectation_suite(discard_failed_expectations=False)

        # Creates a Checkpoint, which is the primary means for validating data in a production deployment of Great Expectations
        checkpoint = Checkpoint(
            name=self.checkpoint_name,
            run_name_template="%Y%m%d-%H%M%S-my-run-name-template",
            data_context=self.context,
            batch_request=my_batch_request,
            expectation_suite_name=self.expectation_suite_name,
            action_list=[
                {
                    "name": "store_validation_result",
                    "action": {"class_name": "StoreValidationResultAction"},
                },
                {
                    "name": "store_evaluation_params",
                    "action": {"class_name": "StoreEvaluationParametersAction"},
                },
                {"name": "update_data_docs", "action": {"class_name": "UpdateDataDocsAction"}},
            ],
            runtime_configuration={
                "result_format": {
                    "result_format": "COMPLETE",
                    "unexpected_index_column_names": [self.sk],
                    "return_unexpected_index_query": True,
                    "include_unexpected_rows": False
                },
            },
        )
        self.context.add_or_update_checkpoint(checkpoint=checkpoint)

        self.checkpoint_result = checkpoint.run()

        self._generateInvalidRowInformationTable()

        self._generateValidAndInvalidRowTables()

        return self.checkpoint_result

    def buildDocs(self):
        """ The method helps to build and save your validation result informaiton as a Data Doc """
        self.context.build_data_docs()
        self.context.open_data_docs()

    def setExpectations(self, validator):
        """ The method helps to set each type of validation to the validator (Expecation Suite) by assessing the user provided validation type """
        for validation in self.list_validation:
            if validation.name == IS_NULL:
                validator.expect_column_values_to_not_be_null(
                    column=validation.column
                    , meta={
                        "key": validation.column + "_" + validation.name
                        , "pass": validation._pass
                        , "display_name": "Null Validation: " + validation.column
                    }
                )
            elif validation.name == IS_OUT_OF_RANGE:
                validator.expect_column_values_to_be_between(
                    column=validation.column
                    , min_value=validation.options[0]
                    , max_value=validation.options[1]
                    , meta={
                        "key": validation.column + "_" + validation.name
                        , "pass": validation._pass
                        , "display_name": "Range Validation: " + validation.column
                    }
                )
            elif validation.name == IS_NOT_MATCHING_REGEX:
                validator.expect_column_values_to_match_regex(
                    column=validation.column
                    , regex=validation.options[0]
                    , meta={
                        "key": validation.column + "_" + validation.name + "_" + str(validation.options[0])
                        , "pass": validation._pass
                        , "display_name": "Regex Validation: " + validation.column
                    }
                )
            elif validation.name == IS_NOT_EXPECTED_DATA_TYPE:
                validator.expect_column_values_to_match_regex(
                    column=validation.column
                    , regex=validation.options[1]
                    , meta={
                        "key": validation.column + "_" + validation.name + "_" + validation.options[0]
                        , "pass": validation._pass
                        , "display_name": validation.options[0] + " Validation: " + validation.column
                    }
                )
        return validator

    # Method is used to create the Invalid Row Information table - stores the SK, validation type, and the column of which the validation was applied.
    def _generateInvalidRowInformationTable(self):
        """ The method reads the Validation Result (Checkpoint Result) and creates/overwrites the Invalid Row Information Table """
        pattern = r'^ValidationResultIdentifier'
        validationResultIdentifierProperty = next(
            (key for key in self.checkpoint_result["run_results"] if re.search(pattern, str(key))), None)

        if (
        not self.checkpoint_result["run_results"][validationResultIdentifierProperty]["validation_result"]["success"]):

            schema = StructType([
                StructField(self.sk, StringType(), True),
                StructField("column_name", StringType(), True),
                StructField("validation_type", StringType(), True),
                StructField("display_name", StringType(), True),
                StructField("timestamp", TimestampType(), True),
                StructField("pass", BooleanType(), True)
            ])
            self.invalid_row_information_df = self.spark.createDataFrame([], schema=schema)

            for result in \
            self.checkpoint_result["run_results"][validationResultIdentifierProperty]["validation_result"]["results"]:

                if (not result["success"]):
                    filtered_invalid_rows = self.spark.createDataFrame([], schema=schema)
                    queried_rows = eval(self.formatQueryString(("self." + result["result"]["unexpected_index_query"]),
                                                               result["expectation_config"]["expectation_type"]))
                    filtered_invalid_rows = queried_rows.select(col(self.sk).cast("int"))
                    filtered_invalid_rows = filtered_invalid_rows.withColumn("column_name", lit(
                        result["expectation_config"]["kwargs"]["column"]))
                    filtered_invalid_rows = filtered_invalid_rows.withColumn("validation_type", lit(
                        result["expectation_config"]["meta"]["key"]))
                    filtered_invalid_rows = filtered_invalid_rows.withColumn("display_name", lit(
                        result["expectation_config"]["meta"]["display_name"]))
                    filtered_invalid_rows = filtered_invalid_rows.withColumn("timestamp", lit(current_timestamp()))

                    # Update the is_valid column
                    invalid_sks = [int(row[self.sk]) for row in filtered_invalid_rows.collect()]
                    self.df = self.df.withColumn("is_valid",
                                                 when(col(self.sk).cast("int").isin(invalid_sks), False).otherwise(
                                                     col("is_valid")))  # set is_valid values to the main df

                    # Update the pass column: If the _pass value is False AND the validation is False -> Set Pass to False
                    if (not result["expectation_config"]["meta"]["pass"]):
                        filtered_invalid_rows = filtered_invalid_rows.withColumn("pass", lit(False))
                        self.df = self.df.withColumn("pass", when(col(self.sk).cast("int").isin(invalid_sks),
                                                                  lit(False)).otherwise(
                            col("pass")))  # set pass values to the main df
                    else:
                        filtered_invalid_rows = filtered_invalid_rows.withColumn("pass", lit(True))

                    # Union the filtered invalid rows to the dataframe storing all the invalid rows
                    self.invalid_row_information_df = self.invalid_row_information_df.union(filtered_invalid_rows)

            # save the invalid row information table
            clonedTable = self.targetTableLocation
            clonedTable.changeTableName(f'{clonedTable.getTableName()}_invalid_row_information')
            self.fabricInterface.saveDeltaTable(self.invalid_row_information_df, clonedTable)

            # Creates/Overwrites the Invalid row information table
            # loadToTrusted(self.invalid_row_information_df, 0, f"abfss://{trusted_workspace_id}@onelake.dfs.fabric.microsoft.com/{self.trusted_lakehouse_id}/Tables/{self.source_table_name}_invalid_row_information")

    # Method is used to generate the Fabric table of both valid and invalid rows of the df.
    def _generateValidAndInvalidRowTables(self):
        """ The method reads through the updated df and filters out the df to Invalid and Valid data, which then helps to create the Invalid and Valid Tables """
        # Drop the 'validtion_type' and the 'column_name' columns
        self.df = self.df.drop('validation_type', 'column_name')

        # Create source_table_meta_information Fabric table
        schema = StructType([
            StructField("source_table", StringType(), True),
            StructField("row_count", IntegerType(), True)
        ])
        meta_info_df = self.spark.createDataFrame([(self.source_table_name, self.df.count())], schema=schema)

        # Filter the valid rows, proceed with data type conversion and finally create/overwrite the Valid rows table
        valid_rows_df = self.df.where(
            (col("is_valid") == True) | ((col("is_valid") == False) & (col("pass") == True))).drop('is_valid')

        # valid_rows_df = self.convertToDataType(valid_rows_df)

        clonedTable = self.targetTableLocation
        clonedTable.changeTableName(f'{clonedTable.getTableName()}')
        self.fabricInterface.saveDeltaTable(valid_rows_df, clonedTable)

        # Filter the invalid rows and create/overwrite the Invalid rows table
        invalid_rows_df = self.df.where(col("is_valid") == False).drop('is_valid')

        clonedTable = self.targetTableLocation
        clonedTable.changeTableName(f'{clonedTable.getTableName()}_invalid_rows')
        self.fabricInterface.saveDeltaTable(invalid_rows_df, clonedTable)

        clonedTable = self.targetTableLocation
        clonedTable.changeTableName(f'{clonedTable.getTableName()}_meta_info')
        self.fabricInterface.saveDeltaTable(meta_info_df, clonedTable)

    def formatQueryString(self, query_string, expectation_name):
        """ The method helps to wrap the Expression of the query string in double quotes"""
        query_string = (query_string[:22] + "\"" + query_string[22:-2] + "\"" + query_string[-2:])
        if (expectation_name == "expect_column_values_to_match_regex"):
            query_string = self.wrapSingleQuotes(query_string)
        return query_string

    def wrapSingleQuotes(self, query_string):
        """ The method helps to wrap the Regex expression of the query string in single quotes"""
        rlike_section = query_string.split('RLIKE(')[1]
        remove_ending_brackets = rlike_section[:-5]
        final_string = query_string.split('RLIKE(')[0] + "RLIKE(" + remove_ending_brackets.split(', ', 2)[
            0] + "," + "\'" + remove_ending_brackets.split(', ', 2)[1] + "\'" + rlike_section[-5:]
        return final_string

    def convertToDataType(self, valid_rows_df):
        """ The method helps to convert the successfuly validated columns to their respective valid data type for Trusted Loading """
        for column, data_type in self.trusted_metadata:
            if data_type == "string":
                valid_rows_df = valid_rows_df.withColumn(column, col(column).cast("string"))
            elif data_type == "int":
                valid_rows_df = valid_rows_df.withColumn(column, col(column).cast("int"))
            elif data_type == "double":
                valid_rows_df = valid_rows_df.withColumn(column, col(column).cast("double"))
            elif data_type == "boolean":
                valid_rows_df = valid_rows_df.withColumn(column, col(column).cast("boolean"))
        return valid_rows_df