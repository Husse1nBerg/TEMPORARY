import { NextResponse } from 'next/server';
import { headers } from 'next/headers';

export async function GET() {
  try {
    const headersList = headers();
    const authorization = headersList.get('authorization');
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    if (!authorization) {
        return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const response = await fetch(`${backendUrl}/api/auth/session`, {
      method: 'GET',
      headers: {
        'Authorization': authorization,
      },
    });

    const data = await response.json();

    if (!response.ok) {
        return NextResponse.json({ error: data.detail || 'Session check failed' }, { status: response.status });
    }
      
    return NextResponse.json(data, { status: 200 });

  } catch (error) {
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}