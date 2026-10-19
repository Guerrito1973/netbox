from utilities.choices import ChoiceSet


class ScanStatusChoices(ChoiceSet):
    key = "ScanRun.status"
    STATUS_PENDING = "pending"
    STATUS_RUNNING = "running"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"

    CHOICES = (
        (STATUS_PENDING, "Pending", "gray"),
        (STATUS_RUNNING, "Running", "blue"),
        (STATUS_COMPLETED, "Completed", "green"),
        (STATUS_FAILED, "Failed", "red"),
    )


class HostStatusChoices(ChoiceSet):
    key = "DiscoveredHost.status"
    STATUS_NEW = "new"
    STATUS_KNOWN = "known"
    STATUS_IGNORED = "ignored"

    CHOICES = (
        (STATUS_NEW, "New", "orange"),
        (STATUS_KNOWN, "Known", "green"),
        (STATUS_IGNORED, "Ignored", "gray"),
    )

