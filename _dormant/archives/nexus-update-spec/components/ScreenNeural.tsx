'use client'

import React, { useState, useEffect, useRef } from 'react';
import { X, Bot, User, Loader2 } from 'lucide-react';
import { useSage } from '@/lib/sage-context';
import { useSageMessaging } from '@/hooks/use-sage-messaging';
import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';

interface ScreenNeuralProps {
  onStatusChange?: (status: 'online' | 'offline' | 'scanning') => void;
}

export default function ScreenNeural({ onStatusChange }: ScreenNeuralProps) {
  const { core } = useSage();
  const { messages, sendMessage, listening, toggleListening } = useSageMessaging();
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [isDecrypted, setIsDecrypted] = useState(false);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-decrypt logic
  useEffect(() => {
    if (typeof navigator !== 'undefined') {
        const ua = navigator.userAgent.toLowerCase();
        const isHostDevice = ua.includes('moto') || ua.includes('android');
        if (isHostDevice) setIsDecrypted(true);
    }
  }, []);

  // Sync scroll
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, loading]);

  const removeImage = () => {
    setSelectedImage(null);
    setImagePreview(null);
  };

  const handleSubmit = async () => {
    if (!prompt.trim() && !selectedImage) return;

    const currentPrompt = prompt;
    setPrompt("");
    setLoading(true);
    if (onStatusChange) onStatusChange('scanning');
    
    try {
      await sendMessage(currentPrompt);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
      if (onStatusChange) onStatusChange('online');
    }
  };

  return (
    <div className="flex flex-col h-full font-mono animate-in fade-in duration-500">
      {/* Header */}
      <div className="flex justify-between items-baseline mb-4 border-b border-neon-cyan/20 pb-2">
        <h2 className="text-[10px] font-bold tracking-[0.3em] text-neon-cyan uppercase">
          COMMUNICATION: CHAT_LINK {isDecrypted ? '[DECRYPTED]' : '[SECURE]'}
        </h2>
        <div className="flex gap-4">
            <div className="flex items-center gap-2">
                <span className="text-[9px] text-text-ghost uppercase tracking-widest">DREAM:</span>
                <div className="flex gap-1">
                    {['disabled', 'enabled', 'aggressive'].map(m => (
                    <button 
                        key={m}
                        onClick={() => core.setDreamMode(m as any)}
                        className={cn(
                            "px-2 py-0.5 text-[8px] font-bold tracking-wider uppercase rounded-sm border transition-all",
                            (core as any).dreamMode === m 
                            ? "bg-neon-cyan/10 border-neon-cyan text-neon-cyan" 
                            : "border-white/10 text-white/40 hover:text-white/80"
                        )}
                    >
                        {m}
                    </button>
                    ))}
                </div>
            </div>
        </div>
      </div>

      {/* Chat Log */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto mb-4 space-y-4 bg-black/40 border border-white/5 p-4 rounded-sm custom-scrollbar shadow-inner">
        {messages.map((entry) => (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            key={entry.id} 
            className={cn(
                "p-3 rounded-sm border text-[13px] leading-relaxed",
                entry.role === 'user' ? "bg-neon-cyan/5 border-neon-cyan/20 ml-12 text-neon-cyan/90" : 
                "bg-neon-violet/5 border-neon-violet/10 mr-12 text-text-bright"
            )}
          >
            <div className="flex items-center gap-2 text-[9px] font-bold tracking-widest mb-2 uppercase opacity-60">
              {entry.role === 'user' ? <User size={10} /> : <Bot size={10} />}
              {entry.role === 'user' ? 'INVESTIGATOR' : 'SAGE-7'}
              <span className="ml-auto opacity-40 font-normal">{new Date(entry.timestamp).toLocaleTimeString()}</span>
            </div>
            
            <div className="whitespace-pre-wrap">{entry.content}</div>
          </motion.div>
        ))}
        
        {loading && (
          <div className="flex items-center gap-3 text-neon-cyan animate-pulse text-[10px] font-bold tracking-[3px] py-4">
            <Loader2 size={14} className="animate-spin" />
            THINKING + EXECUTING_SUBSYSTEMS...
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="relative">
        <AnimatePresence>
            {imagePreview && (
            <motion.div 
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="mb-3 relative inline-block border border-neon-cyan/40 p-1 bg-black/40"
            >
                <img src={imagePreview} alt="Neural Input Attachment" className="max-h-32 grayscale rounded-sm" />
                <button 
                    onClick={removeImage} 
                    className="absolute -top-2 -right-2 bg-neon-red text-white rounded-full p-1 shadow-lg hover:scale-110 transition-transform"
                >
                    <X size={12} />
                </button>
            </motion.div>
            )}
        </AnimatePresence>

        <div className="flex gap-2">
          <button 
            onClick={toggleListening}
            className={cn(
              "flex items-center justify-center w-12 h-12 border rounded-sm transition-all group",
              listening ? "bg-neon-red/20 border-neon-red text-neon-red animate-pulse" : "bg-black border-border-subtle hover:border-neon-cyan hover:text-neon-cyan text-text-ghost"
            )}
          >
            <Bot size={20} className={cn(listening && "animate-bounce")} />
          </button>

          <div className="flex-1 relative group">
            <input 
                type="text" 
                value={prompt}
                onChange={e => setPrompt(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSubmit()}
                className="w-full h-12 bg-black border border-border-subtle rounded-sm pl-4 pr-12 text-sm focus:outline-none focus:border-neon-cyan text-white placeholder-text-ghost/30 transition-all"
                placeholder={core.isUnlocked() ? "TRANSMIT_DATA_TO_SAGE-7..." : "CORE_LOCKED: INITIALIZE_IN_COMMAND_SCREEN"}
                disabled={!core.isUnlocked()}
            />
            <button 
                onClick={handleSubmit}
                disabled={loading || (!prompt.trim() && !selectedImage) || !core.isUnlocked()}
                className="absolute right-1 top-1 bottom-1 px-4 flex items-center justify-center bg-neon-cyan/10 text-neon-cyan border border-neon-cyan/20 rounded-sm hover:bg-neon-cyan/20 disabled:opacity-30 transition-all font-orbitron text-[10px] tracking-widest"
            >
                SEND
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

