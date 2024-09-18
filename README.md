# r3c0nkthx 

**A Recon Tool for Bug Bounty Hunters and Security Researchers**

Meet `r3c0nkthx`: your trusty sidekick to streamline reconnaissance for large-scope engagements to help you zero in on active targets and potential areas of interest by searching the Wayback Machine and checking each target's current HTTP status.

## Features

* Processes multiple input formats: text files, single domains, and comma-separated domain lists
* Checks domain presence in the Wayback Machine
* Verifies current HTTP status of domains
* Identifies interesting URL patterns (e.g., API endpoints, admin pages)
* Supports proxy usage for requests
* Provides verbose output options
* Saves results to an output file
* Uses multi-threading for improved performance

## Installation
1. **Prerequisites:** Ensure you have `curl` and `go` installed.
2. **Install waybackurls:** 
   ```bash
   go install github.com/tomnomnom/waybackurls@latest
   ```
3. Install r3c0nkthx:
   ```Bash
   pip3 install tqdm  # If you don't already have it
   git clone https://github.com/richeeta/r3c0nkthx.git
   cd r3c0nkthx
   ```
     
# Usage
```Bash
python3 r3c0nkthx.py <input> [options]
```
`<input>`:
* A file with domains (one per line)
* A single domain (e.g., `example.com`)
* A comma-separated list of domains (e.g., "`example.com,example.org`")

# When to Use
Picture this: you've stumbled across a new bug bounty program. Excitedly, you run `subdomain -d n3wb0unty.com`, only to get a list longer than a Walmart receipt. 
How do you efficiently sift through them all?

`r3c0nkthx`! It takes your huge, overwhelming list of subdomains and:
* Checks which subdomains have a presence in the Wayback Machine, uncovering potentially forgotten endpoints.
* Verifies the current HTTP status of each domain, identifying live targets.
* Highlights interesting URL patterns that might warrant further investigation.

Instead of manually `gobuster`ing each subdomain one-by-one, you can now refocus your energy on the most promising leads!

# Options
* `-v`: Enable verbose output (prints Wayback URLs and HTTP responses)
* `-vv`: Enable extra verbose output (for future extensibility)
* `--proxy`: Specify a proxy (e.g., `http://proxy:port`)
* `-o <file>`: Save output to a file

# Examples
```bash
python r3c0nkthx.py domains.txt                                 # Process a file with domains and/or subdomains
python r3c0nkthx.py google-analytics.com                        # Process a single domain
python r3c0nkthx.py "id.apple.com,beta.icloud.com,nytimes.com"  # Process multiple domains and subdomains
python r3c0nkthx.py example.com --proxy http://127.0.0.1:8080   # Proxy through Burp
python r3c0nkthx.py domains.txt -o output.txt                   # Save output to a file
python r3c0nkthx.py example.com -v                              # Enable verbose output
```

### Example Output
```bash
┌──(richie㉿kali)-[~]
└─$ python3 r3c0nkthx.py google.com,google.org
google.com | Wayback URLs: 12514 | HTTP Status Code: 301
Wayback URLs with Interesting Directories or Parameters:
 - /admin/ URLs: [6444]
google.org | Wayback URLs: 414037 | HTTP Status Code: 302
Wayback URLs with Interesting Directories or Parameters:
 - /api/ URLs: [81]
 - /js/ URLs: [265]
 - /account/ URLs: [1]
 - /cgi-bin/ URLs: [9]
 - /wp-admin/ URLs: [2]
```

# Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

# License
This project is licensed under the MIT License — see the LICENSE file for details.   

# Disclaimer
This tool is intended for use in authorized security testing and bug bounty programs. Always ensure you have permission before testing any systems you do not own. I'm not responsible for any misuse or damage caused by this tool.
