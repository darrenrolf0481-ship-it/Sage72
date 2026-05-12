import { NextResponse } from 'next/server';
import fs from 'fs/promises';
import { UPLOAD_DIR, ensureDirs, guessType } from '@/lib/backend-utils';

export async function GET() {
  await ensureDirs();
  
  try {
    const files = await fs.readdir(UPLOAD_DIR);
    const fileList = await Promise.all(
      files.map(async (name) => {
        const stats = await fs.stat(`${UPLOAD_DIR}/${name}`);
        if (stats.isFile()) {
           return {
            name,
            size: stats.size,
            timestamp: Math.floor(stats.mtime.getTime() / 1000),
            type: guessType(name),
            url: `/api/files/${name}`
          };
        }
        return null;
      })
    );

    return NextResponse.json({
      status: 'success',
      files: fileList.filter(f => f !== null)
    });
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}
