import socket as s;
sock = s.socket(s.AF_UNIX)
sock.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)
sock.bind('/home/lrh/cmpshare/DesignAlteration/designalteration.sock')