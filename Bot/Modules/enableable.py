from typing import Protocol

# interface
class Enableable:
    is_enable: bool
    
    async def initiate(self) -> None:
        """Initiates the objects function, whatever it does
        """
        ...
    def enable(self) -> None:
        """Enables the object
        """
        ...
    def disable(self) -> None: 
        """Disables the object
        """
        ...