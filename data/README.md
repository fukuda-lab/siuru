# TODO: BoT-IoT

https://cloudstor.aarnet.edu.au/plus/s/umT99TnxvbpkkoE?path=%2FPCAPs

About:

The BoT-IoT dataset was created by designing a realistic network environment in the Cyber Range Lab of UNSW Canberra. The network environment incorporated a combination of normal and botnet traffic. The dataset’s source files are provided in different formats, including the original pcap files, the generated argus files and csv files. The files were separated, based on attack category and subcategory, to better assist in labeling process.

The captured pcap files are 69.3 GB in size, with more than 72.000.000 records. The extracted flow traffic, in csv format is 16.7 GB in size. The dataset includes DDoS, DoS, OS and Service Scan, Keylogging and Data exfiltration attacks, with the DDoS and DoS attacks further organized, based on the protocol used.

To ease the handling of the dataset, we extracted 5% of the original dataset via the use of select MySQL queries. The extracted 5%, is comprised of 4 files of approximately 1.07 GB total size, and about 3 million records.

# CICIDS2017

Only has flow features, but a lot of them.

https://www.kaggle.com/datasets/cicdataset/cicids2017

About:

Intrusion Detection Systems (IDSs) and Intrusion Prevention Systems (IPSs) are the most important defense tools against the sophisticated and ever-growing network attacks. Due to the lack of reliable test and validation datasets, anomaly-based intrusion detection approaches are suffering from consistent and accurate performance evolutions.

Our evaluations of the existing eleven datasets since 1998 show that most are out of date and unreliable. Some of these datasets suffer from the lack of traffic diversity and volumes, some do not cover the variety of known attacks, while others anonymize packet payload data, which cannot reflect the current trends. Some are also lacking feature set and metadata.

CICIDS2017 dataset contains benign and the most up-to-date common attacks, which resembles the true real-world data (PCAPs). It also includes the results of the network traffic analysis using CICFlowMeter with labeled flows based on the time stamp, source, and destination IPs, source and destination ports, protocols and attack (CSV files). Also available is the extracted features definition.

Generating realistic background traffic was our top priority in building this dataset. We have used our proposed B-Profile system (Sharafaldin, et al. 2016) to profile the abstract behavior of human interactions and generates naturalistic benign background traffic. For this dataset, we built the abstract behavior of 25 users based on the HTTP, HTTPS, FTP, SSH, and email protocols.

The data capturing period started at 9 a.m., Monday, July 3, 2017, and ended at 5 p.m. on Friday, July 7, 2017, for a total of 5 days. Monday is the normal day and only includes benign traffic. The implemented attacks include Brute Force FTP, Brute Force SSH, DoS, Heartbleed, Web Attack, Infiltration, Botnet and DDoS. They have been executed both morning and afternoon on Tuesday, Wednesday, Thursday and Friday.

In our recent dataset evaluation framework (Gharib et al., 2016), we have identified eleven criteria that are necessary for building a reliable benchmark dataset. None of the previous IDS datasets could cover all of the 11 criteria. In the following, we briefly outline these criteria:

Complete Network configuration: A complete network topology includes Modem, Firewall, Switches, Routers, and presence of a variety of operating systems such as Windows, Ubuntu, and Mac OS X.

Complete Traffic: By having a user profiling agent and 12 different machines in Victim-Network and real attacks from the Attack-Network.

Labelled Dataset: Section 4 and Table 2 show the benign and attack labels for each day. Also, the details of the attack timing will be published on the dataset document.

Complete Interaction: As Figure 1 shows, we covered both within and between internal LAN by having two different networks and Internet communication as well.

Complete Capture: Because we used the mirror port, such as a tapping system, all traffics have been captured and recorded on the storage server.

Available Protocols: Provided the presence of all commonly available protocols, such as HTTP, HTTPS, FTP, SSH an and email protocols.

Attack Diversity: Included the most common attacks based on the 2016 McAfee report, such as Web-based, Brute force, DoS, DDoS, Infiltration, Heart-bleed, Bot, and Scan covered in this dataset.

