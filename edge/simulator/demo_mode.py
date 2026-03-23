import json
import structlog
import time
import argparse
from edge.config.settings import config

logger = structlog.get_logger(__name__)

def run_scenario(scenario_id: str):
    logger.info(f"Loading demo scenario '{scenario_id}'...")
    try:
        with open('edge/config/demo_scenarios.json', 'r') as f:
            data = json.load(f)
            scenario = data['scenarios'].get(scenario_id)
            if not scenario:
                logger.error("Scenario not found.")
                return

        logger.info(f"Starting execution of {len(scenario['steps'])} steps...")
        
        # Start edge components in background maybe, depending on harness
        # We'd execute the steps based on simulated timeline triggers
        import requests
        for step in scenario['steps']:
            logger.info(f"STEP: {step['message']}")
            if 'time' in step:
                time.sleep(step['time'])
            try:
                if step.get('action') == 'set_pattern':
                    logger.info(f"Setting pattern: {step.get('pattern')}")
                elif step.get('action') == 'trigger_alert':
                    requests.post("http://localhost:8000/api/v1/alerts", json=step.get('payload', {}))
                elif step.get('action') == 'override_phase':
                    j_id = step.get('junction_id', config.junction.junction_id)
                    requests.post(f"http://localhost:8000/api/v1/junctions/{j_id}/override", json=step.get('payload', {}))
            except Exception as e:
                logger.error(f"Failed to execute step action: {e}")

    except Exception as e:
        logger.error(f"Failed to load scenario: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", default="full")
    args = parser.parse_args()
    
    run_scenario(args.scenario)
