import { useParams } from 'react-router-dom';
import { useProjects } from '../hooks/useProjects';
import { CURRENT_USER } from '../constants/user';

export default function ProjectPage() {
    const { projectId } = useParams<{ projectId: string }>();
    const { data: project } = useProjects(CURRENT_USER.id).getProject(projectId || '');

    if (!project) {
        return <div>Loading...</div>;
    }

    return (
        <div className="container mx-auto px-4 py-8">
            <h1 className="text-2xl font-bold text-gray-900 mb-6">{project.project_name}</h1>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div className="bg-white p-6 rounded-lg shadow-md">
                    <h2 className="text-xl font-semibold text-gray-900 mb-4">Project Details</h2>
                    <div className="space-y-2">
                        <p><span className="font-medium">Created by:</span> {project.username}</p>
                        <p><span className="font-medium">Models:</span> {project.models_count || 0}</p>
                        <p><span className="font-medium">Experiments:</span> {project.experiments_count || 0}</p>
                    </div>
                </div>
            </div>
        </div>
    );
} 