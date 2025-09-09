from invenio_access.permissions import system_identity
from invenio_records_resources.proxies import current_service_registry

from oarepo_runtime.datastreams.types import StreamBatch, StreamEntry
from oarepo_runtime.datastreams.writers import BaseWriter
from oarepo_runtime.datastreams.writers.utils import record_invenio_exceptions

from ...utils.identity_utils import get_user_and_identity


class PublishWriter(BaseWriter):
    def __init__(
        self,
        *,
        service,
        request_name="publish_draft",
        identity=None,
        direct_call=True,
        **kwargs
    ):
        if isinstance(service, str):
            service = current_service_registry.get(service)

        self._service = service
        if isinstance(identity, str):
            _, identity = get_user_and_identity(email=identity)
        elif isinstance(identity, int):
            _, identity = get_user_and_identity(user_id=identity)
        self._identity = identity or system_identity
        self._request_name = request_name
        self._direct_call = direct_call

    def write(self, batch: StreamBatch) -> StreamBatch:
        for entry in batch.ok_entries:
            if entry.deleted:
                continue

            with record_invenio_exceptions(entry):
                self._write_entry(entry)

    def _write_entry(self, entry: StreamEntry):
        if self._direct_call:
            data = self._service.publish(self._identity, entry.id)
        else:
            data = self._publish_via_request(self._identity, entry.id)

        entry.entry = data.to_dict()

    def _publish_via_request(self, identity, entry_id):
        from invenio_requests.proxies import (
            current_requests_service as current_invenio_requests_service,
        )
        from oarepo_requests.proxies import current_oarepo_requests_service

        draft = self._service.read_draft(identity, entry_id)
        request = current_oarepo_requests_service.create(
            identity=identity,
            data=None,
            request_type=self._request_name,
            topic=draft._record,
        )

        submit_result = current_invenio_requests_service.execute_action(
            identity, request.id, "submit"
        )
        accept_result = current_invenio_requests_service.execute_action(
            identity, request.id, "accept"
        )

        return self._service.read(identity, draft["id"])
