import { useState } from 'react';
import { useProjects } from '../hooks/useProjects';
import { CURRENT_USER } from '../constants/user';
import CreateProjectModal from '../components/CreateProjectModal';
import ProjectCard from '../components/ProjectCard';
import type { CreateProjectRequest, Project } from '../types/api';

type ProjectFormData = Omit<CreateProjectRequest, 'username'>;

export default function Projects() {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const { getProjects, createProject } = useProjects(CURRENT_USER.id);
    const { data: projects, isLoading, error } = getProjects();
    const createProjectMutation = createProject();

    const handleCreateProject = async (projectData: ProjectFormData) => {
        try {
            await createProjectMutation.mutateAsync({
                username: CURRENT_USER.id,
                ...projectData
            });
            setIsModalOpen(false);
        } catch (error) {
            console.error('Failed to create project:', error);
        }
    };

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

    if (!projects || projects.length === 0) {
        return (
            <div className="text-center py-12">
                <h2 className="text-2xl font-semibold text-gray-700">No Projects Found</h2>
                <p className="text-gray-500 mt-2">Create your first project to get started!</p>
                <button
                    onClick={() => setIsModalOpen(true)}
                    className="mt-4 inline-block px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
                >
                    Create Project
                </button>
                <CreateProjectModal
                    isOpen={isModalOpen}
                    onClose={() => setIsModalOpen(false)}
                    onSubmit={handleCreateProject}
                    error={createProjectMutation.error instanceof Error ? createProjectMutation.error.message : undefined}
                    isLoading={createProjectMutation.isPending}
                />
            </div>
        );
    }

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">My Projects</h1>
                    <p className="text-gray-600 mt-2">Manage your machine learning projects</p>
                </div>
                <button
                    onClick={() => setIsModalOpen(true)}
                    className="px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
                >
                    Create Project
                </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {projects.map(project => (
                    <ProjectCard
                        key={project._id}
                        project={project}
                    />
                ))}
            </div>
            <CreateProjectModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onSubmit={handleCreateProject}
                error={createProjectMutation.error instanceof Error ? createProjectMutation.error.message : undefined}
                isLoading={createProjectMutation.isPending}
            />
        </div>
    );
} 