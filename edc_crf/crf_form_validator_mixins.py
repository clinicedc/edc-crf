from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from django.core.exceptions import ObjectDoesNotExist
from edc_consent import ConsentDefinitionDoesNotExist, site_consents
from edc_consent.consent_definition import ConsentDefinition
from edc_form_validators import INVALID_ERROR, ReportDatetimeFormValidatorMixin
from edc_sites import site_sites
from edc_utils import age, to_utc
from edc_visit_tracking.modelform_mixins import get_related_visit

if TYPE_CHECKING:
    from edc_visit_tracking.model_mixins import VisitModelMixin


__all__ = ["BaseFormValidatorMixin", "CrfFormValidatorMixin"]


class BaseFormValidatorMixin(ReportDatetimeFormValidatorMixin):
    """A base mixin of common properties needed for PRN/CRF validation
    to be declared with FormValidators.
    """

    @property
    def subject_identifier(self) -> str | None:
        if "subject_identifier" in self.cleaned_data:
            subject_identifier = self.cleaned_data.get("subject_identifier")
        else:
            subject_identifier = getattr(self.instance, "subject_identifier", None)
        return subject_identifier

    @property
    def subject_consent(self):
        cdef = self.get_consent_definition_or_raise()
        return cdef.model_cls.objects.get(subject_identifier=self.subject_identifier)

    def get_consent_definition_or_raise(self) -> ConsentDefinition:
        """Assert falls within a valid consent period

        See also: modelform (self.get_consent_definition_or_raise())
        """
        consent_definition = None
        site = self.cleaned_data.get("site") or self.instance.site or self.current_site

        try:
            consent_definition = site_consents.get_consent_definition(
                report_datetime=self.report_datetime,
                site=site_sites.get(site.id),
            )
        except ConsentDefinitionDoesNotExist as e:
            self.raise_validation_error(str(e), INVALID_ERROR)
        return consent_definition

    @property
    def age_in_years(self) -> int | None:
        if self.report_datetime:
            return age(self.subject_consent.dob, to_utc(self.report_datetime)).years
        return None


class CrfFormValidatorMixin(BaseFormValidatorMixin):
    """Assumes model is a CRF and has a key to related/subject_visit.

    Declare with FormValidator (not modelform).
    """

    @property
    def subject_identifier(self) -> str:
        """Always returns the subject_identifier from related_visit"""
        return self.related_visit.subject_identifier

    @property
    def report_datetime(self) -> datetime:
        """Returns report_datetime or raises.

        Report datetime is always a required field on a CRF model,
        Django will raise a field ValidationError before getting
        here if report_datetime is None.
        """
        report_datetime = None
        if self.report_datetime_field_attr in self.cleaned_data:
            report_datetime = self.cleaned_data.get(self.report_datetime_field_attr)
        elif self.instance:
            report_datetime = self.instance.report_datetime
        return report_datetime

    def get_consent_definition_or_raise(self) -> ConsentDefinition:
        """Assert falls within a valid consent period

        See also: modelform (self.get_consent_definition_or_raise())
        """
        consent_definition = None
        site_id = self.related_visit.site.id
        try:
            consent_definition = site_consents.get_consent_definition(
                report_datetime=self.report_datetime,
                site=site_sites.get(site_id),
            )
        except ConsentDefinitionDoesNotExist as e:
            self.raise_validation_error(str(e), INVALID_ERROR)
        return consent_definition

    @property
    def related_visit_model_attr(self):
        return self.model.related_visit_model_attr()

    @property
    def related_visit(self) -> VisitModelMixin:
        """Returns a subject visit model instance or None"""
        return get_related_visit(self, related_visit_model_attr=self.related_visit_model_attr)

    @property
    def visit_schedule(self):
        return self.related_visit.visit_schedule

    @property
    def schedule(self):
        return self.related_visit.schedule

    @property
    def offschedule_datetime(self) -> datetime | None:
        try:
            obj = self.related_visit.schedule.offschedule_model_cls.objects.get(
                subject_identifier=self.subject_identifier
            )
        except ObjectDoesNotExist:
            offschedule_datetime = None
        else:
            offschedule_datetime = obj.offschedule_datetime
        return offschedule_datetime
