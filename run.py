#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

from helpers.cli import CLI
from helpers.command import Command

if sys.version_info[0] == 2:
    message = (
        'Python 3 is recommended.'
        'Kindly install Python 3.+ to install farmstack seamlessly!'
    )
    CLI.framed_print(message, color=CLI.COLOR_ERROR)
    sys.exit(1)



if __name__ == '__main__':
    installation_modules = sys.argv[1:]
    # print(installation_modules)
    print(len(sys.argv))
    try:
        if len(sys.argv) > 1:
            for module in installation_modules:
                # install modules
                if module == '-cs' or module == '--compose-steward':
                    compose_steward()
                elif module == '-cp' or module == '--compose-participant':
                    compose_particpant()
                elif module == '-u' or module == '--update':
                    update()
            
    except Exception as e:
        print(e)