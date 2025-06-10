import { useParams } from 'react-router-dom';
import { useProjects } from '../hooks/useProjects';
import { CURRENT_USER } from '../constants/user';

export default function Project() {
    const { id } = useParams();
    const { data: project, isLoading, error } = useProjects(CURRENT_USER.id).getProject(id || '');

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-center py-12">
                <h2 className="text-2xl font-semibold text-red-600">Error Loading Project</h2>
                <p className="text-gray-700 mt-2">{error instanceof Error ? error.message : 'An error occurred while loading the project'}</p>
            </div>
        );
    }

    if (!project) {
        return (
            <div className="text-center py-12">
                <h2 className="text-2xl font-semibold text-gray-700">Project Not Found</h2>
                <p className="text-gray-500 mt-2">The project you're looking for doesn't exist or has been deleted.</p>
            </div>
        );
    }

    return (
        <div className="container mx-auto px-4 py-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-6">{project.project_name}</h1>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div className="bg-white p-6 rounded-lg shadow-md">
                    <h2 className="text-xl font-semibold text-gray-900 mb-4">Project Details</h2>
                    <div className="space-y-2">
                        <p><span className="font-medium">Created by:</span> {project.username}</p>
                        <p><span className="font-medium">Description:</span> {project.description || 'No description'}</p>
                        <p><span className="font-medium">Type:</span> {project.project_type || 'Not specified'}</p>
                        <p><span className="font-medium">Framework:</span> {project.framework || 'Not specified'}</p>
                        <p><span className="font-medium">Python Version:</span> {project.python_version || 'Not specified'}</p>
                        <p><span className="font-medium">Models:</span> {project.models_count || 0}</p>
                        <p><span className="font-medium">Experiments:</span> {project.experiments_count || 0}</p>
                        <p><span className="font-medium">Status:</span> {project.status || 'Active'}</p>
                        {project.created_at && (
                            <p><span className="font-medium">Created:</span> {new Date(project.created_at).toLocaleDateString()}</p>
                        )}
                    </div>
                </div>
                {project.dependencies && project.dependencies.length > 0 && (
                    <div className="bg-white p-6 rounded-lg shadow-md">
                        <h2 className="text-xl font-semibold text-gray-900 mb-4">Dependencies</h2>
                        <div className="space-y-1">
                            {project.dependencies.map((dep, index) => (
                                <p key={index} className="font-mono text-sm">{dep}</p>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
} 