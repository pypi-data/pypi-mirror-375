import unittest
from unittest.mock import MagicMock, call

import clearskies
from clearskies.contexts import Context
from clearskies.test_base import TestBase


class StringTest(TestBase):
    def test_default(self):
        class Pet(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()

            id = clearskies.columns.Uuid()
            name = clearskies.columns.String()

        context = clearskies.contexts.Context(
            clearskies.endpoints.Create(
                Pet,
                writeable_column_names=["name"],
                readable_column_names=["id", "name"],
            ),
        )

        (status_code, response_data, response_headers) = context(
            request_method="POST",
            body={"name": "Spot"},
        )
        assert len(response_data["data"]["id"]) == 36
