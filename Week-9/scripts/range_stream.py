import concurrent.futures
import time
import urllib.request

class RangeStream:
    """Read ordered HTTP byte ranges while prefetching a bounded number of chunks."""
    def __init__(self, url, total, block=8 * 1024 * 1024, workers=4):
        self.url, self.total, self.block = url, total, block
        self.pool = concurrent.futures.ThreadPoolExecutor(max_workers=workers)
        self.next_offset = 0
        self.pending = []
        self.buffer = b''
        self.position = 0
        for _ in range(workers):
            self.schedule()

    def schedule(self):
        if self.next_offset < self.total:
            start = self.next_offset
            end = min(start + self.block, self.total) - 1
            self.next_offset = end + 1
            self.pending.append(self.pool.submit(self.fetch, start, end))

    def fetch(self, start, end):
        request = urllib.request.Request(self.url, headers={'Range': f'bytes={start}-{end}'})
        for attempt in range(3):
            try:
                with urllib.request.urlopen(request, timeout=60) as response:
                    expected = f'bytes {start}-{end}/{self.total}'
                    if response.status != 206 or response.headers.get('Content-Range') != expected:
                        raise ValueError('Server did not return the requested byte range')
                    data = response.read()
                    if len(data) != end - start + 1:
                        raise ValueError('Incomplete HTTP byte range')
                    return data
            except Exception:
                if attempt == 2:
                    raise
                time.sleep(2)

    def read(self, size=-1):
        if size < 0:
            raise ValueError('Unbounded remote reads are disabled')
        pieces = []
        while size:
            if self.position == len(self.buffer):
                if not self.pending:
                    break
                self.buffer = self.pending.pop(0).result()
                self.position = 0
                self.schedule()
            count = min(size, len(self.buffer) - self.position)
            pieces.append(self.buffer[self.position:self.position + count])
            self.position += count
            size -= count
        return b''.join(pieces)

    def __enter__(self):
        return self

    def __exit__(self, *unused):
        self.pool.shutdown(wait=True, cancel_futures=True)


