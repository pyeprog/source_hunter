class Logger:
    def __init__(self, debug=0):
        self.debug = debug

    def set_debug(self, debug):
        self.debug = debug

    def info(self, msg):
        if self.debug == 1:
            print(msg)

    def verbose_info(self, msg):
        if self.debug > 1:
            print(msg)


logger = Logger()
