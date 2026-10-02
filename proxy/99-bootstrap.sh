#!/bin/sh
# The proxy-conf volume hides the image's /etc/nginx/conf.d. If the volume is
# empty (first boot), install the 100%-stable bootstrap so nginx can start
# before the controller has rendered anything.
if [ ! -s /etc/nginx/conf.d/default.conf ]; then
    cp /etc/nginx/bootstrap.conf /etc/nginx/conf.d/default.conf
fi
