import { useState } from 'react';

interface CreateProjectModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSubmit: (projectData: {
        project_name: string;
        description: string;
        project_type: string;
        framework: string;
        python_version: string;
        dependencies: string[];
    }) => void;
    error?: string | null;
    isLoading?: boolean;
}

const CreateProjectModal = ({ isOpen, onClose, onSubmit, error, isLoading = false }: CreateProjectModalProps) => {
    const [formData, setFormData] = useState({
        project_name: '',
        description: '',
        project_type: 'Image Classification',
        framework: 'PyTorch',
        python_version: '3.9',
        dependencies: ['torch==2.0.1', 'torchvision==0.15.2', 'numpy==1.24.3', 'pandas==2.0.3']
    });

    const [currentDependency, setCurrentDependency] = useState('');

    if (!isOpen) return null;

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSubmit(formData);
        setFormData({
            project_name: '',
            description: '',
            project_type: 'Image Classification',
            framework: 'PyTorch',
            python_version: '3.9',
            dependencies: ['torch==2.0.1', 'torchvision==0.15.2', 'numpy==1.24.3', 'pandas==2.0.3']
        });
    };

    const handleAddDependency = () => {
        if (currentDependency.trim()) {
            setFormData(prev => ({
                ...prev,
                dependencies: [...prev.dependencies, currentDependency.trim()]
            }));
            setCurrentDependency('');
        }
    };

    const handleRemoveDependency = (index: number) => {
        setFormData(prev => ({
            ...prev,
            dependencies: prev.dependencies.filter((_, i) => i !== index)
        }));
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center overflow-y-auto py-10">
            <div className="bg-white rounded-lg p-6 w-[600px] max-h-[90vh] overflow-y-auto">
                <h2 className="text-xl font-semibold mb-4">Create New Project</h2>
                {error && (
                    <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
                        <p className="text-sm text-red-600">{error}</p>
                    </div>
                )}
                <form onSubmit={handleSubmit} id="create-project-form" name="create-project-form" className="space-y-6">
                    {/* Basic Information */}
                    <div>
                        <h3 className="text-sm font-medium text-gray-700 mb-4">Basic Information</h3>
                        <div className="space-y-4">
                            <div>
                                <label htmlFor="project-name" className="block text-sm font-medium text-gray-700 mb-1">
                                    Project Name*
                                </label>
                                <input
                                    type="text"
                                    id="project-name"
                                    name="project-name"
                                    value={formData.project_name}
                                    onChange={(e) => setFormData(prev => ({ ...prev, project_name: e.target.value }))}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                    autoComplete="off"
                                    placeholder="Enter project name"
                                    aria-label="Project name"
                                />
                            </div>
                            <div>
                                <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
                                    Description
                                </label>
                                <textarea
                                    id="description"
                                    name="description"
                                    value={formData.description}
                                    onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    rows={3}
                                    placeholder="Enter project description"
                                    aria-label="Project description"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Project Configuration */}
                    <div>
                        <h3 className="text-sm font-medium text-gray-700 mb-4">Project Configuration</h3>
                        <div className="space-y-4">
                            <div>
                                <label htmlFor="project-type" className="block text-sm font-medium text-gray-700 mb-1">
                                    Project Type
                                </label>
                                <select
                                    id="project-type"
                                    name="project-type"
                                    value={formData.project_type}
                                    onChange={(e) => setFormData(prev => ({ ...prev, project_type: e.target.value }))}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="Image Classification">Image Classification</option>
                                    <option value="Object Detection">Object Detection</option>
                                    <option value="Segmentation">Segmentation</option>
                                    <option value="Natural Language Processing">Natural Language Processing</option>
                                    <option value="Time Series">Time Series</option>
                                    <option value="Other">Other</option>
                                </select>
                            </div>
                            <div>
                                <label htmlFor="framework" className="block text-sm font-medium text-gray-700 mb-1">
                                    Framework
                                </label>
                                <select
                                    id="framework"
                                    name="framework"
                                    value={formData.framework}
                                    onChange={(e) => setFormData(prev => ({ ...prev, framework: e.target.value }))}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="PyTorch">PyTorch</option>
                                    <option value="TensorFlow">TensorFlow</option>
                                    <option value="JAX">JAX</option>
                                    <option value="Scikit-learn">Scikit-learn</option>
                                </select>
                            </div>
                            <div>
                                <label htmlFor="python-version" className="block text-sm font-medium text-gray-700 mb-1">
                                    Python Version
                                </label>
                                <select
                                    id="python-version"
                                    name="python-version"
                                    value={formData.python_version}
                                    onChange={(e) => setFormData(prev => ({ ...prev, python_version: e.target.value }))}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="3.9">Python 3.9</option>
                                    <option value="3.10">Python 3.10</option>
                                    <option value="3.11">Python 3.11</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    {/* Dependencies */}
                    <div>
                        <h3 className="text-sm font-medium text-gray-700 mb-4">Dependencies</h3>
                        <div className="space-y-4">
                            <div className="flex space-x-2">
                                <input
                                    type="text"
                                    value={currentDependency}
                                    onChange={(e) => setCurrentDependency(e.target.value)}
                                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    placeholder="Add dependency (e.g., numpy==1.24.3)"
                                />
                                <button
                                    type="button"
                                    onClick={handleAddDependency}
                                    className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
                                >
                                    Add
                                </button>
                            </div>
                            <div className="space-y-2">
                                {formData.dependencies.map((dep, index) => (
                                    <div key={index} className="flex items-center justify-between bg-gray-50 px-3 py-2 rounded">
                                        <code className="text-sm">{dep}</code>
                                        <button
                                            type="button"
                                            onClick={() => handleRemoveDependency(index)}
                                            className="text-red-500 hover:text-red-700"
                                        >
                                            Remove
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Actions */}
                    <div className="flex justify-end space-x-3 pt-4 border-t">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-4 py-2 text-gray-600 hover:text-gray-800"
                            id="cancel-create-project"
                            name="cancel-create-project"
                            disabled={isLoading}
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className={`px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center ${isLoading ? 'opacity-75 cursor-not-allowed' : ''
                                }`}
                            id="submit-create-project"
                            name="submit-create-project"
                            disabled={isLoading}
                        >
                            {isLoading ? (
                                <>
                                    <svg
                                        className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                                        xmlns="http://www.w3.org/2000/svg"
                                        fill="none"
                                        viewBox="0 0 24 24"
                                    >
                                        <circle
                                            className="opacity-25"
                                            cx="12"
                                            cy="12"
                                            r="10"
                                            stroke="currentColor"
                                            strokeWidth="4"
                                        ></circle>
                                        <path
                                            className="opacity-75"
                                            fill="currentColor"
                                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                                        ></path>
                                    </svg>
                                    Creating...
                                </>
                            ) : (
                                'Create Project'
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default CreateProjectModal; 