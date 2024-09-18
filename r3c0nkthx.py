#!/usr/bin/python3
# r3c0nkthx v1.0.0
# Author: Richard Hyunho Im (@richeeta)
# Description: 
# A recon tool designed for bug bounty hunters and security researchers to quickly assess 
# a domain's presence in the Wayback Machine (archived URLs) and to check the current 
# HTTP status of a domain via curl. It supports multiple input formats including text files, 
# single domains, and comma-separated domain lists. The tool includes options for proxy usage, 
# verbosity levels for detailed output, and the ability to save results to an output file. 
#
# Common Use Cases:
# - Quickly identifying how many URLs Wayback Machine has for a given domain
# - Checking HTTP status codes of multiple domains at scale
#
# Usage: 
# python r3c0nkthx.py <input>
# 
# <input>: A file with domains (one per line), a single domain, or a comma-separated list of domains
#
# Options:
# -v        : Enable verbose output (prints Wayback URLs and HTTP responses)
# -vv       : Enable extra verbose output (for future extensibility)
# --proxy   : Specify a proxy to route curl requests through
# -o <file> : Save the output to a specified file
#
# Examples:
# python r3c0nkthx.py domains.txt                 # Process a file with domains
# python r3c0nkthx.py example.com                 # Process a single domain
# python r3c0nkthx.py "example.com,example.org"   # Process multiple domains (comma-separated)
# python r3c0nkthx.py example.com --proxy http://IP:port
# python r3c0nkthx.py domains.txt -o output.txt   # Save output to a file
# python r3c0nkthx.py example.com -v              # Enable verbose output
# python r3c0nkthx.py example.com -vv             # Enable extra verbose output
#

import sys
import subprocess
import argparse
import os
from tqdm import tqdm
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed

# Helper to check and install missing tools
def check_and_install_tool(tool_name, install_command=None):
    """Check if a tool is installed, otherwise prompt for installation."""
    if shutil.which(tool_name) is None:
        print(f"{tool_name} is not installed.")
        if install_command:
            try:
                print(f"Attempting to install {tool_name}...")
                subprocess.check_call(install_command, shell=True)
                print(f"{tool_name} installed successfully.")
            except subprocess.CalledProcessError as e:
                print(f"Failed to install {tool_name}: {e}")
                sys.exit(1)
        else:
            print(f"Please install {tool_name} manually and try again.")
            sys.exit(1)

# Function to install missing Python packages
def install_missing_packages():
    try:
        import tqdm
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tqdm"])

# Ensure that `waybackurls` and `curl` are installed
def ensure_dependencies():
    # Check if 'curl' and 'waybackurls' are installed, else prompt for installation
    check_and_install_tool('curl')
    check_and_install_tool('waybackurls', install_command="go install github.com/tomnomnom/waybackurls@latest")

# Function to check Wayback URLs for a domain
def check_wayback_urls(domain, verbose=False):
    try:
        result = subprocess.run(['waybackurls', domain], capture_output=True, text=True)
        urls = result.stdout.strip().split('\n')
        if verbose:
            for url in urls:
                print(f"Wayback URL: {url}")
        return urls
    except Exception as e:
        print(f"Error running waybackurls for {domain}: {e}")
        return []

# Function to check HTTP response using curl
def check_http_response(domain, proxy=None, verbose=False):
    curl_cmd = ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', domain]
    if proxy:
        curl_cmd.extend(['--proxy', proxy])
    try:
        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        if verbose:
            print(f"HTTP response: {result.stdout}")
        return int(result.stdout.strip())
    except Exception as e:
        print(f"Error running curl for {domain}: {e}")
        return None

# Function to print results with colored output
def print_colored_output(domain, wayback_count, http_status, interesting_directories):
    """Prints the result for each domain with colored output."""
    bold_domain = f"\033[1m{domain}\033[0m"

    # Wayback URL coloring
    if 5 <= wayback_count <= 9999:
        wayback_color = f"\033[92m{wayback_count}\033[0m"  # Green
    else:
        wayback_color = f"{wayback_count}"

    # HTTP status coloring
    if http_status == 200:
        http_color = f"\033[92m{http_status}\033[0m"  # Green
    elif http_status in [301, 302, 404]:
        http_color = f"\033[93m{http_status}\033[0m"  # Orange/Yellow
    elif http_status in [400, 401, 403, 503]:
        http_color = f"\033[91m{http_status}\033[0m"  # Red
    else:
        http_color = f"{http_status}"

    # Print the main result
    print(f"{bold_domain} | Wayback URLs: {wayback_color} | HTTP Status Code: {http_color}")

    # Print interesting directories or parameters
    print("Wayback URLs with Interesting Directories or Parameters:")
    for key, value in interesting_directories.items():
        if value > 0:
            print(f" - {key} URLs: [{value}]")
    
    sys.stdout.flush()

# Function to find interesting URLs
def find_interesting_urls(urls):
    patterns = {
        "/api/": 0,
        "/admin/": 0,
        "/js/": 0,
        "/account/": 0,
        "/cgi-bin/": 0,
        "/wp-admin/": 0,
        "response_type=token": 0,
        "password=": 0,
        "isAdmin=": 0
    }

    for url in urls:
        for pattern in patterns.keys():
            if pattern in url:
                patterns[pattern] += 1
    
    return patterns

# Main function to handle different input formats
def process_domain(domain, proxy=None, verbose=False, output_file=None):
    wayback_urls = check_wayback_urls(domain, verbose=verbose)
    http_status = check_http_response(domain, proxy=proxy, verbose=verbose)
    interesting_directories = find_interesting_urls(wayback_urls)

    if output_file:
        with open(output_file, 'a') as f:
            f.write(f"{domain} | Wayback URLs: {len(wayback_urls)} | HTTP Status Code: {http_status}\n")
            for key, value in interesting_directories.items():
                if value > 0:
                    f.write(f" - {key} URLs: [{value}]\n")

    print_colored_output(domain, len(wayback_urls), http_status, interesting_directories)

def process_input(input_data, proxy=None, verbose=False, output_file=None):
    # Process domain names
    if ',' in input_data:
        domains = [domain.strip() for domain in input_data.split(',')]
    else:
        try:
            with open(input_data, 'r') as file:
                domains = [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            domains = [input_data.strip()]

    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(process_domain, domain, proxy, verbose, output_file): domain for domain in domains}
        for future in tqdm(as_completed(futures), total=len(domains), desc="Processing domains"):
            future.result()

# Command-line argument parsing
def parse_arguments():
    parser = argparse.ArgumentParser(description="Recon Tool for checking Wayback URLs and HTTP status codes.")
    parser.add_argument('input', help="Input: a file containing domains or a single domain or comma-separated domains")
    parser.add_argument('-o', '--output', help="Output file to save results", default=None)
    parser.add_argument('--proxy', help="Specify proxy for curl requests", default=None)
    parser.add_argument('-v', action='store_true', help="Verbose output")
    parser.add_argument('-vv', action='store_true', help="Extra verbose output")
    return parser.parse_args()

if __name__ == "__main__":
    # Install required dependencies
    install_missing_packages()
    ensure_dependencies()

    # Parse command-line arguments
    args = parse_arguments()

    # Process input
    process_input(args.input, proxy=args.proxy, verbose=args.v or args.vv, output_file=args.output)
