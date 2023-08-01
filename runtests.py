#!/usr/bin/env python
import logging
import os
from os.path import abspath, dirname

from edc_test_utils import DefaultTestSettings, func_main

app_name = "edc_crf"
base_dir = dirname(abspath(__file__))

project_settings = DefaultTestSettings(
    calling_file=__file__,
    BASE_DIR=base_dir,
    APP_NAME=app_name,
    ETC_DIR=os.path.join(base_dir, app_name, "tests", "etc"),
    SUBJECT_VISIT_MODEL="edc_visit_tracking.subjectvisit",
    SUBJECT_VISIT_MISSED_MODEL="visit_schedule_app.subjectvisitmissed",
    INSTALLED_APPS=[
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.messages",
        "django.contrib.sessions",
        "django.contrib.sites",
        "django.contrib.staticfiles",
        "django_crypto_fields.apps.AppConfig",
        "django_revision.apps.AppConfig",
        "multisite",
        "edc_action_item.apps.AppConfig",
        "edc_appointment.apps.AppConfig",
        "edc_consent.apps.AppConfig",
        "edc_device.apps.AppConfig",
        "edc_export.apps.AppConfig",
        "edc_facility.apps.AppConfig",
        "edc_identifier.apps.AppConfig",
        "edc_list_data.apps.AppConfig",
        "edc_metadata.apps.AppConfig",
        "edc_notification.apps.AppConfig",
        "edc_protocol.apps.AppConfig",
        "edc_reference.apps.AppConfig",
        "edc_registration.apps.AppConfig",
        "edc_sites.apps.AppConfig",
        "edc_timepoint.apps.AppConfig",
        "edc_visit_schedule.apps.AppConfig",
        "visit_schedule_app.apps.AppConfig",
        "edc_visit_tracking.apps.AppConfig",
        "edc_crf.apps.AppConfig",
    ],
    add_dashboard_middleware=True,
).settings


def main():
    func_main(project_settings, f"{app_name}.tests")


if __name__ == "__main__":
    logging.basicConfig()
    main()
