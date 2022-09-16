
from time import sleep
from threading import Thread


def loop(obj):
    count = 0
    while obj.logging == True:
        sleep(1)
        count += 1
        print(obj.logging)
        print(count)


def wait(obj):
    sleep(10)
    obj.logging = False
    print("Set to false")
    print(obj.logging)


class ObjectClass:
    logging = True

    def __init__(self) -> None:
        self.logging = True

    def looping(self):
        #
        looping_thread = Thread(target=loop, args=(self,))
        stop_looping_thread = Thread(target=wait, args=(self,))
        looping_thread.start()
        stop_looping_thread.start()
        looping_thread.join()
        stop_looping_thread.join()


obj_obj = ObjectClass()

obj_obj.looping()
