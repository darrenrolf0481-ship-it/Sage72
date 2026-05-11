import { NextResponse } from 'next/server';
import fs from 'fs/promises';
import { PROJECT_DIR, ensureDirs } from '@/lib/backend-utils';

async function walk(dir: string, base: string = dir): Promise<any[]> {
  const entries = await fs.readdir(dir, { withFileTypes: true });
  const files = await Promise.all(
    entries.map(async (entry) => {
      const res = `${dir}/${entry.name}`;
      if (entry.isDirectory()) {
         return walk(res, base);
      } else {
        const stats = await fs.stat(res);
        return {
          name: entry.name,
          path: res.replace(base + '/', ''),
          size: stats.size
        };
      }
    })
  );
  return files.flat();
}

export async function GET() {
  await ensureDirs();
  try {
    const files = await walk(PROJECT_DIR);
    return NextResponse.json({ status: 'success', files });
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}
