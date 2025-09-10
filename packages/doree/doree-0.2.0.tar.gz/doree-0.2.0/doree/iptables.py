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