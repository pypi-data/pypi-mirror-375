import time
import logging
from datetime import datetime


logger = logging.getLogger(__name__)

GRANULARITY_TTL_RATE = {
    "m": 60,
    "h": 24,
    "d": 14,
}


class ItemTracker:
    def __init__(self, r_client, tracker_name="simple_tracker", verbose=False):
        """
        r_client: Redis client object
        tracker_name: Base name for tracking keys
        verbose: Whether to print logs
        ttl_days: Default TTL in days (default: 3)
        """
        self.base_key = tracker_name
        self.r = r_client
        self.verbose = verbose

    def track_item_occurrence(self, item_name):
        """
        Track item occurrence using atomic counting for multiple time granularities

        Parameters:
        - item_name: Name of the item to track
        """
        timestamp_ms = int(time.time() * 1000)
        granularities = ["m", "h", "d"]

        # Use pipeline for better performance
        pipe = self.r.pipeline()

        for granularity in granularities:
            key = _get_time_key(self.base_key, granularity, timestamp_ms)
            pipe.hincrby(key, item_name, 1)
            pipe.expire(key, _get_ttl_by_granularity(granularity))

        results = pipe.execute()

        if self.verbose:
            for i, granularity in enumerate(granularities):
                count = results[
                    i * 2
                ]  # Results are [incr_result, expire_result, incr_result, expire_result, ...]
                logger.info(
                    f"[ItemTracker] Tracked item '{item_name}' with count {count} at {timestamp_ms} for granularity {granularity}"
                )

    def get_item_count(self, item_name, granularity):
        """
        Get item count for a specific time granularity

        Parameters:
        - item_name: Name of the item to count
        - granularity: Time granularity - 'm', 'h', 'd'

        Returns:
        - Count of item_name in the specified time granularity
        """
        _guard_granularity(granularity)
        key = _get_time_key(self.base_key, granularity)
        count = self.r.hget(key, item_name)
        return int(count) if count is not None else 0

    def get_count_distribution(self, granularity):
        """
        Get distribution for all tracked items within the most recent time period of specified granularity

        Parameters:
        - granularity: Time granularity - 'm', 'h', 'd'

        Returns:
        - List of dictionaries containing item names and total counts
        """
        _guard_granularity(granularity)
        keys = _get_time_keys(self.base_key, granularity)
        result = []
        for key in keys:
            if not self.r.exists(key):
                continue
            items = self.r.hgetall(key)

            for item_bytes, count_bytes in items.items():
                item_name = (
                    item_bytes.decode() if isinstance(item_bytes, bytes) else item_bytes
                )
                count = int(
                    count_bytes.decode()
                    if isinstance(count_bytes, bytes)
                    else count_bytes
                )

                result.append(
                    {
                        "item_name": item_name,
                        "total_count": count,
                        "freq": granularity,
                        "period": key.split(":")[-1],
                    }
                )

        return result


class AsyncItemTracker:
    def __init__(self, redis_client, tracker_name="simple_tracker", verbose=False):
        """
        redis_client: Async Redis client object (e.g., aioredis client)
        tracker_name: Base name for tracking keys
        verbose: Whether to print logs
        ttl_days: Default TTL in days (default: 3)
        """
        self.base_key = tracker_name
        self.r = redis_client
        self.verbose = verbose

    async def track_item_occurrence(self, item_name):
        """
        Track item occurrence using atomic counting for multiple time granularities

        Parameters:
        - item_name: Name of the item to track
        """
        timestamp_ms = int(time.time() * 1000)
        granularities = ["m", "h", "d"]

        # Use pipeline for better performance
        pipe = self.r.pipeline()

        for granularity in granularities:
            key = _get_time_key(self.base_key, granularity, timestamp_ms)
            pipe.hincrby(key, item_name, 1)
            pipe.expire(key, _get_ttl_by_granularity(granularity))

        results = await pipe.execute()

        if self.verbose:
            for i, granularity in enumerate(granularities):
                count = results[
                    i * 2
                ]  # Results are [incr_result, expire_result, incr_result, expire_result, ...]
                logger.info(
                    f"[AsyncItemTracker] Tracked item '{item_name}' with count {count} at {timestamp_ms} for granularity {granularity}"
                )

    async def get_item_count(self, item_name, granularity):
        """
        Get item count for a specific time granularity

        Parameters:
        - item_name: Name of the item to count
        - granularity: Time granularity - 'm', 'h', 'd'

        Returns:
        - Count of item_name in the specified time granularity
        """
        _guard_granularity(granularity)
        key = _get_time_key(self.base_key, granularity)
        count = await self.r.hget(key, item_name)
        return int(count) if count is not None else 0

    async def get_count_distribution(self, granularity):
        """
        Get distribution for all tracked items within the most recent time period of specified granularity

        Parameters:
        - granularity: Time granularity - 'm', 'h', 'd'

        Returns:
        - List of dictionaries containing item names and total counts
        """
        _guard_granularity(granularity)
        keys = _get_time_keys(self.base_key, granularity)

        result = []
        for key in keys:
            if not await self.r.exists(key):
                continue

            items = await self.r.hgetall(key)
            for item_bytes, count_bytes in items.items():
                item_name = (
                    item_bytes.decode() if isinstance(item_bytes, bytes) else item_bytes
                )
                count = int(
                    count_bytes.decode()
                    if isinstance(count_bytes, bytes)
                    else count_bytes
                )

                result.append(
                    {
                        "item_name": item_name,
                        "total_count": count,
                        "freq": granularity,
                        "period": key.split(":")[-1],
                    }
                )

        return result


