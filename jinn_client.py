import os
import sys
import subprocess
import hashlib
import time
import base64
import requests
import platform
import json

# Placeholder for string obfuscation
def decode_string(encoded_str):
    """
    Decodes a base64 encoded string.
    This is a basic obfuscation technique.
    """
    try:
        return base64.b64decode(encoded_str).decode('utf-8')
    except Exception:
        return encoded_str

def encode_string(plain_str):
    """
    Helper to encode strings during development.
    """
    return base64.b64encode(plain_str.encode('utf-8')).decode('utf-8')

# Security Check
def check_security():
    """
    Checks for packet capture tools and other security threats.
    """
    blacklisted_apps = [
        "tcpdump", "wireshark", "tshark", "httpcanary",
        "org.kunge.tcpdump", "app.greyshirts.sslcapture"
    ]

    # Check running processes
    try:
        # ps -A for Linux/Android
        output = subprocess.check_output(["ps", "-A"], stderr=subprocess.DEVNULL).decode('utf-8').lower()

        for app in blacklisted_apps:
            if app in output:
                # Obfuscated message: "Security Violation Detected: " + app
                msg = decode_string("U2VjdXJpdHkgVmlvbGF0aW9uIERldGVjdGVkOiA=") + app
                print(msg)
                sys.exit(1)

    except Exception as e:
        # If ps fails (e.g. permission denied), we might continue or strict exit.
        # For robustness, we continue but could log/warn.
        pass

def get_permanent_hwid():
    """
    Generates a robust, permanent HWID based on device hardware info.
    """
    hw_info = ""

    # 1. Android ID
    try:
        # settings get secure android_id
        android_id = subprocess.check_output(
            ["settings", "get", "secure", "android_id"],
            stderr=subprocess.DEVNULL
        ).decode('utf-8').strip()
        hw_info += android_id
    except Exception:
        pass

    # 2. CPU Serial
    try:
        # getprop ro.serialno
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

    # Fallback for non-Android (Linux sandbox or PC)
    if not hw_info:
        try:
            # Machine ID on Linux
            with open('/etc/machine-id', 'r') as f:
                hw_info += f.read().strip()
        except Exception:
            pass

        # Or generic platform info
        hw_info += platform.node() + platform.machine() + platform.processor()

    # Hash the info to create a short unique Device ID
    hwid_hash = hashlib.sha256(hw_info.encode('utf-8')).hexdigest()

    # Return a formatted string, e.g., first 16 chars
    return hwid_hash[:16].upper()

def print_logo():
    logo = r"""
       _ _____ _   _ _   _
      | |_   _| \ | | \ | |
      | | | | |  \| |  \| |
  _   | | | | | . ` | . ` |
 | |__| |_| |_| |\  | |\  |
  \____/|_____|_| \_|_| \_|

    """
    print(logo)

def client_main():
    """
    The main functionality of the tool to be executed after approval.
    """
    # Placeholder for user logic
    print("Executing Main Tool Logic...")

def main():
    # 1. Clear Screen & Show Logo
    os.system('cls' if os.name == 'nt' else 'clear')
    print_logo()

    # 2. Security Check
    check_security()

    # 3. HWID & Key Generation
    hwid = get_permanent_hwid()
    # Format: JINN-XXXX-HWID (using first 4 chars of HWID as the 'XXXX' for uniqueness)
    user_key = f"JINN-{hwid[:4]}-{hwid}"

    print(f"User Key: {user_key}")
    print("Checking Approval...")

    # 4. Server Communication
    # Placeholder URL - encoded to obfuscate
    # "https://example.com/api/check_approval"
    server_url_encoded = "aHR0cHM6Ly9leGFtcGxlLmNvbS9hcGkvY2hlY2tfYXBwcm92YWw="
    server_url = decode_string(server_url_encoded)

    approved = False
    time_remaining = ""

    try:
        # Send Key+HWID to Server
        response = requests.post(
            server_url,
            data={'key': user_key, 'hwid': hwid},
            verify=True, # SSL Verification
            timeout=5
        )

        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'approved':
                approved = True
                time_remaining = data.get('time_remaining', 'Unknown')

    except requests.RequestException:
        # Server error or unreachable implies not approved or offline
        pass

    # 5. Logic Branch
    if approved:
        print("\nApproval Successful")
        print(f"Time Remaining: {time_remaining}")
        print("Assalam o Alaikum ho gaya approval")

        # Execute main logic
        client_main()

    else:
        # Not Approved Flow
        os.system('cls' if os.name == 'nt' else 'clear')
        print_logo()

        msg = decode_string("WW91ciBLZXkgaXMgTk9UIEFwcHJvdmVk") # "Your Key is NOT Approved"
        print(f"\n{msg}\n")

        print("Payment Methods:")
        print("-" * 30)
        # "EasyPaisa: 03189713740"
        print(decode_string("RWFzeVBhaXNhOiAwMzE4OTcxMzc0MA=="))
        # "Binance ID: 936186916"
        print(decode_string("QmluYW5jZSBJRDogOTM2MTg2OTE2"))
        print("-" * 30)

        print("\nPricing Table:")
        print("Pakistan: Week=150 | 15 Days=280 | 30 Days=550 PKR")
        print("Global:   Week=$1.5 | 15 Days=$3 | 30 Days=$5 USD")

        input("\nPress Enter to exit...")
        sys.exit()

if __name__ == "__main__":
    main()
