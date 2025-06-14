import { memo, useMemo } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { HiChevronRight, HiArrowLeft } from 'react-icons/hi';
import { useProjects } from '../hooks/useProjects';
import { CURRENT_USER } from '../constants/user';

const Breadcrumb = memo(() => {
    const location = useLocation();

    const projectId = useMemo(() => {
        const match = location.pathname.match(/\/project\/([^/]+)/);
        return match ? match[1] : '';
    }, [location.pathname]);

    const { data: project } = useProjects(CURRENT_USER.id).getProject(projectId);

    const breadcrumbs = useMemo(() => {
        const pathSegments = location.pathname.split('/').filter(Boolean);

        // Base breadcrumb is always Home
        const crumbs = [
            { path: '/home', label: 'Home' }
        ];

        if (pathSegments.includes('projects')) {
            crumbs.push({ path: '/projects', label: 'Projects' });
        }

        if (pathSegments.includes('project')) {
            // Add project name breadcrumb
            if (project) {
                crumbs.push({
                    path: `/project/${projectId}/`,
                    label: project.project_name || 'Untitled Project'
                });
            }

            // Add section breadcrumb if we're in a specific section
            if (pathSegments.includes('data')) {
                crumbs.push({ path: `/project/${projectId}/data`, label: 'Data' });
            }

            if (pathSegments.includes('models')) {
                crumbs.push({ path: `/project/${projectId}/models`, label: 'Models' });
            }

            if (pathSegments.includes('experiments')) {
                crumbs.push({ path: `/project/${projectId}/experiments`, label: 'Experiments' });
            }
        }

        return crumbs;
    }, [location.pathname, project, projectId]);

    // Don't render breadcrumbs on home page
    if (location.pathname === '/home') {
        return null;
    }

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
});

Breadcrumb.displayName = 'Breadcrumb';

export default Breadcrumb; 