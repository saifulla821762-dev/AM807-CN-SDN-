NAME:- SAIFULLA
SRN:- PES2UG25AM807
SECTION:- A
# Topology-Change-Detector
Detect network topology changes using SDN (Mininet + Ryu)

## Overview

This project implements a Software Defined Networking (SDN) application using Mininet and the Ryu controller to dynamically detect changes in network topology. The controller monitors switch and link events in real time and updates the network state accordingly.

The system demonstrates:

- Controller–switch interaction
- Flow rule installation using OpenFlow
- Packet handling using packet_in events
- Dynamic topology change detection
- Network behavior analysis using Wireshark and Mininet tools

## Objectives
Detect topology changes such as link failures
Maintain an updated view of the network
Demonstrate SDN concepts including match–action flow rules
Analyze OpenFlow communication using Wireshark

## Tools and Technologies
- Mininet
- Ryu Controller
- OpenFlow 1.3
- Wireshark

## Setup and Execution
### Step 1: Start Wireshark Capture

Start Wireshark and select the loopback (lo) interface. Apply the following filter:

```openflow_v4```

This captures OpenFlow 1.3 messages exchanged between the controller and switches.

### Step 2: Start Ryu Controller

Open Terminal 1 and run:

```python
python3 -m ryu.cmd.manager --observe-links topo_detect.py
```
<img width="1063" height="217" alt="image" src="https://github.com/user-attachments/assets/78799e73-9ccc-412a-90fe-f073f0d30e1b" />

This launches the custom controller with topology discovery enabled.

### Step 3: Start Mininet Topology

Open Terminal 2 and run:

```python
sudo mn --topo linear,2 \
--controller=remote,ip=127.0.0.1,port=6653 \
--switch ovsk,protocols=OpenFlow13
```
<img width="407" height="411" alt="image" src="https://github.com/user-attachments/assets/bdf11f5d-d5c0-4821-a23a-1e0dfd1f40f4" />

This creates a linear topology with two switches and two hosts.

## Initial Topology Detection

Upon starting Mininet, the controller detects switches and links dynamically.

<img width="832" height="243" alt="image" src="https://github.com/user-attachments/assets/ca510c43-344e-4d61-a123-57f8796819ec" />

Terminal 2 displays controller logs showing:

- Switch discovery events
- Link addition between switches
- Updated topology state

## OpenFlow Communication Analysis
Controller–Switch Handshake

<img width="1510" height="850" alt="image" src="https://github.com/user-attachments/assets/2201064f-9c34-4f50-9f79-62c2e22c4033" />


Shows OpenFlow handshake messages including:

- OFPT_HELLO
- OFPT_FEATURES_REQUEST
- OFPT_FEATURES_REPLY
- OFPT_FLOW_MOD

This confirms successful communication and installation of flow rules.

## Packet Processing (Runtime Behavior)

<img width="1502" height="848" alt="image" src="https://github.com/user-attachments/assets/538966b4-27b0-455a-9809-24b67ba31f25" />

Shows:

- OFPT_PACKET_IN messages (switch → controller)
- OFPT_PACKET_OUT messages (controller → switch)

This demonstrates how the controller processes packets and installs forwarding logic dynamically.

## Learning Phase (First pingall)

Run the following in Mininet:

```mininet> pingall```

<img width="1531" height="850" alt="image" src="https://github.com/user-attachments/assets/8108d381-deba-40c4-b7b7-c6591986fba4" />

During the first execution:

- Unknown packets are sent to the controller
- The controller learns MAC addresses
- Flow rules are installed using FLOW_MOD

## Functional Testing
Scenario 1: Normal Operation

```mininet> pingall```

All hosts successfully communicate with each other.

This verifies:

- Correct flow rule installation
- Functional forwarding behavior

## Scenario 2: Topology Failure

Simulate a link failure:

```mininet> link s1 s2 down```

<img width="770" height="122" alt="image" src="https://github.com/user-attachments/assets/18072913-16e2-4db7-9199-c6a4def17434" />

Controller logs show:

- Link removal events
- Updated topology state

## Wireshark Analysis of Topology Change

<img width="1502" height="849" alt="image" src="https://github.com/user-attachments/assets/d581ac8b-d450-483f-9295-4163c765e697" />

Displays OFPT_PORT_STATUS messages indicating:

- Port state changes
- Link failure notification to the controller

This proves real-time topology change detection at the protocol level.

## Key Features Implemented
- Learning Switch Logic using packet_in events
- Flow Rule Installation using OFPFlowMod
- Topology Discovery using Ryu topology API
- Dynamic Link Monitoring (add/remove events)
- Traffic Analysis using Wireshark

## Conclusion

This project successfully demonstrates an SDN-based topology change detection system. The controller dynamically updates network state upon link failures and maintains efficient packet forwarding through OpenFlow rules.

The use of Wireshark further validates controller–switch communication and provides insight into OpenFlow message exchanges, including packet handling and topology updates.
