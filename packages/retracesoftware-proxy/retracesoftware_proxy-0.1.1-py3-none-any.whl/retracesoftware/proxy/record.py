import retracesoftware.functional as functional
import retracesoftware_utils as utils
import retracesoftware.stream as stream

from retracesoftware.proxy.proxytype import dynamic_proxytype, superdict, is_descriptor, extending_proxytype, dynamic_int_proxytype, make_extensible, Proxy
# from retracesoftware.proxy.gateway import gateway_pair
from retracesoftware.proxy.proxysystem import ProxySystem
from retracesoftware.proxy.thread import write_thread_switch
from retracesoftware.install.tracer import Tracer
import sys
import os
import types

class Placeholder:
    __slots__ = ['id', '__weakref__']

    def __init__(self, id):
        self.id = id

class ExtendedProxy:
    __slots__ = []

class ProxyRef:
    def __init__(self, module, name):
        self.module = module
        self.name = name

    def resolve(self):
        return getattr(sys.modules[self.module], self.name)

class ProxySpec(ProxyRef):
    def __init__(self, module, name, methods, members):
        super().__init__(module, name)
        self.methods = methods
        self.members = members

    def __str__(self):
        return f'ProxySpec(module = {self.module}, name = {self.name}, methods = {self.methods}, members = {self.members})'
    
def keys_where_value(pred, dict):
    for key,value in dict.items():
        if pred(value): yield key

types_lookup = {v:k for k,v in types.__dict__.items() if isinstance(v, type)}

def resolve(obj):
    try:
        return getattr(sys.modules[obj.__module__], obj.__name__)
    except:
        return None
    
def resolveable(obj):
    try:
        return getattr(sys.modules[obj.__module__], obj.__name__) is obj
    except:
        return False

def resolveable_name(obj):
    if obj in types_lookup:
        return ('types', types_lookup[obj])
    elif resolve(obj) is obj:
        return (obj.__module__, obj.__name__)
    else:
        return None

# when 
class RecordProxySystem(ProxySystem):
    
    def bind(self, obj):
        self.bindings[obj] = self.writer.handle(Placeholder(self.next_placeholder_id))
        self.writer(self.bindings[obj])
        self.next_placeholder_id += 1

    def before_fork(self):
        self.writer.close()
        super().before_fork()
        # self.writer.path = self.dynamic_path

    def after_fork_in_child(self):
        new_path = self.new_child_path(self.writer.path)
        new_path.parent.mkdir()
        self.writer.path = new_path
        super().after_fork_in_child()

    def after_fork_in_parent(self):
        super().after_fork_in_parent()
        self.thread_state.value = self.saved_thread_state
        self.writer.reopen()

    def __init__(self, thread_state, 
                 immutable_types, 
                 tracing_config,
                 path):
        
        self.fork_counter = 0

        self.getpid = thread_state.wrap(
            desired_state = 'disabled', function = os.getpid)
        
        self.pid = self.getpid()

        self.writer = stream.writer(path)
        
        w = self.writer.handle('TRACE')
        def trace_writer(*args):
            print(f'Trace: {args}')
            w(*args)

        self.extended_types = {}
        self.bindings = utils.id_dict()
        self.next_placeholder_id = 0

        serialize = functional.walker(self.bindings.get_else_key)
        
        thread_switch_monitor = \
            utils.thread_switch_monitor(
                functional.repeatedly(functional.sequence(utils.thread_id, self.writer)))

        # self.sync = lambda function: functional.observer(on_call = functional.always(writer.handle('SYNC')), function = function)
        self.sync = lambda function: functional.firstof(thread_switch_monitor, functional.always(self.writer.handle('SYNC')), function)

        # trace_handle = writer.handle('TRACE')
        # tracer = Tracer(tracing_config, writer = trace_handle)

        # on_ext_result = writer.handle('RESULT')
        # on_ext_result = functional.if_then_else(
        #     functional.isinstanceof(str), self.writer.handle('RESULT'), functional.sequence(serialize, self.writer))
 
        # on_int_call = functional.mapargs(transform = serialize, function = self.writer.handle('CALL'))
            
        error = self.writer.handle('ERROR')

        def write_error(cls, val, traceback):
            error(cls, val)
        
        self.set_thread_id = functional.partial(utils.set_thread_id, self.writer)

        def watch(f): return functional.either(thread_switch_monitor, f)

        tracer = Tracer(tracing_config, writer = trace_writer)

        # def wrap_int_to_ext(self, obj): return obj
        # def wrap_ext_to_int(self, obj): return obj
        
        # def on_int_call(self, func, *args, **kwargs):
        #     pass

        # def on_ext_result(self, result):
        #     pass

        # def on_ext_error(self, err_type, err_value, err_tarceback):
        #     pass

        # def ext_apply(self, func, *args, **kwargs):
        #     return func(*args, **kwargs)
        
        # def int_apply(self, func, *args, **kwargs):
        #     return func(*args, **kwargs)

        self.wrap_int_to_ext = watch
        
        self.on_int_call = functional.mapargs(transform = serialize, function = self.writer.handle('CALL'))
        
        self.on_ext_result = functional.if_then_else(
                                functional.isinstanceof(str), 
                                self.writer.handle('RESULT'), 
                                functional.sequence(serialize, self.writer))
        
        self.on_ext_error = write_error

        self.ext_apply = self.int_apply = functional.apply

        super().__init__(thread_state = thread_state, tracer = tracer, immutable_types = immutable_types)
            # wrap_int_to_ext = watch,
            # on_int_call = on_int_call,
            # on_ext_result = on_ext_result,
            # on_ext_error = write_error)
        
        # self.ext_handler, self.int_handler = gateway_pair(
        #     thread_state,
        #     self.tracer,
        #     immutable_types = immutable_types,
        #     wrap_int_to_ext = watch,
        #     int_proxytype = self.int_proxytype,
        #     ext_proxytype = self.proxytype,
        #     on_int_call = on_int_call,
        #     on_ext_result = on_ext_result,
        #     on_ext_error = write_error)
            
    def ext_proxytype(self, cls):
        assert isinstance(cls, type), f"record.proxytype requires a type but was passed: {cls}"

        # resolved = resolve(cls)

        proxytype = super().ext_proxytype(cls)

        if resolveable_name(cls):
            module, name = resolveable_name(cls)
            ref = self.writer.handle(ProxyRef(name = name, module = module))
        else:
            blacklist = ['__getattribute__']
            descriptors = {k: v for k,v in superdict(cls).items() if k not in blacklist and is_descriptor(v) }

            methods = [k for k, v in descriptors.items() if utils.is_method_descriptor(v)]
            members = [k for k, v in descriptors.items() if not utils.is_method_descriptor(v)]

            ref = self.writer.handle(ProxySpec(name = cls.__name__, 
                                            module = cls.__module__,
                                            methods = methods,
                                            members = members))
  
        self.writer.type_serializer[proxytype] = functional.constantly(ref)
        return proxytype

    def extend_type(self, base):

        if base in self.extended_types:
            return self.extended_types[base]

        extended = super().extend_type(base)
        
        self.extended_types[base] = extended 

        return extended
