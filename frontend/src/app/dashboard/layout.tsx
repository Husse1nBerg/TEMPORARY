
// Protected layout for dashboard pages

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';
import axios from 'axios';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        router.push('/auth/login');
        return;
      }

      // Verify token with backend
      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL}/api/auth/session`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      if (response.data.valid) {
        setIsAuthenticated(true);
      } else {
        localStorage.removeItem('token');
        router.push('/auth/login');
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      localStorage.removeItem('token');
      router.push('/auth/login');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center"
        >
          <Loader2 className="w-12 h-12 text-green-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading dashboard...</p>
        </motion.div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return <>{children}</>;
}
