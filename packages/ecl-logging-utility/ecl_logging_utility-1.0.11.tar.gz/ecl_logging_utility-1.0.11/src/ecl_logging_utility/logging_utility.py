import logging
import json
import os
import structlog
import sys
import traceback
import atexit
import time
import uuid

from datetime import datetime
from queue import Queue, Empty
from opensearchpy import OpenSearch
from structlog.contextvars import bind_contextvars, clear_contextvars
from structlog.processors import CallsiteParameter
from threading import Thread, Event

from .slack_session_manager import SlackSessionManager

# Constants
LOG_LEVEL_MAP = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

DEFAULT_LOG_LEVEL = logging.INFO
ERROR_CRITICAL_LEVELS = ('error', 'critical')
FIELD_MAPPINGS = {
    'pathname': 'file_path',
    'lineno': 'line_number',
    'func_name': 'function_name'
}

# OpenSearch constants
DEFAULT_OPENSEARCH_HOST = 'localhost'
DEFAULT_OPENSEARCH_PORT = '9200'
DEFAULT_BATCH_SIZE = '10'
DEFAULT_FLUSH_INTERVAL = '5'
DEFAULT_TIMEOUT = 10
HTTPS_PORT = 443
QUEUE_TIMEOUT = 1
MAX_RETRY_ATTEMPTS = 3
RETRY_SLEEP_MULTIPLIER = 0.5
WORKER_THREAD_JOIN_TIMEOUT = 5
SLACK_TIMEOUT = 5

# Default service names
DEFAULT_APP_VERSION = 'AMBIVALENT_APP_VERSION'
DEFAULT_SERVICE_NAME = 'AMBIVALENT_SERVICE_NAME'
DEFAULT_LOG_SERVICE_NAME = 'logs'

# Cache for environment variables
_env_cache = {}


def _get_env_with_cache(key, default=None):
    """Get environment variable with caching"""
    if key not in _env_cache:
        _env_cache[key] = os.getenv(key, default)
    return _env_cache[key]


