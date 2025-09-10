import retracesoftware.functional as functional
import retracesoftware_utils as utils
import retracesoftware.stream as stream

from retracesoftware.install.tracer import Tracer
from retracesoftware.proxy.thread import per_thread_messages
from retracesoftware.proxy.proxytype import dynamic_proxytype, dynamic_int_proxytype, extending_proxytype, make_extensible, dynamic_stubtype, stubtype_from_spec, Stub
# from retracesoftware.proxy.gateway import gateway_pair
from retracesoftware.proxy.record import ProxyRef, ProxySpec, Placeholder
from retracesoftware.proxy.proxysystem import ProxySystem

import os
import weakref
# we can have a dummy method descriptor, its has a __name__ and when called, returns the next element

# for types, we can patch the __new__ method
# do it from C and immutable types can be patched too
# patch the tp_new pointer?

class ReplayProxySystem(ProxySystem):
    
    def stubtype(self, cls):
        return dynamic_proxytype(handler = self.ext_handler, cls = cls)

    def create_stub(self): return True

    def stubtype_from_spec(self, spec):
        print (f'FOOO!!! {spec}')
        return stubtype_from_spec(
            handler = self.ext_handler,
            module = spec.module, 
            name = spec.name,
            methods = spec.methods,
            members = spec.members)

    @utils.striptraceback
    def next_result(self):
        while True:
            next = self.messages()

            if next == 'CALL':
                func = self.messages()
                args = self.messages()
                kwargs = self.messages()

                try:
                    func(*args, **kwargs)
                except:
                    pass

            elif next == 'RESULT':
                return self.messages()
            elif next == 'ERROR':
                err_type = self.messages()
                err_value = self.messages()
                utils.raise_exception(err_type, err_value)
            else:
                assert not isinstance(next, str)
                return next

    def bind(self, obj):
        read = self.messages()
        
        assert isinstance(read, Placeholder)

        self.bindings[read] = obj

    # def dynamic_path(self):
    #     if self.getpid() != self.pid:
    #         self.pid = self.getpid()
    #         # ok we are in child, calculate new path
    #         self.path = self.path / f'fork-{self.fork_counter}'
    #         self.fork_counter = 0
        
    #     return self.path

    def after_fork_in_child(self):
        self.reader.path = self.new_child_path(self.reader.path)
        super().after_fork_in_child()

    def __init__(self, 
                 thread_state,
                 immutable_types,
                 tracing_config,
                 path,
                 fork_path = []):
        
        # self.writer = writer
        # super().__init__(thread_state = thread_state)
        reader = stream.reader(path)

        self.bindings = utils.id_dict()
        self.set_thread_id = utils.set_thread_id
        self.fork_path = fork_path
        deserialize = functional.walker(self.bindings.get_else_key)

        self.messages = functional.sequence(per_thread_messages(reader), deserialize)

        # messages = reader

        def readnext():
            try:
                return self.messages()
            except Exception as error:
                self.thread_state.value = 'disabled'
                print(f'Error reading stream: {error}')
                os._exit(1)

            # print(f'read: {obj}')
            # return obj


        # lookup = weakref.WeakKeyDictionary()
        
        # debug = debug_level(config)

        # int_refs = {}
            
        def read_required(required):
            obj = readnext()
            if obj != required:
                print(f'Expected: {required} but got: {obj}')
                for i in range(5):
                    print(readnext())

                utils.sigtrap(None)
                os._exit(1)
                raise Exception(f'Expected: {required} but got: {obj}')

        def trace_writer(name, *args):
            print(f'Trace: {name} {args}')
            
            read_required('TRACE')
            read_required(name)

            for arg in args:
                read_required(arg)

        # self.tracer = Tracer(tracing_config, writer = trace_writer)
        # self.immutable_types = immutable_types

        self.reader = reader

        # def foo(cls):
        #     print(cls)
        #     assert isinstance(cls, type)
        #     immutable_types.add(cls)

        # add_stubtype = functional.side_effect(foo)
        add_stubtype = functional.side_effect(immutable_types.add)

        reader.type_deserializer[ProxyRef] = functional.sequence(lambda ref: ref.resolve(), self.stubtype, add_stubtype)
        reader.type_deserializer[ProxySpec] = functional.sequence(self.stubtype_from_spec, add_stubtype)

        # on_ext_result = functional.if_then_else(
        #     functional.is_instanceof(str), writer.handle('RESULT'), writer)

        # def int_proxytype(gateway):
        #     return lambda cls: dynamic_int_proxytype(handler = gateway, cls = cls, bind = self.bind)

        def is_stub_type(obj):
            return functional.typeof(obj) is type and issubclass(obj, Stub)

        create_stubs = functional.walker(functional.when(is_stub_type, lambda cls: cls()))

        self.ext_apply = functional.repeatedly(functional.sequence(self.next_result, create_stubs))
        
        def read_sync(): read_required('SYNC')

        self.sync = lambda function: utils.observer(on_call = functional.always(read_sync), function = function)
    
        super().__init__(thread_state = thread_state, 
                         tracer = Tracer(tracing_config, writer = trace_writer), 
                         immutable_types = immutable_types)

        # super().__init__(
        #     thread_state=thread_state, 
        #     immutable_types= immutable_types,
        #     tracer=self.tracer,
        #     ext_apply = ext_apply)
        
        # self.ext_handler, self.int_handler = gateway_pair(
        #     thread_state,
        #     self.tracer,
        #     immutable_types = immutable_types,
        #     ext_apply = ext_apply,
        #     int_proxytype = int_proxytype,
        #     ext_proxytype = functional.identity)

    # def extend_type(self, base):
        
    #     # ok, how to provide __getattr__ style access, 

    #     extended = extending_proxytype(
    #         cls = base,
    #         thread_state = self.thread_state, 
    #         int_handler = self.int_handler,
    #         ext_handler = self.ext_handler,
    #         on_subclass_new = self.bind,
    #         is_stub = True)

    #     self.immutable_types.add(extended)
    #     # proxytype = extending_proxytype(base)

    #     # make_extensible(cls = extended, 
    #     #                 int_handler = self.int_handler, 
    #     #                 ext_handler = self.ext_handler,
    #     #                 on_new = self.reader.supply)

    #     return extended
