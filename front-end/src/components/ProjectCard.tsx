import type { Project } from '../types/api';

interface ProjectCardProps {
    project: Project;
}

export default function ProjectCard({ project }: ProjectCardProps) {
    if (!project) {
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
        <div className="block bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-all">
            <div className="flex justify-between items-start mb-4">
                <h2 className="text-xl font-semibold text-gray-900">{project.project_name}</h2>
                <span className={`px-2 py-1 text-xs rounded-full ${project.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                    {project.status || 'Active'}
                </span>
            </div>

            <p className="text-gray-600 mb-4 line-clamp-2">{project.description || 'No description'}</p>

            <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                    <p className="text-sm text-gray-500">Type</p>
                    <p className="text-sm font-medium">{project.project_type || 'Not specified'}</p>
                </div>
                <div>
                    <p className="text-sm text-gray-500">Framework</p>
                    <p className="text-sm font-medium">{project.framework || 'Not specified'}</p>
                </div>
            </div>

            <div className="flex justify-between items-center pt-4 border-t border-gray-100">
                <div className="flex space-x-4">
                    <div className="text-center">
                        <p className="text-sm text-gray-500">Models</p>
                        <p className="text-sm font-medium">{project.models_count || 0}</p>
                    </div>
                    <div className="text-center">
                        <p className="text-sm text-gray-500">Experiments</p>
                        <p className="text-sm font-medium">{project.experiments_count || 0}</p>
                    </div>
                </div>
                {project.created_at && (
                    <p className="text-xs text-gray-500">
                        Created {new Date(project.created_at).toLocaleDateString()}
                    </p>
                )}
            </div>
        </div>
    );
} 