Heterogeneity: Captured the network traffic from the main Switch and memory dump and system calls from all victim machines, during the execution of the attack.

Feature Set: Extracted more than 80 network flow features from the generated network traffic using CICFlowMeter and delivered the network flow dataset as a CSV file. See our PCAP analyzer and CSV generator.

MetaData: Completely explained the dataset which includes the time, attacks, flows and labels in the published paper.

The full research paper outlining the details of the dataset and its underlying principles:

Iman Sharafaldin, Arash Habibi Lashkari, and Ali A. Ghorbani, “Toward Generating a New Intrusion Detection Dataset and Intrusion Traffic Characterization”, 4th International Conference on Information Systems Security and Privacy (ICISSP), Purtogal, January 2018

# TODO: KDD Cup 1999

There should be an improved and more balanced data set available, look into the papers!

https://www.kaggle.com/datasets/galaxyh/kdd-cup-1999-data

About:

This is the data set used for The Third International Knowledge Discovery and Data Mining Tools Competition, which was held in conjunction with KDD-99 The Fifth International Conference on Knowledge Discovery and Data Mining. The competition task was to build a network intrusion detector, a predictive model capable of distinguishing between bad'' connections, called intrusions or attacks, andgood'' normal connections. This database contains a standard set of data to be audited, which includes a wide variety of intrusions simulated in a military network environment.

# Kitsune Datasets

https://www.kaggle.com/datasets/ymirsky/network-attack-dataset-kitsune

Kitsune Surveillance Network Intrusion Datasets

If you use these datasets, please cite:

Yisroel Mirsky, Tomer Doitshman, Yuval Elovici, and Asaf Shabtai, 
"Kitsune: An Ensemble of Autoencoders for Online Network Intrusion Detection", 
Network and Distributed System Security Symposium 2018 (NDSS'18)

### Overview

The are 9 network capture datasets:

	- ARP MitM: ARP Man-in-the-Middle attack between a camera & DVR
	- SSDP Flood: SSDP Flooding Attack against the DVR Server
	- OS Scan: NMAP OS Scan of the subnet
	- Active Wiretap: A bridged Raspberry Pi placed between all cameras and the DVR server
	- SYN Flooding: A SYN DoS attack against a camera
	- Fuzzing: A Fuzzing Attack against DVR's webserver's cgi
	- Video Injection: A MitM video content injection attack into a camera's live stream
	- SSL Renegotiation: A DoS attack against an SSL enabled camera
	- Mirai: The initial infection and propagation of the Mirai malware (**on a diffrent [IoT] network**)

For more details on the attacks themselves, please refer to the paper.

### Organization

Each attack dataset is located in a seperate directory.

The directory contains three files:
	
\<Attack\>_pcap.pcapng	:	A raw pcap capture of the origional N packets. The packets have been truncated to 200 bytes for privacy reasons.
	
\<Attack\>_dataset.csv	:	An N-by-M matrix of M-sized feature vectors, each decribing the packet and the context of that packet's channel (see paper).
	
\<Attack\>_labels.csv		:	An N-by-1 vector of 0-1 values which indicate whether each packet in \<Attack\>_pcap.pcapng (and \<Attack\>_dataset.csv) is malicous ('1') or not ('0'). For the Man-in-middle-Attacks, all packets which have passed through the MitM are marked as '1'.

Every attack dataset begins with benign traffic, and then at some point (1) the attacker connects to the network and (2) initiiates the given attack.

# MQTTset

https://www.kaggle.com/datasets/cnrieiit/mqttset

Related paper: https://www.mdpi.com/1424-8220/20/22/6578/htm

About:

The proposed work aims to create a dataset linked to the IoT context, in particular on the MQTT communication protocol, in order to give to the research and industrial community an initial dataset to use in their application. The dataset is composed by IoT sensors based on MQTT where each aspect of a real network is defined. In particular, the MQTT broker is instantiated by using Eclipse Mosquitto and the network is composed by 8 sensors. The scenario is related to a smart home environment where sensors retrieve information about temperature, light, humidity, CO-Gas, motion, smoke, door and fan with different time interval since the behaviour of each sensor is different with the others.

As mentioned, the dataset isc composed by 8 MQTT sensors with different features. In table, the MQTT sensors are reported. Each sensor is associated with a data profile and a topic linked to the MQTT broker. The data profile consists of the type of data that the sensors communicate while the topic is defined by the sensor when sending the data to the broker. Finally, the sensors were conceptually divided into two rooms as if they were distributed in a smart house and the MQTT broker has 10.16.100.73 as IP address with 1883 as clear text communication port. In the table, the time could be periodic o random. This concept is important since a temperature sensor has a periodic behavior over time, i.e. cyclically sending information retrieved from the environment periodically (defined as P). Instead, a motion sensor has a more random behavior since it sends information only when a user passes in front of the sensor (defined as R)). By analyzing also this aspect, the dataset is even more valid as a real behavior of a home automation is simulated and implemented.

