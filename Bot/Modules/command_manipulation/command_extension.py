from Modules.utils import IterTools, StringTools
from Modules.command_manipulation._core import extension_decorator

def command_extension(*extensions):
    extensions = IterTools.for_each_item(
        extensions,
        StringTools.clean,
        lambda phrase: phrase.split(' ')
        )
    min_extension_size = IterTools.get_smallest_size(extensions)
    
    return extension_decorator(extensions, min_extension_size)