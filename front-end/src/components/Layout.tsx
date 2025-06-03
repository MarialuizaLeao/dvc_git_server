import type { ReactNode } from 'react';
import Sidebar from './Sidebar';

interface LayoutProps {
    children: ReactNode;
}

const Layout = ({ children }: LayoutProps) => {
    return (
        <div className="min-h-screen bg-white">
            <header className="bg-white border-b border-gray-200">
                <div className="max-w-7xl mx-auto px-4">
                    <h1 className="text-xl py-4">MLOps Platform</h1>
                </div>
            </header>
            <div className="max-w-7xl mx-auto px-4">
                <div className="flex">
                    <Sidebar />
                    <main className="flex-1 py-6 pl-8">
                        {children}
                    </main>
                </div>
            </div>
        </div>
    );
};

export default Layout; 