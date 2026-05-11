import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';
import { UPLOAD_DIR } from '@/lib/backend-utils';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ filename: string }> }
) {
  const { filename } = await params;
  const filePath = path.join(UPLOAD_DIR, filename);

  try {
    const text = await fs.readFile(filePath, 'utf-8');
    return NextResponse.json({ status: 'success', content: text });
  } catch {
    return NextResponse.json({ error: 'Binary file - cannot display as text' }, { status: 400 });
  }
}
