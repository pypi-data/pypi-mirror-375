"""Command class for xwolfx"""

class Command:
    """Basic command class for handling bot commands"""
    
    def __init__(self, name, handlers=None, sub_commands=None):
        self.name = name
        self.handlers = handlers or {}
        self.sub_commands = sub_commands or []
    
    def execute(self, context, command_type='both'):
        """Execute the command with given context"""
        if command_type in self.handlers:
            return self.handlers[command_type](context)
        elif 'both' in self.handlers:
            return self.handlers['both'](context)
        else:
            raise NotImplementedError(f"Handler for {command_type} not implemented")