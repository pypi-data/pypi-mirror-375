"""Models for the django-tomselect package."""

from django.db import models


class EmptyModel(models.Model):
    """This model serves only as a placeholder for the queryset that is passed to the widget.

    Because we get the model and resulting queryset from the view, and we don't want to repeat ourselves by also
    specifying the model in the widget, we need to pass a model to the widget that is not None. This model is
    used only to satisfy the widget's need for a queryset, and is not used for anything else.
    """

    objects = models.Manager()

    class Meta:  # pylint: disable=R0903
        """Meta options for the EmptyModel."""

        managed = False
        app_label = "django_tomselect"
        verbose_name = "Empty Model"
        verbose_name_plural = "Empty Models"
