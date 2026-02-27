import requests

from transmission_rpc import Client
# https://transmission-rpc.readthedocs.io/en/stable/
torrent_url = "https://github.com/trim21/transmission-rpc/raw/v4.1.0/tests/fixtures/iso.torrent"
c = Client(host="192.168.10.121", port=9091, username="transmission", password="transmission")