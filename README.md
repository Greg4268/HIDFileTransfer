# HID File Transfer Via Arduino Uno R4 WiFi
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![C++](https://img.shields.io/badge/c++-%2300599C.svg?style=for-the-badge&logo=c%2B%2B&logoColor=white) 

> An educational project demonstrating Arduino-based HID automation for file transfers between Windows and web servers.

![Arduino-to-Server](https://cdn.jsdelivr.net/gh/Greg4268/Arduino_HID_Testing@main/docs/webpage_image.png)

## 📚 Educational Purpose

This project is designed for **educational purposes only** to demonstrate:

- Human Interface Device (HID) programming with Arduino
- PowerShell automation techniques
- Web server deployment and file handling with Flask
- Client-server communication basics
- Simple authentication implementation

The techniques demonstrated should only be used on personal devices with appropriate authorization.

## 🛠️ Project Components

The repository consists of three main parts:

1. **Arduino Code (`offload.cpp`)**
   - Configures an Arduino board to act as a USB HID device
   - Executes PowerShell commands on Windows hosts via Keyboard library
   - Launches the file upload process automatically

2. **PowerShell Script (`pwshScript.ps1`)**
   - Scans the Windows desktop for files
   - Creates proper multipart/form-data POST requests
   - Uploads files to the remote server
   - Compatible with older PowerShell versions (<7)

3. **Web Server (`server.py`)**
   - Flask-based file upload server
   - Supports basic authentication
   - Provides a simple web interface for viewing and managing files
   - Demonstrates RESTful API design principles

## 🧠 Learning Objectives

By studying this project, you can learn about:

- **Windows Vulnerabilities**: How simply plugging in a usb drive, cable, or usb-connected device could compromise your system
- **HID Programming**: How USB devices can simulate keyboard/mouse inputs
- **PowerShell Automation**: Script execution, file system operations, network requests
- **Web Development**: REST API design, file uploads, authentication implementation
- **Security Concepts**: Basic authentication, secure file handling
- **Deployment**: Web application hosting on platforms like Railway

## 🚀 Getting Started

### Prerequisites

- Arduino board with USB HID capabilities (Uno R4 WiFi, Leonardo, Micro, Pro Micro, etc.)
- Windows computer for testing
- Basic knowledge of Arduino programming, PowerShell, and Python
- GitHub account for hosting the PowerShell script
- Railway account (or similar) for hosting the server

## 🔒 Important Security Notes

This project is for educational purposes only. When working with this code:

- Only use on personal devices or with explicit permission
- Never use on production environments or with sensitive data
- The authentication implemented is basic and not suitable for production use
- Files are stored temporarily and will be lost when the server restarts

## 📋 License

This project is released under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔄 Usage Flow

1. Connect Arduino to a Windows computer
2. Arduino executes PowerShell commands to download and run script.ps1
3. PowerShell script scans desktop files and uploads them to the server
4. Files can be viewed and downloaded from the web interface
5. Files can be deleted through the web interface

## 📝 Notes

- The server uses Railway's ephemeral filesystem - files will not persist after server restarts
- For learning purposes only - not intended for production use
- Demonstrates technical concepts in a simplified manner for educational clarity

---
