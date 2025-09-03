import { NextResponse } from 'next/server';

export async function GET() {
    // This route is typically called by the client to signal a logout.
    // With JWT, logout is mainly handled client-side by deleting the token.
    // This server route can be used to clear any server-side session cookies if you were using them.
    // For now, it just confirms the logout action.
    
    const response = NextResponse.json({ message: 'Logout successful' }, { status: 200 });

    // Example of clearing a cookie if you were using one
    // response.cookies.set('session', '', { expires: new Date(0) });

    return response;
}