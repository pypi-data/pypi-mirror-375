import retracesoftware.functional as functional
import retracesoftware_utils as utils
import types
from retracesoftware.proxy.gateway import adapter_pair1
from types import SimpleNamespace
from retracesoftware.proxy.proxytype import ExtendingProxy

from retracesoftware.proxy.proxytype import extending_proxytype, make_extensible, dynamic_proxytype, dynamic_int_proxytype, instantiable_dynamic_proxytype

def proxy(proxytype):
    def set_type(cls, obj):
        obj.__class__ = cls
        return obj

    def can_set_type(cls, obj): return issubclass(cls, ExtendingProxy)

    create = functional.if_then_else(can_set_type, set_type, utils.create_wrapped)
    
    return functional.spread(
        create,
        functional.sequence(functional.typeof, proxytype),
        None)

def maybe_proxy(proxytype):
    return functional.if_then_else(
            functional.isinstanceof(utils.Wrapped),
            utils.unwrap,
            proxy(functional.memoize_one_arg(proxytype)))

unproxy_execute = functional.mapargs(starting = 1, 
                                     transform = functional.walker(utils.try_unwrap), 
                                     function = functional.apply)

class ProxySystem:
    
    def wrap_int_to_ext(self, obj): return obj
    def wrap_ext_to_int(self, obj): return obj
    
    def on_int_call(self, func, *args, **kwargs):
        pass

    def on_ext_result(self, result):
        pass

    def on_ext_error(self, err_type, err_value, err_traceback):
        pass

    def ext_apply(self, func, *args, **kwargs):
        return func(*args, **kwargs)
    
    def int_apply(self, func, *args, **kwargs):
        return func(*args, **kwargs)

    def __init__(self, thread_state, immutable_types, tracer):
        
        self.thread_state = thread_state
        self.fork_counter = 0
        self.tracer = tracer
        self.immutable_types = immutable_types
        
        def is_immutable_type(cls):
            return issubclass(cls, tuple(immutable_types))

        is_immutable = functional.sequence(functional.typeof, functional.memoize_one_arg(is_immutable_type))

        def proxyfactory(proxytype):
            return functional.walker(functional.when_not(is_immutable, maybe_proxy(proxytype)))

        int_spec = SimpleNamespace(
            proxytype = self.int_proxytype,
            proxy = proxyfactory(self.int_proxytype),
            on_call = tracer('proxy.int.call', self.on_int_call),
            on_result = tracer('proxy.int.result'),
            on_error = tracer('proxy.int.error'),
            apply = self.int_apply,
        )

        ext_spec = SimpleNamespace(
            proxytype = self.ext_proxytype,
            proxy = proxyfactory(self.ext_proxytype),
            on_call = tracer('proxy.ext.call'),
            on_result = self.on_ext_result,
            on_error = self.on_ext_error,
            apply = self.ext_apply
        )

        int2ext, ext2int = adapter_pair1(int_spec, ext_spec)

        # self.ext_handler = thread_state.dispatch(default, internal = internal, external = external)

        def gateway(name, internal = functional.apply, external = functional.apply):
            default = tracer(name, unproxy_execute)
            return thread_state.dispatch(default, internal = internal, external = external)
    
        self.ext_handler = gateway('proxy.int.disabled.event', internal = self.wrap_int_to_ext(int2ext))
        self.int_handler = gateway('proxy.ext.disabled.event', external = self.wrap_ext_to_int(ext2int))

    # return (gateway('proxy.int.disabled.event', internal = wrap_int_to_ext(int_to_ext)),
    #         gateway('proxy.ext.disabled.event',
    #                 external = tracer('proxy.ext_to_int.wrap', ext_to_int)))

    #     # def adapter_pair1(int, ext):


    #     self.ext_handler, self.int_handler = gateway_pair(
    #         thread_state,
    #         self.tracer,
    #         immutable_types = immutable_types,
    #         wrap_int_to_ext = wrap_int_to_ext,
    #         int_proxytype = self.int_proxytype,
    #         ext_proxytype = self.ext_proxytype,
    #         ext_apply = ext_apply,
    #         on_int_call = on_int_call,
    #         on_ext_result = on_ext_result,
    #         on_ext_error = on_ext_error)


    def new_child_path(self, path):
        return path.parent / f'fork-{self.fork_counter}' / path.name

    def before_fork(self):
        self.saved_thread_state = self.thread_state.value
        self.thread_state.value = 'disabled'

    def after_fork_in_child(self):
        self.thread_state.value = self.saved_thread_state
        self.fork_counter = 0

    def after_fork_in_parent(self):
        self.thread_state.value = self.saved_thread_state
        self.fork_counter += 1

    def create_stub(self): return False
        
    def int_proxytype(self, cls):
        return dynamic_int_proxytype(
                handler = self.int_handler,
                cls = cls,
                bind = self.bind)

    def ext_proxytype(self, cls):
        assert isinstance(cls, type)
        if utils.is_extendable(cls):
            return self.extend_type(cls)
        else:    
            return instantiable_dynamic_proxytype(
                    handler = self.ext_handler, 
                    cls = cls,
                    thread_state = self.thread_state,
                    create_stub = self.create_stub())

    def extend_type(self, base):

        extended = extending_proxytype(
            cls = base,
            thread_state = self.thread_state, 
            ext_handler = self.ext_handler,
            int_handler = self.int_handler,
            on_subclass_new = self.bind,
            is_stub = self.create_stub())
        
        self.immutable_types.add(extended)

        return extended

    def __call__(self, obj):
        assert not isinstance(obj, BaseException)
        assert not isinstance(obj, utils.wrapped_function)
            
        if type(obj) == type:
            return self.ext_proxytype(obj)
            
        elif type(obj) == types.BuiltinFunctionType:
            return utils.wrapped_function(handler = self.ext_handler, target = obj)
        
        else:
            proxytype = dynamic_proxytype(handler = self.ext_handler, cls = type(obj))

            return utils.create_wrapped(proxytype, obj)
            # raise Exception(f'object {obj} was not proxied as its not a extensible type and is not callable')
    
