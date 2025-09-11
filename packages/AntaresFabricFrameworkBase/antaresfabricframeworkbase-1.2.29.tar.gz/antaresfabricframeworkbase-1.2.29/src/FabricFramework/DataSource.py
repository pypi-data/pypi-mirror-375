from pyspark.sql import SparkSession

from FabricFramework.FabricLocations import *
from FabricFramework.FabricDataInterface import *
from FabricFramework.ApiDataSource import *

class DataSource(object):
    """Base class for data sources using Spark sessions."""

    def __init__(self):
        """Initialize Spark session with a default application name."""
        self.spark = SparkSession.builder.appName("Default").getOrCreate()
        self.fabricInterface = FabricDataInterface()

    @staticmethod
    def getDataSourceType(connection, source, function=None, constants=None):
        """Factory method to get the appropriate data source type based on the source type."""
        sourceType = source["source_type"].upper()

        if sourceType == 'SQL':
            return SQLDataSource(connection, source, function, constants)
        elif sourceType == 'BLOB-CSV':
            return BLOBCSVDataSource(connection, source, function, constants)
        elif sourceType == 'BLOB-PARQUET':
            return BLOBParquetDataSource(connection, source, function, constants)
        elif sourceType == 'FABRIC-TEXT':
            return FabricTextDataSource(connection, source, function, constants)
        elif sourceType == 'FABRIC-TABLE':
            return FabricTableDataSource(connection, source, function, constants)
        elif sourceType == 'REST-API':
            return RestAPIDataSource(connection, source, function, constants)

    def loadTable(self):
        """Placeholder method to be overridden in subclass."""
        pass

    def execute_function(self, function, *args, **kwargs):
        """Execute a function with the provided arguments and keyword arguments."""
        return function(*args, **kwargs)

class SQLDataSource(DataSource):
    """Data source for SQL databases."""

    def __init__(self, connection, source, function=None, constants=None):
        """Initialize SQL data source with connection details and table."""
        self.url = connection
        self.driver = "com.microsoft.sqlserver.jdbc.SQLServerDriver"  # JDBC driver for SQL Server
        self.source = source
        self.source_name = source["source_name"]
        self.preProcessingEnabled = source["preprocessing_enabled"]
        self.p_options = source["preprocessing_options"]
        self.function = function
        super().__init__()

    def loadTable(self):
        """Load table using JDBC with the specified connection properties."""
        connection_properties = {
            "driver": self.driver,
            "url": self.url
        }

        if self.preProcessingEnabled:
            self.execute_function(self.function, self.source)

        df = self.spark.read.jdbc(url=self.url, table=self.source_name, properties=connection_properties)
        return df

class BLOBCSVDataSource(DataSource):
    """Data source for loading CSV files from Azure Blob storage."""

    def __init__(self, connection, source, function=None, constants=None):
        """Initialize data source with connection details, table (blob path), header, and schema."""
        self.url = connection
        self.source_name = source["source_name"]
        self.preProcessingEnabled = source["preprocessing_enabled"]
        self.header = source["header"]
        self.schema = source["schema"]
        super().__init__()

    def loadTable(self):

        if self.preProcessingEnabled:
            return self.execute_function(self.function, self.source)
        else:
            """Load a CSV file from Azure Blob using Spark."""
            connection_tokens = self.url.split(';')
            storage_account_name = connection_tokens[1].split('=')[1]
            storage_account_access_key = connection_tokens[2].split('=', 1)[1]
            blob_container = connection_tokens[4].split('=')[1]

            self.spark.conf.set(f'fs.azure.account.key.{storage_account_name}.blob.core.windows.net',
                                storage_account_access_key)

            blob_relative_path = self.source_name
            blob_url = f"wasbs://{blob_container}@{storage_account_name}.blob.core.windows.net/{blob_relative_path}"
            df = self.spark.read.format("csv").option("header", self.header).load(blob_url)
            return df


class BLOBParquetDataSource(DataSource):
    """Data source for loading Parquet files from Azure Blob storage."""

    def __init__(self, connection, source, function=None, constants=None):
        """Initialize data source with connection details, table (blob path), header, and schema."""
        self.url = connection
        self.source_name = source["source_name"]
        self.header = source["header"]
        self.schema = source["schema"]
        super().__init__()

    def loadTable(self):
        """Load a Parquet file from Azure Blob using Spark."""
        connection_tokens = self.url.split(';')
        storage_account_name = connection_tokens[1].split('=')[1]
        storage_account_access_key = connection_tokens[2].split('=', 1)[1]
        blob_container = connection_tokens[4].split('=')[1]

        self.spark.conf.set(f'fs.azure.account.key.{storage_account_name}.blob.core.windows.net', storage_account_access_key)

        blob_relative_path = self.source_name
        blob_url = f"wasbs://{blob_container}@{storage_account_name}.blob.core.windows.net/{blob_relative_path}"
        if self.schema:
            df = self.spark.read.schema(self.schema).parquet(blob_url)
        else:
            df = self.spark.read.parquet(blob_url)
        return df

class FabricTextDataSource(DataSource):
    """Data source for loading text files from a Fabric container."""

    def __init__(self, connection, source, function=None, constants=None):
        """Initialize data source with connection details and file-specific options."""
        self.url = connection
        self.file = source["source_name"]
        self.header = source["header"]
        self.schema = source["schema"]
        self.destination = source["destination_name"]
        self.preProcessingEnabled = source["preprocessing_enabled"]
        self.p_options = source["preprocessing_options"]
        self.function = function
        self.source = source
        super().__init__()

    def loadTable(self):
        """Load a text file from Fabric using configured options and execute any preprocessing functions if specified."""
        if self.url:
            connection_tokens = self.url.split(';')
            workspace_id = connection_tokens[0]
            lakehouse_id = connection_tokens[1]

            # Create lakehouse location
            lakehouse_datasource = FabricLakehouseLocation("FabricTextSource", workspace_id, lakehouse_id)

            if self.preProcessingEnabled:
                return self.execute_function(self.function, self.source)
            else:
                print("Text source files must have preprocessing enabled and include pre processing options with at least header and delimiter details.")

        return None

class FabricTableDataSource(DataSource):
    def __init__(self, connection, source, function=None, constants=None):
        """Initialize data source with connection details and file-specific options."""
        self.url = connection
        self.file = source["source_name"]
        self.header = source["header"]
        self.schema = source["schema"]
        self.destination = source["destination_name"]
        self.preProcessingEnabled = source["preprocessing_enabled"]
        self.p_options = source["preprocessing_options"]
        self.function = function
        self.source = source
        super().__init__()

    def loadTable(self):
        """Load a text file from Fabric using configured options and execute any preprocessing functions if specified."""
        if self.url:
            connection_tokens = self.url.split(';')
            workspace_id = connection_tokens[0]
            lakehouse_id = connection_tokens[1]

            # Create lakehouse location
            lakehouse_datasource = FabricLakehouseLocation("FabricTableSource", workspace_id, lakehouse_id)

            if self.preProcessingEnabled:
                return self.execute_function(self.function, self.source)
            else:
                # create the table location
                tableLocation = FabricTableLocation(self.source['source_name'], lakehouse_datasource)
                # return the dataframe as is (without preprocessing)
                return self.fabricInterface.loadLatestDeltaTable(tableLocation)

