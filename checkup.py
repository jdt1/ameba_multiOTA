#!/usr/bin/env python

"""
This package can be used to check if a
specified MAC address is present on the
network using nmap. It is developed for
linux and might not work on other
operating systems.
- jdt -
"""

import nmap
import sys
import os


if os.name == 'posix':
    if os.geteuid() != 0:
        exit("Must be run with root privileges, "
             "otherwise nmap can't read the MAC-addresses.")
else:
    print(f'Operating system \'{os.name}\' not supported, '
          'this might not work.')


def is_up(cidr, addr, verbose=False):
    nm = nmap.PortScanner()
    scan = list(nm.scan(hosts=cidr, arguments='-sP -T5').items())
    meta, results = scan[0], list(scan[1][1].items())
    
    if verbose:
        stats = meta[1]['scanstats']
        elapsed = stats['elapsed']
        uphosts = stats['uphosts']
        print(f'Scanned in {elapsed} [s], found {uphosts} hosts UP.')   
    
    for ip, info in results:
        try:
            if info['addresses']['mac'] == addr:
                if verbose:
                    print('Found the device on the network.')
                    print(info)
                return True
        except KeyError:
            pass

    return False


if __name__ == '__main__':
    if len(sys.argv) < 3:
        raise ValueError(f'Usage: {sys.argv[0]} CIDR-range MAC-address')
    else:
        cidr = sys.argv[1]
        addr = sys.argv[2]
        if is_up(cidr, addr, verbose=True):
            print(f'Addres {addr} is UP')        
        else:
            print(f'Addres {addr} is DOWN')