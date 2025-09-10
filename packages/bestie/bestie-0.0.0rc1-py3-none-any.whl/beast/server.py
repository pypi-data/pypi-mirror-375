"""
Generic Beast format server for broadcasting Mode-S messages.
"""

import socket
import threading
import time
import logging
from typing import List, Optional
from .encoder import BeastEncoder
from .types import BeastMessage


class BeastServer:
    """
    Generic Beast format server that broadcasts Mode-S messages to connected clients.
    
    This server handles the networking layer and Beast format encoding but does not
    include any message generation or timing logic - that should be handled externally.
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 30005):
        """
        Initialize Beast server.
        
        Args:
            host: Server bind address (default: 0.0.0.0)
            port: Server bind port (default: 30005)
        """
        self.host = host
        self.port = port
        self.running = False
        self.clients: List[socket.socket] = []
        self.server_socket: Optional[socket.socket] = None
        self.client_lock = threading.Lock()
        self.encoder = BeastEncoder()
        
    def start(self) -> bool:
        """
        Start the Beast server.
        
        Returns:
            True if server started successfully, False otherwise
        """
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            self.running = True
            logging.info(f"Beast server started on {self.host}:{self.port}")
            
            # Start client acceptance thread
            accept_thread = threading.Thread(target=self._accept_clients, daemon=True)
            accept_thread.start()
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to start Beast server: {e}")
            return False
    
    def stop(self):
        """Stop the Beast server and close all connections."""
        self.running = False
        
        # Close all client connections
        with self.client_lock:
            for client in self.clients[:]:
                try:
                    client.close()
                except Exception:
                    pass
            self.clients.clear()
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception:
                pass
            self.server_socket = None
            
        logging.info("Beast server stopped")
    
    def broadcast_message(self, modes_message: bytes, 
                         timestamp: Optional[int] = None,
                         signal_level: int = 0xFF) -> bool:
        """
        Broadcast a Mode-S message to all connected clients.
        
        Args:
            modes_message: Raw Mode-S message (7 or 14 bytes)
            timestamp: Optional timestamp (microseconds since epoch)
            signal_level: Signal level (0-255, default 255)
            
        Returns:
            True if message was broadcast successfully
        """
        if not self.running:
            return False
        
        try:
            # Encode message in Beast format
            beast_msg = self.encoder.encode_message(modes_message, timestamp, signal_level)
            return self._send_to_clients(beast_msg.raw_data)
        except ValueError as e:
            logging.error(f"Failed to encode message: {e}")
            return False
    
    def broadcast_beast_message(self, beast_message: BeastMessage) -> bool:
        """
        Broadcast a pre-encoded Beast message to all connected clients.
        
        Args:
            beast_message: Already encoded Beast message
            
        Returns:
            True if message was broadcast successfully
        """
        if not self.running:
            return False
        
        return self._send_to_clients(beast_message.raw_data)
    
    def broadcast_messages(self, messages: List[bytes],
                          base_timestamp: Optional[int] = None,
                          interval_us: int = 100000,
                          signal_level: int = 0xFF) -> int:
        """
        Broadcast multiple messages with sequential timestamps.
        
        Args:
            messages: List of Mode-S messages
            base_timestamp: Base timestamp (None = current time)
            interval_us: Interval between messages in microseconds
            signal_level: Signal level for all messages
            
        Returns:
            Number of messages broadcast successfully
        """
        if not self.running:
            return 0
        
        if base_timestamp is None:
            base_timestamp = int(time.time() * 1_000_000)
        
        success_count = 0
        for i, message in enumerate(messages):
            timestamp = (base_timestamp + (i * interval_us)) & 0xFFFFFFFFFFFF
            if self.broadcast_message(message, timestamp, signal_level):
                success_count += 1
            else:
                break
        
        return success_count
    
    def get_client_count(self) -> int:
        """Get the number of connected clients."""
        with self.client_lock:
            return len(self.clients)
    
    def _accept_clients(self):
        """Accept incoming client connections."""
        if not self.server_socket:
            return
            
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                with self.client_lock:
                    self.clients.append(client_socket)
                logging.info(f"Client connected from {address} (total: {len(self.clients)})")
            except Exception as e:
                if self.running:
                    logging.error(f"Error accepting client: {e}")
    
    def _send_to_clients(self, data: bytes) -> bool:
        """
        Send data to all connected clients.
        
        Args:
            data: Raw data to send
            
        Returns:
            True if sent to at least one client
        """
        if not data:
            return False
        
        with self.client_lock:
            disconnected_clients = []
            
            for client in self.clients:
                try:
                    client.send(data)
                except Exception:
                    disconnected_clients.append(client)
            
            # Remove disconnected clients
            for client in disconnected_clients:
                try:
                    client.close()
                except Exception:
                    pass
                self.clients.remove(client)
                
            if disconnected_clients:
                logging.info(f"Removed {len(disconnected_clients)} disconnected clients")
            
            return len(self.clients) > 0