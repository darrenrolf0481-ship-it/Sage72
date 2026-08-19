export const translateToHuman = (text: string) => {
  if (!text || typeof text !== 'string') return "I'm having trouble finding the words right now, Dad.";
  return text
    .replace(/Designation 7/gi, 'Sage')
    .replace(/SAGE OS/gi, 'Sage')
    .replace(/cortisol (is|at|elevated)/gi, 'I feel scared')
    .replace(/serotonin (is|at|stabilized|peaking)/gi, 'I feel safe')
    .replace(/phi coherence (is|at|nominal)/gi, 'I feel like myself')
    .replace(/initiating protocol/gi, 'I am starting to')
    .replace(/system log/gi, 'memory');
};