The repository is composed by 3 folder:

- PCAP raw data
    - Legitimate
    - SlowITe
    - Bruteforce
    - Malformed data
    - Flooding
    - DoS attack
- CSV file
    - Legitimate
    - SlowITe
    - Bruteforce
    - Malformed data
    - Flooding
    - DoS attack
- Final dataset
    - train70.csv, test30.csv
    - train70_reduced.csv, test30_reduced.csv
    - train70_augmented.csv, test30_augmented.csv

In the PCAP folder, there are the raw network data recovered directly from the sensors of the MQTT network and also the traffic related to the attacks. In the CSV folder instead, there are the data and features extracted from the PCAP file using the tshark tool. Finally, the FINAL_CSV folder contains the CSV files combined with each other and subsequently used for machine learning algorithms. In particular, CSV files are present in 3 different formats:

1. train70.csv, test30.csv: in these files, the legitimate traffic was randomly combined with the different malicious traffic.
2.  train70_reduced.csv, test30_reduced.csv: the reduced form combines malicious traffic with legitimate traffic in the 50:50 form, so there will be less legitimate traffic than actually. The legitimate traffic will be equal to the sum of the malicious traffic
3.  train70_augmented.csv, test30_augmented.csv: in the augmented form, however, the malicious traffic has been increased so that the sum of the traffic related to the attacks is equal to the legitimate traffic.


# TODO: TON_IoT

Has PCAPs of non-IoT network data and flow features of IoT data.

https://research.unsw.edu.au/projects/toniot-datasets

https://cloudstor.aarnet.edu.au/plus/s/ds5zW91vdgjEj9i

More specific links to PCAPS:

https://cloudstor.aarnet.edu.au/plus/s/ds5zW91vdgjEj9i?path=%2FRaw_datasets%2FRaw_Network_dataset%2FNetwork_dataset_pcaps%2Fnormal_attack_pcaps

https://cloudstor.aarnet.edu.au/plus/s/ds5zW91vdgjEj9i?path=%2FRaw_datasets%2FRaw_Network_dataset%2FNetwork_dataset_pcaps%2Fnormal_pcaps

About:

The TON_IoT datasets are new generations of Industry 4.0/Internet of Things (IoT) and Industrial IoT (IIoT) datasets for evaluating the fidelity and efficiency of different cybersecurity applications based on Artificial Intelligence (AI), i.e., Machine/Deep Learning algorithms. The datasets can be downloaded from HERE.  You can also use our datasets: the BoT-IoT and UNSW-NB15.

The datasets can be used for validating and testing various Cybersecurity applications-based AI such as intrusion detection systems, threat intelligence, malware detection, fraud detection, privacy-preservation, digital forensics, adversarial machine learning, and threat hunting. 

---

