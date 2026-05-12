'use client';

import { useEffect, useState, useCallback } from 'react';
import { useSage } from '@/lib/sage-context';
import { Message } from '@/core/types';

export function useSageMessaging() {
  const { core } = useSage();
  const [messages, setMessages] = useState<Message[]>([]);
  const [listening, setListening] = useState(false);

  useEffect(() => {
    // Sync initial messages
    setMessages(core.getMessages());

    const onNewMsg = (msg: Message) => {
      setMessages(prev => [...prev.slice(-49), msg]);
    };
    
    const onCleared = () => {
      setMessages([]);
    };

    core.on('new-message', onNewMsg);
    core.on('chat_cleared', onCleared);
    
    return () => {
      core.off('new-message', onNewMsg);
      core.off('chat_cleared', onCleared);
    };
  }, [core]);

  const sendMessage = useCallback((text: string) => {
    return core.sendMessage(text);
  }, [core]);

  const toggleListening = useCallback(() => {
    const nextState = !core.isListening();
    core.setListening(nextState);
    setListening(nextState);
  }, [core]);

  return { messages, sendMessage, listening, toggleListening };
}
