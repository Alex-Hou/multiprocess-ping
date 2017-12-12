#!/usr/bin/env python3
import argparse
import os
from functools import partial
from ipaddress import ip_network
from multiprocessing import Pool
from subprocess import STDOUT, DEVNULL, call

PROG_ARGS = [
    {
        'name_of_flags': ['-c', '--count'],
        'default': 2,
        'help': ('Stop after sending (and receiving) count ECHO_RESPONSE '
                 'packets.'),
        'type': int,
    },
    {
        'name_of_flags': ['-W', '--waittime'],
        'default': 100,
        'help': ('Time in milliseconds to wait for a reply for each packet '
                 'sent.'),
    },
    {
        'name_of_flags': ['-p', '--process'],
        'default': os.cpu_count() or 2,
        'help': 'Number of processes running ping.',
        'type': int,
    },
    {
        'name_of_flags': ['iprange'],
        'help': 'IP addresses to ping. Use CIDR format like 192.168.0.0/24',
    }
]


def ping(ip, count, wait='100'):
    return ip, call(['ping', '-c', str(count), '-W', str(wait), str(ip)],
                    stdout=DEVNULL, stderr=STDOUT)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for arg in PROG_ARGS:
        parser.add_argument(
            *arg.pop('name_of_flags'),
            **arg
        )
    args = parser.parse_args()
    ipaddr_args = ip_network(args.iprange)
    partial_ping = partial(ping, count=args.count, wait=args.waittime)
    with Pool(args.process) as p:
        result = p.map(partial_ping, ipaddr_args)
    for r in result:
        print('{}\t{}'.format(r[0], 'Y' if r[1] == 0 else 'N'))
