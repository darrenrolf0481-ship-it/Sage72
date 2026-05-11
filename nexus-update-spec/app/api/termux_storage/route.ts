import { NextResponse } from 'next/server';

export async function POST() {
  return NextResponse.json({
    status: 'triggered',
    message: 'Termux storage permission requested. Run: termux-setup-storage in Termux terminal if files are not visible.'
  });
}
