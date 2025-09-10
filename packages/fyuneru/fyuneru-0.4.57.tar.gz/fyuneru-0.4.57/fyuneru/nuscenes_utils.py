from enum import Enum
from functools import reduce
from typing import Callable


class NuScenesIndex(Enum):
    ATTRIBUTE = "attribute.json"
    # 标定token + 传感器 token信息
    CALIBRATED_SENSOR = "calibrated_sensor.json"
    CATEGORY = "category.json"
    EGO_POSE = "ego_pose.json"
    INSTANCE = "instance.json"
    LIDARSEG = "lidarseg.json"
    LOG = "log.json"
    MAP = "map.json"
    SAMPLE_ANNOTATION = "sample_annotation.json"
    # 多个sample data token + calibration token
    SAMPLE_DATA = "sample_data.json"
    # 时间戳+sample data token
    SAMPLE_TIME = "sample_time.json"
    SAMPLE = "sample.json"
    SCENE = "scene.json"
    # 传感器的token和channel名称
    SENSOR = "sensor.json"
    VISIBILITY = "visibility.json"
    SAMPLES_SUB = "samples"
    SWEEPS_SUB = "sweeps"


def sort_sample(sample_time: dict) -> list[str]:
    """
    排序sample索引
    """
    sorted_sample_time = sorted(sample_time.items(), key=lambda entry: int(entry[0]))
    return [sample_token for _, sample_token in sorted_sample_time]


def init_sample_data(sample_data_s: list[dict]) -> Callable[[str, str], dict]:
    """
    初始化sample信息
    """
    index_by_sample_sensor: dict[tuple[str, str], dict] = reduce(
        lambda acc, sample_data: acc.update(
            {
                (
                    sample_data["sample_token"],
                    sample_data["calibrated_sensor_token"],
                ): sample_data
            }
        )
        or acc,
        sample_data_s,
        dict(),
    )
    return lambda sample_token, calibrated_sensor_token: index_by_sample_sensor[
        (sample_token, calibrated_sensor_token)
    ]


def init_calibrated_sensor(calibrated_sensor_s: list[dict]) -> Callable[[str], dict]:
    """
    索引calibrated_sensor
    """
    index_by_calibrated_token: dict[str, dict] = reduce(
        lambda acc, calibrated_sensor: acc.update(
            {calibrated_sensor["token"]: calibrated_sensor}
        )
        or acc,
        calibrated_sensor_s,
        dict(),
    )
    return lambda calibrated_sensor_token: index_by_calibrated_token[
        calibrated_sensor_token
    ]


def init_sensor(sensor_s: list[dict]) -> Callable[[str], dict]:
    """
    索引sensor
    """
    index_by_sensor_token: dict[str, dict] = reduce(
        lambda acc, sensor: acc.update({sensor["channel"]: sensor}) or acc,
        sensor_s,
        dict(),
    )
    return lambda sensor_token: index_by_sensor_token[sensor_token]
