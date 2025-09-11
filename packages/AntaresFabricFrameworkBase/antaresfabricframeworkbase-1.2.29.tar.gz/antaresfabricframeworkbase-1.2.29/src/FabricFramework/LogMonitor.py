import os
from azure.identity import DefaultAzureCredential
from azure.monitor.ingestion import LogsIngestionClient
from azure.core.exceptions import HttpResponseError
from datetime import datetime
import threading


class Log:
    """
    Class representing a log entry with a stream name and log information.
    """
    def __init__(self, stream_name, log_info):
        """
        Initialize a Log object.

        :param stream_name: Name of the log stream.
        :param log_info: Dictionary containing log information.
        """
        self._stream_name = stream_name
        self._log_info = log_info

    @property
    def log_info(self):
        return self._log_info

    @property
    def stream_name(self):
        return self._stream_name


class LogAssembler:
    """
    Class for assembling log entries with given parameters.
    """

    def __init__(self, stream_name, constants, source, status, layer):
        """
        Initialize a LogAssembler object.

        :param stream_name: Name of the log stream.
        :param constants: Dictionary containing constant values for the log.
        :param source: Dictionary containing source information.
        :param status: Status of the log entry.
        :param layer: Layer information for the log entry.
        """
        self.stream_name = stream_name
        self.constants = constants
        self.source = source
        self.entity_log = {
            "LogRunID": self.constants['LOGRUN_ID'],
            "UserName": self.constants['USERNAME'],
            "Group": source["system_code"],
            "SourceID": source["SourceID"],
            "Entity": source["source_name"],
            "Layer": layer,
            "Source": source["source_type"],
            "Target": source["destination_name"],
            "StartDateTime": self.constants['EXECUTION_STARTDATETIME'],
            "EndDateTime": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "LogDateTime": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "LogType": self.constants['LOGGING_LEVEL'],
            "Status": status,
            "SourceRows": "",
            "TargetRows": "",
            "Error": "",
            "ValidationRules": "",
            "Parameters": source["preprocessing_options"]
        }

    def createLog(self):
        return Log(self.stream_name, self.entity_log)


class Logger:
    """
    Singleton class for managing and uploading logs to Azure.
    """
    _instance = None

    @classmethod
    def getInstance(cls, *args, **kwargs):
        """
        Get the singleton instance of Logger.

        :param args: Positional arguments.
        :param kwargs: Keyword arguments.
        :return: Singleton instance of Logger.
        """
        if not cls._instance:
            cls._instance = cls(*args, **kwargs)
        return cls._instance

    def __init__(self, az_tenant_id, az_client_id, az_client_secret, dce_endpoint, dcr_immutableid, buffer=1000):
        """
        Initialize the Logger object with Azure credentials and configuration.

        :param az_tenant_id: Azure tenant ID.
        :param az_client_id: Azure client ID.
        :param az_client_secret: Azure client secret.
        :param dce_endpoint: Data Collection Endpoint URL.
        :param dcr_immutableid: Data Collection Rule immutable ID.
        :param buffer: Buffer size for log batching.
        """
        if not hasattr(self, 'initialised'):  # This checks if the __init__ has been called before
            self.initialised = True
            self.logs = []
            self.az_tenant_id = az_tenant_id
            self.az_client_id = az_client_id
            self.az_client_secret = az_client_secret
            self.dce_endpoint = dce_endpoint
            self.dcr_immutableid = dcr_immutableid
            self.buffer = buffer

            # Set Azure credentials as environment variables
            os.environ["AZURE_TENANT_ID"] = self.az_tenant_id
            os.environ["AZURE_CLIENT_ID"] = self.az_client_id
            os.environ["AZURE_CLIENT_SECRET"] = self.az_client_secret

    def appendLogs(self, log_entry):
        self.logs.append(log_entry)

    def saveLogs(self, log_batch, stream_name):
        """
        Save a batch of logs to Azure Monitor.

        :param log_batch: List of log entries.
        :param stream_name: Name of the log stream.
        """
        credential = DefaultAzureCredential()
        client = LogsIngestionClient(endpoint=self.dce_endpoint, credential=credential, logging_enable=True)

        try:
            client.upload(rule_id=self.dcr_immutableid, stream_name=stream_name, logs=log_batch)
        except HttpResponseError as e:
            print(f"Log upload failed: {e}")

    def queueLog(self, log):
        """
        Queue a log entry for uploading. If the buffer is full, upload the current batch of logs.

        :param log: Log object to be queued.
        """
        if len(self.logs) < self.buffer:
            self.appendLogs(log.log_info)
        else:
            log_batch = self.logs
            thread = threading.Thread(target=self.saveLogs, args=(log_batch, log.stream_name))
            thread.start()
            self.logs = []
            self.appendLogs(log.log_info)

    def updateAndQueueLog(self, currentLog, updates, stream):
        """
        Update an existing log entry with new information and queue it for uploading.

        :param currentLog: Log object to be updated.
        :param updates: Log object containing updates.
        :param stream: Name of the log stream.
        :return: Updated Log object.
        """
        newLogEntities = currentLog.log_info.copy()

        if updates:
            updatedLogEntities = updates.log_info
            for key in newLogEntities:
                if key in updatedLogEntities:
                    newLogEntities[key] = updatedLogEntities[key]

        log = Log(stream, newLogEntities)
        self.queueLog(log)

        return log

    def flushLogs(self, stream_name):
        """
        Flush the current logs buffer, uploading any remaining logs to Azure Monitor.

        :param stream_name: Name of the log stream.
        """
        if self.logs:
            log_batch = self.logs
            thread = threading.Thread(target=self.saveLogs, args=(log_batch, stream_name))
            thread.start()
            self.logs = []
