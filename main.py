import platform
import re
import socket
import subprocess


def show_menu():
    print("""
========================================
       IT OPERATIONS DIAGNOSTIC TOOL
========================================

1. Device Information
2. Network Information
3. Connectivity Test
4. DNS Test
5. Full Diagnostic
6. Exit
""")

#################  1 : Device Information  ##########################

def device_information():
    print(f"""
========== DEVICE INFORMATION ==========

        Hostname:    {platform.node()}
Operating System:    {platform.system()}
      OS Release:    {platform.release()}
      OS Version:    {platform.version()}
    Architecture:    {platform.machine()}
       Processor:    {platform.processor()}
""")

#################  2 : Network Information  ##########################

def get_active_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return None
    finally:
        s.close()

def get_network_information():
    """Return a dict for the adapter Windows uses to reach the internet, or None."""
    result = subprocess.run(["ipconfig", "/all"], capture_output=True, text=True)
    lines = result.stdout.splitlines()

    adapters = []
    current = None
    last_key = None

    for line in lines:
        # Unindented lines are adapter headers, e.g. "Wireless LAN adapter Wi-Fi:"
        if line.strip() and not line.startswith(" "):
            last_key = None
            if "adapter" in line:
                name = line.split("adapter", 1)[1].strip().rstrip(":").strip()
                current = {
                    "name": name,
                    "ipv4": "Not found",
                    "subnet": "Not found",
                    "gateway": "Not found",
                    "dns": [],
                }
                adapters.append(current)
            else:
                current = None
            continue

        if current is None or not line.strip():
            continue

        if ". :" in line:
            value = line.split(":", 1)[1].strip()

            if "IPv4 Address" in line:
                current["ipv4"] = value.replace("(Preferred)", "").strip()
                last_key = None
            elif "Subnet Mask" in line:
                current["subnet"] = value
                last_key = None
            elif "Default Gateway" in line:
                last_key = "gateway"
                if value and ":" not in value:
                    current["gateway"] = value
            elif "DNS Servers" in line:
                last_key = "dns"
                if value:
                    current["dns"].append(value)
            else:
                last_key = None
        else:
            value = line.strip()
            if last_key == "gateway" and current["gateway"] == "Not found" and ":" not in value:
                current["gateway"] = value
            elif last_key == "dns":
                current["dns"].append(value)

    active_ip = get_active_ip()
    for adapter in adapters:
        if adapter["ipv4"] == active_ip:
            return adapter
    return None

def network_information():
    active = get_network_information()

    print("""
========== NETWORK INFORMATION ==========""")

    if active is None:
        print("No active network connection found.")
    else:
        print(f"""
      Interface:    {active['name']}
   IPv4 Address:    {active['ipv4']}
    Subnet Mask:    {active['subnet']}
Default Gateway:    {active['gateway']}""")

        if active["dns"]:
            print(f"     DNS Server:    {active['dns'][0]}")
            for server in active["dns"][1:]:
                print(f"                  {server}")
        else:
            print("DNS Server:    Not found")
    print()

#################  3 : Connectivity Test   ###########################

def ping(target):
    """Send one ping. Return True only if a real reply (TTL=) comes back."""
    result = subprocess.run(
        ["ping", "-n", "1", "-w", "2000", target],
        capture_output=True,
        text=True,
    )
    return "TTL=" in result.stdout

def print_check(label, target, passed):
    print(f"""
{label}:
  Target:    {target}
  Status:    {'PASS' if passed else 'FAIL'}""")

def connectivity_test():
    print(f"""
========== CONNECTIVITY TEST ==========""")

    # 1. Default gateway
    active = get_network_information()
    gateway = active["gateway"] if active else "Not found"
    gateway_ok = gateway != "Not found" and ping(gateway)
    print_check("Default Gateway", gateway, gateway_ok)

    # 2. Internet (by IP address)
    internet_ok = ping("8.8.8.8")
    print_check("Internet", "8.8.8.8", internet_ok)

    # 3. Domain (by name)
    domain_ok = ping("google.com")
    print_check("Domain", "google.com", domain_ok)

    overall = gateway_ok and internet_ok and domain_ok
    print(f"\nOverall Connectivity: {'PASS' if overall else 'FAIL'}")
    print()

##################     4 : DNS Test       ############################