def _guard_granularity(granularity):
    """
    Guard function to validate time granularity
    """
    if granularity not in ["m", "h", "d"]:
        raise ValueError("Invalid granularity. Use 'm', 'h', 'd'")


def _get_ttl_by_granularity(granularity):
    """Calculate TTL based on granularity"""
    ttl_map = {
        "m": GRANULARITY_TTL_RATE["m"] * 60,
        "h": GRANULARITY_TTL_RATE["h"] * 3600,
        "d": GRANULARITY_TTL_RATE["d"] * 86400,
    }
    return ttl_map.get(granularity, 2 * 86400)


def _get_time_key(base_key, granularity, timestamp_ms=None):
    """
    Generate a Redis key for the specific time granularity

    Parameters:
    - base_key: Base key for tracking
    - granularity: Time granularity - 'm', 'h', 'd'
    - timestamp_ms: Timestamp to generate key for (default: current time)

    Returns:
    - Key name in format: {base_key}:{granularity}:{time_period}
    """
    if timestamp_ms is None:
        timestamp_ms = int(time.time() * 1000)

    dt = datetime.fromtimestamp(timestamp_ms / 1000)

    if granularity == "m":
        time_key = dt.strftime("%Y%m%d%H%M")
    elif granularity == "h":
        time_key = dt.strftime("%Y%m%d%H")
    elif granularity == "d":
        time_key = dt.strftime("%Y%m%d")
    else:
        raise ValueError("Invalid granularity. Use 'm', 'h', 'd'")

    return f"{base_key}:{granularity}:{time_key}"


def _get_time_keys(base_key, granularity):
    """
    Generate Redis keys for the recent time periods based on granularity

    Parameters:
    - base_key: Base key for tracking
    - granularity: Time granularity - 'm', 'h', 'd'

    Returns:
    - List of key names for recent time periods
    """
    periods = GRANULARITY_TTL_RATE[granularity]
    keys = []

    for i in range(periods):
        # Calculate timestamp for i periods back
        if granularity == "m":
            # For minutes, go back i minutes
            timestamp_ms = int((time.time() - i * 60) * 1000)
        elif granularity == "h":
            # For hours, go back i hours
            timestamp_ms = int((time.time() - i * 3600) * 1000)
        elif granularity == "d":
            # For days, go back i days
            timestamp_ms = int((time.time() - i * 86400) * 1000)
        else:
            raise ValueError("Invalid granularity. Use 'm', 'h', 'd'")

        key = _get_time_key(base_key, granularity, timestamp_ms)
        keys.append(key)

    return keys


def get_tracker(r_client, tracker_name="simple_tracker", verbose=False):
    """
    Create an ItemTracker decorator function for tracking item occurrences

    Parameters:
    - r_client: Redis client object
    - tracker_name: Base name for tracking keys
    - verbose: Whether to print logs
    - ttl_days: Default TTL in days (default: 3)
    """
    tracker = ItemTracker(r_client, tracker_name, verbose)

    def track_item(item_name):
        def wrapper(func):
            def inner(*args, **kwargs):
                tracker.track_item_occurrence(item_name)
                return func(*args, **kwargs)

            return inner

        return wrapper

    return track_item


def get_async_tracker(redis_client, tracker_name="simple_tracker", verbose=False):
    """
    Create an AsyncItemTracker decorator function for tracking item occurrences

    Parameters:
    - redis_client: Async Redis client object
    - tracker_name: Base name for tracking keys
    - verbose: Whether to print logs
    - ttl_days: Default TTL in days (default: 3)
    """
    tracker = AsyncItemTracker(redis_client, tracker_name, verbose)

    def track_item(item_name):
        def wrapper(func):
            async def inner(*args, **kwargs):
                await tracker.track_item_occurrence(item_name)
                return await func(*args, **kwargs)

            return inner

        return wrapper

    return track_item
