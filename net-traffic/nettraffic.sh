#!/usr/bin/env bash

while true
do
    tshark -T pdml | python /opt/net-traffic/nettraffic.py
done

