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
        elif isinstance(originator, int):
            return originator
        elif isinstance(originator, str):
            try:
                return int(originator)
            except (ValueError, TypeError):
                pass
        subscriber_id = data.get('subscriberId')
        if isinstance(subscriber_id, int):
            return subscriber_id
        elif isinstance(subscriber_id, str):
            try:
                return int(subscriber_id)
            except (ValueError, TypeError):
                pass
        return None
    
    def _get_target_channel_id(self, data: Dict[str, Any]) -> Optional[int]:
        """Extract target channel ID for group messages"""
        if not data.get('isGroup'):
            return None
        
        target_group_id = data.get('targetGroupId')
        if isinstance(target_group_id, int):
            return target_group_id
        elif isinstance(target_group_id, str):
            try:
                return int(target_group_id)
            except (ValueError, TypeError):
                pass
        
        recipient = data.get('recipient')
        if isinstance(recipient, dict):
            recipient_id = recipient.get('id')
            if isinstance(recipient_id, int):
                return recipient_id
            elif isinstance(recipient_id, str):
                try:
                    return int(recipient_id)
                except (ValueError, TypeError):
                    pass
        elif isinstance(recipient, int):
            return recipient
        elif isinstance(recipient, str):
            try:
                return int(recipient)
            except (ValueError, TypeError):
                pass
        
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