import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';
import { DATA_DIR, ensureDirs } from '@/lib/backend-utils';

export async function POST(request: NextRequest) {
  await ensureDirs();
  
  try {
    const body = await request.json();
    const memories = body.memories || [];
    
    // Save to local staging
    const syncFile = path.join(DATA_DIR, 'memory_manifest.json');
    let existing: any[] = [];
    
    try {
      const data = await fs.readFile(syncFile, 'utf-8');
      existing = JSON.parse(data);
    } catch {
      // New file
    }
    
    // Merge and dedupe by ID
    const idSet = new Set(existing.map(m => m.id));
    let newCount = 0;
    for (const mem of memories) {
      if (!idSet.has(mem.id)) {
        existing.push(mem);
        newCount++;
      }
    }
    
    await fs.writeFile(syncFile, JSON.stringify(existing, null, 2));
    
    return NextResponse.json({
      status: 'synced',
      total_memories: existing.length,
      new_memories: newCount,
      message: `Staged ${newCount} new memories to local manifest.`
    });
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}
