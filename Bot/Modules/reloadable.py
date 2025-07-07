import asyncio
import functools
import weakref
import inspect

class ReloadableComponent:
    _instances: weakref.WeakSet["ReloadableComponent"] = weakref.WeakSet()
    
    _loop: asyncio.AbstractEventLoop | None
    """
    The event loop used to schedule async load/reload.
    """
    
    def __init__(self, *args, **kwargs):
        pass
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        _subclass_init = cls.__init__
        
        @functools.wraps(_subclass_init)
        def __init__(self, *args, **kwargs):
            ReloadableComponent._instances.add(self)
            
            self._loop = None
            
            _subclass_init(self, *args, **kwargs)
            self._dispatch_function(self.load)
        
        cls.__init__ = __init__
    
    
    def _dispatch_function(self, func):
        if not inspect.iscoroutinefunction(func):
            return func()
        
        if self._loop is None:
            try: 
                self._loop = asyncio.get_running_loop()
            except RuntimeError:
                raise RuntimeError(
                "There is no loop present in this thread, you should pass self._loop manually"
                )
        
        self._loop.create_task(func())
    
    
    def load(self):
        """
        Called automatically after initialization to perform setup or resource loading.
        
        This method is intended to be overridden by subclasses to define any setup,
        resource allocation, or initialization logic required by the component.
        It is automatically called at the end of the component's __init__ method,
        so subclasses do not need to call it manually.
        
        If this method is implemented as an async coroutine, 
        **self._loop must be set to a valid asyncio event loop before this method is called**.
        Failure to set self._loop will result in errors or unexpected behavior.
        
        Override this method to implement custom loading behavior for your component.
        """
        pass
    
    
    def reload(self):
        """
        Reloads the module or component.
        
        This method **must** be overridden by subclasses to implement custom
        reload logic when the bot is reloaded. It is called automatically during
        the bot's reload process to allow for resource cleanup, reinitialization,
        or other necessary updates.
        
        If this method is implemented as an async coroutine, 
        **self._loop must be set to a valid asyncio event loop before this method is called**.
        Failure to set self._loop will result in errors or unexpected behavior.
        
        Raises:
            NotImplementedError: If the method is not overridden in a subclass.
        """
        raise NotImplementedError("Subclasses of ReloadableComponent must implement the reload() method.")
    
    
    @classmethod
    def reload_all_instances(cls):
        """Attempts to reload all instances of ReloadableComponent
        """
        for instance in cls._instances:
            try:
                instance._dispatch_function(instance.reload)
            except RuntimeError as e:
                print(f"[[WARNING]]: Failed to reload {instance.__class__.__name__} — REASON: {e}")
                print(e)
