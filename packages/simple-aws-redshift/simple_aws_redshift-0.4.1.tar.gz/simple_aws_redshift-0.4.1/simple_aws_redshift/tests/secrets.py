# -*- coding: utf-8 -*-

from home_secret.api import hs

# fmt: off
admin_username = hs.t("providers.db.simple_aws_redshift_dev.username")
admin_password = hs.t("providers.db.simple_aws_redshift_dev.password")
# fmt: on

if __name__ == "__main__":
    print(f"{admin_username.v = }")
    print(f"{admin_password.v = }")
