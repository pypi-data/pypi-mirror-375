# `AntaresFabricFramework`

The `AntaresFabricFramework` is an accelerator for Microsoft Fabric data ingestion, validation and transformation. It uses a configuration file to describe each source and destination and includes details for data validation and preprocessing.

## Contents

- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)
- [Contact Information](#contact-information)

## Installation
The following options are available to install the library into a Fabric environment: 

1. <b>PyPi (Recommended):</b>
To use the latest base version available in the publish repository (PyPi), open fabric and edit or create an environment. Open the environment, click public libraries, click Add from PyPi, in the library text box type AntaresFabricFrameworkBase, then click publish. 

2. <b>Custom Library:</b>
The dist folder contains the wheel (.whl) file that can be uploaded into the Fabric environment as a custom library. To do that, open fabric and edit or create an environment. Open the environment, click custom libraries, then click Upload and upload the .whl file. Click Publish. 
If changes are required to the base code, follow these steps to deploy the custom library:
- Fork the repository
- Create a new branch
- Edit the code
- Build the wheel file (eg. `py -m build`)
- Upload as per above 

To install the base notebooks required for the framework (Constants_py, PreProcessingUtils_py and OrchestrateIngestion), follow these steps:

1. Clone this repo to the destination (eg. customers devops)
2. Create a new branch
3. Create the control workspace in Fabric
4. Connect the new branch in the repo to the workspace and in the git folder section type 'FabricArtifacts' to point to that folder in the repo (this is where the notebooks and lakehouse are stored).

After it syncs, the control workspace should contain a control lakehouse and the 3 notebooks as listed earlier. 


## Usage

In order to run the framework, there are a few key dependencies that need to be in place:

1. <b>Ingestion Configuration file (or table):</b>
The ingestion configuration is a json file that contains information about the source of the data, how we want to save the data, and some optional parameters we can use during the ingestion process. 
There is a sample file in the repository [ingestion_configuration.json](SupportingFiles/ingestion_configuration.json) containing all of the attributes used during the data ingestion. 
After the initial execution of the framework, the file will be saved into a fabric table and read from the table each time after that. The table can be edited via SQL commands in a notebook or if the table is deleted, the json file will become the initial source again. 
The ingestgion configuration file and table are both located in the Control Lakehouse. 

2. <b>Keyvault:</b> is used for storing all connection and credential details for all sources (except for Fabric tables and files - these don't require additional keyvault connection details.)
The Keyvault connection details will need to be included in the aformentioned ingestion configuration file. 

3. <b>Constants notebook:</b> A Constants_py notebook is required to sit in the Control lakehouse and contains global constants to be used during the ingestion. These global constants are generally set once and used throughout the framework. 
Global constants include the names of each stage in the medallion architecture and the Azure Log Monitor details. There is a sample Constants_py notebook in the repository.

4. <b>Azure Log Monitor (OPTIONAL):</b> If the Azure Monitor Log service is setup, the framework can push logs from anywhere in the preprocessing stage and at predefined stages in the ingestion process. 
The logging is turned on via the Constants notebook, by setting the `LOGGING_LEVEL` to either `INFO` or `DEBUG`. `NONE` will turn off the logging. INFO will provide high level processing information at each major step in the ingestion. DEBUG will provide more detailed logs at higher intervals.
The schema of the log table that is required to be setup is can also be found in the repository under [AuditLogEntity.json](SupportingFiles/AuditLogEntity.json)

5. <b>PreProcessing notebook (OPTIONAL):</b> Prior to the ingestion into the first (RAW) stage, a preprocessing function can be run to modify the data coming from the source. Typically, this is used to clean up or validate manually input .csv files or to merge multiple files into a single table. 
This is optional and does not need to exist for the ingestion to work. To create a preprocessing function use the following function definition in the PreProcessing_py notebook:

    def preProcess(source):

    source - will be the ingestion configuration source record for a single sourceID. 

6. <b>Deployment Testing Notebook (OPTIONAL):</b> The library provides a testing feature built within the Antares Test framework in order to validate the the deployment to the tenant environment using test data. The test data can be found in the [test-framework-source-dataset](FabricFramework/test-framework-source-dataset) folder, and its recommended to be uploaded to a prelanding lakehouse and load them as fabric tables. Consequently, create a seperate ingestion_configuration file for deployment testing.

To run the deployment test, the below libraries can be imported:

    from FabricFramework.FabricFramework import *
    from FabricFramework.DeploymentTesting import *

Execute the constants and preprocess notebooks:

    %run Constants_py
    %run PreProcessorUtils_py

Instantiate the library as:

    dt = DeploymentTesting(<location of ingestion_configuration.json>, <location of ingestion configuration table>, <constants>, <pre processing function>)

The framework ingestion process can be executed as follows:

    dt.runIngestion() - this will run through the entire ingestion configuration (Every source)

The framework deployment testing process can be executed as follows:

    dt.runDeploymentTesting() - this will run through the entire ingestion configuration (Every source)

7. <b>Orchestration Notebook:</b> The main notebook that is used to execute the ingestion process code. This note book can also contain a parameters cell that can be used to capture additiona parameters (in the form of global constants). 
For example, if the notebook is executed via a data pipeline in Fabric, the Data Pipeline Run ID can be passed in as a parameter and tracked via the logging module so users can trace back any errors to a specific pipeline. 

To run the ingestion framework, the library can be imported:

    from FabricFramework.FabricFramework import *

Execute the constants and preprocess notebooks:

    %run Constants_py
    %run PreProcessorUtils_py

Instantiate the library as:

    ff = FabricFramework(<location of ingestion_configuration.json>, <location of ingestion configuration table>, <constants>, <pre processing function>)

The framework ingestion process can be executed as follows:

    ff.runIngestion() - this will run through the entire ingestion configuration (Every source)

You can also provide 3 parameters for more granual control over that is run as part of the ingestion:

    ff.runIngestion(layer=[LAKEHOUSE_RAW_STAGE_NAME, LAKEHOUSE_TRUSTED_STAGE_NAME], system_code=['Test'], sourceID=[1, 3, 5])

<b>layer</b> - determines the stage that should be run (eg. RAW and TRUSTED, or just RAW or just TRUSTED). The names of each stage is determines by the constants (eg. LAKEHOUSE_RAW_STAGE_NAME) in the constants notebook

<b>system_code</b> - determines which specific system code(s) should be run as part of this execution (this can be a list of system codes)

<b>sourceID</b> - determines which sourceID's should be run on this run (if the ingestion is turned off in the ingestion configuration, the systemID will still be ignored)



## Features


## Contributing
Guidelines for contributing to the project:
1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature-branch`)
5. Open a pull request

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE.txt) file for details.

## Contact Information
For any questions, please contact [martonm@antaressolutions.com.au](mailto:martonm@antaressolutions.com.au).
