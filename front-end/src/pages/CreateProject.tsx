import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useProjects } from '../hooks/useProjects';
import { CURRENT_USER } from '../constants/user';

export default function CreateProject() {
    const navigate = useNavigate();
    const mutation = useProjects(CURRENT_USER.id).createProject();
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setError(null);

        const formData = new FormData(e.currentTarget);
        const projectData = {
            username: CURRENT_USER.username,
            project_name: formData.get('project_name') as string,
            description: formData.get('description') as string,
            project_type: formData.get('project_type') as string,
            framework: formData.get('framework') as string,
            python_version: formData.get('python_version') as string,
            dependencies: (formData.get('dependencies') as string).split('\n').filter(Boolean)
        };

        try {
            const result = await mutation.mutateAsync(projectData);
            navigate(`/project/${result.id}/data`);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to create project');
        }
    };

    return (
        <div className="container mx-auto px-4 py-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-6">Create New Project</h1>

            {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
                    {error}
                </div>
            )}

            <form onSubmit={handleSubmit} className="max-w-2xl bg-white p-6 rounded-lg shadow-md">
                <div className="space-y-6">
                    <div>
                        <label htmlFor="project_name" className="block text-sm font-medium text-gray-700">
                            Project Name *
                        </label>
                        <input
                            type="text"
                            name="project_name"
                            id="project_name"
                            required
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        />
                    </div>

                    <div>
                        <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                            Description
                        </label>
                        <textarea
                            name="description"
                            id="description"
                            rows={3}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        />
                    </div>

                    <div>
                        <label htmlFor="project_type" className="block text-sm font-medium text-gray-700">
                            Project Type
                        </label>
                        <select
                            name="project_type"
                            id="project_type"
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        >
                            <option value="">Select a type</option>
                            <option value="image_classification">Image Classification</option>
                            <option value="object_detection">Object Detection</option>
                            <option value="segmentation">Segmentation</option>
                            <option value="nlp">Natural Language Processing</option>
                            <option value="time_series">Time Series</option>
                            <option value="other">Other</option>
                        </select>
                    </div>

                    <div>
                        <label htmlFor="framework" className="block text-sm font-medium text-gray-700">
                            Framework
                        </label>
                        <select
                            name="framework"
                            id="framework"
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        >
                            <option value="">Select a framework</option>
                            <option value="pytorch">PyTorch</option>
                            <option value="tensorflow">TensorFlow</option>
                            <option value="jax">JAX</option>
                            <option value="scikit-learn">scikit-learn</option>
                        </select>
                    </div>

                    <div>
                        <label htmlFor="python_version" className="block text-sm font-medium text-gray-700">
                            Python Version
                        </label>
                        <select
                            name="python_version"
                            id="python_version"
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        >
                            <option value="">Select a version</option>
                            <option value="3.9">3.9</option>
                            <option value="3.10">3.10</option>
                            <option value="3.11">3.11</option>
                        </select>
                    </div>

                    <div>
                        <label htmlFor="dependencies" className="block text-sm font-medium text-gray-700">
                            Dependencies (one per line)
                        </label>
                        <textarea
                            name="dependencies"
                            id="dependencies"
                            rows={5}
                            placeholder="numpy==1.24.3&#10;pandas==2.0.3&#10;scikit-learn==1.3.0"
                            className="mt-1 block w-full font-mono text-sm rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        />
                    </div>

                    <div className="flex justify-end space-x-3">
                        <button
                            type="button"
                            onClick={() => navigate('/projects')}
                            className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={mutation.isPending}
                            className={`px-4 py-2 text-white bg-blue-500 rounded-md hover:bg-blue-600 ${mutation.isPending ? 'opacity-50 cursor-not-allowed' : ''
                                }`}
                        >
                            {mutation.isPending ? 'Creating...' : 'Create Project'}
                        </button>
                    </div>
                </div>
            </form>
        </div>
    );
} 