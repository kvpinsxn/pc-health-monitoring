from app import main


def test_metrics_collects_system_values():
    main.metrics()

    assert main.CPU_USAGE._value.get() >= 0
    assert main.MEM_USAGE._value.get() >= 0
    assert main.DISK_USAGE._value.get() >= 0
    assert main.PROCESS_MEMORY._value.get() > 0
