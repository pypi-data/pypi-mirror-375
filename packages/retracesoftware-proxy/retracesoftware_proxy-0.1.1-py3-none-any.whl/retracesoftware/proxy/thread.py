import retracesoftware.functional as functional
import retracesoftware_utils as utils

# def thread_aware_writer(writer):
#     on_thread_switch = functional.sequence(utils.thread_id(), writer.handle('THREAD_SWITCH'))
#     return utils.threadawareproxy(on_thread_switch = on_thread_switch, target = writer)

class ThreadSwitch:
    __slots__ = ['id']

    def __init__(self, id):
        self.id = id

def set_thread_id(writer, id):
    utils.set_thread_id(writer.handle(ThreadSwitch(id)))

def write_thread_switch(writer):
    on_thread_switch = functional.repeatedly(functional.sequence(utils.thread_id, writer))

    return lambda f: utils.thread_aware_proxy(target = f, on_thread_switch = on_thread_switch, sticky = False)

def prefix_with_thread_id(f, current):
    def next():
        nonlocal current, f
        obj = f()

        while isinstance(obj, ThreadSwitch):
            current = obj.id
            obj = f()

        return (current, obj)

    return next

def per_thread_messages(messages):
    thread_id = utils.thread_id
    # thread_id = lambda: 'FOOOOO!!!'

    demux = utils.demux(source = prefix_with_thread_id(messages, thread_id()), key_function = lambda obj: obj[0])

    # def next():
    #     thread,message = demux(thread_id())
    #     return message
    
    # return next
    return functional.repeatedly(lambda: demux(thread_id())[1])
