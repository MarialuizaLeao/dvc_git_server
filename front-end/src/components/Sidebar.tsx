import { Link, useLocation } from 'react-router-dom';

const Sidebar = () => {
    const location = useLocation();

    const isActive = (path: string) => {
        return location.pathname === path;
    };

    const menuItems = [
        { path: '/project-data', label: '📄 Dados do projeto' },
        { path: '/models', label: '⚛️ Modelos' },
        { path: '/experiments', label: '🧪 Experimentos' },
    ];

    return (
        <div className="w-48 py-4">
            <nav className="space-y-1">
                {menuItems.map((item) => (
                    <Link
                        key={item.path}
                        to={item.path}
                        className={`block w-full px-4 py-2 text-left ${isActive(item.path)
                            ? 'bg-blue-100 text-blue-700'
                            : 'hover:bg-gray-100'
                            }`}
                    >
                        {item.label}
                    </Link>
                ))}
            </nav>
        </div>
    );
};

export default Sidebar; 