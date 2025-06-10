import { Link, useLocation } from 'react-router-dom';
import { HiChevronRight, HiArrowLeft } from 'react-icons/hi';
import { useProjects } from '../hooks/useProjects';
import { CURRENT_USER } from '../constants/user';

const Breadcrumb = () => {
    const location = useLocation();

    // Don't render breadcrumbs on home page
    if (location.pathname === '/home') {
        return null;
    }

    const getProjectId = () => {
        const match = location.pathname.match(/\/project\/([^/]+)/);
        return match ? match[1] : '';
    };

    const projectId = getProjectId();
    const { data: project } = useProjects(CURRENT_USER.id).getProject(projectId);

    const getBreadcrumbs = () => {
        const pathSegments = location.pathname.split('/').filter(Boolean);

        // Base breadcrumb is always Home
        const breadcrumbs = [
            { path: '/home', label: 'Home' }
        ];

        if (pathSegments.includes('projects')) {
            breadcrumbs.push({ path: '/projects', label: 'Projects' });
        }

        if (pathSegments.includes('project')) {
            const projectId = pathSegments[pathSegments.indexOf('project')];


            breadcrumbs.push({ path: '/projects', label: 'Projects' });


            // Add project name breadcrumb
            if (project) {
                breadcrumbs.push({ path: `/project/${projectId}/`, label: 'MNIST Classification' });
            }

            // Add section breadcrumb if we're in a specific section
            if (pathSegments.includes('data')) {
                breadcrumbs.push({ path: `/project/${projectId}/data`, label: 'Data' });
            }

            if (pathSegments.includes('models')) {
                breadcrumbs.push({ path: `/project/${projectId}/models`, label: 'Models' });
            }

            if (pathSegments.includes('experiments')) {
                breadcrumbs.push({ path: `/project/${projectId}/experiments`, label: 'Experiments' });
            }
        }

        return breadcrumbs;
    };

    const breadcrumbs = getBreadcrumbs();

    return (
        <nav className="flex items-center text-sm text-gray-500 py-4 px-6 border-b border-gray-200">
            <Link to="/home" className="hover:text-gray-700 mr-4">
                <HiArrowLeft className="w-6 h-6" />
            </Link>
            {breadcrumbs.map((item, index) => (
                <div key={item.path} className="flex items-center">
                    <Link to={item.path} className="hover:text-gray-700">
                        {item.label}
                    </Link>
                    {index < breadcrumbs.length - 1 && (
                        <HiChevronRight className="w-5 h-5 mx-2 text-gray-400" />
                    )}
                </div>
            ))}
        </nav>
    );
};

export default Breadcrumb; 