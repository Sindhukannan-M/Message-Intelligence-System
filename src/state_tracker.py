from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ItemState:
    item_id: str
    title: str
    status: str = "Pending"
    deadline: Optional[str] = None
    priority: Optional[str] = None
    source_message_id: Optional[str] = None
    related_message_ids: list = field(default_factory=list)


class StateTracker:
    """
    Maintains the latest known state of tasks/events as messages
    arrive chronologically.
    """

    def __init__(self):
        self.items = {}

    def create_item(
        self,
        item_id: str,
        title: str,
        source_message_id: str,
        deadline: Optional[str] = None,
    ):
        self.items[item_id] = ItemState(
            item_id=item_id,
            title=title,
            deadline=deadline,
            source_message_id=source_message_id,
            related_message_ids=[source_message_id],
        )

    def update_item(
        self,
        item_id: str,
        message_id: str,
        status: Optional[str] = None,
        deadline: Optional[str] = None,
        priority: Optional[str] = None,
    ):
        if item_id not in self.items:
            return False

        item = self.items[item_id]

        if status:
            item.status = status

        if deadline:
            item.deadline = deadline

        if priority:
            item.priority = priority

        if message_id not in item.related_message_ids:
            item.related_message_ids.append(message_id)

        return True

    def get_item(self, item_id: str):
        return self.items.get(item_id)

    def get_all_items(self):
        return list(self.items.values())