CREATE VIEW guid_lookup (
	guid,
	tablename
)
AS
SELECT guid, "experiment"
from experiment 
UNION
SELECT guid, "sensor"
from sensor
UNION
SELECT guid, "channel"
from channel
UNION
SELECT guid, "sensor_capture"
from sensor_capture 
UNION
SELECT guid, "channel_capture"
from channel_capture
UNION
SELECT guid, "ts_representation"
from ts_representation 
UNION
SELECT guid, "container"
from container 
;
