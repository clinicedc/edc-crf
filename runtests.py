#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

import django

app_name = "edc_crf"

if __name__ == "__main__":
    os.environ["DJANGO_SETTINGS_MODULE"] = f"{app_name}.tests.test_settings"
    django.setup()
    from django.test.runner import DiscoverRunner

    tags = [t.split("=")[1] for t in sys.argv if t.startswith("--tag")]
    failfast = any([True for t in sys.argv if t.startswith("--failfast")])
    keepdb = any([True for t in sys.argv if t.startswith("--keepdb")])
    skip_checks = any([True for t in sys.argv if t.startswith("--skip_checks")])
    opts = dict(failfast=failfast, tags=tags, keepdb=keepdb, skip_checks=skip_checks)
    failures = DiscoverRunner(**opts).run_tests([f"{app_name}.tests"], **opts)
    sys.exit(failures)
