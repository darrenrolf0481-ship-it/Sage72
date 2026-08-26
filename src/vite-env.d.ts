/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_GEMINI_API_KEY: string;
  readonly VITE_GROK_API_KEY: string;
  readonly VITE_OPENROUTER_API_KEY: string;
  readonly VITE_GITHUB_TOKEN: string;
  readonly VITE_OLLAMA_API_KEY: string;
  readonly BASE_URL: string;
  [key: string]: string | undefined;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

declare module 'framer-motion' {
  export const motion: any;
  export const AnimatePresence: any;
  export const useAnimation: any;
  export const useMotionValue: any;
  export const useTransform: any;
  export const useDragControls: any;
  export const useScroll: any;
  export const useSpring: any;
  export const useInView: any;
  export const LazyMotion: any;
  export const domAnimation: any;
  export const domMax: any;
  export const m: any;
  export default motion;
}