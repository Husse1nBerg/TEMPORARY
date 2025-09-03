'use client'; 

import { Button } from '@/components/ui/button';
import { useEffect } from 'react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center text-center px-4">
      <h1 className="text-4xl font-bold text-red-600 mb-4">Something went wrong!</h1>
      <p className="text-lg text-gray-600 mb-8">
        We encountered an unexpected error. Please try again.
      </p>
      <Button onClick={() => reset()}>
        Try again
      </Button>
    </div>
  );
}