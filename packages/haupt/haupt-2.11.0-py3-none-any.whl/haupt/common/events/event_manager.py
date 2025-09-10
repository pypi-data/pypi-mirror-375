from typing import List, Tuple

from clipped.manager_interface import ManagerInterface

from haupt.common.events import event_actions
from haupt.common.events.event import Event


class EventManager(ManagerInterface):
    def _get_state_data(  # pylint:disable=arguments-differ
        self, event: Event
    ) -> Tuple[str, Event]:
        return event.event_type, event

    def subscribe(self, event: Event):  # pylint:disable=arguments-differ
        """
        >>> subscribe(SomeEvent)
        """
        super().subscribe(obj=event)

    def knows(self, event_type: str) -> bool:  # pylint:disable=arguments-differ
        return super().knows(key=event_type)

    def get(self, event_type: str) -> Event:  # pylint:disable=arguments-differ
        return super().get(key=event_type)

    def user_write_events(self) -> List[str]:
        """Return event types where use acted on an object.

        The write events are events with actions:
            * CREATED
            * UPDATED
            * DELETED
            * RESUMED
            * COPIED
            * CLONED
            * STOPPED
        """
        return [
            event_type
            for event_type, event in self.items
            if event.get_event_action() in event_actions.WRITE_ACTIONS
        ]

    def user_view_events(self) -> List[str]:
        """Return event types where use viewed a main object."""
        return [
            event_type
            for event_type, event in self.items
            if event.get_event_action() == event_actions.VIEWED
        ]
