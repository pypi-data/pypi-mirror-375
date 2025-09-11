from haupt.common.events import event_actions, event_subjects
from haupt.common.events.event import ActorEvent, Attribute, Event
from haupt.common.events.registry.attributes import (
    PROJECT_RESOURCE_ATTRIBUTES,
    PROJECT_RESOURCE_OWNER_ATTRIBUTES,
    PROJECT_RUN_EXECUTOR_ATTRIBUTES,
    PROJECT_RUN_EXECUTOR_OWNER_ATTRIBUTES,
)

RUN_CREATED = "{}.{}".format(event_subjects.RUN, event_actions.CREATED)
RUN_STOPPED = "{}.{}".format(event_subjects.RUN, event_actions.STOPPED)
RUN_SKIPPED = "{}.{}".format(event_subjects.RUN, event_actions.SKIPPED)
RUN_NEW_STATUS = "{}.{}".format(event_subjects.RUN, event_actions.NEW_STATUS)
RUN_NEW_ARTIFACTS = "{}.{}".format(event_subjects.RUN, event_actions.NEW_ARTIFACTS)
RUN_SUCCEEDED = "{}.{}".format(event_subjects.RUN, event_actions.SUCCEEDED)
RUN_FAILED = "{}.{}".format(event_subjects.RUN, event_actions.FAILED)
RUN_DONE = "{}.{}".format(event_subjects.RUN, event_actions.DONE)
RUN_RESUMED = "{}.{}".format(event_subjects.RUN, event_actions.RESUMED)
RUN_UPDATED_ACTOR = "{}.{}.{}".format(
    event_subjects.RUN, event_actions.UPDATED, event_subjects.ACTOR
)
RUN_CREATED_ACTOR = "{}.{}.{}".format(
    event_subjects.RUN, event_actions.CREATED, event_subjects.ACTOR
)
RUN_SYNCED_ACTOR = "{}.{}.{}".format(
    event_subjects.RUN, event_actions.SYNCED, event_subjects.ACTOR
)
RUN_VIEWED_ACTOR = "{}.{}.{}".format(
    event_subjects.RUN, event_actions.VIEWED, event_subjects.ACTOR
)
RUN_DELETED_ACTOR = "{}.{}.{}".format(
    event_subjects.RUN, event_actions.DELETED, event_subjects.ACTOR
)
RUN_STOPPED_ACTOR = "{}.{}.{}".format(
    event_subjects.RUN, event_actions.STOPPED, event_subjects.ACTOR
)
RUN_APPROVED_ACTOR = "{}.{}.{}".format(
    event_subjects.RUN, event_actions.APPROVED, event_subjects.ACTOR
)
RUN_TRANSFERRED_ACTOR = "{}.{}.{}".format(
    event_subjects.RUN, event_actions.TRANSFERRED, event_subjects.ACTOR
)
RUN_INVALIDATED_ACTOR = "{}.{}.{}".format(
    event_subjects.RUN, event_actions.INVALIDATED, event_subjects.ACTOR
)
RUN_RESUMED_ACTOR = "{}.{}.{}".format(
    event_subjects.RUN, event_actions.RESUMED, event_subjects.ACTOR
)
RUN_RESTARTED_ACTOR = "{}.{}.{}".format(
    event_subjects.RUN, event_actions.RESTARTED, event_subjects.ACTOR
)
RUN_COPIED_ACTOR = "{}.{}.{}".format(
    event_subjects.RUN, event_actions.COPIED, event_subjects.ACTOR
)
RUN_SKIPPED_ACTOR = "{}.{}.{}".format(
    event_subjects.RUN, event_actions.SKIPPED, event_subjects.ACTOR
)
RUN_STATS_ACTOR = "{}.{}.{}".format(
    event_subjects.RUN, event_actions.STATS, event_subjects.ACTOR
)
RUN_LINEAGE_ACTOR = "{}.{}.{}".format(
    event_subjects.RUN, event_actions.LINEAGE, event_subjects.ACTOR
)
RUN_ALERT_ACTOR = "{}.{}.{}".format(
    event_subjects.RUN, event_actions.ALERT, event_subjects.ACTOR
)

EVENTS = {
    RUN_CREATED,
    RUN_STOPPED,
    RUN_RESUMED,
    RUN_SKIPPED,
    RUN_NEW_STATUS,
    RUN_NEW_ARTIFACTS,
    RUN_SUCCEEDED,
    RUN_FAILED,
    RUN_DONE,
    RUN_CREATED_ACTOR,
    RUN_SYNCED_ACTOR,
    RUN_UPDATED_ACTOR,
    RUN_VIEWED_ACTOR,
    RUN_DELETED_ACTOR,
    RUN_STOPPED_ACTOR,
    RUN_APPROVED_ACTOR,
    RUN_TRANSFERRED_ACTOR,
    RUN_INVALIDATED_ACTOR,
    RUN_RESUMED_ACTOR,
    RUN_RESTARTED_ACTOR,
    RUN_COPIED_ACTOR,
    RUN_SKIPPED_ACTOR,
    RUN_STATS_ACTOR,
    RUN_LINEAGE_ACTOR,
    RUN_ALERT_ACTOR,
}