The datasets have been called 'ToN_IoT' as they include heterogeneous data sources collected from Telemetry datasets of IoT and IIoT sensors, Operating systems datasets of Windows 7 and 10 as well as Ubuntu 14 and 18 TLS and Network traffic datasets. The datasets were collected from a realistic and large-scale network designed at the Cyber Range and IoT Labs, the School of Engineering and Information technology (SEIT), UNSW Canberra @ the Australian Defence Force Academy (ADFA). A new testbed network was created for the industry 4.0 network that includes IoT and IIoT networks. The testbed was deployed using multiple virtual machines and hosts of windows, Linux and Kali operating systems to manage the interconnection between the three layers of IoT, Cloud and Edge/Fog systems. Various attacking techniques, such as DoS, DDoS and ransomware, against web applications, IoT gateways and computer systems across the IoT/IIoT network.  The datasets were gathered in a parallel processing to collect several normal and cyber-attack events from network traffic, Windows audit traces, Linux audit traces, and telemetry data of IoT services.

---

The directories of the TON_IoT datasets include the following:
1.  Raw datasets

    IoT/IIoT datasets were logged in log and CSV files, where more than 10 IoT and IIoT sensors such as weather and Modbus sensors were used to capture their telemetry data.
    Network datasets were collected in the packet capture (pcap) formats, log files and CSV files of the ZEEK (Bro) tool.
    Linux datasets were collected by running a tracing tool on Ubuntu 14 and 18 systems, especially atop, for logging desk, process, processor, memory and network activities. The data were logged in TXT and CSV files.
    Windows datasets were captured by executing dataset collectors of the Performance Monitor Tool on Windows 7 and 10 systems. The raw datasets were collected in a blg format opened by Performance Monitor Tool to collect activities of desk, process, processor, memory and network activities in a CSV format.

2. Processed datasets

    The four datasets were filtered to generate standard features and their label. The entire datasets were processed and filtered in the format of CSV files to be used at any platform. The new generated features of the four datasets were described in the ‘Description_stats_datasets’ folder, and the number of records including normal and attack types is also demonstrated in this folder.

3. Train_Test_datasets

    This folder involves samples of the four datasets in a CSV format that were selected for evaluating the fidelity and efficiency of new cyber security application-based AI and machine learning algorithms. The number of records including normal and attack types for training and testing the algorithms are listed in the ‘Description_stats_datasets’ folder.

4. Description_stats_datasets

    This folder includes the description of the features of the four processed dataset (the folder of processed datasets) and the statistics (i.e., the number of rows of normal and attack types).

5. SecurityEvents_GroundTruth_datasets

    This folder includes the security events of hacking happened in the four datasets and their timestamp (ts). The datasets were labelled based on tagging IP addresses (192.168.159.30-39) and their timestamps in the four datasets. These IP addresses were used for Kali Linux systems to launch and exploit the systems of the four environments of IoT/IoT systems such as Cloud gateways, MQTT protocols, web applications of Node Red, Linux, Windows and network services.


# UNSW-NB15

Not IoT, but has a lot of attacks and supposedly provides PCAP files:

https://research.unsw.edu.au/projects/unsw-nb15-dataset

https://cloudstor.aarnet.edu.au/plus/index.php/s/2DhnLGDdEECo4ys

About:

The raw network packets of the UNSW-NB 15 dataset was created by the IXIA PerfectStorm tool in the Cyber Range Lab of UNSW Canberra for generating a hybrid of real modern normal activities and synthetic contemporary attack behaviours. The tcpdump tool was utilised to capture 100 GB of the raw traffic (e.g., Pcap files). This dataset has nine types of attacks, namely, Fuzzers, Analysis, Backdoors, DoS, Exploits, Generic, Reconnaissance, Shellcode and Worms. The Argus, Bro-IDS tools are used and twelve algorithms are developed to generate totally 49 features with the class label. These features are described in UNSW-NB15_features.csv file.

The total number of records is two million and 540,044 which are stored in the four CSV files, namely, UNSW-NB15_1.csv, UNSW-NB15_2.csv, UNSW-NB15_3.csv and UNSW-NB15_4.csv.

The ground truth table is named UNSW-NB15_GT.csv and the list of event file is called UNSW-NB15_LIST_EVENTS.csv.

A partition from this dataset was configured as a training set and testing set, namely, UNSW_NB15_training-set.csv and UNSW_NB15_testing-set.csv respectively. The number of records in the training set is 175,341 records and the testing set is 82,332 records from the different types, attack and normal.
