__model = open("/proc/device-tree/model").read()
if "walnutpi-2b" in __model:
    from walnutpi_npu import NPU
    from walnutpi_npu import YOLO11
