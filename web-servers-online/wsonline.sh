#!/usr/bin/env bash

while true; do
        /sbin/zmap --verbosity=0 -p 80 -f "saddr,sport,success,timestamp-str" -O json -o - | /opt/zmap/env/bin/python /opt/zmap/zmap.py
done

