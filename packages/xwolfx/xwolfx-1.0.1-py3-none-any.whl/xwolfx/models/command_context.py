"""Command context model for xwolfx"""

from .base import Base
from typing import Optional, Dict, Any, List

class CommandContext(Base):
    """Command context for handling bot commands"""
    
    def __init__(self, client, data: Dict[str, Any]):
        """Initialize command context"""
        super().__init__(client)
        
        self.is_channel = data.get('isChannel', False)
        self.is_group = data.get('isGroup', self.is_channel)
        self.argument = data.get('argument', '')
        self.target_channel_id = data.get('targetChannelId')
        self.source_subscriber_id = data.get('sourceSubscriberId')
        self.timestamp = data.get('timestamp')
        self.type = data.get('type')
        self.route: List[Dict] = data.get('route', [])
        self.language = data.get('language', 'en')
    
    def get_phrase(self, phrase_name: str) -> str:
        """Get a phrase by name (placeholder implementation)"""
        # This would normally lookup phrases from the phrase system
        return f"Phrase: {phrase_name}"
    
    async def reply(self, content: str, options: Optional[Dict] = None) -> bool:
        """Reply to the command"""
        if self.is_channel and self.target_channel_id:
            return await self.client.send_channel_message(self.target_channel_id, content, options)
        elif self.source_subscriber_id:
            return await self.client.send_private_message(self.source_subscriber_id, content, options)
        return False