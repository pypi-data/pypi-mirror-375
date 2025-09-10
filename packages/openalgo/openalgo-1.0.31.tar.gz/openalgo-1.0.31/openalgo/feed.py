# -*- coding: utf-8 -*-
"""
OpenAlgo WebSocket API Documentation - Feed Methods
    https://docs.openalgo.in
"""

import json
import threading
import time
from typing import List, Dict, Any, Callable, Optional
import websocket
from .base import BaseAPI

class FeedAPI(BaseAPI):
    """
    Market data feed API methods for OpenAlgo using WebSockets.
    Inherits from the BaseAPI class.
    """

    def __init__(self, api_key, host="http://127.0.0.1:5000", version="v1", ws_port=8765, ws_url=None):
        """
        Initialize the FeedAPI object with API key and optionally a host URL, API version, and WebSocket details.

        Attributes:
        - api_key (str): User's API key.
        - host (str): Base URL for the API endpoints. Defaults to localhost.
        - version (str): API version. Defaults to "v1".
        - ws_port (int): WebSocket server port. Defaults to 8765.
        - ws_url (str, optional): Custom WebSocket URL. If provided, this overrides host and ws_port settings.
        """
        super().__init__(api_key, host, version)
        
        # WebSocket configuration
        self.ws_port = ws_port
        
        # Use custom WebSocket URL if provided
        if ws_url:
            self.ws_url = ws_url
        else:
            # Extract host without protocol for WebSocket
            if host.startswith("http://"):
                self.ws_host = host[7:]
            elif host.startswith("https://"):
                self.ws_host = host[8:]
            else:
                self.ws_host = host
                
            # Remove any path component and port if present
            self.ws_host = self.ws_host.split('/')[0].split(':')[0]
            
            # Create default WebSocket URL
            self.ws_url = f"ws://{self.ws_host}:{self.ws_port}"
        self.ws = None
        self.connected = False
        self.authenticated = False
        self.ws_thread = None
        
        # Message management
        self.message_queue = []
        self.lock = threading.Lock()
        
        # Data storage
        self.ltp_data = {}  # Structure: {'EXCHANGE:SYMBOL': {'price': price, 'timestamp': timestamp}}
        self.quotes_data = {}  # Structure: {'EXCHANGE:SYMBOL': {'open': open, 'high': high, 'low': low, 'close': close, 'ltp': ltp, 'timestamp': timestamp}}
        self.depth_data = {}  # Structure: {'EXCHANGE:SYMBOL': {'ltp': ltp, 'timestamp': timestamp, 'depth': {'buy': [...], 'sell': [...]}}}
        
        # Callback registry
        self.ltp_callback = None
        self.quote_callback = None
        self.quotes_callback = None
        self.depth_callback = None

    def connect(self) -> bool:
        """
        Connect to the WebSocket server and authenticate.
        
        Returns:
            bool: True if connection and authentication are successful, False otherwise.
        """
        try:
            def on_message(ws, message):
                self._process_message(message)
                
            def on_error(ws, error):
                print(f"WebSocket error: {error}")
                
            def on_open(ws):
                print(f"Connected to {self.ws_url}")
                self.connected = True
                self._authenticate()
                
            def on_close(ws, close_status_code, close_reason):
                print(f"Disconnected from {self.ws_url}")
                self.connected = False
                self.authenticated = False
            
            # Initialize WebSocket connection
            self.ws = websocket.WebSocketApp(
                self.ws_url,
                on_message=on_message,
                on_error=on_error,
                on_open=on_open,
                on_close=on_close
            )
            
            # Start WebSocket connection in a separate thread
            self.ws_thread = threading.Thread(target=self.ws.run_forever)
            self.ws_thread.daemon = True
            self.ws_thread.start()
            
            # Wait for connection to establish
            timeout = 5
            start_time = time.time()
            while not self.connected and time.time() - start_time < timeout:
                time.sleep(0.1)
            
            if not self.connected:
                print("Failed to connect to the WebSocket server")
                return False
                
            # Wait for authentication to complete
            timeout = 5
            start_time = time.time()
            while not self.authenticated and time.time() - start_time < timeout and self.connected:
                time.sleep(0.1)
                
            return self.authenticated
            
        except Exception as e:
            print(f"Error connecting to WebSocket: {e}")
            return False

    def disconnect(self) -> None:
        """Disconnect from the WebSocket server."""
        if self.ws:
            self.ws.close()
            # Wait for websocket to close
            timeout = 2
            start_time = time.time()
            while self.connected and time.time() - start_time < timeout:
                time.sleep(0.1)
            self.ws = None
            self.connected = False
            self.authenticated = False

    def _authenticate(self) -> None:
        """Authenticate with the WebSocket server using the API key."""
        if not self.connected:
            print("Cannot authenticate: not connected")
            return
            
        auth_msg = {
            "action": "authenticate",
            "api_key": self.api_key
        }
        
        # Print authentication info like the test example
        print(f"Authenticating with API key: {self.api_key[:8]}...{self.api_key[-8:]}")
        self.ws.send(json.dumps(auth_msg))

    def _process_message(self, message_str: str) -> None:
        """
        Process incoming WebSocket messages.
        
        Args:
            message_str (str): The message string received from the WebSocket.
        """
        try:
            message = json.loads(message_str)
            
            # Handle authentication response
            if message.get("type") == "auth":
                # Print full authentication response like in the test example
                print(f"Authentication response: {message}")
                if message.get("status") == "success":
                    self.authenticated = True
                    print("Authentication successful!")
                else:
                    print(f"Authentication failed: {message}")
                return
                
            # Handle subscription response
            if message.get("type") == "subscribe":
                print(f"Subscription response: {message}")
                return
                
            # Handle market data
            if message.get("type") == "market_data":
                exchange = message.get("exchange")
                symbol = message.get("symbol")
                if exchange and symbol:
                    mode = message.get("mode")
                    market_data = message.get("data", {})
                    
                    # Handle LTP data (mode 1)
                    if mode == 1 and "ltp" in market_data:
                        with self.lock:
                            # Get LTP and timestamp from the message
                            ltp = market_data.get("ltp")
                            timestamp = market_data.get("timestamp", int(time.time() * 1000))
                            
                            # Store both price and timestamp with format 'EXCHANGE:SYMBOL'
                            symbol_key = f"{exchange}:{symbol}"
                            self.ltp_data[symbol_key] = {
                                'price': ltp,
                                'timestamp': timestamp
                            }
                            
                            # Print when LTP data is received (same as test file)
                            print(f"LTP {symbol_key}: {ltp} | Time: {timestamp}")
                        
                        # Invoke callback if set
                        if self.ltp_callback:
                            try:
                                # Create a clean market data update without redundant fields
                                clean_data = {
                                    'type': 'market_data',
                                    'symbol': symbol,
                                    'exchange': exchange,
                                    'mode': mode,
                                    'data': {
                                        'ltp': ltp,
                                        'timestamp': timestamp
                                    }
                                }
                                # Include LTT if available in original data
                                if 'ltt' in market_data:
                                    clean_data['data']['ltt'] = market_data['ltt']
                                # Check if ltt is in the nested data structure (which seems to be the case)
                                elif 'ltt' in market_data.get('data', {}):
                                    clean_data['data']['ltt'] = market_data['data']['ltt']
                                    
                                # Pass the cleaned message to callback
                                self.ltp_callback(clean_data)
                            except Exception as e:
                                print(f"Error in LTP callback: {str(e)}")                 
                    # Handle Quotes data (mode 2)
                    elif mode == 2:
                        with self.lock:
                            # Extract quote data fields
                            quote_data = {
                                'open': market_data.get("open", 0),
                                'high': market_data.get("high", 0),
                                'low': market_data.get("low", 0),
                                'close': market_data.get("close", 0),
                                'ltp': market_data.get("ltp", 0),
                                'volume': market_data.get("volume", 0),
                                'timestamp': market_data.get("timestamp", int(time.time() * 1000))
                            }
                            
                            # Store quote data with format 'EXCHANGE:SYMBOL'
                            symbol_key = f"{exchange}:{symbol}"
                            self.quotes_data[symbol_key] = quote_data
                            
                            # Print when quote data is received (same as test file)
                            print(f"Quote {symbol_key}: Open: {quote_data['open']} | High: {quote_data['high']} | "
                                  f"Low: {quote_data['low']} | Close: {quote_data['close']} | "
                                  f"LTP: {quote_data['ltp']}")
                        
                        # Invoke callback if set
                        if self.quote_callback:
                            try:
                                # Create a clean market data update without redundant fields
                                clean_data = {
                                    'type': 'market_data',
                                    'symbol': symbol,
                                    'exchange': exchange,
                                    'mode': mode,
                                    'data': quote_data.copy()
                                }
                                # Pass the cleaned message to callback
                                self.quote_callback(clean_data)
                            except Exception as e:
                                print(f"Error in Quote callback: {str(e)}")                 
                    # Handle Market Depth data (mode 3)
                    elif mode == 3 and "depth" in market_data:
                        with self.lock:
                            # Extract depth data
                            depth_data = {
                                'ltp': market_data.get("ltp", 0),
                                'timestamp': market_data.get("timestamp", int(time.time() * 1000)),
                                'depth': market_data.get("depth", {"buy": [], "sell": []})
                            }
                            
                            # Store depth data with format 'EXCHANGE:SYMBOL'
                            symbol_key = f"{exchange}:{symbol}"
                            self.depth_data[symbol_key] = depth_data
                            
                            # Print when depth data is received
                            buy_depth = depth_data.get('depth', {}).get('buy', [])
                            sell_depth = depth_data.get('depth', {}).get('sell', [])
                            
                            print(f"\nDepth {symbol_key} - LTP: {depth_data.get('ltp')}")
                            
                            # Print buy depth summary
                            print("\nBUY DEPTH:")
                            print("-" * 40)
                            print(f"{'Level':<6} {'Price':<10} {'Quantity':<10} {'Orders':<10}")
                            print("-" * 40)
                            
                            if buy_depth:
                                for i, level in enumerate(buy_depth):
                                    print(f"{i+1:<6} {level.get('price', 'N/A'):<10} {level.get('quantity', 'N/A'):<10} {level.get('orders', 'N/A'):<10}")
                            else:
                                print("No buy depth data available")
                                
                            # Print sell depth summary
                            print("\nSELL DEPTH:")
                            print("-" * 40)
                            print(f"{'Level':<6} {'Price':<10} {'Quantity':<10} {'Orders':<10}")
                            print("-" * 40)
                            
                            if sell_depth:
                                for i, level in enumerate(sell_depth):
                                    print(f"{i+1:<6} {level.get('price', 'N/A'):<10} {level.get('quantity', 'N/A'):<10} {level.get('orders', 'N/A'):<10}")
                            else:
                                print("No sell depth data available")
                                
                            print("-" * 40)
                        
                        # Invoke callback if set
                        if self.depth_callback:
                            try:
                                # Create a clean market data update
                                clean_data = {
                                    'type': 'market_data',
                                    'symbol': symbol,
                                    'exchange': exchange,
                                    'mode': mode,
                                    'data': depth_data.copy()
                                }
                                # Pass the cleaned message to callback
                                self.depth_callback(clean_data)
                            except Exception as e:
                                print(f"Error in Depth callback: {str(e)}")
                        
        except json.JSONDecodeError:
            print(f"Invalid JSON message: {message_str}")
        except Exception as e:
            print(f"Error handling message: {e}")

    def subscribe_ltp(self, instruments: List[Dict[str, Any]], on_data_received: Optional[Callable] = None) -> bool:
        """
        Subscribe to LTP updates for instruments.
        
        Args:
            instruments: List of instrument dictionaries with keys:
                - exchange (str): Exchange code (e.g., 'NSE', 'BSE', 'NFO')
                - symbol (str): Trading symbol
                - exchange_token (str, optional): Exchange token for the instrument
            on_data_received: Callback function for data updates
                
        Returns:
            bool: True if subscription successful, False otherwise
        """
        if not self.connected:
            print("Not connected to WebSocket server")
            return False
            
        if not self.authenticated:
            print("Not authenticated with WebSocket server")
            return False
                
        # Set callback if provided
        if on_data_received:
            self.ltp_callback = on_data_received
        
        # Subscribe to each instrument individually (matching the working test implementation)
        for instrument in instruments:
            exchange = instrument.get("exchange")
            symbol = instrument.get("symbol")
            exchange_token = instrument.get("exchange_token")
            
            # If only exchange_token is provided, we need to map it to a symbol
            if not symbol and exchange_token:
                symbol = exchange_token
                
            if not exchange or not symbol:
                print(f"Invalid instrument: {instrument}")
                continue
                
            # Use the exact same message format as the working test
            subscription_msg = {
                "action": "subscribe",
                "symbol": symbol,
                "exchange": exchange,
                "mode": 1,  # 1 for LTP
                "depth": 5  # Default depth level
            }
            
            print(f"Subscribing to {exchange}:{symbol} LTP")
            try:
                self.ws.send(json.dumps(subscription_msg))
                
                # Small delay to ensure the message is processed separately (just like the test)
                time.sleep(0.1)
            except Exception as e:
                print(f"Error subscribing to {exchange}:{symbol}: {e}")
                return False
        
        return True

    def unsubscribe_ltp(self, instruments: List[Dict[str, Any]]) -> bool:
        """
        Unsubscribe from LTP updates for instruments.
        
        Args:
            instruments: List of instrument dictionaries with keys:
                - exchange (str): Exchange code (e.g., 'NSE', 'BSE', 'NFO')
                - symbol (str): Trading symbol
                - exchange_token (str, optional): Exchange token for the instrument
                
        Returns:
            bool: True if unsubscription successful, False otherwise
        """
        if not self.connected or not self.authenticated:
            return False
        
        # Unsubscribe from each instrument individually (matching the working test implementation)
        for instrument in instruments:
            exchange = instrument.get("exchange")
            symbol = instrument.get("symbol")
            exchange_token = instrument.get("exchange_token")
            
            # If only exchange_token is provided, we need to map it to a symbol
            if not symbol and exchange_token:
                symbol = exchange_token
                
            if not exchange or not symbol:
                print(f"Invalid instrument: {instrument}")
                continue
                
            # Print information about unsubscription
            print(f"Unsubscribing from {exchange}:{symbol}")
            
            # Use the exact same message format as the working test
            unsubscribe_msg = {
                "action": "unsubscribe",
                "symbol": symbol,
                "exchange": exchange,
                "mode": 1  # 1 for LTP
            }
            
            try:
                self.ws.send(json.dumps(unsubscribe_msg))
                
                # Clean up the data
                with self.lock:
                    symbol_key = f"{exchange}:{symbol}"
                    if symbol_key in self.ltp_data:
                        del self.ltp_data[symbol_key]
                
                # Small delay to ensure the message is processed separately
                time.sleep(0.1)
            except Exception as e:
                print(f"Error unsubscribing from {exchange}:{symbol}: {e}")
                return False
        
        return True
        
    def subscribe_quote(self, instruments: List[Dict[str, Any]], on_data_received: Optional[Callable] = None) -> bool:
        """
        Subscribe to Quote updates for instruments.
        
        Args:
            instruments: List of instrument dictionaries with keys:
                - exchange (str): Exchange code (e.g., 'NSE', 'BSE', 'NFO')
                - symbol (str): Trading symbol
                - exchange_token (str, optional): Exchange token for the instrument
            on_data_received: Callback function for data updates
            
        Returns:
            bool: True if subscription request sent successfully
        """
        if not self.connected:
            print("Not connected to WebSocket server. Connect first.")
            return False
            
        if not self.authenticated:
            print("Not authenticated with WebSocket server")
            return False
                
        # Set callback if provided
        if on_data_received:
            self.quote_callback = on_data_received
        
        # Subscribe to each instrument individually
        for instrument in instruments:
            exchange = instrument.get("exchange")
            symbol = instrument.get("symbol")
            exchange_token = instrument.get("exchange_token")
            
            # If only exchange_token is provided, we need to map it to a symbol
            if not symbol and exchange_token:
                symbol = exchange_token
                
            if not exchange or not symbol:
                print(f"Invalid instrument: {instrument}")
                continue
                
            # Use the same message format as for LTP but with mode 2 for Quote
            subscription_msg = {
                "action": "subscribe",
                "symbol": symbol,
                "exchange": exchange,
                "mode": 2,  # 2 for Quote
                "depth": 5  # Default depth level
            }
            
            print(f"Subscribing to {exchange}:{symbol} Quote")
            try:
                self.ws.send(json.dumps(subscription_msg))
                
                # Small delay to ensure the message is processed separately
                time.sleep(0.1)
            except Exception as e:
                print(f"Error subscribing to {exchange}:{symbol}: {e}")
                return False
        
        return True
    
    def unsubscribe_quote(self, instruments: List[Dict[str, Any]]) -> bool:
        """
        Unsubscribe from Quote updates for instruments.
        
        Args:
            instruments: List of instrument dictionaries with keys:
                - exchange (str): Exchange code (e.g., 'NSE', 'BSE', 'NFO')
                - symbol (str): Trading symbol
                - exchange_token (str, optional): Exchange token for the instrument
                
        Returns:
            bool: True if unsubscription successful, False otherwise
        """
        if not self.connected or not self.authenticated:
            return False
        
        # Unsubscribe from each instrument individually
        for instrument in instruments:
            exchange = instrument.get("exchange")
            symbol = instrument.get("symbol")
            exchange_token = instrument.get("exchange_token")
            
            # If only exchange_token is provided, we need to map it to a symbol
            if not symbol and exchange_token:
                symbol = exchange_token
                
            if not exchange or not symbol:
                print(f"Invalid instrument: {instrument}")
                continue
                
            # Print information about unsubscription
            print(f"Unsubscribing from {exchange}:{symbol}")
            
            # Use the same message format as for LTP but with mode 2 for Quote
            unsubscribe_msg = {
                "action": "unsubscribe",
                "symbol": symbol,
                "exchange": exchange,
                "mode": 2  # 2 for Quote
            }
            
            try:
                self.ws.send(json.dumps(unsubscribe_msg))
                
                # Clean up the data
                with self.lock:
                    symbol_key = f"{exchange}:{symbol}"
                    if symbol_key in self.quotes_data:
                        del self.quotes_data[symbol_key]
                
                # Small delay to ensure the message is processed separately
                time.sleep(0.1)
            except Exception as e:
                print(f"Error unsubscribing from {exchange}:{symbol}: {e}")
                return False
        
        return True
        
    def subscribe_depth(self, instruments: List[Dict[str, Any]], on_data_received: Optional[Callable] = None) -> bool:
        """
        Subscribe to Market Depth updates for instruments.
        
        Args:
            instruments: List of instrument dictionaries with keys:
                - exchange (str): Exchange code (e.g., 'NSE', 'BSE', 'NFO')
                - symbol (str): Trading symbol
                - exchange_token (str, optional): Exchange token for the instrument
            on_data_received: Callback function for data updates
            
        Returns:
            bool: True if subscription request sent successfully
        """
        if not self.connected:
            print("Not connected to WebSocket server. Connect first.")
            return False
            
        if not self.authenticated:
            print("Not authenticated with WebSocket server")
            return False
                
        # Set callback if provided
        if on_data_received:
            self.depth_callback = on_data_received
        
        # Subscribe to each instrument individually
        for instrument in instruments:
            exchange = instrument.get("exchange")
            symbol = instrument.get("symbol")
            exchange_token = instrument.get("exchange_token")
            
            # If only exchange_token is provided, we need to map it to a symbol
            if not symbol and exchange_token:
                symbol = exchange_token
                
            if not exchange or not symbol:
                print(f"Invalid instrument: {instrument}")
                continue
                
            # Use the same message format as for Quote but with mode 3 for Market Depth
            subscription_msg = {
                "action": "subscribe",
                "symbol": symbol,
                "exchange": exchange,
                "mode": 3,  # 3 for Market Depth
                "depth": 5  # Default depth level
            }
            
            print(f"Subscribing to {exchange}:{symbol} Market Depth")
            try:
                self.ws.send(json.dumps(subscription_msg))
                
                # Small delay to ensure the message is processed separately
                time.sleep(0.1)
            except Exception as e:
                print(f"Error subscribing to {exchange}:{symbol}: {e}")
                return False
        
        return True
    
    def unsubscribe_depth(self, instruments: List[Dict[str, Any]]) -> bool:
        """
        Unsubscribe from Market Depth updates for instruments.
        
        Args:
            instruments: List of instrument dictionaries with keys:
                - exchange (str): Exchange code (e.g., 'NSE', 'BSE', 'NFO')
                - symbol (str): Trading symbol
                - exchange_token (str, optional): Exchange token for the instrument
                
        Returns:
            bool: True if unsubscription successful, False otherwise
        """
        if not self.connected or not self.authenticated:
            return False
        
        # Unsubscribe from each instrument individually
        for instrument in instruments:
            exchange = instrument.get("exchange")
            symbol = instrument.get("symbol")
            exchange_token = instrument.get("exchange_token")
            
            # If only exchange_token is provided, we need to map it to a symbol
            if not symbol and exchange_token:
                symbol = exchange_token
                
            if not exchange or not symbol:
                print(f"Invalid instrument: {instrument}")
                continue
                
            # Print information about unsubscription
            print(f"Unsubscribing from {exchange}:{symbol}")
            
            # Use the same message format as for Quote but with mode 3 for Market Depth
            unsubscribe_msg = {
                "action": "unsubscribe",
                "symbol": symbol,
                "exchange": exchange,
                "mode": 3  # 3 for Market Depth
            }
            
            try:
                self.ws.send(json.dumps(unsubscribe_msg))
                
                # Clean up the data
                with self.lock:
                    symbol_key = f"{exchange}:{symbol}"
                    if symbol_key in self.depth_data:
                        del self.depth_data[symbol_key]
                
                # Small delay to ensure the message is processed separately
                time.sleep(0.1)
            except Exception as e:
                print(f"Error unsubscribing from {exchange}:{symbol}: {e}")
                return False
        
        return True

    def get_ltp(self, exchange: str = None, symbol: str = None) -> Dict[str, Any]:
        """
        Get the latest LTP data in nested format.
        
        Args:
            exchange (str, optional): Filter by exchange
            symbol (str, optional): Filter by symbol (requires exchange to be specified)
            
        Returns:
            dict: Dictionary with LTP data in nested format:
                {"ltp": {"EXCHANGE": {"SYMBOL": {"timestamp": timestamp, "ltp": price}}}}
        """
        with self.lock:
            # Create nested format response
            result = {"ltp": {}}
            
            # Process each item in the data structure
            for symbol_key, data in self.ltp_data.items():
                # Extract exchange and symbol from the key (format: "EXCHANGE:SYMBOL")
                if ":" in symbol_key:
                    parts = symbol_key.split(":")
                    ex = parts[0]  # Exchange
                    sym = parts[1]  # Symbol
                    
                    # Filter by exchange if specified
                    if exchange and ex != exchange:
                        continue
                        
                    # Filter by symbol if specified
                    if symbol and sym != symbol:
                        continue
                    
                    # Initialize exchange dict if not exists
                    if ex not in result["ltp"]:
                        result["ltp"][ex] = {}
                    
                    # Add data to the nested structure
                    result["ltp"][ex][sym] = {
                        "timestamp": data['timestamp'],
                        "ltp": data['price']
                    }
            
            return result
            
    def get_quotes(self, exchange: str = None, symbol: str = None) -> Dict[str, Any]:
        """
        Get the latest Quote data in nested format.
        
        Args:
            exchange (str, optional): Filter by exchange
            symbol (str, optional): Filter by symbol (requires exchange to be specified)
            
        Returns:
            dict: Dictionary with Quote data in nested format:
                {"quote": {"EXCHANGE": {"SYMBOL": {
                    "timestamp": timestamp,
                    "open": open,
                    "high": high,
                    "low": low,
                    "close": close,
                    "ltp": ltp,
                    "volume": volume
                }}}}
        """
        with self.lock:
            # Create nested format response
            result = {"quote": {}}
            
            # Process each item in the data structure
            for symbol_key, data in self.quotes_data.items():
                # Extract exchange and symbol from the key (format: "EXCHANGE:SYMBOL")
                if ":" in symbol_key:
                    parts = symbol_key.split(":")
                    ex = parts[0]  # Exchange
                    sym = parts[1]  # Symbol
                    
                    # Filter by exchange if specified
                    if exchange and ex != exchange:
                        continue
                        
                    # Filter by symbol if specified
                    if symbol and sym != symbol:
                        continue
                    
                    # Initialize exchange dict if not exists
                    if ex not in result["quote"]:
                        result["quote"][ex] = {}
                    
                    # Add data to the nested structure
                    result["quote"][ex][sym] = {
                        "timestamp": data['timestamp'],
                        "open": data['open'],
                        "high": data['high'],
                        "low": data['low'],
                        "close": data['close'],
                        "ltp": data['ltp'],
                        "volume": data.get('volume', 0)
                    }
            
            return result
            
    def get_depth(self, exchange: str = None, symbol: str = None) -> Dict[str, Any]:
        """
        Get the latest Market Depth data in nested format.
        
        Args:
            exchange (str, optional): Filter by exchange
            symbol (str, optional): Filter by symbol (requires exchange to be specified)
            
        Returns:
            dict: Dictionary with Market Depth data in nested format:
                {"depth": {"EXCHANGE": {"SYMBOL": {
                    "timestamp": timestamp,
                    "ltp": ltp,
                    "buyBook": {
                        "1": {"price": price, "qty": quantity, "orders": orders},
                        # Additional levels...
                    },
                    "sellBook": {
                        "1": {"price": price, "qty": quantity, "orders": orders},
                        # Additional levels...
                    }
                }}}}
        """
        with self.lock:
            # Create nested format response
            result = {"depth": {}}
            
            # Process each item in the data structure
            for symbol_key, data in self.depth_data.items():
                # Extract exchange and symbol from the key (format: "EXCHANGE:SYMBOL")
                if ":" in symbol_key:
                    parts = symbol_key.split(":")
                    ex = parts[0]  # Exchange
                    sym = parts[1]  # Symbol
                    
                    # Filter by exchange if specified
                    if exchange and ex != exchange:
                        continue
                        
                    # Filter by symbol if specified
                    if symbol and sym != symbol:
                        continue
                    
                    # Initialize exchange dict if not exists
                    if ex not in result["depth"]:
                        result["depth"][ex] = {}
                    
                    # Initialize the symbol structure
                    result["depth"][ex][sym] = {
                        "timestamp": data.get('timestamp', int(time.time() * 1000)),
                        "ltp": data.get('ltp', 0),
                        "buyBook": {},
                        "sellBook": {}
                    }
                    
                    # Process buy depth book
                    buy_depth = data.get('depth', {}).get('buy', [])
                    for i, level in enumerate(buy_depth):
                        level_num = str(i + 1)
                        result["depth"][ex][sym]["buyBook"][level_num] = {
                            "price": str(level.get('price', 0)),
                            "qty": str(level.get('quantity', 0)),
                            "orders": str(level.get('orders', 0))
                        }
                    
                    # If there are fewer than 5 levels, add empty levels to complete the structure
                    for i in range(len(buy_depth), 5):
                        level_num = str(i + 1)
                        result["depth"][ex][sym]["buyBook"][level_num] = {
                            "price": "0",
                            "qty": "0",
                            "orders": "0"
                        }
                    
                    # Process sell depth book
                    sell_depth = data.get('depth', {}).get('sell', [])
                    for i, level in enumerate(sell_depth):
                        level_num = str(i + 1)
                        result["depth"][ex][sym]["sellBook"][level_num] = {
                            "price": str(level.get('price', 0)),
                            "qty": str(level.get('quantity', 0)),
                            "orders": str(level.get('orders', 0))
                        }
                    
                    # If there are fewer than 5 levels, add empty levels to complete the structure
                    for i in range(len(sell_depth), 5):
                        level_num = str(i + 1)
                        result["depth"][ex][sym]["sellBook"][level_num] = {
                            "price": "0",
                            "qty": "0",
                            "orders": "0"
                        }
            
            return result
