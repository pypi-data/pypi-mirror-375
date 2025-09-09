import json
import os
from pathlib import Path

from probeX.framework.config.env import PROBE_HOME

_REPORT_HOME = Path(PROBE_HOME).joinpath("reports")


class Reporter:

    def __init__(self, report_dir):
        self.report_path = _REPORT_HOME.joinpath(report_dir)
        self.report_url = f"http://localhost:8008/{report_dir}/"
