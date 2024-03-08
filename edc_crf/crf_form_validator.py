from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _
from edc_appointment.form_validator_mixins import WindowPeriodFormValidatorMixin
from edc_consent.form_validators import ConsentDefinitionFormValidatorMixin
from edc_form_validators import INVALID_ERROR, FormValidator
from edc_registration import get_registered_subject_model_cls
from edc_utils import floor_secs, formatted_datetime, to_utc
from edc_utils.date import to_local
from edc_visit_tracking.modelform_mixins import get_related_visit

from .crf_form_validator_mixins import CrfFormValidatorMixin

if TYPE_CHECKING:
    from edc_appointment.models import Appointment
    from edc_visit_tracking.model_mixins import VisitModelMixin


class CrfFormValidatorError(Exception):
    pass


class CrfFormValidator(
    WindowPeriodFormValidatorMixin,
    ConsentDefinitionFormValidatorMixin,
    CrfFormValidatorMixin,
    FormValidator,
):
    """Form validator for CRfs.

    CRFs have a FK to related_visit_model_cls.
    """

    report_datetime_field_attr = "report_datetime"

    def _clean(self) -> None:
        self.validate_crf_report_datetime()
        super()._clean()

    @property
    def registered_subject(self):
        return get_registered_subject_model_cls().objects.get(
            subject_identifier=self.subject_identifier
        )

    @property
    def screening_identifier(self) -> str:
        return self.registered_subject.screening_identifier

    @property
    def gender(self):
        return self.registered_subject.gender

    @property
    def dob(self):
        return self.registered_subject.dob

    def validate_crf_report_datetime(self) -> None:
        if self.report_datetime:
            # falls within appointment's window period
            self.validate_crf_datetime_in_window_period()
            # not before consent date
            report_datetime = to_utc(self.report_datetime)
            consent_datetime = self.get_consent_datetime_or_raise(
                report_datetime=report_datetime, fldname="report_datetime"
            )
            if floor_secs(report_datetime) < floor_secs(consent_datetime):
                msg = _("Invalid. Cannot be before date of consent. Participant consented on")
                formatted_date = formatted_datetime(to_local(consent_datetime))
                err_message = format_lazy(
                    "{msg} {formatted_date}", msg=msg, formatted_date=formatted_date
                )
                self.raise_validation_error(
                    {self.report_datetime_field_attr: err_message},
                    INVALID_ERROR,
                )

    def validate_crf_datetime_in_window_period(self) -> None:
        opts = [
            self.appointment,
            self.report_datetime,
            self.report_datetime_field_attr,
        ]
        self.datetime_in_window_or_raise(*opts)

    @property
    def appointment(self) -> Appointment:
        try:
            return self.related_visit.appointment
        except AttributeError:
            msg = _("is required")
            verbose_name = self.related_visit._meta.verbose_name
            self.raise_validation_error(
                format_lazy("{verbose_name} {msg}.", msg=msg, verbose_name=verbose_name),
                INVALID_ERROR,
            )

    @property
    def related_visit_model_attr(self) -> str:
        """Returns the field name attr if the  related_visit.

        Note: during testing, `self.instance` and `self.model` are
        set on the FormValidator class by a modelform mixin. If you
        are testing the FormValidator in isolation, add these
        values manually on behalf of the modelform. See also
        `related_visit`.
        """
        try:
            return self.instance.related_visit_model_attr()
        except AttributeError:
            return self.model.related_visit_model_attr()

    @property
    def related_visit(self) -> VisitModelMixin | None:
        """Returns a related_visit (subject visit) model instance
        or None.
        """
        try:
            return get_related_visit(
                self, related_visit_model_attr=self.related_visit_model_attr
            )
        except AttributeError as e:
            raise CrfFormValidatorError(f"{e}. See {self.__class__}")

    def validate_datetime_against_report_datetime(self, field: str) -> None:
        """Datetime cannot be after report_datetime"""
        if (
            self.cleaned_data.get(field)
            and floor_secs(self.report_datetime)
            and floor_secs(to_utc(self.cleaned_data.get(field)))
            > floor_secs(self.report_datetime)
        ):
            self.raise_validation_error(
                {field: _("Cannot be after report datetime")}, INVALID_ERROR
            )

    def validate_date_against_report_datetime(self, field: str) -> None:
        """Date cannot be after report_datetime"""
        if (
            self.cleaned_data.get(field)
            and self.report_datetime
            and self.cleaned_data.get(field) > self.report_datetime.date()
        ):
            self.raise_validation_error(
                {field: _("Cannot be after report datetime")}, INVALID_ERROR
            )

    @property
    def subject_visit(self) -> VisitModelMixin:
        warnings.warn(
            "The subject_visit attribute is deprecated in favor of related_visit.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.related_visit
