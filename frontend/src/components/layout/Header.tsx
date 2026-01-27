import React from 'react';
import { MoonIcon, SunIcon, BellIcon, SearchIcon } from 'lucide-react';
import { UserButton } from '@clerk/clerk-react';

import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { useTheme } from '../../contexts/ThemeContext';

export const Header: React.FC = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b bg-background px-6">
      <div className="relative ml-auto flex-1 md:grow-0">
        <SearchIcon className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
        <Input
          type="search"
          placeholder="Search domains..."
          className="w-full rounded-lg bg-background pl-8 md:w-[200px] lg:w-[336px]"
        />
      </div>
      <Button variant="outline" size="icon" onClick={toggleTheme}>
        {theme === 'dark' ? (
          <SunIcon className="h-5 w-5" />
        ) : (
          <MoonIcon className="h-5 w-5" />
        )}
        <span className="sr-only">Toggle theme</span>
      </Button>
      <Button variant="outline" size="icon">
        <BellIcon className="h-5 w-5" />
        <span className="sr-only">Toggle notification</span>
      </Button>
      <UserButton />
    </header>
  );
};