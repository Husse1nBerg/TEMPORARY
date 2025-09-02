'use client';

import * as React from 'react';
import Link from 'next/link';
import { Leaf } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

interface MobileNavProps {
  isOpen: boolean;
  setIsOpen: React.Dispatch<React.SetStateAction<boolean>>;
}

const MobileNav = ({ isOpen, setIsOpen }: MobileNavProps) => {
  const navItems = [
    { href: '/dashboard', label: 'Dashboard' },
    { href: '/dashboard/products', label: 'Products' },
    { href: '/dashboard/stores', label: 'Stores' },
    { href: '/dashboard/analytics', label: 'Analytics' },
  ];

  return (
    <div
      className={cn(
        'fixed inset-0 top-16 z-50 grid h-[calc(100vh-4rem)] grid-flow-row auto-rows-max overflow-auto p-6 pb-32 shadow-md animate-in slide-in-from-bottom-80 md:hidden',
        { hidden: !isOpen }
      )}
    >
      <div className="relative z-20 grid gap-6 rounded-md bg-popover p-4 text-popover-foreground shadow-md">
        <Link href="/" className="flex items-center space-x-2">
          <Leaf className="h-6 w-6 text-primary" />
          <span className="font-bold">CROPS Price Tracker</span>
        </Link>
        <nav className="grid grid-flow-row auto-rows-max text-sm">
          {navItems.map((item, index) => (
            <Link
              key={index}
              href={item.href}
              className={cn(
                'flex w-full items-center rounded-md p-2 text-sm font-medium hover:underline'
              )}
              onClick={() => setIsOpen(false)}
            >
              {item.label}
            </Link>
          ))}
        </nav>
        <Button asChild>
            <Link href="/auth/login">Login</Link>
        </Button>
      </div>
    </div>
  );
};

export default MobileNav;