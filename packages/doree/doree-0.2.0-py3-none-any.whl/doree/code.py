from IPython.display import Javascript, display

import footPrinting
import hackWindows
import passwordCrack
import macChanger
import iptables
import phishing

def print_codes(codes):
    codes = codes[::-1]

    for code in codes:
        js_code = f'''
        var cell = Jupyter.notebook.insert_cell_below('code');
        cell.set_text(`{code}`);
        '''
        display(Javascript(js_code))


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