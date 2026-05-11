import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';
import { DATA_DIR, ensureDirs } from '@/lib/backend-utils';

export async function POST(request: NextRequest) {
  await ensureDirs();
  
  try {
    const body = await request.json();
    // Log to local lab journal
    const journalFile = path.join(DATA_DIR, 'lab_journal.jsonl');
    const entry = { ...body, timestamp: Date.now() / 1000 };
    
    await fs.appendFile(journalFile, JSON.stringify(entry) + '\n');
    
    return NextResponse.json({ status: 'logged', message: 'Lab signal recorded.' });
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}