def _safe_int(value, default):
    """Safely convert string to int with fallback"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def get_log_level():
    """Get log level from environment variable"""
    level_str = _get_env_with_cache('ECL_LOGGING_UTILITY_LOG_LEVEL', 'INFO').upper()
    return LOG_LEVEL_MAP.get(level_str, DEFAULT_LOG_LEVEL)


def build_opensearch_dashboard_url(host, field_name, field_value):
    """
    Build OpenSearch Dashboard URL for filtered search

    Args:
        host (str): OpenSearch domain host (without protocol)
        field_name (str): Field to filter on (e.g., "log_uuid")
        field_value (str): Exact value to match (e.g., "1234test")

    Returns:
        str: Complete OpenSearch Dashboard URL
    """

    # Base dashboard URL
    base_url = f"https://{host}/_dashboards"

    # Get index pattern UUID from environment variable
    index_pattern_uuid = os.getenv('ECL_LOGGING_UTILITY_INDEX_PATTERN_UUID')

    if index_pattern_uuid:
        # Use the new data-explorer/discover format with proper indexPattern UUID
        # Global state: (filters:!(),refreshInterval:(pause:!t,value:0),time:(from:now-1h,to:now))
        g_part = "(filters:!(),refreshInterval:(pause:!t,value:0),time:(from:now-12h,to:now))"

        # App state with discover structure and metadata containing indexPattern UUID
        a_part = f"(discover:(columns:!(_source),interval:auto,sort:!()),metadata:(indexPattern:'{index_pattern_uuid}',view:discover))"

        # Query part with filters
        q_part = f"(filters:!(('$state':(store:appState),meta:(alias:!n,disabled:!f,key:{field_name},negate:!f,params:(query:'{field_value}'),type:phrase),query:(match_phrase:({field_name}:'{field_value}')))),query:(language:kuery,query:''))"

        # Construct the complete URL using data-explorer format
        discover_url = f"{base_url}/app/data-explorer/discover/#?_g={g_part}&_a={a_part}&_q={q_part}"
    else:
        # Skip index pattern entirely if UUID not set - just use basic discover URL
        g_part = "(filters:!(),refreshInterval:(pause:!t,value:0),time:(from:now-12h,to:now))"
        a_part = f"(columns:!(_source),filters:!(('$state':(store:appState),meta:(alias:!n,disabled:!f,key:{field_name},negate:!f,params:(query:'{field_value}'),type:phrase),query:(match_phrase:({field_name}:'{field_value}')))),interval:auto,query:(language:kuery,query:''),sort:!())"
        discover_url = f"{base_url}/app/discover#/?_g={g_part}&_a={a_part}"

    return discover_url


def rename_fields(_, __, event_dict):
    """Custom processor to rename fields"""
    for old_key, new_key in FIELD_MAPPINGS.items():
        if old_key in event_dict:
            event_dict[new_key] = event_dict.pop(old_key)
    return event_dict


def add_log_id_processor(_, method_name, event_dict):
    """Custom processor to add log_id for error/critical logs"""
    if method_name in ERROR_CRITICAL_LEVELS:
        event_dict['log_id'] = str(uuid.uuid4())
    return event_dict


def error_handler_processor(_, method_name, event_dict):
    """Custom processor for error-specific actions"""
    if method_name in ERROR_CRITICAL_LEVELS:
        slack_webhook_url = _get_env_with_cache('ECL_LOGGING_UTILITY_SLACK_WEBHOOK_URL')
        if slack_webhook_url:
            try:
                log_id = event_dict.get('log_id')
                opensearch_host = _get_env_with_cache('ECL_LOGGING_UTILITY_OPENSEARCH_HOST', DEFAULT_OPENSEARCH_HOST)
                service_name = _get_env_with_cache('ECL_LOGGING_UTILITY_SERVICE_NAME', DEFAULT_LOG_SERVICE_NAME)

                discover_url = build_opensearch_dashboard_url(opensearch_host, "log_id", log_id)

                payload = {
                    "text": f"🚨 Error in {service_name}",
                    "attachments": [{
                        "color": "danger",
                        "fields": [
                            {"title": key.replace('_', ' ').title(), "value": str(value), "short": len(str(value)) < 50}
                            for key, value in event_dict.items()
                        ],
                        "actions": [{
                            "type": "button",
                            "text": "View Full Log",
                            "url": discover_url
                        }]
                    }]
                }
                Thread(
                    target=lambda: SlackSessionManager().get_session().post(slack_webhook_url, json=payload, timeout=SLACK_TIMEOUT),
                    daemon=True).start()
            except Exception as e:
                print(f"Failed to send error log to Slack: {e}\n Trace: {traceback.format_exc()}")
    return event_dict


class OpenSearchLogger:
    _instance = None
    _initialized = False

    def __new__(cls, service_name: str = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, service_name: str = None):
        if self._initialized:
            return

        self.host = _get_env_with_cache('ECL_LOGGING_UTILITY_OPENSEARCH_HOST', DEFAULT_OPENSEARCH_HOST)
        self.port = _safe_int(_get_env_with_cache('ECL_LOGGING_UTILITY_OPENSEARCH_PORT', DEFAULT_OPENSEARCH_PORT), int(DEFAULT_OPENSEARCH_PORT))
        self.username = _get_env_with_cache('ECL_LOGGING_UTILITY_OPENSEARCH_USERNAME')
        self.password = _get_env_with_cache('ECL_LOGGING_UTILITY_OPENSEARCH_PASSWORD')
        self.batch_size = _safe_int(_get_env_with_cache('ECL_LOGGING_UTILITY_OPENSEARCH_BATCH_SIZE', DEFAULT_BATCH_SIZE), int(DEFAULT_BATCH_SIZE))
        self.flush_interval = _safe_int(_get_env_with_cache('ECL_LOGGING_UTILITY_OPENSEARCH_FLUSH_INTERVAL', DEFAULT_FLUSH_INTERVAL), int(DEFAULT_FLUSH_INTERVAL))

        http_auth = None
        if self.username and self.password:
            http_auth = (self.username, self.password)

        scheme = "http"
        use_ssl = False
        verify_certs = False
        if self.port == HTTPS_PORT:
            scheme = "https"
            use_ssl = True
            verify_certs = True

        self.index_prefix = service_name if service_name else DEFAULT_LOG_SERVICE_NAME
        self.log_queue = Queue()
        self.shutdown_event = Event()

        self.client = OpenSearch(
            hosts=[{'host': self.host, 'port': self.port}],
            scheme=scheme,
            http_auth=http_auth,
            use_ssl=use_ssl,
            verify_certs=verify_certs,
            timeout=DEFAULT_TIMEOUT
        )

        self.worker_thread = Thread(target=self._worker, daemon=True)
        self.worker_thread.start()

        atexit.register(self._cleanup)
        self._initialized = True

    def _worker(self):
        """Background worker that processes the log queue"""
        batch = []
        last_flush = time.time()

        while not self.shutdown_event.is_set():
            try:
                log_entry = self.log_queue.get(timeout=QUEUE_TIMEOUT)
                batch.append(log_entry)

                if len(batch) >= self.batch_size or (time.time() - last_flush) >= self.flush_interval:
                    self._flush_batch(batch)
                    batch = []
                    last_flush = time.time()

            except Empty:
                if batch and (time.time() - last_flush) >= self.flush_interval:
                    self._flush_batch(batch)
                    batch = []
                    last_flush = time.time()
            except Exception as e:
                print(f"OpenSearch worker error: {e}")

        # Final flush on shutdown
        if batch:
            self._flush_batch(batch)

    def _flush_batch(self, batch):
        """Send batch of logs to OpenSearch with retry logic"""
        if not batch:
            return

        for attempt in range(MAX_RETRY_ATTEMPTS):
            try:
                if len(batch) == 1:
                    # Single log
                    log_entry = batch[0]
                    self.client.index(
                        index=log_entry['index'],
                        body=log_entry['body']
                    )
                else:
                    # Bulk insert
                    actions = []
                    for log_entry in batch:
                        actions.extend([
                            {"index": {"_index": log_entry['index']}},
                            log_entry['body']
                        ])
                    self.client.bulk(body=actions)
                break
            except Exception as e:
                if attempt == MAX_RETRY_ATTEMPTS - 1:
                    print(f"Failed to send logs to OpenSearch after {MAX_RETRY_ATTEMPTS} attempts: {e}")
                else:
                    time.sleep(RETRY_SLEEP_MULTIPLIER * (attempt + 1))

    def _cleanup(self):
        """Cleanup on shutdown"""
        self.shutdown_event.set()
        if hasattr(self, 'worker_thread') and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=WORKER_THREAD_JOIN_TIMEOUT)

    def __call__(self, logger, method_name, event_dict):
        # Queue the log entry for background processing
        index_name = f"{self.index_prefix}-{datetime.now().strftime('%Y.%m')}"

        # Handle both dict and string event_dict
        if isinstance(event_dict, dict):
            body = event_dict.copy()
        else:
            # If event_dict is already a string (from JSON renderer), parse it back
            try:
                body = json.loads(event_dict) if isinstance(event_dict, str) else event_dict
            except (json.JSONDecodeError, TypeError):
                body = {'message': str(event_dict)}

        log_entry = {
            'index': index_name,
            'body': body
        }

        try:
            self.log_queue.put_nowait(log_entry)
        except Exception as e:
            print(f"Failed to queue log for OpenSearch: {e}")

        return event_dict


# Custom JSON renderer that beautifies the entire log output
def beautified_json_renderer(_, __, event_dict):
    """Render the log entry as beautified JSON with newlines"""
    try:
        beautified = json.dumps(event_dict, indent=2, default=str, ensure_ascii=False)
        return f"\n{beautified}\n"
    except (TypeError, ValueError):
        # Fallback to regular JSON if beautification fails
        return json.dumps(event_dict, default=str)


def configure_logging():
    app_version = _get_env_with_cache('ECL_LOGGING_UTILITY_APP_VERSION', DEFAULT_APP_VERSION)
    service_name = _get_env_with_cache('ECL_LOGGING_UTILITY_SERVICE_NAME', DEFAULT_SERVICE_NAME)
    log_level = get_log_level()

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.CallsiteParameterAdder(
            [
                CallsiteParameter.PATHNAME,
                CallsiteParameter.LINENO,
                CallsiteParameter.MODULE,
                CallsiteParameter.FUNC_NAME,
            ]
        ),
        rename_fields,
        structlog.processors.EventRenamer(to='message'),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        add_log_id_processor,
    ]

    if _get_env_with_cache('ECL_LOGGING_UTILITY_OPENSEARCH_ENABLED', 'False').lower() == 'true':
        processors.append(OpenSearchLogger(service_name=service_name))

    processors.extend([
        error_handler_processor,
        beautified_json_renderer
    ])

    structlog.configure(
        processors=processors,
        context_class=structlog.threadlocal.wrap_dict(dict),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        cache_logger_on_first_use=False,
    )

    # Create logger with static context
    return structlog.get_logger(service_name).bind(
        app_version=app_version,
        service_name=service_name
    )


# Initialize logger with static context
logger = configure_logging()