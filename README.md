# Metro Station Platform Management with Siemens LOGO! PLC and Modbus via Python

This project simulates the management of train arrivals and departures at a metro station with four platforms. A Siemens LOGO! PLC is used as the operational technology (OT) element for controlling platform states. The PLC communicates with an external device running Python scripts via the Modbus TCP protocol. By implementing the logic externally, this approach showcases the advantages of scalability and the simplicity of using a high-level programming language like Python over traditional PLC programming languages like Ladder or Function Block Diagram (FDB).

Key benefits of this approach include:
- **Scalability**: The external implementation allows seamless adaptation to changes, such as adding more platforms or modifying the logic.
- **Complexity Management**: Python's rich ecosystem and advanced libraries simplify the development of complex behaviors compared to Ladder or FDB, which are often cumbersome for large-scale logic.
- **Modbus TCP Protocol**: This choice facilitates standard and robust communication between the PLC and the Python-based logic controller, ensuring flexibility and interoperability.

## **Train Simulation and LED Indication**
The simulation includes a physical interface with four LED lamps connected to the PLC’s outputs (Q0 to Q3). The LEDs provide real-time signals related to the train’s status on each track:
1. **Train Arriving**:
   - LEDs flash at 0.5-second intervals (on/off).
2. **Train Ready to Depart**:
   - LEDs flash at 0.3-second intervals (on/off).
3. **Train Departed**:
   - LEDs remain continuously lit to indicate the train is in transit.

![image](https://github.com/user-attachments/assets/ca3f5d21-d058-4aaf-8bcf-8e6bcf2d3f07)

## **Station Master’s Role**

The station master interacts with the system using four switches connected to the PLC’s inputs (I0 to I3). Their responsibilities include managing train operations through the following sequence of steps:

1. **Train Arriving**:
   - When a train approaches a platform, the corresponding LED flashes at **0.5-second intervals** (on/off), signaling an arriving train.
2. **Accepting the Train Stop**:
   - The station master closes the switch on the respective track to accept the train. This action signals the train to stop at the platform. During this period, the LED turns **off** to indicate the train has halted.
3. **Train Ready to Depart**:
   - Once the train completes its scheduled stop, the LED begins flashing at **0.3-second intervals** (on/off), signaling that the train is ready to depart.
4. **Authorizing Departure**:
   - The station master opens the switch on the respective track to authorize the train's departure. The LED switches to a **continuous light** to indicate the train is now in transit, exiting the platform.

The coordinated interaction between the station master, PLC, and visual LED indicators ensures safe and efficient management of train arrivals and departures at the station.

## **Project Structure**
The repository consists of two key scripts, each designed to independently handle specific functionalities:

### **1. PLC Management and Simulation (`var4B.py`)**
This Python script is responsible for:
- **PLC Communication**:
  - Modbus TCP is used to interact with the Siemens LOGO! PLC.
  - Reads input signals from the station master (switch states).
  - Controls output signals to LEDs, indicating train statuses.
- **Train Behavior Simulation**:
  - Simulates real-world train operations with randomized intervals for arrival, stopping, and departure durations.
  - Ensures smooth operation using threading locks for each platform.
- **ZeroMQ Integration**:
  - Acts as a publisher to broadcast real-time platform status updates to connected systems.
- **Logging and Debugging**:
  - Logs events for monitoring and debugging purposes.

Key functions include:
- `set_output`: Controls the PLC outputs.
- `read_inputs`: Reads input signals from the PLC.
- `handle_train`: Manages train operations on a specific platform.
- `zmq_publisher`: Publishes platform status updates via ZeroMQ.
- `simulate_train_arrivals`: Handles the simulation of train arrivals and operations.

### **2. WebSocket Bridge and Dashboard (`var4_socket_bridge.js`)**
This Node.js script bridges the Python backend with a real-time visualization dashboard:
- **WebSocket Server**:
  - Sends platform status updates to connected clients in real-time.
  - Operates on `ws://localhost:8080`.
- **HTTP Server**:
  - Hosts a simple HTML page displaying the real-time status of the platforms.
- **ZeroMQ Subscriber**:
  - Subscribes to messages from the Python publisher to retrieve platform status updates.
- **Dynamic Dashboard**:
  - Displays the status of each platform (`idle`, `arriving`, `stopped`, `ready_to_depart`, `departing`) with intuitive visual indicators.

<img width="990" alt="Screenshot 2024-11-25 at 11 36 17" src="https://github.com/user-attachments/assets/b8a3e856-8016-4f9e-8833-97d4c26a5025">

## **Workflow**
1. **Simulation and Broadcasting**:
   - The Python script simulates train operations and broadcasts platform statuses using ZeroMQ.
2. **Data Bridging**:
   - The Node.js script subscribes to ZeroMQ updates, processes the data, and forwards it to WebSocket clients.
3. **Real-Time Visualization**:
   - The dashboard dynamically updates to reflect platform states, providing a user-friendly interface.
4. **Station Master Interaction**:
   - The station master operates switches to control train stops and departures, ensuring safe platform management.

## **Highlights**
### **Advantages of the External Logic Approach**
- **Ease of Implementation**:
  - Python offers a more expressive and powerful framework for handling complex logic, avoiding the steep learning curve and limitations of Ladder and FDB languages.
- **Modularity**:
  - Separating PLC control from visualization ensures error isolation and system stability.
- **Scalability**:
  - Easily supports additional platforms, features, or changes in logic with minimal effort.

### **Challenges in Ladder and FDB Languages**:
- **Coding Complexity**:
  - Implementing equivalent logic in Ladder or FDB would require extensive rungs or blocks, reducing readability and maintainability.
- **Limited Debugging Tools**:
  - Debugging in these environments is less efficient compared to Python’s rich logging and debugging tools.
- **Scalability**:
  - Adding new features or scaling the system would involve significant rework in Ladder/FDB compared to Python's flexible coding capabilities.

## **Setup and Usage**
### **Prerequisites**
- Siemens LOGO! PLC with Modbus TCP enabled.
- Python 3.x environment.
- Node.js environment.
- `pymodbus` library for Modbus TCP communication.
- `zeromq` library for inter-process communication.

### **Running the Project**
1. Start the Python script (`var4B.py`) to simulate train operations and publish platform statuses.
2. Launch the Node.js WebSocket server and dashboard (`var4_socket_bridge.js`).
3. Access the dashboard at `http://localhost:3000` to monitor platform statuses in real-time.

This project demonstrates a modern approach to industrial automation, using Python to extend the capabilities of traditional PLC systems. By combining PLC hardware with external logic and visualization tools, the system achieves enhanced flexibility, scalability, and operational efficiency.
