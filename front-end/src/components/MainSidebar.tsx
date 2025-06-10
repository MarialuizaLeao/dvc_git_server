import { Link, useLocation } from 'react-router-dom';
import { VscHome } from 'react-icons/vsc';
import { BiHelpCircle } from 'react-icons/bi';
import { FaParking } from 'react-icons/fa';
import { BsFolder } from 'react-icons/bs';

const MainSidebar = () => {
    const location = useLocation();

    const isActive = (path: string) => {
        return location.pathname === path;
    };

    const verticalMenuItems = [
        { path: '/home', icon: VscHome, label: 'Home' },
        { path: '/projects', icon: BsFolder, label: 'Projects' },
        { path: '/help', icon: BiHelpCircle, label: 'Help' },
    ];

    return (
        <aside className="w-16 bg-gradient-to-b from-blue-300 via-blue-400 to-purple-600 flex flex-col items-center py-4 flex-shrink-0">
            <div className="w-12 h-12 rounded-full flex items-center justify-center mb-8 overflow-hidden">
                <img src="/logo.svg" alt="Logo" className="w-full h-full" />
            </div>

            <nav className="flex-1">
                <ul className="space-y-4">
                    {verticalMenuItems.map((item) => (
                        <li key={item.path}>
                            <Link
                                to={item.path}
                                className={`w-10 h-10 rounded-full flex items-center justify-center transition-colors ${isActive(item.path)
                                        ? 'bg-blue-100 text-blue-700'
                                        : 'text-white hover:bg-white/20'
                                    }`}
                                title={item.label}
                            >
                                <item.icon className="w-5 h-5" />
                            </Link>
                        </li>
                    ))}
                </ul>
            </nav>

            <div className="mt-auto">
                <Link
                    to="/profile"
                    className="w-10 h-10 rounded-full flex items-center justify-center text-white hover:bg-white/20"
                    title="Profile"
                >
                    <FaParking className="w-5 h-5" />
                </Link>
            </div>
        </aside>
    );
};

export default MainSidebar; 