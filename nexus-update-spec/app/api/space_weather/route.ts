import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const res = await fetch('https://services.swpc.noaa.gov/products/noaa-planetary-k-index-forecast.json', {
      next: { revalidate: 3600 } // Cache for an hour
    });
    const data = await res.json();
    
    // Parse latest Kp index
    const latest = Array.isArray(data) && data.length > 0 ? data[data.length - 1] : [0, 0, 0];
    const kp = parseFloat(latest[1]);
    const g_scale = Math.min(5, Math.max(0, Math.floor(kp / 2)));
    
    return NextResponse.json({
      status: 'success',
      g_scale,
      s_scale: Math.min(5, g_scale + 1),
      r_scale: Math.max(0, 5 - g_scale),
      raw: latest
    });
  } catch {
    // Fallback simulated data
    return NextResponse.json({
      status: 'simulated',
      g_scale: 2,
      s_scale: 3,
      r_scale: 2
    });
  }
}
