from django.conf import settings
from django.contrib.sites.managers import CurrentSiteManager
from django.db import models
from django.db.models.deletion import PROTECT
from edc_consent.model_mixins import RequiresConsentFieldsModelMixin
from edc_constants.constants import INCOMPLETE
from edc_metadata.model_mixins.updates import UpdatesCrfMetadataModelMixin
from edc_model.models.historical_records import HistoricalRecords
from edc_offstudy.model_mixins import OffstudyCrfModelMixin
from edc_reference.model_mixins import ReferenceModelMixin
from edc_sites.models import SiteModelMixin
from edc_visit_tracking.managers import CrfModelManager
from edc_visit_tracking.model_mixins import (
    VisitTrackingCrfModelMixin,
    PreviousVisitModelMixin,
)

from .choices import CRF_STATUS


class CrfStatusModelMixin(models.Model):
    crf_status = models.CharField(
        verbose_name="CRF status",
        max_length=25,
        choices=CRF_STATUS,
        default=INCOMPLETE,
        help_text="If some data is still pending, flag this CRF as incomplete",
    )

    comments = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True


class CrfNoManagerModelMixin(
    VisitTrackingCrfModelMixin,
    RequiresConsentFieldsModelMixin,
    PreviousVisitModelMixin,
    UpdatesCrfMetadataModelMixin,
    OffstudyCrfModelMixin,
    SiteModelMixin,
    ReferenceModelMixin,
):
    """ Base model for all scheduled models
    """

    subject_visit = models.OneToOneField(
        settings.SUBJECT_VISIT_MODEL, on_delete=PROTECT
    )

    def natural_key(self):
        return self.subject_visit.natural_key()

    natural_key.dependencies = [
        settings.SUBJECT_VISIT_MODEL,
        "sites.Site",
        "edc_appointment.appointment",
    ]

    class Meta:
        abstract = True
        indexes = [models.Index(fields=["subject_visit", "site", "id"])]


class CrfModelMixin(CrfNoManagerModelMixin):

    on_site = CurrentSiteManager()
    objects = CrfModelManager()
    history = HistoricalRecords(inherit=True)

    class Meta(CrfNoManagerModelMixin.Meta):
        abstract = True
