'use client';

import { useState, useEffect } from 'react';
import toast from 'react-hot-toast';

export function useWebSocket(onMessage: (data: any) => void) {
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const wsUrl = process.env.NEXT_PUBLIC_WEBSOCKET_URL || 'ws://localhost:8000/ws';
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'price_update') {
        toast.success(`Price updated: ${data.price.product_name}`);
      }
      // Pass the message to the component's handler
      onMessage(data); 
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      toast.error('Real-time connection error.');
      setIsConnected(false);
    };

    // Cleanup on component unmount
    return () => {
      ws.close();
    };
  }, [onMessage]);

  return { isConnected };
}