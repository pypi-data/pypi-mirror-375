from vyomcloudbridge.services.queue_worker import QueueWorker
from vyomcloudbridge.services.dir_watcher import DirWatcher
from vyomcloudbridge.services.mission_stats import MissionStats
from vyomcloudbridge.services.machine_stats import MachineStats
from vyomcloudbridge.services.vyom_listener import VyomListener
from vyomcloudbridge.utils.installation_info import InstallationInfo
from typing import Dict, Type


AVAILABLE_SERVICES: Dict[str, Type] = {
    "queueworker": QueueWorker,
    "dirwatcher": DirWatcher,
    "missionstats": MissionStats,
    "machinestats": MachineStats,
    "vyomlistener": VyomListener,
}

installation_info = InstallationInfo()
if installation_info.is_full_installation:
    from vyomcloudbridge.services.mavproxy_hq import MavproxyHq
    from vyomcloudbridge.services.ros_publisher import RosPublisher
    from vyomcloudbridge.services.robot_stats import RobotStat

    AVAILABLE_SERVICES["mavproxyhq"] = MavproxyHq
    AVAILABLE_SERVICES["rospublisher"] = RosPublisher
    AVAILABLE_SERVICES["robotstat"] = RobotStat
