import time

class StopWatch:

	def __init__(self):
		self.startTime = None

	def start(self):
		self.startTime = time.time()
		return self.startTime

	def timeElapsed(self):
		now = time.time()
		span = now - self.startTime
		elapsedTimeSecs = round(span, 2)

		return elapsedTimeSecs

	def stop(self):
		self.stopped = time.time()
		span = self.stopped - self.startTime
		elapsedTimeSecs = round(span, 2)

		self.startTime = time.time() #by resetting this, can start once then keep hitting stop() to measure next segment

		return elapsedTimeSecs