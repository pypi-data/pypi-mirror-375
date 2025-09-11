from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, concat_ws, sha2, expr
from delta.tables import *
from datetime import *
import pytz

from FabricFramework.FabricLocations import *


class FabricDataInterface:
    """
    Class representing the interface for data operations in the Fabric framework.
    """

    def __init__(self, name="default"):
        """
        Initialize a FabricDataInterface object.

        :param name: Name of the data interface.
        """
        self.name = name
        self.spark = SparkSession.builder.appName("Default_Config").getOrCreate()

    def saveCDCWrapper(self, sourceDataFrame, fabricTableLocation, savetype='cdc-overwrite', primarykey=[],
                       rowhash_columns=[], transactional_watermark_column=None):
        """
        Wrapper method for saving CDC data with support for multiple date partitions.

        :param sourceDataFrame: Source DataFrame to be saved.
        :param fabricTableLocation: FabricTableLocation object representing the target location.
        :param savetype: Save type (e.g., 'overwrite', 'transactions', 'incremental').
        :param primarykey: List of primary key columns.
        :param rowhash_columns: List of columns for row hash.
        :param transactional_watermark_column: Column used for transactional watermark.
        :return: Total record count of the saved data.
        """
        targetRecordCount = 0

        if not sourceDataFrame:
            print("Error occurred during the Fabric CDC save operation: Source Data is empty or does not exist.")
            return targetRecordCount

        if not primarykey and not rowhash_columns:
            print("No Primary Key or Row hash columns have been supplied. Cannot save CDC table.")
            return targetRecordCount

        print(f'CDC {savetype} type save in progress to location {fabricTableLocation.abfss_path()}')

        # Split source data based on distinct 'source_extract_dtm' values if it exists
        list_of_dfs = [sourceDataFrame]
        if "source_extract_dtm" in sourceDataFrame.columns:
            list_of_dfs = []
            source_extract_dtm_distinct = sourceDataFrame.select("source_extract_dtm").distinct().orderBy(
                'source_extract_dtm')
            distinct_value_list = [row["source_extract_dtm"] for row in source_extract_dtm_distinct.collect()]

            for source_extract_dtm in distinct_value_list:
                filtered_df = sourceDataFrame.filter(sourceDataFrame['source_extract_dtm'] == source_extract_dtm)
                list_of_dfs.append(filtered_df)

        for df in list_of_dfs:
            targetRecordCount += self.saveCDCTable(df, fabricTableLocation, savetype, primarykey, rowhash_columns,
                                                   transactional_watermark_column)

        return targetRecordCount

    def saveCDCTable(self, df, fabricTableLocation, savetype='cdc-overwrite', primarykey=[], rowhash_columns=[],
                     transactional_watermark_column=None):
        """
        Save CDC data to a Delta table.

        :param df: DataFrame to be saved.
        :param fabricTableLocation: FabricTableLocation object representing the target location.
        :param savetype: Save type (e.g., 'overwrite', 'transactions', 'incremental').
        :param primarykey: List of primary key columns.
        :param rowhash_columns: List of columns for row hash.
        :param transactional_watermark_column: Column used for transactional watermark.
        :return: Record count of the saved data.
        """
        table_path = fabricTableLocation.abfss_path()

        # Get current datetime and calculate a deducted datetime for record end date
        australiaSydneyTimezone = pytz.timezone("Australia/Sydney")
        current_datetime = datetime.now(australiaSydneyTimezone)
        deducted_datetime = current_datetime - timedelta(seconds=2)
        current_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        deducted_datetime = deducted_datetime.strftime("%Y-%m-%d %H:%M:%S")
        highest_datetime = "9999-12-31 00:00:00"

        # Select columns for row hash if not provided
        if not rowhash_columns:
            selected_columns = [col for col in df.columns if col not in primarykey]
        else:
            selected_columns = [col for col in df.columns if col in rowhash_columns and col not in primarykey]

        # Add necessary columns for CDC operations
        df = df.withColumn('key_hash', sha2(concat_ws("_", *primarykey), 256))
        df = df.withColumn('row_hash', sha2(concat_ws("_", *selected_columns), 256))
        df = df.withColumn('Record_Start_Date', expr(f"CAST('{current_datetime}' AS TIMESTAMP)"))
        df = df.withColumn('Record_End_Date', expr(f"CAST('{highest_datetime}' AS TIMESTAMP)"))
        df = df.withColumn('Is_Current', lit(1))
        df = df.withColumn('Is_Deleted', lit(0))
        df = df.withColumn('Last_CDC_Ops', lit("INSERT"))

        # Handle different save types
        if not DeltaTable.isDeltaTable(self.spark, table_path) or savetype == 'cdc-overwrite':
            df.write.mode("overwrite").option("overWriteSchema", "true").format("delta").save(table_path)
            print(f'CDC {savetype} type save to {fabricTableLocation.abfss_path()} complete.')
            return df.count()

        elif savetype == 'cdc-transactions':
            target_df = self.loadLatestDeltaTable(fabricTableLocation)
            print(f'Target Dataframe loaded. It has {target_df.count()} records.')

            watermark_column = df.select(transactional_watermark_column).first()[0]
            source_records_count = target_df.filter(col(transactional_watermark_column) == watermark_column).count()

            print(f'Source data contains {source_records_count} records')

            if source_records_count == 0:
                df.write.mode("append").format("delta").save(table_path)

            print(f'Source has been appended to target. Target now contains {df.count()} records.')

            return df.count()

        elif savetype == 'cdc-incremental':
            target_df = self.loadLatestDeltaTable(fabricTableLocation)
            print(f'Target Dataframe loaded. It has {target_df.count()} records.')

            # Filter the target data for is_current = 1 and is_deleted = 0
            filtered_target_df = target_df.filter((target_df.Is_Current == 1) & (target_df.Is_Deleted == 0))
            newRecords = df.alias("s") \
                .join(filtered_target_df.alias("t"), on=["key_hash"], how="leftanti") \
                .select("s.*")

            print(f'There are {newRecords.count()} new records in the source data.')

            updateRecords = df.alias("s") \
                .join(filtered_target_df.alias("t"), on=["key_hash"], how="inner").where(
                f"t.Is_Current = 1 AND t.Is_Deleted = 0 AND t.row_hash != s.row_hash") \
                .select("s.*")

            print(f'There are {updateRecords.count()} matched (on primary key) records between the target and source data.')

            updateRecords = updateRecords.withColumn("Last_CDC_Ops", lit("UPDATE"))
            updateRecords = updateRecords.withColumn("Record_End_Date",
                                                     expr(f"CAST('{highest_datetime}' AS TIMESTAMP)"))

            mergeRecords = newRecords.union(updateRecords)

            if not mergeRecords.isEmpty():
                print("Merging Source to Target...")

                insertValues = {"key_hash": "s.key_hash", "row_hash": "s.row_hash",
                                "Record_Start_Date": "s.Record_Start_Date", "Record_End_Date": "s.Record_End_Date",
                                "Is_Current": "s.Is_Current", "Is_Deleted": "s.Is_Deleted",
                                "Last_CDC_Ops": "s.Last_CDC_Ops"}

                for c in [i for i in target_df.columns]:
                    insertValues[f"{c}"] = f"s.{c}"

                try:
                    print("Updating Values in Target...")
                    DeltaTable.forPath(self.spark, table_path).alias("t") \
                        .merge(mergeRecords.alias("s"), f"t.key_hash = s.key_hash") \
                        .whenMatchedUpdate(
                        condition=f"t.Is_Current=1 AND t.Is_Deleted = 0 AND t.row_hash != s.row_hash",
                        set={"t.Record_End_Date": expr(f"CAST('{deducted_datetime}' AS TIMESTAMP)"),
                             "t.Is_Current": "0", "t.key_hash": "NULL"}).execute()

                    print("Inserting new values to Target...")
                    DeltaTable.forPath(self.spark, table_path).alias("t") \
                        .merge(mergeRecords.alias("s"), f"t.key_hash = s.key_hash") \
                        .whenNotMatchedInsert(values=insertValues).execute()

                except Exception as e:
                    print(
                        f'Incremental merge operation failed due to Exception Type: {type(e).__name__}, Args: {e.args}')
                    print(e.java_exception)
                else:
                    updated_df = self.loadLatestDeltaTable(fabricTableLocation)
                    print(f'Incremental merge complete. The updated table now contains {updated_df.count()}')
                    return updated_df.count()
            else:
                print("No new or updated records were found in the source data.")
                return 0

        return 0

    def saveDeltaTable(self, sourceDataFrame, fabricTableLocation, savetype='overwrite', primarykey=[]):
        """
        Save data to a Delta table.

        :param sourceDataFrame: Source DataFrame to be saved.
        :param fabricTableLocation: FabricTableLocation object representing the target location.
        :param savetype: Save type (e.g., 'overwrite', 'incremental', 'merge', 'delta').
        :param primarykey: List of primary key columns.
        :return: Record count of the saved data.
        """
        if not sourceDataFrame:
            print("Error occurred during the Fabric Delta Table save operation: Source Data is empty or does not exist.")
            return

        targetRecordCount = 0

        # Check if the target table exists and set the save type accordingly
        if not DeltaTable.isDeltaTable(self.spark, fabricTableLocation.abfss_path()):
            savetype = 'overwrite'
        else:
            # Create the join conditions based on the primary key columns
            if primarykey:
                joinCondition = " AND ".join([f"target.{key} = source.{key}" for key in primarykey])
            else:
                joinCondition = " AND ".join([f"target.{col} = source.{col}" for col in sourceDataFrame.columns])

            target_table = DeltaTable.forPath(self.spark, fabricTableLocation.abfss_path())

        if savetype == 'overwrite':
            print(f'Overwrite Save of table: {fabricTableLocation.abfss_path()}')
            sourceDataFrame.write.mode("overwrite").option("overWriteSchema", "true").format("delta").save(fabricTableLocation.abfss_path())
            targetRecordCount = sourceDataFrame.count()

        elif savetype == 'incremental':
            print(f'Incremental data save to target: {fabricTableLocation.abfss_path()}')
            target_table.alias("target").merge(sourceDataFrame.alias("source"),
                                               joinCondition).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()
            targetRecordCount = target_table.toDF().count()

        elif savetype == 'merge':
            print(f'Merge data save to target: {fabricTableLocation.abfss_path()}')
            df = sourceDataFrame.withColumn("IsCurrent", lit(True))
            update_set = {"target.IsCurrent": lit(False)}

            target_table.alias("target").merge(df.alias("source"), joinCondition).whenMatchedUpdate(set=update_set).execute()

            matched_rows = df.join(target_table.toDF(), [df[key] == target_table.toDF()[key] for key in primarykey], "left_semi")

            target_table.alias("target").merge(matched_rows.alias("matched"), "false").whenNotMatchedInsertAll().execute()

            targetRecordCount = target_table.toDF().count()

        elif savetype == 'delta':
            print(f'Delta save to target: {fabricTableLocation.abfss_path()}')
            target_table.alias("target").merge(sourceDataFrame.alias("source"),
                                               joinCondition).whenMatchedUpdateAll().whenNotMatchedInsertAll().whenNotMatchedBySourceDelete().execute()
            targetRecordCount = target_table.toDF().count()

        return targetRecordCount

    def loadDeltaLakeTable(self, sourceID, ingestionConfigurationLocation, stage='RAW', filter=None):
        """
        Load a Delta Lake table based on source ID and configuration location.

        :param sourceID: Source ID for the table.
        :param ingestionConfigurationLocation: FabricTableLocation object for the ingestion configuration.
        :param stage: Stage of the lakehouse (e.g., 'RAW', 'TRUSTED').
        :return: DataFrame of the loaded Delta Lake table.
        """
        ingestion_manifest_df = self.loadLatestDeltaTable(ingestionConfigurationLocation)
        source = ingestion_manifest_df.filter(col("SourceID") == sourceID)

        if stage == "TRUSTED":
            workspace_id = source.first()['trusted_workspace_id']
            lakehouse_id = source.first()['trusted_lakehouse_id']
            table_name = source.first()['destination_name']
        else:  # defaults to RAW
            workspace_id = source.first()['raw_workspace_id']
            lakehouse_id = source.first()['raw_lakehouse_id']
            table_name = source.first()['destination_name']

        table_location = FabricTableLocation(table_name, FabricLakehouseLocation(stage, workspace_id, lakehouse_id), filter)

        return self.loadLatestDeltaTable(table_location)

    def loadLatestDeltaTable(self, fabricTableLocation, filter=None):
        """
        Load the latest version of a Delta table.

        :param fabricTableLocation: FabricTableLocation object representing the table location.
        :return: DataFrame of the latest version of the Delta table, or None if the table does not exist.
        """
        table_path = fabricTableLocation.abfss_path()

        if DeltaTable.isDeltaTable(self.spark, table_path):
            latest_version = DeltaTable.forPath(self.spark, table_path).history().select("version").orderBy("version", ascending=False).first()[0]
            if filter:
                latest_data = self.spark.read.format("delta").option("versionAsOf", latest_version).load(table_path).filter(filter)
            else:
                latest_data = self.spark.read.format("delta").option("versionAsOf", latest_version).load(table_path)
            return latest_data

        print(f'Could not load Delta table. Location {table_path} does not exist.')
        return None

    def loadIngestionConfiguration(self, fabricFileLocation, fabricTableLocation):
        """
        Load the ingestion configuration from a Delta table or a JSON file.

        :param fabricFileLocation: FabricFileLocation object for the configuration file.
        :param fabricTableLocation: FabricTableLocation object for the configuration table.
        :return: DataFrame of the ingestion configuration.
        """
        ingestion_manifest = self.loadLatestDeltaTable(fabricTableLocation)

        if ingestion_manifest:
            return ingestion_manifest
        else:
            print("Ingestion Configuration Table does not exist, creating from file...")
            ingestion_manifest = self.spark.read.option("multiline", "true").json(fabricFileLocation.abfss_path())
            self.saveDeltaTable(ingestion_manifest, fabricTableLocation)

        return ingestion_manifest

