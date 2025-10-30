import { Github } from 'lucide-react';
import Link from 'next/link';

export function Header() {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-sm">
      <div className="container mx-auto flex h-16 max-w-screen-2xl items-center justify-between px-4">
        <div className="flex items-center space-x-8">
          <Link href="/" className="font-bold text-lg text-foreground border-b-2 border-white pb-1">
            KeenAI Quant
          </Link>
          <nav className="hidden md:flex items-center space-x-6 text-sm font-medium text-gray-400">
            <Link href="/agents" className="hover:text-foreground transition-colors">Agents</Link>
            <Link href="/trading" className="hover:text-foreground transition-colors">Trading</Link>
            <Link href="/analytics" className="hover:text-foreground transition-colors">Analytics</Link>
            <Link href="/backtesting" className="hover:text-foreground transition-colors">Backtesting</Link>
          </nav>
        </div>
        <div className="flex items-center space-x-4">
          <Link href="https://github.com" target="_blank" rel="noopener noreferrer">
            <Github className="h-5 w-5 text-gray-400 hover:text-foreground transition-colors" />
          </Link>
        </div>
      </div>
    </header>
  );
}
