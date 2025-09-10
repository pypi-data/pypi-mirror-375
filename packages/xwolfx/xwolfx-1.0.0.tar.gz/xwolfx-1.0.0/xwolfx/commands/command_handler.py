"""Command handler for xwolfx"""

from typing import List, Dict, Any, Optional, Callable
from ..models.command_context import CommandContext

class CommandHandler:
    """Command handler for processing bot commands"""
    
    def __init__(self, client):
        """Initialize command handler"""
        self.client = client
        self._commands: List = []
        
        # Set up message event listener
        self.client.on('message', self._handle_message)
    
    def register(self, commands):
        """Register commands"""
        if not isinstance(commands, list):
            commands = [commands]
        
        if not commands:
            raise ValueError("Commands cannot be an empty array")
        
        self._commands = commands
    
    def is_command(self, message_body: str) -> bool:
        """Check if a message is a command"""
        if not message_body or not self._commands:
            return False
        
        # Simple command detection - check if message starts with any registered command
        first_word = message_body.split()[0] if message_body.split() else ""
        
        for command in self._commands:
            # Simplified phrase matching
            if hasattr(command, 'name') and first_word.startswith('!'):
                return True
        
        return False
    
    async def _handle_message(self, message):
        """Handle incoming message for command processing"""
        if not message.body:
            return False
        
        # Skip if sender is the bot itself (basic self-ignore)
        if hasattr(self.client, 'current_subscriber') and \
           self.client.current_subscriber and \
           message.source_subscriber_id == self.client.current_subscriber.get('id'):
            return False
        
        # Create context for command processing
        context_data = {
            'isChannel': message.is_channel,
            'isGroup': message.is_group,
            'argument': message.body,
            'targetChannelId': message.target_channel_id,
            'sourceSubscriberId': message.source_subscriber_id,
            'timestamp': message.timestamp,
            'type': message.type,
            'route': []
        }
        
        command_context = self._get_command_context(self._commands, context_data)
        
        if not command_context.get('callback'):
            return False
        
        callback = command_context['callback']
        del command_context['callback']
        
        # Execute the command
        context = CommandContext(self.client, command_context)
        return await callback(context)
    
    def _get_command_context(self, commands: List, context: Dict[str, Any]) -> Dict[str, Any]:
        """Find matching command and prepare context"""
        for command in commands:
            if hasattr(command, 'name') and hasattr(command, 'handlers'):
                # Simple command matching - check if message starts with command trigger
                if context['argument'].startswith('!'):
                    command_word = context['argument'].split()[0][1:]  # Remove ! prefix
                    
                    if command.name.endswith(f"_{command_word}") or command_word in command.name:
                        # Set callback based on context type
                        if 'both' in command.handlers:
                            context['callback'] = command.handlers['both']
                        elif context['isChannel'] and 'channel' in command.handlers:
                            context['callback'] = command.handlers['channel']
                        elif not context['isChannel'] and 'private' in command.handlers:
                            context['callback'] = command.handlers['private']
                        
                        # Remove command from argument
                        words = context['argument'].split()
                        if words:
                            context['argument'] = ' '.join(words[1:])
                        
                        break
        
        return context