import socket
import time
import logging
import traceback
import threading
from typing import Optional, Callable, Deque
from collections import deque
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

__version__ = "1.0.2"
__all__ = ["PlotJugglerClient", "PJData", "AnalyticsModel", "AnalyticsMode"]

class AnalyticsMode:
    OFF = "off"
    BASIC = "basic"
    IN_JUGGLER = "in_juggler"
    PERIODIC = "periodic"

class AnalyticsModel(BaseModel):
    num_values: int
    frequency: float  # in Hz (momentary)
    duration: float  # in seconds (total)
    rate: float  # in bytes per second (momentary)
    window_size: float = Field(default=5.0)  # window size in seconds

class PJData(BaseModel):
    timestamp: float = Field(default_factory=time.time)
    values: dict[str, float | int | bool]
    analytics : Optional[AnalyticsModel] = None


class PlotJugglerClient:
    def __init__(self, ip: str, port: int, analytics: AnalyticsMode = AnalyticsMode.OFF,
                 periodic_interval: float = 5.0, analytics_callback: Optional[Callable[[AnalyticsModel], None]] = None,
                 analytics_window: float = 5.0):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.analytics_mode = analytics
        self.analytics = AnalyticsModel(num_values=0, frequency=0, duration=0, rate=0, window_size=analytics_window)
        self.periodic_interval = periodic_interval
        self.analytics_callback = analytics_callback
        self.analytics_window = analytics_window

        # Threading lock for protecting shared analytics data
        self._analytics_lock = threading.Lock()

        # Analytics tracking variables
        self._start_time = time.time()
        self._last_send_time = 0
        self._total_bytes_sent = 0
        self._send_count = 0

        # Rolling window data for momentary calculations
        self._send_timestamps: Deque[float] = deque()
        self._send_sizes: Deque[int] = deque()

        # Periodic analytics variables
        self._periodic_thread: Optional[threading.Thread] = None
        self._stop_periodic = threading.Event()

        # Start periodic analytics if enabled
        if self.analytics_mode == AnalyticsMode.PERIODIC:
            self._start_periodic_analytics()

    def _clean_old_data(self, current_time: float):
        """Remove data older than the analytics window"""
        cutoff_time = current_time - self.analytics_window

        # Remove old timestamps and corresponding sizes
        while self._send_timestamps and self._send_timestamps[0] < cutoff_time:
            self._send_timestamps.popleft()
            self._send_sizes.popleft()

    def _calculate_momentary_metrics(self, current_time: float) -> tuple[float, float]:
        """Calculate momentary frequency and rate based on recent window"""
        self._clean_old_data(current_time)

        if len(self._send_timestamps) < 2:
            return 0.0, 0.0

        # Calculate frequency (messages per second) in the window
        window_duration = current_time - self._send_timestamps[0]
        if window_duration > 0:
            frequency = len(self._send_timestamps) / window_duration
        else:
            frequency = 0.0

        # Calculate rate (bytes per second) in the window
        total_bytes_in_window = sum(self._send_sizes)
        if window_duration > 0:
            rate = total_bytes_in_window / window_duration
        else:
            rate = 0.0

        return frequency, rate

    def _start_periodic_analytics(self):
        """Start the periodic analytics logging thread"""
        if self._periodic_thread is not None:
            return  # Already started

        self._stop_periodic.clear()
        self._periodic_thread = threading.Thread(target=self._periodic_analytics_worker, daemon=True)
        self._periodic_thread.start()
        logger.info(f"Started periodic analytics logging every {self.periodic_interval} seconds")

    def _periodic_analytics_worker(self):
        """Worker thread for periodic analytics logging"""
        while not self._stop_periodic.wait(self.periodic_interval):
            try:
                analytics = self.get_analytics()

                # Log analytics
                logger.info(f"Analytics: {analytics.frequency:.2f} Hz, "
                           f"{analytics.rate:.0f} B/s, "
                           f"{analytics.duration:.1f}s runtime, "
                           f"{self._send_count} messages sent")

                # Call custom callback if provided
                if self.analytics_callback:
                    try:
                        self.analytics_callback(analytics)
                    except Exception as e:
                        logger.error(f"Error in analytics callback: {e}")

            except Exception as e:
                logger.error(f"Error in periodic analytics: {e}")

    def _stop_periodic_analytics(self):
        """Stop the periodic analytics logging thread"""
        if self._periodic_thread is not None:
            self._stop_periodic.set()
            self._periodic_thread.join(timeout=1.0)
            self._periodic_thread = None
            logger.info("Stopped periodic analytics logging")

    def send(self, data: PJData):
        if not isinstance(data, PJData):
            raise ValueError("data must be an instance of PJData")

        send_data = data

        if self.analytics_mode == AnalyticsMode.IN_JUGGLER:
            # Create a deep copy to avoid modifying the original data object
            send_data = data.model_copy(deep=True)

            send_data.analytics = self.get_analytics()

        # Serialize data
        json_data = send_data.model_dump_json().encode()

        # Update analytics if enabled
        if self.analytics_mode != AnalyticsMode.OFF:
            self._update_analytics(len(json_data), data)

        # Send data
        self.sock.sendto(json_data, (self.ip, self.port))

    def _update_analytics(self, json_size: int, data: PJData):
        """Update analytics based on the sent data"""
        current_time = time.time()

        with self._analytics_lock:
            # Update counters
            self._send_count += 1
            self._total_bytes_sent += json_size

            # Add to rolling window
            self._send_timestamps.append(current_time)
            self._send_sizes.append(json_size)

            # Calculate momentary metrics
            momentary_freq, momentary_rate = self._calculate_momentary_metrics(current_time)

            # Update analytics with momentary values
            self.analytics.frequency = momentary_freq
            self.analytics.rate = momentary_rate

            # Update total duration (this remains cumulative)
            self.analytics.duration = current_time - self._start_time

            # Count number of values in the current data
            self.analytics.num_values = len(data.values)

            self._last_send_time = current_time

    def get_analytics(self) -> AnalyticsModel:
        """Get current analytics data"""
        with self._analytics_lock:
            return self.analytics.model_copy()

    def reset_analytics(self):
        """Reset analytics counters"""
        with self._analytics_lock:
            self._start_time = time.time()
            self._last_send_time = 0
            self._total_bytes_sent = 0
            self._send_count = 0
            self._send_timestamps.clear()
            self._send_sizes.clear()
            self.analytics = AnalyticsModel(num_values=0, frequency=0, duration=0, rate=0,
                                            window_size=self.analytics_window)

    def set_periodic_interval(self, interval: float):
        """Change the periodic analytics interval"""
        self.periodic_interval = interval
        if self.analytics_mode == AnalyticsMode.PERIODIC and self._periodic_thread is not None:
            # Restart with new interval
            self._stop_periodic_analytics()
            self._start_periodic_analytics()

    def set_analytics_callback(self, callback: Optional[Callable[[AnalyticsModel], None]]):
        """Set or update the analytics callback function"""
        self.analytics_callback = callback

    def set_analytics_window(self, window_size: float):
        """Change the analytics window size for momentary calculations"""
        with self._analytics_lock:
            self.analytics_window = window_size
            self.analytics.window_size = window_size
            # Clean old data with new window size
            if self._send_timestamps:
                current_time = time.time()
                self._clean_old_data(current_time)

    def close(self):
        """Close the client and stop all background tasks"""
        self._stop_periodic_analytics()
        self.sock.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            logger.error(traceback.format_exc())
            pass  # Socket might already be closed

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()