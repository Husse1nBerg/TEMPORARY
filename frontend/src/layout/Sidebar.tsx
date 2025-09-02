'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, ShoppingCart, Store, BarChart2 } from 'lucide-react';
import { cn } from '@/lib/utils';

const Sidebar = () => {
  const pathname = usePathname();

  const navItems = [
    { href: '/dashboard', label: 'Dashboard', icon: Home },
    { href: '/dashboard/products', label: 'Products', icon: ShoppingCart },
    { href: '/dashboard/stores', label: 'Stores', icon: Store },
    { href: '/dashboard/analytics', label: 'Analytics', icon: BarChart2 },
  ];

  return (
    <aside className="hidden md:block w-64 flex-shrink-0 border-r bg-background">
      <div className="flex flex-col h-full">
        <div className="p-4">
          <Link href="/" className="flex items-center space-x-2">
            <span className="font-bold text-lg">CROPS Dashboard</span>
          </Link>
        </div>
        <nav className="flex-1 px-2 py-4 space-y-1">
          {navItems.map((item) => (
            <Link
              key={item.label}
              href={item.href}
              className={cn(
                'flex items-center px-3 py-2 text-sm font-medium rounded-md',
                pathname === item.href
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
              )}
            >
              <item.icon className="mr-3 h-5 w-5" />
              {item.label}
            </Link>
          ))}
        </nav>
      </div>
    </aside>
  );
};

export default Sidebar;