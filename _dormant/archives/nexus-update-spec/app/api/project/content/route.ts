import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';
import { PROJECT_DIR } from '@/lib/backend-utils';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const filePathParam = searchParams.get('path');

  if (!filePathParam) {
    return NextResponse.json({ error: 'Missing path' }, { status: 400 });
  }

  const target = path.join(PROJECT_DIR, filePathParam);
  
  // Security: prevent escaping PROJECT_DIR
  const resolvedBase = path.resolve(PROJECT_DIR);
  const resolvedTarget = path.resolve(target);

  if (!resolvedTarget.startsWith(resolvedBase)) {
    return NextResponse.json({ error: 'Access denied' }, { status: 403 });
  }

  try {
    const text = await fs.readFile(resolvedTarget, 'utf-8');
    return NextResponse.json({ status: 'success', content: text });
  } catch {
    return NextResponse.json({ error: 'Cannot read binary file' }, { status: 400 });
  }
}
