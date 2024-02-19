import json
import logging.config
import sys, os, getopt, time, datetime

from logger import JsonConsoleHandler, JsonFormatter
from scancode import scan_code_to_key
from rdpy.core import log, rss

from rdpy.protocol.rdp import rdp
from twisted.internet import reactor

# Create a logger
logger = logging.getLogger('json_logger')
logger.setLevel(logging.INFO)

# Create a JSON formatter
json_formatter = JsonFormatter()

# Create a JSON console handler and set the formatter
json_console_handler = JsonConsoleHandler(sys.stdout)
json_console_handler.setFormatter(json_formatter)

# Add the console handler to the logger
logger.addHandler(json_console_handler)

class HoneyPotServer(rdp.RDPServerObserver):
    def __init__(self, controller, rssFileSizeList):
        rdp.RDPServerObserver.__init__(self, controller)
        self._rssFileSizeList = rssFileSizeList
        self._dx, self._dy = 0, 0
        self._rssFile = None
        
    def onReady(self):
        if self._rssFile is None:
            #compute which RSS file to keep
            width, height = self._controller.getScreen()
            size = width * height
            rssFilePath = sorted(self._rssFileSizeList, key = lambda x: abs(x[0][0] * x[0][1] - size))[0][1]
            logger.debug({
                "time": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "message": "Select file ({0}, {1}) -> {2}s".format(width, height, rssFilePath)
            })

            self._rssFile = rss.createReader(rssFilePath)

        domain, username, password = self._controller.getCredentials()
        hostname = self._controller.getHostname()

        logger.info(json.dumps({
            "time": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "type": "credentials",
            "ip": self._controller.addr.host,
            "domain": domain,
            "username": username,
            "password": password,
            "hostname": hostname,
        }))
        self.start()
        
    def onClose(self):
         logger.info(json.dumps({
            "time": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "type": "close",
            "ip": self._controller.addr.host,
            "pressed": self._controller.pressed,
            "pointer": self._controller.pointer,
        }))

    def onKeyEventScancode(self, code, isPressed, isExtended):
        key = scan_code_to_key(int(code))
    
        self._controller.pressed.append(key)

        logger.info(json.dumps({
            "time": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "type": "keyevent_scancode",
            "ip": self._controller.addr.host,
            "code": code,
            "key": key,
            "isPressed": isPressed,
            "isExtended": isExtended,
        }))

    def onKeyEventUnicode(self, code, isPressed):
        logger.info(json.dumps({
            "time": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "type": "keyevent_unicode",
            "ip": self._controller.addr.host,
            "code": code,
            "isPressed": isPressed,
        }))

    def onPointerEvent(self, x, y, button, isPressed):
        self._controller.pointer.append({
            "button": button,
            "x": x,
            "y": y,
        })
        
        logger.info(json.dumps({
            "time": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "type": "pointer_event",
            "ip": self._controller.addr.host,
            "button": button,
            "x": x,
            "y": y,
            "isPressed": isPressed,
        }))
        pass
    def start(self):
        self.loopScenario(self._rssFile.nextEvent())
        
    def loopScenario(self, nextEvent):
        if nextEvent.type.value == rss.EventType.UPDATE:
            self._controller.sendUpdate(nextEvent.event.destLeft.value + self._dx, nextEvent.event.destTop.value + self._dy, nextEvent.event.destRight.value + self._dx, nextEvent.event.destBottom.value + self._dy, nextEvent.event.width.value, nextEvent.event.height.value, nextEvent.event.bpp.value, nextEvent.event.format.value == rss.UpdateFormat.BMP, nextEvent.event.data.value)
            
        elif nextEvent.type.value == rss.EventType.CLOSE:
            self._controller.close()
            return
            
        elif nextEvent.type.value == rss.EventType.SCREEN:
            self._controller.setColorDepth(nextEvent.event.colorDepth.value)
            #compute centering because we cannot resize client
            clientSize = nextEvent.event.width.value, nextEvent.event.height.value
            serverSize = self._controller.getScreen()
            
            self._dx, self._dy = (max(0, serverSize[0] - clientSize[0]) / 2), max(0, (serverSize[1] - clientSize[1]) / 2)
            #restart connection sequence
            return
        
        e = self._rssFile.nextEvent()
        reactor.callLater(float(e.timestamp.value) / 1000.0, lambda:self.loopScenario(e))
        
class HoneyPotServerFactory(rdp.ServerFactory):
    def __init__(self, rssFileSizeList, privateKeyFilePath, certificateFilePath):
        rdp.ServerFactory.__init__(self, 16, privateKeyFilePath, certificateFilePath)
        self._rssFileSizeList = rssFileSizeList
        
    def buildObserver(self, controller, addr):
        logger.info(json.dumps({
            "time": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "type": "connection",
            "ip": addr.host,
            "port": addr.port,
            "message": "Connection from [{0}:{1}]".format(addr.host, addr.port)
        }))
        
        controller.pressed = []
        controller.pointer = []
        controller.addr = addr
        
        return HoneyPotServer(controller, self._rssFileSizeList)
    
def readSize(filePath):
    r = rss.createReader(filePath)
    while True:
        e = r.nextEvent()
        if e is None:
            return None
        elif e.type.value == rss.EventType.SCREEN:
            return e.event.width.value, e.event.height.value
    
if __name__ == "__main__":
    log._LOG_LEVEL = log.Level.NONE
    listen = "3389"
    privateKeyFilePath = None
    certificateFilePath = None
    rssFileSizeList = []
    os.environ["TZ"] = "Europe/Amsterdam"
    time.tzset()
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hl:k:c:L:")
    except getopt.GetoptError:
        help()
    for opt, arg in opts:
        if opt == "-l":
            listen = arg
        elif opt == "-k":
            privateKeyFilePath = arg
        elif opt == "-c":
            certificateFilePath = arg
    
    #build size map
    logger.debug(json.dumps({
        "time": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "message": "Start RDPHoneypot"
    }))
    
    logger.debug(json.dumps({
        "time": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "message": "Build size map"
    }))

    for arg in args:
        size = readSize(arg)
        rssFileSizeList.append((size, arg))
        logger.debug(json.dumps({
            "time": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "message": "({0}, {1}) -> {2}".format(size[0], size[1], arg)
        }))
    
    reactor.listenTCP(int(listen), HoneyPotServerFactory(rssFileSizeList, privateKeyFilePath, certificateFilePath))
    reactor.run()


