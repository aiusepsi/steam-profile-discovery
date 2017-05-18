#!/usr/bin/env python
# Send string

BUFSIZE = 4096
STEAM_MAGIC_1 = 0xFFFFFFFF
STEAM_MAGIC_2 = 0xA05F4C21
pack_format_hdr= "<III"
pack_format_msg = "<I"

def send_string():
    import struct
    import steammessages_remoteclient_discovery_pb2

    discovery_header = steammessages_remoteclient_discovery_pb2.CMsgRemoteClientBroadcastHeader()
    discovery_header.client_id = 42
    discovery_header.instance_id = 1

    serialized_discovery_header = discovery_header.SerializeToString()
    serialized_hdr = struct.pack(pack_format_hdr, STEAM_MAGIC_1, STEAM_MAGIC_2, len(serialized_discovery_header))


    discovery_msg = steammessages_remoteclient_discovery_pb2.CMsgRemoteClientBroadcastDiscovery()
    discovery_msg.seq_num = 1
    serialized_discovery = discovery_msg.SerializeToString()
    serialized_msg = struct.pack(pack_format_msg, len(serialized_discovery))

    msg = serialized_hdr + serialized_discovery_header + serialized_msg + serialized_discovery
    return msg

# Parse the recv string
def parse_recv(recv_string):
    import struct
    import steammessages_remoteclient_discovery_pb2

    recv_hdr_string = recv_string[0:12]

    recv_hdr = struct.unpack(pack_format_hdr, recv_string[0:12])
    hdr_length = recv_hdr[2]

    hdr_string = recv_string[12:12+hdr_length]
    msg_length_str = recv_string[12+hdr_length:12+hdr_length+4]
    msg_length = struct.unpack(pack_format_msg, msg_length_str)[0]
    msg_string = recv_string[12+hdr_length+4:]

    hdr = steammessages_remoteclient_discovery_pb2.CMsgRemoteClientBroadcastHeader.FromString(hdr_string)
    msg = steammessages_remoteclient_discovery_pb2.CMsgRemoteClientBroadcastStatus.FromString(msg_string)

    for u in msg.users:
        yield "http://steamcommunity.com/profiles/" + str(u.steamid)

def do_stuff():
    import socket

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    s.bind(("", 0))

    send_addr = ("<broadcast>", 27036)

    msg = send_string()
    s.sendto(msg, send_addr)

    profile_set = set()

    while True:
        recv_string, address = s.recvfrom(BUFSIZE)
        for profile in parse_recv(recv_string):
            if profile not in profile_set:
                print profile
                profile_set.add(profile)

if __name__ == "__main__":
    do_stuff()
