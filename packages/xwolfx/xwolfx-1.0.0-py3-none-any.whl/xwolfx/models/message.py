"""Message model for xwolfx"""

from .base import Base
from typing import Optional, Dict, Any

class Message(Base):
    """Message model representing a WOLF message"""
    
    def __init__(self, client, data: Dict[str, Any]):
        """Initialize message from data"""
        super().__init__(client)
        
        self.id = data.get('id')
        self.body = str(data.get('data', '')).strip() if data.get('data') else ''
        self.source_subscriber_id = self._get_originator_id(data)
        self.target_channel_id = self._get_target_channel_id(data)
        self.target_group_id = self.target_channel_id
        self.is_channel = data.get('isGroup', False)
        self.is_group = self.is_channel
        self.timestamp = data.get('timestamp')
        self.type = data.get('mimeType')
        self.embeds = data.get('embeds', [])
        self.metadata = data.get('metadata')
        self.edited = data.get('edited')
        
        # Check if this is a command (will be implemented when command handler is ready)
        self.is_command = False
    
    def _get_originator_id(self, data: Dict[str, Any]) -> Optional[int]:
        """Extract originator ID from various data formats"""
        originator = data.get('originator')
        if isinstance(originator, dict):
            return originator.get('id')
        elif isinstance(originator, (int, str)):
            return originator
        return data.get('subscriberId')
    
    def _get_target_channel_id(self, data: Dict[str, Any]) -> Optional[int]:
        """Extract target channel ID for group messages"""
        if not data.get('isGroup'):
            return None
        
        target_group_id = data.get('targetGroupId')
        if target_group_id:
            return target_group_id
        
        recipient = data.get('recipient')
        if isinstance(recipient, dict):
            return recipient.get('id')
        elif isinstance(recipient, (int, str)):
            return recipient
        
        return None
    
    async def reply(self, content: str, options: Optional[Dict] = None) -> bool:
        """Reply to the message"""
        if self.is_channel and self.target_channel_id:
            return await self.client.send_channel_message(self.target_channel_id, content, options)
        elif self.source_subscriber_id:
            return await self.client.send_private_message(self.source_subscriber_id, content, options)
        return False
    
    async def reply_private(self, content: str, options: Optional[Dict] = None) -> bool:
        """Send the message sender a private message"""
        if self.source_subscriber_id:
            return await self.client.send_private_message(self.source_subscriber_id, content, options)
        return False
    
    async def delete(self) -> bool:
        """Delete the message (channel messages only)"""
        if not self.is_channel:
            raise NotImplementedError("Deleting private messages is not supported")
        
        if self.target_channel_id and self.timestamp:
            return await self.client.delete_message(self.target_channel_id, self.timestamp)
        return False