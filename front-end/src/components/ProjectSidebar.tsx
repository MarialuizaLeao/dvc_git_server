import { Link, useLocation } from 'react-router-dom';
import { VscFile } from 'react-icons/vsc';
import { TbAtom, TbGitBranch } from 'react-icons/tb';
import { GoBeaker } from 'react-icons/go';

interface ProjectSidebarProps {
    projectId: string;
}

const ProjectSidebar = ({ projectId }: ProjectSidebarProps) => {
    const location = useLocation();

    const isActive = (path: string) => {
        return location.pathname === path;
    };

    const mainMenuItems = [
        { path: `/project/${projectId}/data`, label: 'Project Data', icon: VscFile },
        { path: `/project/${projectId}/pipeline`, label: 'Pipeline', icon: TbGitBranch },
        { path: `/project/${projectId}/models`, label: 'Models', icon: TbAtom },
        { path: `/project/${projectId}/experiments`, label: 'Experiments', icon: GoBeaker },
    ];

    return (
        <aside className="w-64 bg-gray-50 border-r border-gray-200 flex-shrink-0 overflow-y-auto">
            <nav className="mt-5 px-4">
                <ul className="space-y-2">
                    {mainMenuItems.map((item) => (
                        <li key={item.path}>
                            <Link
                                to={item.path}
                                className={`flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${isActive(item.path)
                                        ? 'bg-blue-100 text-blue-700'
                                        : 'text-gray-700 hover:bg-gray-100'
                                    }`}
                            >
                                <item.icon className="w-5 h-5 mr-3" />
                                {item.label}
                            </Link>
                        </li>
                    ))}
                </ul>
            </nav>
        </aside>
    );
};

export default ProjectSidebar; 