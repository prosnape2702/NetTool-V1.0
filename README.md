\# IT Operations Diagnostic Tool



A Python-based Windows diagnostic tool designed to collect system and network information, test network connectivity, troubleshoot DNS resolution, and provide a basic diagnostic report.



This project was created as a hands-on way for me to develop practical knowledge in IT operations, networking, troubleshooting, and Python automation.





\#######################################      START OF FEATURES      ##########################################



The tool provides six menu options:



1\. Device Information

2\. Network Information

3\. Connectivity Test

4\. DNS Test

5\. Full Diagnostic

6\. Exit



\#################  1 : Device Information  ##########################



Collects basic information about the Windows device, including:



\- Hostname

\- Operating system

\- OS release and version

\- System architecture

\- Processor information



The information is collected using Python's `platform` module.



\#################  2 : Network Information  ##########################



Detects the active network adapter and displays:



\- Active network interface

\- IPv4 address

\- Subnet mask

\- Default gateway

\- Configured DNS server(s)



The program runs `ipconfig /all` and parses the output to obtain the network configuration.



Instead of assuming that Wi-Fi or Ethernet is the active connection, the program determines which local IP address Windows would use to reach an external destination and matches that address to the appropriate network adapter.



\#################  3 : Connectivity Test   ###########################



Tests connectivity at several stages:



\- Default gateway

\- Internet connectivity using `8.8.8.8`

\- Domain connectivity using `google.com`



Each test returns either `PASS` or `FAIL`.



This helps distinguish between problems involving the local network, external connectivity, and domain-based communication.



\##################     4 : DNS Test       ############################



Tests DNS resolution using:



\- The system's configured DNS resolver

\- Google Public DNS (`8.8.8.8`)



The tool uses `nslookup` to resolve `google.com` and compares whether resolution succeeds through each resolver.



Depending on the results, the tool can identify possible situations such as:



\- No Internet connectivity

\- Configured DNS resolver problems

\- External/public DNS being blocked by network policy

\- DNS resolution failure through both resolvers



The diagnostic messages describe possible causes rather than assuming a single root cause.



\#################  5 : Full Diagnostic   ############################



Runs the major checks together and produces a consolidated report containing:



\- Device information

\- Network configuration

\- Gateway connectivity

\- Internet connectivity

\- Domain connectivity

\- System DNS status

\- Public DNS status



The report concludes with either:



`HEALTHY`



or



`ATTENTION REQUIRED`



When attention is required, the program provides possible causes based on the observed results.



\## Technologies Used




\- Python

\- Windows Command Line

\- `ipconfig`

\- `ping`

\- `nslookup`

\- Python `platform` module

\- Python `socket` module

\- Python `subprocess` module

\- Python `re` module / regular expressions



\## Example Diagnostic Output



```text

========== FULL SYSTEM DIAGNOSTIC ==========



DEVICE

Hostname:             EXAMPLE-PC

Operating System:     Windows 11

Architecture:         AMD64



NETWORK

Interface:            Ethernet

IPv4 Address:         192.168.1.10

Subnet Mask:          255.255.255.0

Default Gateway:      192.168.1.1

DNS Server:           192.168.1.1



CONNECTIVITY

Local Gateway:        PASS

Internet:             PASS

Domain Connectivity:  PASS



DNS

System DNS:           PASS

Public DNS:           PASS



\--------------------------------------------

OVERALL STATUS:       HEALTHY

\--------------------------------------------

```



The values above are examples and will depend on the device and network running the tool.



\#######################################      END OF FEATURES      ##########################################



\## TESTING (TESTING.md)



The tool was developed and tested iteratively rather than only being tested after completion.



Testing included:



\- Normal network connectivity

\- Network disconnected

\- Invalid/non-existent domain

\- Invalid menu input

\- Network interface detection

\- DNS resolution

\- Gateway and Internet connectivity



Several issues were discovered during development, including:



\- The network interface originally being hard-coded as Wi-Fi

\- Selecting an adapter based on `ipconfig` list order rather than the route Windows actually uses

\- Only storing one DNS server

\- Connectivity testing unintentionally displaying the Network Information screen



These problems were corrected during development.



Detailed development and testing information is available in \[`TESTING.md`](TESTING.md).



\## Known Limitations



The current version has several limitations:



\- Designed specifically for Windows

\- Depends on English Windows command output

\- Network information is parsed from `ipconfig /all`, so changes to its output format may affect parsing

\- A device or router that blocks ICMP/ping may appear unreachable even when other network services are working

\- DNS testing currently focuses on IPv4 results

\- Only the first IPv4 address returned for a domain is displayed

\- Only the first default gateway is stored

\- Google Public DNS may be intentionally blocked by corporate firewall or network policy

\- Diagnostic results identify possible causes and should not be treated as definitive root-cause analysis



\###########################################################################################################





\## What I Learned



This project allowed me to apply networking concepts through practical development rather than studying them only in theory.



Topics I explored include:



\- Network interfaces

\- IPv4 addressing

\- Subnet masks

\- Default gateways

\- Network routing concepts

\- DNS resolution

\- System and public DNS resolvers

\- ICMP and connectivity testing

\- Windows network configuration

\- Active network interface detection

\- Troubleshooting through fault isolation



From the programming side, the project also gave me practical experience with:



\- Python functions and program structure

\- Dictionaries and lists

\- Exception handling

\- Running Windows commands using `subprocess`

\- Working with sockets

\- Parsing command-line output

\- Regular expressions

\- Reusing functions across multiple diagnostic features

\- Testing and debugging software iteratively





\## Project Motivation



My professional background is in aircraft engineering and operations, and I am currently transitioning into Information Technology while pursuing a Bachelor of Information Technology.



Aircraft troubleshooting involves systematically inspecting systems, isolating faults, verifying possible causes, and escalating issues when necessary. I wanted to apply a similar troubleshooting mindset to IT operations.



I therefore built this project to combine my existing engineering problem-solving approach with practical learning in Windows support, networking, DNS, troubleshooting, and Python automation.





\## Future Improvements



Possible future improvements include:



\- More detailed DNS error detection, including distinguishing an invalid domain from a DNS server failure

\- IPv6 support

\- Wi-Fi information and signal diagnostics

\- VPN detection and diagnostics

\- Windows service and process checks

\- Disk, memory, and system health information

\- Event Viewer/log analysis

\- Exporting diagnostic results to a report file

\- Improved network configuration collection without relying on human-readable `ipconfig` output

\- Additional automated troubleshooting recommendations





\## Disclaimer



This project is a personal learning and portfolio project. It is intended for basic Windows IT diagnostics and educational use rather than production enterprise monitoring.



