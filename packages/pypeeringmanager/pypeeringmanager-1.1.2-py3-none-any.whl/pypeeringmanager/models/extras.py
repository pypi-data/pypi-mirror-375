from pynetbox.core.response import Record, JsonField

class ObjectChanges(Record):
    object_data = JsonField
    postchange_data = JsonField
    prechange_data = JsonField

    def __str__(self):
        return self.request_id
