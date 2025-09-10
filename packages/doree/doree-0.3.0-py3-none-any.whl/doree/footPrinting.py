def footPrinting():
    return [
        """
        2. Foot printing Tools -recon-ng, Dmitry, netdiscover, nmap.
        """,
        """recon-ng commands""",
        """What is recon-ng?
        It’s a reconnaissance (information gathering) framework with a console interface similar to
        Metasploit.
        It automates gathering info like hosts, emails, subdomains from the internet.
        
        Commands explained
        ➡ Open recon-ng
                ➢ recon-ng
            • Starts the recon-ng console. You get a prompt similar to recon-ng .
        
        ➡ Install marketplace modules
            ➢ marketplace install recon/domains-hosts/netcraft
            ➢ marketplace install recon/hosts-hosts/resolve
            ➢ marketplace install recon/domains-hosts/hackertarget
            ➢ marketplace install recon/domains-contacts/whois_pocs
        • Downloads & installs extra modules from the recon-ng repository so you can use them later.
        • Each module is like a plugin for specific tasks (finding hosts, emails, whois data).    
        """,
        """
        ➡ Using Netcraft module
            ➢ modules load recon/domains-hosts/netcraft
            ➢ info
            ➢ options set SOURCE google.com
            ➢ run
        • modules load recon/domains-hosts/netcraft — Loads the Netcraft module which collects
        hosts for a given domain using Netcraft data.
        • info — Shows info about the loaded module (author, what it does, options it needs).
        • options set SOURCE google.com — Sets the domain you want to scan (target).
        • run — Executes the module, starts gathering data
        """,
        """
        ➡ Using Resolve module
            ➢ modules load recon/hosts-hosts/resolve
            ➢ info
            ➢ options set SOURCE facebook.com
            ➢ run
        • This module resolves hostnames to IP addresses.
        • The same info, options set, run pattern applies.
        """,
        """
        ➡ Using Hackertarget module
            ➢ modules load recon/domains-hosts/hackertarget
            ➢ info
            ➢ options set SOURCE facebook.com
            ➢ run
        • Uses HackerTarget API to find hosts and subdomains linked to the target domain.
        """,
        """
        ➡ Using whois_pocs module
            ➢ modules load recon/domains-contacts/whois_pocs
            ➢ info
            ➢ options set SOURCE facebook.com
            ➢ run
        • Finds whois "point of contact" emails or admin names for the target domain.
        """,
        """ """,
        """ 
         B. nmap commands
        """,
        """
         What is nmap?
        Nmap (Network Mapper) is a command-line tool to scan IP addresses or networks.
        It tells you which hosts are live, which ports are open, what services & versions they’re running,
        and sometimes the OS.
        Commands explained
        ➡ Simple scan with URL
            ➢ nmap www.gmail.com
        • Looks up the IP of www.gmail.com and does a default port scan (top 1000 ports).
        • Lists open ports & services.
        """,
        """
        ➡ Detect Operating System
            ➢ nmap -O <ipaddress>
        ➢ To know the ip address use command: ifconfig
        • -O tries to guess the operating system based on TCP/IP fingerprints.
        • Useful to know if target runs Windows, Linux, etc.
        """,
        """
        ➡ Check a single port
            ➢ nmap -p 80 <ipaddress>
        • -p 80 restricts the scan to only port 80 (HTTP).
        • Quickly checks if the web server port is open.
        """,
        """
        ➡ Check multiple specific ports
            ➢ nmap -p 21,80,8080 <ipaddress>
        • -p 21,80,8080 tells nmap to check FTP (21), HTTP (80), alternative HTTP (8080).
        """,
        """
        ➡ Scan all 65535 ports
            ➢ nmap -p- <ipaddress>
        • -p- means scan all ports from 1 to 65535.
        • Very thorough but slower.
        """,
        """
        ➡ Find live hosts in network
            ➢ nmap -sn <ipaddress>
        • -sn disables port scanning, only does a ping sweep to see which hosts respond.
        • Used for network discovery.
        """,
        """
        ➡ Scan for firewalls (ACK scan)
            ➢ nmap -sA <ipaddress>
        • -sA sends ACK packets to map firewall rules.
        • Used to see if a firewall is filtering ports (detects if stateful firewall is present).
        """,
        """""",
        """ C. Dmitry commands""",
        """
         What is dmitry?
        Dmitry (Deepmagic Information Gathering Tool) is a CLI tool that collects information like IP address,
        whois, subdomains, emails, and scans ports.
        Command explained
            ➢ dmitry -winsepo google.com
        • Options:
            // do not press that 0 idiot
            o -w does whois lookup.
            o -i gets target IP address.
            o -n gets Netcraft info.
            o -s searches for subdomains.
            o -e looks for email addresses.
            o -p scans TCP ports.
            o -o writes all output to a file (needs filename).
        Example to save to file:
        ➢ dmitry -winsepo google.com -o result.txt
        • Saves the entire output to result.txt.
        """,
        """ """,
        """ D. netdiscover commands """,
        """
        What is netdiscover?
        Netdiscover is a tool that performs ARP scanning to find live hosts on a local network — showing
        their IP and MAC addresses.
        
        Commands explained
        ➡ Simple scan
            ➢ netdiscover
        • Starts scanning on the default interface, looks for nearby live hosts.
        """,
        """
        ➡ Scan specific subnet
            ➢ netdiscover -r 192.168.153.0/16
        • -r specifies a network range to scan.
        • Here /16 means scan all IPs from 192.168.0.0 to 192.168.255.255.
        """
    ]