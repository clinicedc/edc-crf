from django.apps import apps as django_apps
from edc_constants.constants import INCOMPLETE

from .crf_status_model_mixin import CrfStatusModelMixin


def update_crf_status_command(app_label=None):
    if app_label:
        app_configs = [django_apps.get_app_config(app_label)]
    else:
        app_configs = django_apps.get_app_configs()

    print("Updating CRF Status model for instances set to crf_status=incomplete")
    for app_config in app_configs:
        print(f"  * updating {app_config.name}")
        for model in app_config.get_models():
            if issubclass(model, (CrfStatusModelMixin,)):
                print(f"    - {model._meta.label_lower}")
                for obj in model.objects.filter(crf_status=INCOMPLETE):
                    update_crf_status_for_instance(obj)
