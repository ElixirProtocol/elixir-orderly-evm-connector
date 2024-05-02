#!/usr/bin/env python

import os
import pathlib
from configparser import ConfigParser


def get_account_info():
    config = ConfigParser()
    config_file_path = os.path.join(
        pathlib.Path(__file__).parent.resolve(), "..", "config.ini"
    )
    config.read(config_file_path)
    return (
        config["keys"]["hsm_pin"],
        config["keys"]["hsm_label"],
        config["keys"]["signer_address"],
    )
