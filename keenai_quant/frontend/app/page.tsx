import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { CodePreviewCard } from "@/components/ui/CodePreviewCard";
import { Header } from "@/components/layout/Header";
import { Plus, Github, Package } from 'lucide-react';

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <main className="flex-grow">
        <div className="container mx-auto px-4 py-24">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div className="flex flex-col items-start space-y-6">
              <Badge variant="outline" className="text-sm text-gray-400">
                Own Your Auth
              </Badge>
              <h1 className="text-5xl md:text-7xl font-bold tracking-tighter">
                The most comprehensive authentication framework for TypeScript.
              </h1>
              <div className="flex items-center space-x-2 bg-neutral-900 border border-neutral-800 rounded-md px-4 py-2 w-full md:w-auto">
                <span className="text-gray-400">$</span>
                <span className="text-white">npm install keenai-quant</span>
                <div className="flex-grow" />
                <div className="flex items-center space-x-2">
                    <Package className="h-5 w-5 text-gray-400" />
                    <Github className="h-5 w-5 text-gray-400" />
                </div>
              </div>

              <div className="flex items-center space-x-4">
                <Button size="lg">GET STARTED</Button>
                <Button variant="outline" size="lg">
                  <Plus className="h-4 w-4 mr-2" />
                  Create Sign In Box
                </Button>
              </div>
            </div>
            <div>
              <CodePreviewCard />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
