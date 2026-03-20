import json
import os
import datetime
import structlog
from edge.config.settings import config

logger = structlog.get_logger(__name__)

class FestivalCalendar:
    """Loads festival data configs using settings to guide file locations."""
    def __init__(self):
        self.year = datetime.date.today().year
        self.config_path = config.paths.festival_config
        self.dates_path = config.paths.festival_dates_template.replace('{year}', str(self.year))
        
        self.configs = {}
        self.dates = {}
        
        self._load()

    def _load(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    self.configs = {f['id']: f for f in data.get('festivals', [])}
            
            if os.path.exists(self.dates_path):
                with open(self.dates_path, 'r') as f:
                    dates_data = json.load(f)
                    for fest_id, date_str in dates_data.items():
                        try:
                            self.dates[fest_id] = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                        except ValueError:
                            logger.error("invalid_date_format", festival_id=fest_id, date_str=date_str)
        except Exception as e:
            logger.error("festival_load_failed", error=str(e))

    def get_active_events(self, today: datetime.date) -> list:
        active = []
        for fest_id, cfg in self.configs.items():
            festival_date = self.dates.get(fest_id)
            if festival_date is None:
                continue
                
            days_before = cfg.get('days_before', 0)
            days_after = cfg.get('days_after', 0)
            
            window_start = festival_date - datetime.timedelta(days=days_before)
            window_end = festival_date + datetime.timedelta(days=days_after)
            
            if window_start <= today <= window_end:
                active.append(cfg)
                
        return active

    def get_combined_modifier(self, today: datetime.date) -> float:
        active_events = self.get_active_events(today)
        if not active_events:
            return 1.0
            
        combined_modifier = 1.0
        applied_events = []
        
        region = config.junction.state
        junction_type = getattr(config.junction.junction_type, 'value', str(config.junction.junction_type))
        
        for cfg in active_events:
            scope = cfg.get('geographic_scope', {}).get('states', [])
            if scope and region not in scope:
                continue
                
            modifiers = cfg.get('modifiers_by_junction_type', {})
            modifier = modifiers.get(junction_type, modifiers.get('default', 1.0))
            
            tod = cfg.get('time_of_day_override')
            if tod:
                hour = datetime.datetime.now().hour
                if tod.get('hour_start', 0) <= hour <= tod.get('hour_end', 23):
                    modifier = tod.get('multiplier', modifier)
            
            combined_modifier *= modifier
            applied_events.append(cfg.get('name', cfg.get('id')))
            
        combined_modifier = min(config.festival.festival_modifier_cap, combined_modifier)
        
        if applied_events:
            logger.info("active_festivals", events=applied_events, combined_modifier=combined_modifier)
            
        return combined_modifier

    def get_active_event_names(self, today: datetime.date) -> list[str]:
        return [cfg.get('name', cfg.get('id', 'unknown')) for cfg in self.get_active_events(today)]
