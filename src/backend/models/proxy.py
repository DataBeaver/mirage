# SPDX-License-Identifier: LGPL-3.0-or-later

from typing import TYPE_CHECKING

from . import SyncId
from .model import Model

if TYPE_CHECKING:
    from .model_item import ModelItem


class ModelProxy(Model):
    def __init__(self, sync_id: SyncId) -> None:
        super().__init__(sync_id)
        Model.proxies[sync_id] = self

        for sync_id, model in Model.instances.items():
            if sync_id != self.sync_id and self.accept_source(model):
                for key, item in model.items():
                    # if isinstance(model, ModelProxy):
                        # key = key[1]

                    self.source_item_set(model, key, item)


    def accept_source(self, source: Model) -> bool:
        return True


    def source_item_set(self, source: Model, key, value: "ModelItem") -> None:
        if self.accept_source(source):
            self[source.sync_id, key] = value


    def source_item_deleted(self, source: Model, key) -> None:
        if self.accept_source(source):
            del self[source.sync_id, key]


    def source_cleared(self, source: Model) -> None:
        if self.accept_source(source):
            for source_sync_id, key in self.copy():
                if source_sync_id == source.sync_id:
                    del self[source_sync_id, key]
