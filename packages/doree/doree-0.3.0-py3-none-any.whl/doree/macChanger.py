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