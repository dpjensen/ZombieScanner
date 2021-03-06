"""
zombie scanner
Launcher script
"""


import argparse
import operator
from libs.ICMPSession import ICMPSession
from libs.TCPSession import TCPSession
from libs.helpers import check_ipv4


def get_status(scans):
    """
    Looks for more than one response, to compensate for packet loss
    """
    stat_list = scans.get_header_item_list("status")
    stat_dict = {"open": 0, "closed": 0, "filtered": 0}


    for status in stat_list:
        if status == "open":
            stat_dict["open"] += 1
        elif status == "closed":
            stat_dict["closed"] += 1
        elif status == "filtered":
            stat_dict["filtered"] += 1

    #return the most common packet status type
    return max(stat_dict.iteritems(), key=operator.itemgetter(1))[0]


def main():
    """
    Main method for our launcher
    """
    parser = argparse.ArgumentParser(description='Get IP, port and other options')
    parser.add_argument('dest', help="the IP adress to  ping")
    parser.add_argument('port', nargs='?', default=80, type=int, help="remote host port number")
    parser.add_argument("-v", "--verbose", help="print more TCP/ICMP data", action="store_true")

    #more compact vars for cmd ln args
    args = parser.parse_args()
    addr = args.dest
    port = args.port
    verb = args.verbose
    ping_nums = 5


    if check_ipv4(addr):
        print ''
        print '#### zombie scanner - IP/TCP header data collection ####'
        print ''
        #------ICMP scanning------
        pings = ICMPSession(addr)
        pings.start_ping(ping_nums)

        #------TCP scanning------
        #list of 5 ports
        port_list = [port] * ping_nums
        scans = TCPSession(addr)
        scans.scan_addr_at_port(port_list)
        port_status = get_status(scans)

        #print status of port
        if port_status == "filtered":
            print'data for host: {}, TCP port: {} is filtered'.format(addr, port)
        elif port_status == "open":
            print 'data for host: {}, TCP port: {} is open'.format(addr, port)
        else:
            print 'data for host: {}, TCP port: {} is closed'.format(addr, port)

        #prints lists of data from host
        pings.print_stats()
        print 'avg delay={}ms'.format(pings.delay())
        print 'icmp ipid={}'.format(pings.get_header_item_list("IPID"))
        print 'tcp ipid={}'.format(scans.get_header_item_list("IPID"))



        if verb:
            print ''
            print 'ack numbers={}'.format(scans.get_header_item_list("ack"))
            print "Data from last ICMP packet:"
            print pings.print_dict()

        print ''
    else:
        print 'invalid IPv4 addr'


if __name__ == '__main__':
    main()
