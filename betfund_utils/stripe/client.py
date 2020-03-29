"""Stripe Client."""
import json
import logging
import os

import stripe
from stripe.error import InvalidRequestError

from typing import Union

logging.basicConfig(level="INFO")
_LOGGER = logging.getLogger(__name__)


class StripeClient(object):
    """Stripe Client."""

    def __call__(self, *args, **kwargs):
        return stripe


class StripeCustomer(object):
    """Stripe Customer object."""

    def __init__(self, customer):
        """
        Params
        ------
            customer (db.Model): Betfund SQLAlchemy User model.
        """
        self.client = StripeClient()
        self.customer = customer
        self._api_key = os.getenv("STRIPE_API_KEY")

    def list(self, limit: int = None) -> Union[list, None]:
        """List all current customers `stripe.list(...)`."""
        client = self.client()
        customers = client.Customer.list(
            api_key=self._api_key
        )

        return customers

    def create(self) -> Union[dict, None]:
        """Create `stripe.Customer(...)`"""
        if self._exists():
            _LOGGER.info(
                "<STRIPE CREATE> customerId: {} already exists.".format(
                    self.customer.get("stripeId")
                )
            )

            return None

        client = self.client()

        customer = client.Customer.create(
            email=self.customer.email_address,
            name=" ".join([self.customer.first_name, self.customer.last_name]),
            api_key=self._api_key
        )

        return customer

    def delete(self):
        """Delete `stripe.Customer(...)`"""
        if not self._exists():
            _LOGGER.error(
                "<STRIPE DELETE ERROR> customerId: {} does not exist."
            )

        client = self.client()
        delete_response = client.Customer.delete(
            self.customer.get("stripeId"),
            api_key=self._api_key
        )

        if delete_response.get("deleted") is True:
            _LOGGER.info(
                "<STRIPE DELETE SUCCESS> customerId: {} was deleted".format(
                    self.customer.get("stripeId")
                )
            )

        return delete_response

    def _exists(self) -> bool:
        """Verify existence of Customer."""
        if self.customer.stripe_id:  # need this to be added
            return False

        try:
            client = self.client()
            retrieve_response = client.Customer.retrieve(
                self.customer.get("stripeId"), api_key=self._api_key
            )

            _LOGGER.info(
                "<STRIPE RETRIEVE SUCCESS> customerId: {} {}".format(
                    self.customer.get("stripeId"), json.dumps(retrieve_response, indent=4)
                )
            )

        except InvalidRequestError:
            _LOGGER.error(
                "<STRIPE RETRIEVE ERROR> customerId: {} does not exist.".format(
                    self.customer.get("stripeId")
                )
            )

            return False

        return bool(retrieve_response)