class RunEvent(Event):
    entity_uuid = "project.uuid"


class RunActorEvent(ActorEvent):
    entity_uuid = "project.uuid"


class RunCreatedEvent(RunEvent):
    event_type = RUN_CREATED
    attributes = PROJECT_RUN_EXECUTOR_ATTRIBUTES


class RunStoppedEvent(Event):
    event_type = RUN_STOPPED
    attributes = PROJECT_RESOURCE_ATTRIBUTES


class RunResumedEvent(RunEvent):
    event_type = RUN_RESUMED
    attributes = PROJECT_RESOURCE_ATTRIBUTES


class RunSkippedEvent(RunEvent):
    event_type = RUN_SKIPPED
    attributes = PROJECT_RESOURCE_ATTRIBUTES


class RunNewStatusEvent(RunEvent):
    event_type = RUN_NEW_STATUS
    attributes = PROJECT_RESOURCE_ATTRIBUTES + (
        Attribute("status"),
        Attribute("previous_status", is_required=False),
    )


class RunNewArtifactsEvent(RunEvent):
    event_type = RUN_NEW_ARTIFACTS
    attributes = PROJECT_RESOURCE_ATTRIBUTES + (Attribute("artifacts", attr_type=list),)


class RunSucceededEvent(RunEvent):
    event_type = RUN_SUCCEEDED
    attributes = PROJECT_RESOURCE_ATTRIBUTES


class RunFailedEvent(RunEvent):
    event_type = RUN_FAILED
    attributes = PROJECT_RESOURCE_ATTRIBUTES


class RunDoneEvent(RunEvent):
    event_type = RUN_DONE
    attributes = PROJECT_RUN_EXECUTOR_ATTRIBUTES


class RunCreatedActorEvent(RunActorEvent):
    event_type = RUN_CREATED_ACTOR
    actor_id = "user.id"
    actor_name = "user.username"
    attributes = PROJECT_RUN_EXECUTOR_OWNER_ATTRIBUTES


class RunSyncedActorEvent(RunActorEvent):
    event_type = RUN_SYNCED_ACTOR
    actor_id = "user.id"
    actor_name = "user.username"
    attributes = PROJECT_RUN_EXECUTOR_OWNER_ATTRIBUTES


class RunUpdatedActorEvent(RunActorEvent):
    event_type = RUN_UPDATED_ACTOR
    attributes = PROJECT_RESOURCE_OWNER_ATTRIBUTES


class RunDeletedActorEvent(RunActorEvent):
    event_type = RUN_DELETED_ACTOR
    attributes = PROJECT_RESOURCE_OWNER_ATTRIBUTES


class RunViewedActorEvent(RunActorEvent):
    event_type = RUN_VIEWED_ACTOR
    attributes = PROJECT_RESOURCE_OWNER_ATTRIBUTES


class RunStoppedActorEvent(RunActorEvent):
    event_type = RUN_STOPPED_ACTOR
    attributes = PROJECT_RUN_EXECUTOR_OWNER_ATTRIBUTES


class RunApprovedActorEvent(RunActorEvent):
    event_type = RUN_APPROVED_ACTOR
    attributes = PROJECT_RUN_EXECUTOR_OWNER_ATTRIBUTES


class RunTransferredActorEvent(RunActorEvent):
    event_type = RUN_TRANSFERRED_ACTOR
    attributes = PROJECT_RUN_EXECUTOR_OWNER_ATTRIBUTES


class RunInvalidatedActorEvent(RunActorEvent):
    event_type = RUN_INVALIDATED_ACTOR
    attributes = PROJECT_RUN_EXECUTOR_OWNER_ATTRIBUTES


class RunResumedActorEvent(RunActorEvent):
    event_type = RUN_RESUMED_ACTOR
    attributes = PROJECT_RUN_EXECUTOR_OWNER_ATTRIBUTES


class RunRestartedActorEvent(RunActorEvent):
    event_type = RUN_RESTARTED_ACTOR
    attributes = PROJECT_RESOURCE_OWNER_ATTRIBUTES


class RunCopiedActorEvent(RunActorEvent):
    event_type = RUN_COPIED_ACTOR
    attributes = PROJECT_RESOURCE_OWNER_ATTRIBUTES


class RunSkippedActorEvent(RunActorEvent):
    event_type = RUN_SKIPPED_ACTOR
    attributes = PROJECT_RESOURCE_OWNER_ATTRIBUTES


class RunStatsActorEvent(RunActorEvent):
    event_type = RUN_STATS_ACTOR
    attributes = PROJECT_RESOURCE_OWNER_ATTRIBUTES


class RunLineageActorEvent(RunActorEvent):
    event_type = RUN_LINEAGE_ACTOR
    attributes = PROJECT_RESOURCE_OWNER_ATTRIBUTES


class RunAlertActorEvent(RunActorEvent):
    event_type = RUN_ALERT_ACTOR
    attributes = PROJECT_RESOURCE_OWNER_ATTRIBUTES
