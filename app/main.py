import json
import logging
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import psutil
from prometheus_client import CONTENT_TYPE_LATEST, Gauge, REGISTRY, generate_latest

logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))
logger = logging.getLogger(__name__)

HOST = os.getenv('METRICS_HOST', '0.0.0.0')
PORT = int(os.getenv('APP_PORT', '8080'))
DISK_PATH = os.getenv('DISK_PATH', '/')
METRICS_INTERVAL = float(os.getenv('METRICS_INTERVAL', '5'))

CPU_USAGE = Gauge('pc_cpu_usage_percent', 'CPU usage in percent')
MEM_USAGE = Gauge('pc_memory_usage_percent', 'Memory usage in percent')
CPU_FREQ = Gauge('pc_cpu_frequency_mhz', 'Current CPU frequency in MHz')
DISK_USAGE = Gauge('pc_disk_usage_percent', 'Disk usage in percent')
PROCESS_CPU = Gauge('pc_process_cpu_percent', 'Exporter process CPU usage in percent')
PROCESS_MEMORY = Gauge('pc_process_memory_bytes', 'Exporter process resident memory in bytes')
PROCESS_THREADS = Gauge('pc_process_threads', 'Number of threads used by the exporter')
APP_INFO = Gauge('pc_app_info', 'Exporter application information', ['version'])

APP_VERSION = os.getenv('APP_VERSION', '0.1.0')
APP_INFO.labels(version=APP_VERSION).set(1)


def metrics():
	cpu_usage = psutil.cpu_percent()
	cpu_frequency = psutil.cpu_freq()
	mem = psutil.virtual_memory().percent
	disk_usage = psutil.disk_usage(DISK_PATH).percent
	process = psutil.Process()

	CPU_USAGE.set(cpu_usage)
	CPU_FREQ.set(cpu_frequency.current if cpu_frequency else 0)
	MEM_USAGE.set(mem)
	DISK_USAGE.set(disk_usage)
	PROCESS_CPU.set(process.cpu_percent())
	PROCESS_MEMORY.set(process.memory_info().rss)
	PROCESS_THREADS.set(process.num_threads())


class MetricsHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		if self.path == '/health':
			response = json.dumps({'status': 'ok'}).encode('utf-8')
			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
		elif self.path == '/metrics':
			response = generate_latest(REGISTRY)
			self.send_response(200)
			self.send_header('Content-Type', CONTENT_TYPE_LATEST)
		else:
			response = b'Not found\n'
			self.send_response(404)
			self.send_header('Content-Type', 'text/plain; charset=utf-8')

		self.send_header('Content-Length', str(len(response)))
		self.end_headers()
		self.wfile.write(response)

	def log_message(self, format, *args):
		logger.info('%s - %s', self.address_string(), format % args)


def collect_metrics():
	while True:
		try:
			metrics()
		except Exception:
			logger.exception('Unable to collect system metrics')
		time.sleep(METRICS_INTERVAL)


def main():
	Thread(target=collect_metrics, daemon=True).start()
	server = ThreadingHTTPServer((HOST, PORT), MetricsHandler)
	logger.info('Starting metrics server on %s:%s', HOST, PORT)
	server.serve_forever()


if __name__ == '__main__':
	main()
