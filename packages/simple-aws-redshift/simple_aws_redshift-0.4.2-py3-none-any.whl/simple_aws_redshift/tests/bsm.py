# -*- coding: utf-8 -*-

from boto_session_manager import BotoSesManager

aws_profile = "esc_app_dev_us_east_1"
bsm = BotoSesManager(profile_name=aws_profile)
