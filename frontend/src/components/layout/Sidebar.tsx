import React from 'react';
import { 
  LayoutDashboard, 
  ShieldAlert, 
  Newspaper, 
  Search,
  MenuIcon,
  XIcon
} from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

import { Button } from '../ui/button';

interface NavItem {
  title: string;
  href: string;
  icon: React.ElementType;
}

const navItems: NavItem[] = [
  {
    title: "Dashboard",
    href: "/",
    icon: LayoutDashboard,
  },
  {
    title: "Domains",
    href: "/domains",
    icon: Search,
  },
  {
    title: "Risk Analysis",
    href: "/risk-analysis",
    icon: ShieldAlert,
  },
  {
    title: "News Feeds",
    href: "/news-feeds",
    icon: Newspaper,
  },
];

export const Sidebar: React.FC = () => {
  const location = useLocation();
  const [isOpen, setIsOpen] = React.useState(false);

  return (
    <>
      {/* Mobile menu button */}
      <Button
        variant="ghost"
        size="icon"
        className="fixed left-4 top-4 z-50 md:hidden"
        onClick={() => setIsOpen(!isOpen)}
      >
        {isOpen ? <XIcon /> : <MenuIcon />}
      </Button>

      {/* Sidebar */}
      <aside 
        className={`fixed inset-y-0 left-0 z-40 w-64 bg-background border-r p-4 transition-transform duration-300 ease-in-out transform ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        } md:translate-x-0 md:static md:h-full`}
      >
        <div className="flex items-center gap-2 mb-8">
          <ShieldAlert className="h-8 w-8 text-primary" />
          <span className="text-xl font-bold">DomainSentry</span>
        </div>
        
        <nav className="space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                to={item.href}
                className={`flex items-center gap-3 rounded-lg px-3 py-2 transition-all ${
                  location.pathname === item.href
                    ? 'bg-primary text-primary-foreground'
                    : 'hover:bg-accent hover:text-accent-foreground'
                }`}
              >
                <Icon className="h-5 w-5" />
                {item.title}
              </Link>
            );
          })}
        </nav>
      </aside>

      {/* Overlay for mobile */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-30 bg-black/50 backdrop-blur-sm md:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}
    </>
  );
};