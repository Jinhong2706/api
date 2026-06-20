class Monitor:
    def __init__(self, mid, method, url, data, frequency, enabled=True):
        self.id = mid
        self.method = method
        self.url = url
        self.data = data
        self.frequency = frequency
        self.enabled = enabled
        self.last_run = 0
        self.latest_result = None
        self.history = []
