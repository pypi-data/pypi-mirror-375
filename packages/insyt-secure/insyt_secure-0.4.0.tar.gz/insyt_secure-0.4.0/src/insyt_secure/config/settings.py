import os

# MQTT Settings
MQTT_BROKER = os.getenv('MQTT_BROKER', 'localhost')
MQTT_PORT = int(os.getenv('MQTT_PORT', '1883'))
MQTT_USERNAME = os.getenv('MQTT_USERNAME')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')

# Executor Settings
POD_NAME = os.getenv('POD_NAME', 'local-executor')
MAX_WORKERS = int(os.getenv('MAX_WORKERS', '6'))

# Topic Settings
SUBSCRIBE_TOPIC = "$share/code-executors/code.execute"