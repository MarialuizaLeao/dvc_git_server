import { Link } from 'react-router-dom';
import { useProjects } from '../hooks/useProjects';
import { CURRENT_USER } from '../constants/user';

export default function Projects() {
    const { getProjects } = useProjects(CURRENT_USER.id);
    const { data: projectIds, isLoading, error } = getProjects();

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
                <h2 className="text-2xl font-semibold text-red-600">Error Loading Projects</h2>
                <p className="text-gray-700 mt-2">{error instanceof Error ? error.message : 'An error occurred while loading projects'}</p>
            </div>
        );
    }

    if (!projectIds || projectIds.length === 0) {
        return (
            <div className="text-center py-12">
                <h2 className="text-2xl font-semibold text-gray-700">No Projects Found</h2>
                <p className="text-gray-500 mt-2">Create your first project to get started!</p>
                <Link
                    to="/create-project"
                    className="mt-4 inline-block px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                >
                    Create Project
                </Link>
            </div>
        );
    }

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="flex justify-between items-center mb-8">
                <h1 className="text-3xl font-bold text-gray-900">My Projects</h1>
                <Link
                    to="/create-project"
                    className="px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                >
                    Create Project
                </Link>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {projectIds.map(projectId => (
                    <ProjectCard key={projectId} userId={CURRENT_USER.id} projectId={projectId} />
                ))}
            </div>
        </div>
    );
}

function ProjectCard({ userId, projectId }: { userId: string; projectId: string }) {
    const { getProject } = useProjects(userId);
    const { data: project, isLoading } = getProject(projectId);

    if (isLoading || !project) {
        return (
            <div className="bg-white p-6 rounded-lg shadow-md animate-pulse">
                <div className="h-6 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
                <div className="space-y-2">
                    <div className="h-4 bg-gray-200 rounded w-1/4"></div>
                    <div className="h-4 bg-gray-200 rounded w-1/3"></div>
                </div>
            </div>
        );
    }

    return (
        <Link
            to={`/project/${project._id}/data`}
            className="block bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow"
        >
            <h2 className="text-xl font-semibold text-gray-900 mb-2">{project.project_name}</h2>
            <p className="text-gray-600 mb-4">{project.description || 'No description'}</p>
            <div className="flex justify-between text-sm text-gray-500">
                <span>Models: {project.models_count || 0}</span>
                <span>Experiments: {project.experiments_count || 0}</span>
            </div>
        </Link>
    );
} 