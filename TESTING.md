# IT Operations Diagnostic Tool: Development Testing Log

**Tester: Prosnape270
**Date: 06/10/2026
**Environment: Windows 11, Python 3.14.0

##########################    ITERATION    ##########################

## Iteration 1: Main Menu
**Change:** Menu shows 6 options; each prints "<name> CLICKED"
**Expected:** Menu displays correctly; options 1-5 print CLICKED; 6 exits
**Actual:** Menu layout matches the requested design. Options 1-5 print their CLICKED message and the menu returns. Option 6 prints a goodbye message and exits.
**Result:** PASS

## Iteration 2: Device Information
**Change:** Option 1 shows hostname, OS, version, architecture, processor
**Expected:** Values match Settings > System > About
**Actual:** Uses `socket` and `platform`, so values come directly from the system. Note: `platform.version()` shows the build number (e.g. 10.0.22631), not "Windows 11".
**Result:** PASS

## Iteration 3: Network Information (first version)
**Change:** Option 2 reads `ipconfig /all` and shows IPv4, subnet, gateway, DNS
**Expected:** Values match what `ipconfig /all` shows
**Actual:** Values matched, but the Interface line always showed "Wi-Fi" because it was hardcoded, even on an Ethernet connection
**Result:** FAIL (fixed in Iteration 4)
**Issue found:** Interface name was hardcoded as "Wi-Fi"

## Iteration 4: Real Interface Name
**Change:** Interface name is read from the adapter header
**Expected:** Shows "Wi-Fi" on wireless and "Ethernet" on a cable connection
**Actual:** Name is taken from the header line (e.g. "Wireless LAN adapter Wi-Fi:"), so it no longer depends on the word "Wi-Fi". Adapters named differently (WLAN, Ethernet 2) are also handled.
**Result:** PASS (confirm on both Wi-Fi and Ethernet)

## Iteration 5: Active Adapter Detection
**Change:** Adapter is chosen by the IP Windows uses to reach the internet
**Expected:** With Ethernet, Wi-Fi and Bluetooth connected, the shown adapter matches `route print -4`
**Actual:** The first version picked the first adapter in the `ipconfig` list that had an IP and gateway. That is list order, not the real route, so it could pick the wrong adapter. It was replaced by `get_active_ip()`, which asks Windows which local IP it would use to reach 8.8.8.8 and matches it to an adapter.
**Result:** FAIL (fixed) for the first version. PASS for the final version.
**Issue found:** Adapter choice depended on list order

## Iteration 6: Multiple DNS Servers
**Change:** `"dns"` stored as a list
**Expected:** Two or more DNS servers are all displayed
**Actual:** The first version stored a single DNS value, so extra servers were lost. It now stores a list, and all servers appear, aligned under the first. Key lines are detected with `. :` so IPv6 DNS addresses on continuation lines are not misread as new fields.
**Result:** FAIL (fixed) for the first version. PASS for the final version.
**Issue found:** Only one DNS server was stored

## Iteration 7: Connectivity Test
**Change:** Option 3 pings gateway, 8.8.8.8 and google.com
**Expected:** All PASS normally; FAIL shown for any unreachable target; Overall matches
**Actual:** Each check sends one ping and counts as PASS only if `TTL=` is in the reply, so "Destination host unreachable" is not counted as success. Overall is PASS only if all three pass. Limitation: a router that blocks ping would show FAIL.
**Result:** PASS

## Iteration 8: Merged Network Function
**Change:** `get_active_adapter()` merged into `network_information(show=...)`
**Expected:** Option 2 still prints its screen; option 3 still works
**Actual:** The two similar functions became one with a `show` option, and `connectivity_test()` was updated to use `show=False`. This design made one function responsible for two jobs, which led to Iteration 10.
**Result:** PASS

## Iteration 9: DNS Test
**Change:** Option 4 tests system DNS and Google DNS (8.8.8.8) and diagnoses failures
**Expected:** Normal: DNS Status PASS. Broken DNS config: "Possible DNS configuration/resolver issue"
**Actual:** Uses `nslookup` for both the system DNS and 8.8.8.8, reading only the part after `Name:` so the DNS server's own address is not mistaken for the answer. On failure it pings 8.8.8.8 and shows a diagnosis for each combination of results.
**Result:** PASS for normal case. PASS for broken DNS.

## Iteration 10: Split Data and Display
**Change:** `get_network_information()` returns data; `network_information()` only prints
**Expected:** Option 3 does NOT print the Network Information screen; option 2 still does
**Actual:** Before the fix, option 3 printed the Network Information screen because an old `network_information()` call was still in `connectivity_test()`. After changing it to `get_network_information()
**Result:** PASS
**Issue found:** Option 3 printing the Network Information screen (caused by an old `network_information()` call left in the file)

## Iteration 11: Scenario Testing
**Change:** Tested the completed diagnostic tool under normal and failure scenarios.
**Expected:** The program should handle each scenario without crashing or producing a traceback, while reporting results that match the observed network condition.
**Actual:**
- **Normal connection:** Device and network information were detected correctly. Gateway, Internet, domain connectivity, system DNS, and public DNS all returned PASS. Full Diagnostic reported `HEALTHY`.
- **Network disconnected:** No active network connection was detected. Gateway, Internet, domain connectivity, system DNS, and public DNS returned FAIL. Full Diagnostic reported `ATTENTION REQUIRED` with "No active network connection found." The program continued running without crashing.
- **Invalid domain:** Local gateway and Internet connectivity remained PASS, while domain connectivity, system DNS, and public DNS returned FAIL. Full Diagnostic reported `ATTENTION REQUIRED` and identified DNS resolution failure or an invalid domain as possible causes.
- **Invalid menu input:** Values outside options 1–6 displayed an error message and returned the user to the main menu without crashing.
**Result:** PASS


##########################    SUMMARY    ##########################


| Iteration | Result |
|---|---|
| 1. Main Menu | PASS |
| 2. Device Information | PASS |
| 3. Network Information (first version) | FAIL (fixed) |
| 4. Real Interface Name | PASS |
| 5. Active Adapter Detection | FAIL (fixed), final |
| 6. Multiple DNS Servers | FAIL (fixed), final  |
| 7. Connectivity Test | PASS |
| 8. Merged Network Function | PASS |
| 9. DNS Test | PASS normal, FAIL (fixed) DNS |
| 10. Split Data and Display | FAIL (fixed) |
| 11. Scenario Testing | PASS |

**Issues found:**
1. Interface name hardcoded as "Wi-Fi" (Iteration 3)
2. Active adapter chosen by list order, not by the real route (Iteration 5)
3. Only one DNS server stored (Iteration 6)
4. Option 3 printed the Network Information screen (Iteration 10)

**Fixes made:**
1. Read the adapter name from the `ipconfig` header
2. Match the adapter to the IP Windows uses to reach the internet
3. Store DNS servers as a list
4. Split data collection from display

**Known limitations:**
- English Windows only (labels like "IPv4 Address" and "Name:" are matched in English)
- Routers that block ping show FAIL for the gateway
- Only the first IPv4 address of a domain is shown
- Only the first gateway is stored

**Completed and verified on the V1.0 machine:** Ethernet and Wi-Fi together (Iteration 5), a second DNS server (Iteration 6), a deliberately broken DNS setting (Iteration 9), and an invalid domain (Iteration 11).
