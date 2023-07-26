#!/usr/bin/env python

import os
import sys
import pexpect
from colorama import init, Fore
from art import text2art
import argparse
import json
import getpass
import subprocess

init(autoreset=True)

sudo_password = None



home_directory = os.path.expanduser("~")

PROFILES_FILE = os.path.join(home_directory, ".VPN_Portal", "config.json")

# Create the directory path for the configuration file
config_directory = os.path.join(home_directory, ".VPN_Portal")

# Check if the directory exists, and create it if it doesn't
if not os.path.exists(config_directory):
    os.makedirs(config_directory)

# Function to load VPN profiles from the JSON file
def load_profiles():
    if os.path.exists(PROFILES_FILE):
        with open(PROFILES_FILE, "r") as f:
            return json.load(f)
    return {}

# Function to save VPN profiles to the JSON file
def save_profiles(profiles):
    with open(PROFILES_FILE, "w") as f:
        json.dump(profiles, f)

# Dictionary to store user's VPN profiles
user_vpn_profiles_dictionary = load_profiles()

# Adding user profile to the dictionary
def add_profile(profile_name, config_path):
    user_vpn_profiles_dictionary[profile_name] = config_path
    save_profiles(user_vpn_profiles_dictionary)
    print(Fore.GREEN + f"Profile '{profile_name}' added successfully.")




def connect_vpn(config_path):
    command = f"sudo openvpn {config_path}"
    child = pexpect.spawn(command)
    child.expect(".*[Pp]assword.*")  # Match "Password" or "password"
    child.sendline(sudo_password + "\n")  # Send password followed by newline

    print(Fore.YELLOW + "\nEstablishing a connection...")
    # Waiting for a response from the process
    connection_status = child.expect([pexpect.EOF, "Initialization Sequence Completed", "AUTH_FAILED", "ERROR"])
    if connection_status == 0:
        print(Fore.RED + "\nFailed to establish the VPN connection.")
        sys.exit()
    elif connection_status == 1:
        print(Fore.GREEN + "\nVPN Connected!")
    elif connection_status == 2:
        print(Fore.RED + "\nVPN authentication failed.")
        sys.exit()
    elif connection_status == 3:
        print(Fore.RED + "\nAn error occurred during the VPN connection process.")
        sys.exit()

    print(Fore.BLUE + "\nPress 'Q' and Enter to disconnect from the VPN.")

    # Wait for user input to disconnect from the VPN
    while True:
        user_input = input().strip().lower()
        if user_input == "q":
            # Terminate the VPN connection
            child.sendintr()  # Sends Ctrl+C
            child.expect(pexpect.EOF)
            sys.exit()




def main():
    parser = argparse.ArgumentParser(description="VPN Portal by RafaelB", prog="VPN_Portal.py")
    parser.add_argument("--add_profile", nargs=2, metavar=("<profile_name>", "<path_to_configuration_file>"), help="Add a custom VPN profile.")

    args = parser.parse_args()

    if args.add_profile:
        profile_name, config_path = args.add_profile
        add_profile(profile_name, config_path)
        sys.exit()

    artwork = text2art("VPN Portal")
    custom_text = "by RafaelB"
    print(Fore.BLUE + artwork + f"  {custom_text}")

    # Get the sudo password without echoing it to the terminal
    try:
        global sudo_password
        sudo_password = getpass.getpass("\nPlease enter the sudo password for your user: ")
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n\nExiting the VPN Portal.")
        sys.exit(0)

    print(Fore.BLUE + "\nYour profiles: \n")

    # Add custom profiles to the menu
    menu_profile_list = list(user_vpn_profiles_dictionary.keys())
    if menu_profile_list:
        for i, profile_name in enumerate(menu_profile_list, start=1):
            print(Fore.GREEN + f"{i} = {profile_name}")
    else:
        print(Fore.YELLOW + "No profiles found, add a custom VPN profile using: VPN_Portal.py --add_profile <profile_name> <path_to_configuration_file>")
        sys.exit()

    while True:
        try:
            # Get user input
            platform = input(Fore.YELLOW + "\nPlease enter the number or profile name of your choice: \n\n")

            selected_profile = None
            # If the input is numerical
            if platform.isdigit():
                platform_num = int(platform)
                if platform_num >= 1 and platform_num <= len(menu_profile_list):
                    selected_profile = menu_profile_list[platform_num - 1]
            # If the input is a string
            else:
                lowercased_input = platform.lower()
                for profile_name in user_vpn_profiles_dictionary:
                    if profile_name.lower() == lowercased_input:
                        selected_profile = profile_name

            if selected_profile:
                config_path = user_vpn_profiles_dictionary.get(selected_profile)
                if config_path:
                    connect_vpn(config_path)
                else:
                    print(Fore.RED + f"\nProfile '{selected_profile}' not found. Please add it using '--add_profile'.")
            else:
                print(Fore.RED + "\nInvalid choice. Please select a valid custom profile.")
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\n\nExiting the VPN Portal.")
            sys.exit(0)
        except ValueError:
            print(Fore.RED + "Invalid choice. Please select a valid custom profile.")

if __name__ == "__main__":
    main()
