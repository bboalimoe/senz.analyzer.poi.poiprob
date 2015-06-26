from logentries import LogentriesHandler
from config import LOGENTRIES_TOKEN
import logging

log = logging.getLogger('logentries')
log.setLevel(logging.INFO)
# Note if you have set up the logentries handler in Django, the following line is not necessary
log.addHandler(LogentriesHandler(LOGENTRIES_TOKEN))
