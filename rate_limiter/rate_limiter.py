import time


class RateLimiter:
    """
    our RateLimiter implements the Sliding Window Log algorithm.
    """

    def __init__(self, max_request=5, window_seconds=60):       #default constructor if values are not given the default values will  be 5 and 60.
        # Maximum allowed requests per window
        self.limit = max_request
        # Size of the sliding time window in seconds
        self.window_seconds = window_seconds
        # Dictionary storing user request history -> { "user_id": [timestamp1, timestamp2, ...] }
        self.users = {}

    def is_allowed(self, user_id):
        """
        Checks if a user is allowed to make an API request right now.
        Returns True if allowed, False if rate-limited.
        """
        curr_time = time.time()

        # Step 1: Initialize list if this is the user's first request
        if user_id not in self.users:
            self.users[user_id] = []

        # Step 2: Calculate window cutoff and prune expired timestamps (> 60s old)
        window_start = curr_time - self.window_seconds
        valid_timestamps = []

        for t in self.users[user_id]:
            if t > window_start:
                valid_timestamps.append(t)  # Keep timestamp if it is within the active window

        # Update the user's history with only unexpired timestamps
        self.users[user_id] = valid_timestamps

        # Step 3: Check if request count in active window is under the limit
        if len(self.users[user_id]) < self.limit:
            self.users[user_id].append(curr_time)  # Record current request
            return True   # Request Allowed
        else:
            return False  # Rate Limit Exceeded (HTTP 429)
