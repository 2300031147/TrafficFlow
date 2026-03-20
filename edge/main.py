import time
import sys
import structlog
import traceback
import psutil

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
    ]
)
logger = structlog.get_logger("edge.main")

from edge.config.settings import config, ensure_data_dirs
from edge.hardware.simulated.camera_sim import CameraSim
from edge.hardware.simulated.inference_sim import InferenceSim
from edge.hardware.simulated.signal_sim import SignalSim
from edge.simulator.traffic_generator import SyntheticTrafficGenerator
from edge.intelligence.decision_engine import DecisionEngine
from edge.uplink.sender import CCSender
from edge.detector.lane_counter import LaneCounts
from edge.aggregator.window import ReportingWindow
from edge.detector.stream_server import StreamServer

def main():
    ensure_data_dirs()  # L2: create dirs at runtime, not import time
    logger.info("Initializing UrbanFlow Edge System...")
    logger.info("Loaded config", junction_id=config.junction.junction_id, mode=config.junction.mode)
    
    cameras = {
        'north_in': CameraSim('north_in'),
        'south_in': CameraSim('south_in'),
        'east_in': CameraSim('east_in'),
        'west_in': CameraSim('west_in')
    }
    
    inference = InferenceSim()
    signal = SignalSim()
    
    traffic_gen = SyntheticTrafficGenerator()
    decision_engine = DecisionEngine(signal)
    sender = CCSender()
    window = ReportingWindow()
    stream = StreamServer()
    
    for name, cam in cameras.items():
        cam.start()
        
    inference.initialize()
    logger.info("Signal backend current state", phase=signal.get_current_phase())
    
    stream.start()

    from edge.uplink.watchdog import WatchdogDaemon
    watchdog = WatchdogDaemon(sender=sender, signal_controller=signal)
    watchdog.start()

    try:
        logger.info("Entering main execution loop. Press Ctrl+C to stop.")
        while True:
            time.sleep(config.timing.decision_interval_seconds)
            
            counts_dict = traffic_gen.get_current_counts()
            
            ns_north = counts_dict.get("north_in", LaneCounts())
            ns_south = counts_dict.get("south_in", LaneCounts())
            ew_east = counts_dict.get("east_in", LaneCounts())
            ew_west = counts_dict.get("west_in", LaneCounts())
            
            ns_counts = LaneCounts(
                total_count=ns_north.total_count + ns_south.total_count,
                stopped_count=ns_north.stopped_count + ns_south.stopped_count,
                motorcycles=ns_north.motorcycles + ns_south.motorcycles,
                cars=ns_north.cars + ns_south.cars,
                buses=ns_north.buses + ns_south.buses,
                trucks=ns_north.trucks + ns_south.trucks,
                autorickshaws=ns_north.autorickshaws + ns_south.autorickshaws,
                avg_speed=(ns_north.avg_speed + ns_south.avg_speed) / 2.0
            )
            
            ew_counts = LaneCounts(
                total_count=ew_east.total_count + ew_west.total_count,
                stopped_count=ew_east.stopped_count + ew_west.stopped_count,
                motorcycles=ew_east.motorcycles + ew_west.motorcycles,
                cars=ew_east.cars + ew_west.cars,
                buses=ew_east.buses + ew_west.buses,
                trucks=ew_east.trucks + ew_west.trucks,
                autorickshaws=ew_east.autorickshaws + ew_west.autorickshaws,
                avg_speed=(ew_east.avg_speed + ew_west.avg_speed) / 2.0
            )
            
            decision = decision_engine.run_cycle(ns_counts, ew_counts)
            
            window.record_counts(counts_dict)
            window.record_decision(decision)
            
            if window.is_ready():
                payload = window.pop_payload()
                payload["pi_health"] = {
                    "cpu_percent": psutil.cpu_percent(),
                    "ram_percent": psutil.virtual_memory().percent,
                    "cameras_online": sum(1 for c in cameras.values() if c._running),
                    "buffer_pending": sender.buffer.size()
                }
                sender.send(payload)
            
            logger.info("Tick complete", ns_total=ns_counts.total_count, ew_total=ew_counts.total_count)
            
    except KeyboardInterrupt:
        logger.info("Received KeyboardInterrupt, shutting down...")
    except Exception as e:
        logger.error("Error in main loop", error=str(e), exc_info=True)
    finally:
        watchdog.stop()
        for name, cam in cameras.items():
            cam.stop()
        stream.stop()
        logger.info("UrbanFlow Edge System shut down completely.")

if __name__ == "__main__":
    main()
