from apitizer import db_controller
from apitizer import img_parser
import threading
import time
import cv2


class Updater:
    def __init__(self, parser_config):
        self.parser = img_parser.ImageParser(parser_config)
        self.db_controller = db_controller.DatabaseController()
        self.runner_thread = threading.Thread(target=self.run)

    def initiate(self):
        self.runner_thread.start()

    def update(self):
        results = self.parser.get_results()
        self.db_controller.insert_or_update(results)

    def run(self):
        while True:
            try:
                self.update()
                print("Image updated")
            except cv2.error:
                print("Can not process image")
            except AttributeError:
                print("None type object appeared in result")
            except KeyError:
                print("None type object appeared in result")
            except:
                print("unknown error")

            time.sleep(60)
