# -*- coding: utf-8 -*-

import sys

if sys.version_info < (3, 11):  # pragma: no cover
    from dateutil.parser import parse as parse_datetime
else:  # pragma: no cover
    from datetime import datetime

    parse_datetime = datetime.fromisoformat
