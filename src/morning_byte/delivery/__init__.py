"""Delivery mechanisms for Morning Byte."""

from .email import EmailDelivery
from .local import LocalDelivery

__all__ = ["EmailDelivery", "LocalDelivery"]
