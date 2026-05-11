import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';
import { UPLOAD_DIR, PROJECT_DIR, ensureDirs } from '@/lib/backend-utils';

export async function POST(request: NextRequest) {
  await ensureDirs();
  
  try {
    const formData = await request.formData();
    const file = formData.get('file') as File;
    const target = formData.get('target') as string || 'general';

    if (!file) {
      return NextResponse.json({ error: 'No file provided' }, { status: 400 });
    }

    const destDir = target !== 'coding' ? UPLOAD_DIR : PROJECT_DIR;
    const filePath = path.join(destDir, file.name);
    
    const buffer = Buffer.from(await file.arrayBuffer());
    await fs.writeFile(filePath, buffer);

    let textContent: string | null = null;
    if (file.name.endsWith('.txt') || file.name.endsWith('.js') || file.name.endsWith('.ts') || 
        file.name.endsWith('.tsx') || file.name.endsWith('.py') || file.name.endsWith('.json') || 
        file.name.endsWith('.md')) {
      try {
        textContent = buffer.toString('utf-8');
      } catch {
        // Not text
      }
    }

    return NextResponse.json({
      status: 'uploaded',
      url: `/api/files/${file.name}`,
      name: file.name,
      size: file.size,
      type: file.type || 'application/octet-stream',
      content: textContent
    });
  } catch (error) {
    return NextResponse.json({ error: `UPLOAD_FAILED: ${String(error)}` }, { status: 500 });
  }
}
