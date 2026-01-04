import os
import sys
import subprocess
import hashlib
import time
import base64
import platform
import requests
from termcolor import colored

# --- Constants ---
SERVER_URL = "https://Jinnapvsetup.pythonanywhere.com/validate"

# --- Security & Obfuscation ---

def check_security():
    """
    Checks for packet capture tools (HTTP Debugger, Canary, Wireshark, etc.)
    and exits if found.
    """
    blacklisted_apps = [
        "tcpdump", "wireshark", "tshark", "httpcanary",
        "org.kunge.tcpdump", "app.greyshirts.sslcapture",
        "com.guoshi.httpcanary" # Added package name for HTTP Canary
    ]

    # Check running processes
    try:
        # ps -A for Linux/Android
        output = subprocess.check_output(["ps", "-A"], stderr=subprocess.DEVNULL).decode('utf-8').lower()

        for app in blacklisted_apps:
            if app in output:
                print(colored(f"[!] Security Violation Detected: {app}", "red", attrs=["bold"]))
                sys.exit(1)

    except Exception:
        # If ps fails, we might be in a restricted env.
        # For this implementation, we proceed, but in a real high-sec scenario, we might exit.
        pass

# --- Hardware ID Generation ---

def get_hwid():
    """
    Generates a unique, permanent device ID based on hardware (CPU/Motherboard).
    """
    hw_info = ""

    # 1. Android ID (termux/android specific)
    try:
        android_id = subprocess.check_output(
            ["settings", "get", "secure", "android_id"],
            stderr=subprocess.DEVNULL
        ).decode('utf-8').strip()
        hw_info += android_id
    except Exception:
        pass

    # 2. CPU Serial
    try:
        cpu_serial = subprocess.check_output(
            ["getprop", "ro.serialno"],
            stderr=subprocess.DEVNULL
        ).decode('utf-8').strip()
        hw_info += cpu_serial
    except Exception:
        # Fallback to reading /proc/cpuinfo
        try:
            with open('/proc/cpuinfo', 'r') as f:
                content = f.read()
                for line in content.splitlines():
                    if 'Serial' in line:
                        hw_info += line.split(':')[-1].strip()
                        break
        except Exception:
            pass

    # 3. Manufacturer
    try:
        manufacturer = subprocess.check_output(
            ["getprop", "ro.product.manufacturer"],
            stderr=subprocess.DEVNULL
        ).decode('utf-8').strip()
        hw_info += manufacturer
    except Exception:
        pass

    # Fallback for non-Android (Linux sandbox or PC) - ensures it works in testing envs
    if not hw_info:
        try:
            # Machine ID on Linux
            if os.path.exists('/etc/machine-id'):
                with open('/etc/machine-id', 'r') as f:
                    hw_info += f.read().strip()
        except Exception:
            pass

        # Or generic platform info if everything else fails
        if not hw_info:
            hw_info += platform.node() + platform.machine() + platform.processor()

    # Hash the info to create a short unique Device ID
    # We use MD5 for a shorter string or SHA256 and truncate.
    # User asked for unique ID, SHA256 is safer against collisions.
    hwid_hash = hashlib.sha256(hw_info.encode('utf-8')).hexdigest()

    # Return first 16 chars upper case
    return hwid_hash[:16].upper()

# --- UI Helper Functions ---

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_logo():
    logo = r"""
       _ _____ _   _ _   _
      | |_   _| \ | | \ | |
      | | | | |  \| |  \| |
  _   | | | | | . ` | . ` |
 | |__| |_| |_| |\  | |\  |
  \____/|_____|_| \_|_| \_|
"""
    print(colored(logo, "cyan", attrs=["bold"]))

# --- Main Logic ---

def main_tool_logic():
    """
    Placeholder for the main functionality of the tool after approval.
    """
    print(colored("\n[+] Tool initialized successfully.", "green"))
    print(colored("[+] Waiting for user command...", "yellow"))
    # In a real tool, the loop/menu would start here.
    # For now, we just wait a bit to simulate work
    time.sleep(2)

def main():
    # Security Check at Start
    check_security()

    # Step 1: Logo
    clear_screen()
    print_logo()

    # Step 2: Print HWID
    hwid = get_hwid()
    print(colored(f"Your HWID: {hwid}", "yellow", attrs=["bold"]))
    print("-" * 40)

    # Step 3: Ask for License Key
    try:
        user_key = input(colored("Enter License Key: ", "green")).strip()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit()

    if not user_key:
        print(colored("Key cannot be empty.", "red"))
        sys.exit()

    print(colored("\nValidating key, please wait...", "cyan"))

    # Step 4: Validation
    approved = False
    time_remaining = "Expired"

    try:
        payload = {"key": user_key, "hwid": hwid}
        headers = {
            "User-Agent": "JINN-Client/1.0",
            "Content-Type": "application/json"
        }

        # Securely using requests
        response = requests.post(
            SERVER_URL,
            json=payload,
            verify=True,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            # Assuming the server returns JSON like {"status": "approved", "days_left": "30"}
            # Adjusting based on common patterns since exact response structure wasn't fully detailed beyond fields.
            # Prompt implied: "Time Remaining: [Days] days"

            # Let's handle a few common keys for status
            status = data.get("status", "").lower()
            if status == "approved" or status == "success" or data.get("valid") is True:
                approved = True
                # Try to find time remaining info
                time_remaining = data.get("days_left") or data.get("time_remaining") or data.get("expiry") or "Unknown"
        else:
            # If server returns 403 or 401, it's likely invalid key
            pass

    except requests.RequestException as e:
        print(colored(f"\n[!] Server Error: {e}", "red"))
        print(colored("[!] Please check your internet connection.", "red"))
        sys.exit()
    except Exception as e:
        print(colored(f"\n[!] An error occurred: {e}", "red"))
        sys.exit()

    # Step 4 continued: Logic Branch
    if approved:
        clear_screen()
        print_logo()
        print(colored("Assalam o Alaikum! Approval Successful.", "green", attrs=["bold"]))
        print(colored(f"Time Remaining: {time_remaining} days", "blue", attrs=["bold"]))
        print("-" * 40)

        main_tool_logic()

    else:
        clear_screen()
        print_logo()
        print(colored("Your Key is Invalid or Expired.", "red", attrs=["bold", "blink"]))
        print("-" * 40)

        print(colored("Payment Details:", "yellow", attrs=["bold"]))
        print(f"EasyPaisa: {colored('03189713740', 'white', attrs=['bold'])}")
        print(f"Binance ID: {colored('936186916', 'white', attrs=['bold'])}")

        print(colored("\nPricing:", "yellow", attrs=["bold"]))
        print("Pakistan: 1 Week=150 | 15 Days=280 | 30 Days=550 PKR")
        print("Global:   1 Week=$1.5 | 15 Days=$3 | 30 Days=$5 USD")

        print("-" * 40)
        sys.exit()

if __name__ == "__main__":
    main()
