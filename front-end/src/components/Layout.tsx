import type { ReactNode } from 'react';
import Sidebar from './Sidebar';
import Breadcrumb from './Breadcrumb';
import MainSidebar from './MainSidebar';

interface LayoutProps {
    children: ReactNode;
}

const Layout = ({ children }: LayoutProps) => {
    return (
        <div className="min-h-screen h-screen flex flex-col bg-white overflow-hidden">
            <div className="flex flex-1 overflow-hidden">
                <MainSidebar />
                <div className="flex-1 flex flex-col overflow-hidden">
                    <Breadcrumb />
                    <div className="flex flex-1 overflow-hidden">
                        <Sidebar />
                        <main className="flex-1 p-6 overflow-auto">
                            {children}
                        </main>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Layout; 