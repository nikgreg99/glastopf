import logging
import logstash

logger = logging.getLogger(__name__)


# Global logger for logstash provides an interface for different brokers

from glastopf.modules.reporting.auxiliary.base_logger import BaseLogger

class LogLogStash(BaseLogger):
	def __init__(self, data_dir, config="glastopf.cfg"):
		BaseLogger.__init__(self, config)

		if self.config.getboolean("logstash", "enabled"):
			self.host = self.config.get("logstash", "host")
			self.port = int(self.config.getint("logstash", "port"))
			self.options = {
			 	"enabled": self.config.getboolean("logstash", "enabled"),
			}
		
			self.handler = self.config.get("logstash", "handler")

			if self.handler == "AMQP":
				self.username = self.config.get("logstash", "username")
				self.password = self.config.get("logstash", "password")
				self.exchange = self.config.get("logstash", "exchange")
				self.durable = self.config.getboolean("logstash", "durable")
			elif self.handler != "TCP" and self.handler != "UDP":
				raise Exception("Incorrect logstash handler defined, please use AMQP, UDP or TCP")

			self._setupHandler()

	def _setupHandler(self):
		logstashHandler = None

		if self.handler == 'AMQP':
			logstashHandler = logstash.AMQPLogstashHandler(version=1,
                                                    host=self.host,
                                                    durable=self.durable,
                                                    username=self.username,
                                                    password=self.password,
                                                    exchange=self.exchange )
		elif self.handler == 'TCP':
			logstashHandler = logstash.LogstashHandler(self.host, self.port, version=1)
		elif self.handler == "UDP":
			logstashHandler = logstash.LogstashHandler(self.host, self.port, version=1)

		self.attack_logger = logging.getLogger('python-logstash-handler')
		self.attack_logger.setLevel(logging.INFO)
		self.attack_logger.addHandler(logstashHandler)

	def insert(self, attack_event):
		message = "Glaspot: %(pattern)s attack method from %(source)s against %(host)s:%(port)s. [%(method)s %(url)s]" % {
			'pattern': attack_event.matched_pattern,
			'source': ':'.join((attack_event.source_addr[0], str(attack_event.source_addr[1]))),
			'host': attack_event.sensor_addr[0],
			'port': attack_event.sensor_addr[1],
			'method': attack_event.http_request.request_verb,
			'url': attack_event.http_request.request_url,
        		}
		self.attack_logger.info(message)