def resolve(domain, server=None):
    """Look up a domain with nslookup. Return the first IPv4 address, or None if it fails.
    If server is given, that DNS server is asked. Otherwise the system DNS is used."""
    command = ["nslookup", "-timeout=2", domain]
    if server:
        command.append(server)

    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=15)
    except subprocess.TimeoutExpired:
        return None

    output = result.stdout

    # The answer starts at the "Name:" line. Everything before it is the DNS server's own address.
    if "Name:" not in output:
        return None

    answer = output.split("Name:", 1)[1]
    ips = re.findall(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", answer)
    return ips[0] if ips else None

def print_dns_check(label, ip):
    print(f"{label}:")
    print(f"  Status:    {'PASS' if ip else 'FAIL'}")
    if ip:
        print(f"    IPv4:    {ip}")
    print()

def dns_test():
    domain = "google.com"

    print(f"""
========== DNS TEST ==========

Domain: {domain}""")

    # Configured DNS servers (from network_information)
    active = get_network_information()
    dns_servers = active["dns"] if active else []

    print("\nConfigured DNS Server:")
    if dns_servers:
        for server in dns_servers:
            print(f"    {server}")
    else:
        print("    Not found")
    print()

    # Resolve using the system DNS, then using Google Public DNS
    system_ip = resolve(domain)
    public_ip = resolve(domain, "8.8.8.8")

    print_dns_check("System DNS Resolution", system_ip)
    print_dns_check("Google Public DNS (8.8.8.8)", public_ip)

    system_ok = system_ip is not None
    public_ok = public_ip is not None

    if system_ok and public_ok:
        print("DNS Status:    PASS")
        return

    print("DNS Status:    FAIL")

    # Work out what kind of problem it is
    internet_ok = ping("8.8.8.8")

    print(f"""
Internet IP connectivity: {'PASS' if internet_ok else 'FAIL'}
              System DNS: {'PASS' if system_ok else 'FAIL'}
              Public DNS: {'PASS' if public_ok else 'FAIL'}
""")

    if not internet_ok:
        print("""No internet connectivity. Fix the connection first (run the Connectivity Test),
because DNS cannot be judged until the internet is reachable.""")
    elif not system_ok and public_ok:
        print("""Possible DNS configuration/resolver issue. The internet works and Google DNS
answers, but your configured DNS server does not.""")
    elif system_ok and not public_ok:
        print("""System DNS works, but Google Public DNS is not reachable. A firewall or network
policy may be blocking outside DNS servers. This is usually harmless.""")
    else:
        print("""Internet works, but both DNS lookups failed. DNS resolution failed through 
        both configured and public resolvers. Possible causes include DNS connectivity, 
        filtering/firewall policy, resolver availability, or an invalid domain.""")
    print()

#################  5 : Full Diagnostic   ############################

def get_os_name():
    """Return 'Windows 11' or 'Windows 10' correctly (platform.release() says 10 on both)."""
    system = platform.system()
    if system != "Windows":
        return system

    release = platform.release()
    try:
        build = int(platform.version().split(".")[-1])
    except ValueError:
        build = 0

    if release == "10" and build >= 22000:
        return "Windows 11"
    return f"Windows {release}"


def row(label, value):
    print(f"{label + ':':<22}{value}")


def status(passed):
    return "PASS" if passed else "FAIL"


def full_diagnostic():
    domain = "goog3le.com"

    # ---------- Collect everything first ----------
    active = get_network_information()
    gateway = active["gateway"] if active else "Not found"

    gateway_ok = gateway != "Not found" and ping(gateway)
    internet_ok = ping("8.8.8.8")
    domain_ok = ping(domain)

    system_ok = resolve(domain) is not None
    public_ok = resolve(domain, "8.8.8.8") is not None

    # ---------- Print the report ----------
    print()
    print("========== FULL SYSTEM DIAGNOSTIC ==========")
    print()

    print("DEVICE")
    row("Hostname", socket.gethostname())
    row("Operating System", get_os_name())
    row("Architecture", platform.machine())
    print()

    print("NETWORK")
    if active is None:
        print("No active network connection found.")
    else:
        row("Interface", active["name"])
        row("IPv4 Address", active["ipv4"])
        row("Subnet Mask", active["subnet"])
        row("Default Gateway", active["gateway"])
        if active["dns"]:
            row("DNS Server", active["dns"][0])
            for server in active["dns"][1:]:
                print(f"{'':<22}{server}")
        else:
            row("DNS Server", "Not found")
    print()

    print("CONNECTIVITY")
    row("Local Gateway", status(gateway_ok))
    row("Internet", status(internet_ok))
    row("Domain Connectivity", status(domain_ok))
    print()

    print("DNS")
    row("System DNS", status(system_ok))
    row("Public DNS", status(public_ok))
    print()

    # ---------- Work out the overall status and likely causes ----------
    issues = []

    if active is None:
        issues.append("No active network connection found.")
    elif not gateway_ok and not internet_ok:
        issues.append("Default gateway is unreachable.")
        issues.append("Check the Wi-Fi/cable connection and the router.")
    elif not gateway_ok and internet_ok:
        issues.append("Default gateway did not respond to ping, but the internet works.")
        issues.append("The router may be blocking ping.")
    elif not internet_ok:
        issues.append("Gateway is reachable, but the external connectivity test failed.")
        issues.append("Possible causes include upstream connectivity, routing, firewall policy, or ICMP filtering.")
    else:
        # Internet works, so DNS can be judged
        if not system_ok and public_ok:
            issues.append("DNS resolution through configured resolver failed.")
            issues.append("Public DNS resolution succeeded.")
        elif system_ok and not public_ok:
            issues.append("Public DNS (8.8.8.8) could not be reached, but system DNS works.")
            issues.append("Outside DNS servers may be blocked by a firewall (usually harmless).")
        elif not system_ok and not public_ok:
            issues.append("Both system and public DNS resolution failed.")
            issues.append("Possible causes include DNS connectivity, resolver availability, firewall/filtering policy,"
                          " or an invalid domain.")
        elif not domain_ok:
            issues.append(f"{domain} resolves, but did not respond to ping.")
            issues.append("The site or a firewall may be blocking ping.")

    line = "-" * 44
    print(line)
    if issues:
        print("OVERALL STATUS:       ATTENTION REQUIRED")
        print(line)
        print()
        print("Potential issue:")
        for issue in issues:
            print(issue)
    else:
        print("OVERALL STATUS:       HEALTHY")
        print(line)
    print()


def main():
    options = {
        "1": "Device Information",
        "2": "Network Information",
        "3": "Connectivity Test",
        "4": "DNS Test",
        "5": "Full Diagnostic",
        "6": "Exit",
    }

    while True:
        show_menu()
        choice = input("Select an option: ").strip()

        if choice in options:

            if choice == "1":
                device_information()
            elif choice == "2":
                network_information()
            elif choice == "3":
                connectivity_test()
            elif choice == "4":
                dns_test()
            elif choice == "5":
                full_diagnostic()
            else:
                print("\nExiting IT Operations Diagnostic Tool...")
                break
        else:
            print("\nInvalid option. Please enter a number from 1 to 6.")
            print()


if __name__ == "__main__":
    main()