# BrainLink Pro Unity3D Integration

BrainLink Pro Unity3D Integration is a project that enhances the [BrainLinkParser-Python](https://github.com/Macrotellect/BrainLinkParser-Python) to facilitate low-latency integration of a BrainLink Pro device with Unity3D.

![BrainLink Pro Integration](https://github.com/user-attachments/assets/dcba5fa0-5556-47a9-b2bb-5eee024596c6)

## Installation

### 1. Python Setup
- Install [Python 3.11](https://www.python.org/downloads/).
Note: Version must match exactly.

### 2. Required Python Libraries
Install the following libraries using pip:

```bash
pip install tkinter pyserial fastapi uvicorn
```

### 3. BrainLinkParser
Ensure `BrainLinkParser.py` is located in the same directory as your script or within your Python path.

### 4. Running the Python Script
For Windows 11 users:
1. Open PowerShell in the script's directory.
2. Execute the following command:

   ```bash
   python .\BrainLinkMonitor.py
   ```

### 5. Unity3D Integration
1. Import the provided C# script from `UnityClient/EEGDataReceiver.cs` into your Unity project.
2. Install the necessary dependencies, particularly:
   - Newtonsoft.Json
3. Create a TextMeshPro text element in your scene to display the EEG values.

## Usage
1. Start the Python script to begin receiving data from the BrainLink Pro device.
2. In your Unity project, use the `EEGDataReceiver` script to process and display the incoming EEG data.

## License

This project is a fork of [BrainLinkParser-Python](https://github.com/Macrotellect/BrainLinkParser-Python), 
which does not specify a license. 

The additional code and modifications made in this fork are available for use under 
the MIT License. 

If you're the original author of BrainLinkParser-Python and have any concerns, 
please contact us.

## Acknowledgments
- Original BrainLinkParser by [Macrotellect](https://github.com/Macrotellect)
