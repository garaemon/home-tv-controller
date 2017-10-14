#!/usr/bin/env python

import os
import sys

# add load path to ../home_tv_controller
if __name__ == '__main__':
    libdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    if os.path.exists(os.path.join(libdir, 'home_tv_controller')):
        sys.path.insert(0, libdir)

from home_tv_controller.app import App


def main():
    tv_ip_array = App.find_tvs()
    if len(tv_ip_array) == 0:
        raise Exception('no lgtv found')
    tv_ip = tv_ip_array[0]
    client_key = App.get_new_client_key(tv_ip)
    print(client_key)
    

if __name__ == '__main__':
    main()
