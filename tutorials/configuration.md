# Tutorial: Configuration files

File-based configuration is convenient for two reasons:
1. source code does not need to be edited to implement a new pipeline,
2. the configuration file can be stored as pipeline documentation for generated AD models.

The format of the configuration files is JINJA2 templates: while the structure follows the JSON format, custom placeholders can be added to the configurations that are evaluated during the runtime. The template processing supports the following fields:

| Template     | Description                                                                                                                   |
|--------------|-------------------------------------------------------------------------------------------------------------------------------|
| timestamp    | Will be replaced with the current timestamp. Useful to individualize logfiles or tag models.                                  |
| project_root | The path to the project repository, making the paths in configuration files system-independent.                               |
| git_tag      | Short git commit tag of the repository, as a helper to mark the version of code that was used to train a model.               |
| influx_token | The token is one of the few command-line arguments to the main program. It will be passed to the InfluxDB reporter as kwargs. |

New template fields can be added by extending the configuration processing logic in `IoT-AD.py`.

## Configuration elements

Let's take a look at an example, `flow-based-rf-train.json.jinja`.

### Description

```json
"DESCRIPTION": [
    "Train a random forest classifier. slowite and malariaDoS attack data from ",
    "MQTTset is labeled as 1 and a segment from MQTTset's benign traffic as 0. ",
    "Uses window-based flow features at 10 ms windows."
],
```

The description is a custom field to summarize the pipeline described in the configuration.

### Data sources

```json
"DATA_SOURCES": [
    {
        "type": "dataset",
        "loader": {
            "class": "PcapFileLoader",
            "kwargs": {
                "filepath": "{{ project_root }}/data/MQTTset/Data/PCAP/slowite.pcap",
                "preprocessor_path": "{{ project_root }}/code/cpp-extract-features/cmake-build/pcap-feature-extraction"
            }
        },
        "preprocessors": [
            {
                "class": "CppPacketProcessor",
                "kwargs": {}
            },
            {
                "class": "WindowFlowFeatureProcessor",
                "kwargs": {
                    "window_size_ms": 10
                }
            },
            {
                "class": "FileLabelProcessor",
                "kwargs": {
                    "label_value": 1
                }
            }
        ]
    }
],
```

The data sources section defines a sequence of data sources to be used as input for the model. Currently, the dataset type is supported, but live traffic capture functionality is planned. The PcapFileLoader takes as custom keyword arguments paths to the dataset and to the pre-built C++ packet loader executable. The packet loader is an efficient solution to parse large PCAP files. 

In this example, the `CppPacketProcessor` reads the output from the C++ PCAP file parser and extracts a set of common features. The `WindowFlowFeatureProcessor` combines data from multiple packets into flow statistics to speed up subsequent processing and model training/prediction times. The `FileLabelProcessor` adds the ground truth label to the samples, which can be used for model performance evaluation and reporting.

Since data loaders and preprocessors are defined individually, it is possible to combine various data formats, such as PCAP files and NetFlow dataset files. SIURU only requires that the desired model input features are available from all datasets after preprocessing is complete.

### Model

```json
"MODEL":
{
    "class": "RandomForestModel",
    "train_new_model": true,
    "skip_saving_model": false,
    "model_name": "example-flow-based-rf",
    "model_storage_base_path": "{{ project_root }}/models",
    "encoder":
    {
        "class": "DefaultEncoder",
        "kwargs": {
            "feature_filter": [
                "window_flow_pkt_count",
                "window_flow_sum_pkt_size",
                "window_flow_avg_pkt_size",
                "window_flow_inter_arrival_avg"
            ]
        }
    }
},
"VERSION": "{{ git_tag }}"
```

The model section defines the model to be trained or used for prediction, depending on whether `train_new_model` is set to true or false. To debug pipelines for model training, it can be helpful to set `skip_saving_model` to true, which prevents the creation of training files that need to be manually deleted before rerunning the pipeline.

The model name and storage path are both used to determine the final path and name for the models. Here the `{{ project_root }}` template variable is used to avoid absolute paths.

The `DefaultEncoder` class accepts a feature filter specification using string versions of the features defined in `code/common/features.py`.

Finally, the git version template is used to mark the repository version used to train the model.

### Log

```json
"LOG": [
    {
        "level": "INFO",
        "path": "{{ project_root }}/models/example-flow-based-rf/{{ timestamp }}-training-log.txt"
    }
]
```

If the "LOG" element is defined in the configuration file, SIURU will store the logging output of each run in a dedicated file. The default value for the log path is `logs/other/{{ timestamp }}-log.txt`, using the timestamp from the beginning of execution, and the default logging level is `DEBUG`. It is possible to customize the output file path (e.g. to sort it by model type) by adding the above section to the configuration.