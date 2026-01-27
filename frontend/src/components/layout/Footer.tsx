import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="py-4 px-6 border-t bg-background">
      <div className="container mx-auto">
        <p className="text-center text-sm text-muted-foreground">
          Non-profit OSINT tool. Data from public sources only. Risk scores for research purposes only.
        </p>
      </div>
    </footer>
  );
};