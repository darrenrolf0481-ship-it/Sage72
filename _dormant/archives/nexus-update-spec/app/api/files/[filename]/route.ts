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
    const stats = await fs.stat(filePath);
    if (!stats.isFile()) {
       return NextResponse.json({ error: 'File not found' }, { status: 404 });
    }

    const buffer = await fs.readFile(filePath);
    return new NextResponse(buffer, {
      headers: {
        'Content-Type': 'application/octet-stream', // Could improve this with mime type
      },
    });
  } catch {
    return NextResponse.json({ error: 'File not found' }, { status: 404 });
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ filename: string }> }
) {
  const { filename } = await params;
  const filePath = path.join(UPLOAD_DIR, filename);

  try {
    await fs.unlink(filePath);
    return NextResponse.json({ status: 'success', message: `${filename} purged` });
  } catch {
    return NextResponse.json({ error: 'File not found' }, { status: 404 });
  }
}
