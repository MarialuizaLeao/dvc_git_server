import { useLocation } from 'react-router-dom';
import ProjectSidebar from './ProjectSidebar';

const Sidebar = () => {
    const location = useLocation();

    const getProjectId = () => {
        const match = location.pathname.match(/\/project\/([^/]+)/);
        return match ? match[1] : '';
    };

    const isInsideProject = location.pathname.startsWith('/project/');

    if (!isInsideProject) {
        return null;
    }

    return <ProjectSidebar projectId={getProjectId()} />;
};

export default Sidebar; 