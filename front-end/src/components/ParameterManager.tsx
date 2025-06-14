import React, { useState, useEffect } from 'react';
import { API_ENDPOINTS } from '../constants/api';

interface ParameterValue {
    name: string;
    value: any;
    type: string;
    description?: string;
    required?: boolean;
    validation?: {
        min?: number;
        max?: number;
        pattern?: string;
    };
}

interface ParameterGroup {
    name: string;
    description?: string;
    parameters: ParameterValue[];
}

interface ParameterSet {
    name: string;
    description?: string;
    groups: ParameterGroup[];
    created_at?: string;
    updated_at?: string;
}

interface ParameterManagerProps {
    userId: string;
    projectId: string;
}

export default function ParameterManager({ userId, projectId }: ParameterManagerProps) {
    const [parameterSet, setParameterSet] = useState<ParameterSet | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);
    const [activeTab, setActiveTab] = useState('current');
    const [showCreateDialog, setShowCreateDialog] = useState(false);
    const [showImportDialog, setShowImportDialog] = useState(false);
    const [showExportDialog, setShowExportDialog] = useState(false);
    const [editingParameter, setEditingParameter] = useState<{
        groupIndex: number;
        paramIndex: number;
        parameter: ParameterValue;
    } | null>(null);

    // Load current parameters
    useEffect(() => {
        loadCurrentParameters();
    }, [userId, projectId]);

    const loadCurrentParameters = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const response = await fetch(API_ENDPOINTS.CURRENT_PARAMETERS(userId, projectId));
            if (response.ok) {
                const data = await response.json();
                if (data.parameter_set) {
                    setParameterSet(data.parameter_set);
                }
            } else {
                const errorData = await response.json();
                setError(errorData.detail || 'Failed to load parameters');
            }
        } catch (err) {
            setError('Failed to load parameters');
        } finally {
            setIsLoading(false);
        }
    };

    const createParameterSet = async (newParameterSet: ParameterSet) => {
        setIsLoading(true);
        setError(null);
        try {
            const response = await fetch(API_ENDPOINTS.PARAMETERS(userId, projectId), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(newParameterSet),
            });

            if (response.ok) {
                const data = await response.json();
                setSuccess(data.message);
                setParameterSet(newParameterSet);
                setShowCreateDialog(false);
                setTimeout(() => setSuccess(null), 3000);
            } else {
                const errorData = await response.json();
                setError(errorData.detail || 'Failed to create parameter set');
            }
        } catch (err) {
            setError('Failed to create parameter set');
        } finally {
            setIsLoading(false);
        }
    };

    const updateParameterSet = async (updatedParameterSet: ParameterSet) => {
        setIsLoading(true);
        setError(null);
        try {
            const response = await fetch(API_ENDPOINTS.PARAMETERS(userId, projectId), {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(updatedParameterSet),
            });

            if (response.ok) {
                const data = await response.json();
                setSuccess(data.message);
                setParameterSet(updatedParameterSet);
                setTimeout(() => setSuccess(null), 3000);
            } else {
                const errorData = await response.json();
                setError(errorData.detail || 'Failed to update parameter set');
            }
        } catch (err) {
            setError('Failed to update parameter set');
        } finally {
            setIsLoading(false);
        }
    };

    const deleteParameterSet = async () => {
        if (!confirm('Are you sure you want to delete the current parameter set?')) {
            return;
        }

        setIsLoading(true);
        setError(null);
        try {
            const response = await fetch(API_ENDPOINTS.PARAMETERS(userId, projectId), {
                method: 'DELETE',
            });

            if (response.ok) {
                const data = await response.json();
                setSuccess(data.message);
                setParameterSet(null);
                setTimeout(() => setSuccess(null), 3000);
            } else {
                const errorData = await response.json();
                setError(errorData.detail || 'Failed to delete parameter set');
            }
        } catch (err) {
            setError('Failed to delete parameter set');
        } finally {
            setIsLoading(false);
        }
    };

    const validateParameters = async () => {
        if (!parameterSet) {
            setError('No parameters to validate');
            return;
        }

        setIsLoading(true);
        setError(null);
        try {
            const response = await fetch(API_ENDPOINTS.VALIDATE_PARAMETERS(userId, projectId), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(parameterSet),
            });

            if (response.ok) {
                const data = await response.json();
                if (data.valid) {
                    setSuccess('All parameters are valid!');
                } else {
                    setError(`Validation failed: ${data.errors.join(', ')}`);
                }
                setTimeout(() => {
                    setSuccess(null);
                    setError(null);
                }, 5000);
            } else {
                const errorData = await response.json();
                setError(errorData.detail || 'Failed to validate parameters');
            }
        } catch (err) {
            setError('Failed to validate parameters');
        } finally {
            setIsLoading(false);
        }
    };

    const exportParameters = async (format: string) => {
        if (!parameterSet) {
            setError('No parameters to export');
            return;
        }

        try {
            const response = await fetch(`${API_ENDPOINTS.EXPORT_PARAMETERS(userId, projectId)}?format=${format}`);
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `parameters.${format}`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                setSuccess(`Parameters exported as ${format.toUpperCase()}`);
                setTimeout(() => setSuccess(null), 3000);
            } else {
                const errorData = await response.json();
                setError(errorData.detail || 'Failed to export parameters');
            }
        } catch (err) {
            setError('Failed to export parameters');
        }
    };

    const importParameters = async (file: File) => {
        setIsLoading(true);
        setError(null);
        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch(API_ENDPOINTS.UPLOAD_PARAMETERS(userId, projectId), {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                const data = await response.json();
                setSuccess(data.message);
                await loadCurrentParameters();
                setShowImportDialog(false);
                setTimeout(() => setSuccess(null), 3000);
            } else {
                const errorData = await response.json();
                setError(errorData.detail || 'Failed to import parameters');
            }
        } catch (err) {
            setError('Failed to import parameters');
        } finally {
            setIsLoading(false);
        }
    };

    const updateParameterValue = (groupIndex: number, paramIndex: number, value: any) => {
        if (!parameterSet) return;

        const updatedParameterSet = { ...parameterSet };
        updatedParameterSet.groups[groupIndex].parameters[paramIndex].value = value;
        setParameterSet(updatedParameterSet);
    };

    const saveChanges = async () => {
        if (!parameterSet) return;
        await updateParameterSet(parameterSet);
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center p-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                <span className="ml-2">Loading parameters...</span>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="bg-white p-6 rounded-lg border border-gray-200">
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-2xl font-bold text-gray-900">Parameter Management</h2>
                        <p className="text-gray-600">Manage and configure parameters for your project</p>
                    </div>
                    <div className="flex gap-2">
                        <button
                            onClick={() => setShowImportDialog(true)}
                            className="px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600 transition-colors"
                        >
                            Import
                        </button>
                        <button
                            onClick={() => setShowExportDialog(true)}
                            className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 transition-colors"
                        >
                            Export
                        </button>
                        <button
                            onClick={() => setShowCreateDialog(true)}
                            className="px-4 py-2 bg-indigo-500 text-white rounded hover:bg-indigo-600 transition-colors"
                        >
                            Create New
                        </button>
                    </div>
                </div>
            </div>

            {/* Error and Success Messages */}
            {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                    {error}
                </div>
            )}
            {success && (
                <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
                    {success}
                </div>
            )}

            {/* Main Content */}
            <div className="bg-white rounded-lg border border-gray-200">
                <div className="p-6">
                    {parameterSet ? (
                        <div className="space-y-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <h3 className="text-lg font-medium text-gray-900">{parameterSet.name}</h3>
                                    {parameterSet.description && (
                                        <p className="text-sm text-gray-600">{parameterSet.description}</p>
                                    )}
                                </div>
                                <div className="flex gap-2">
                                    <button
                                        onClick={saveChanges}
                                        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
                                    >
                                        Save Changes
                                    </button>
                                    <button
                                        onClick={deleteParameterSet}
                                        className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
                                    >
                                        Delete
                                    </button>
                                </div>
                            </div>

                            <div className="space-y-4">
                                {parameterSet.groups.map((group, groupIndex) => (
                                    <div key={groupIndex} className="border border-gray-200 rounded-lg p-4">
                                        <h4 className="text-md font-medium text-gray-900 mb-3">{group.name}</h4>
                                        {group.description && (
                                            <p className="text-sm text-gray-600 mb-4">{group.description}</p>
                                        )}
                                        <div className="grid gap-4 md:grid-cols-2">
                                            {group.parameters.map((param, paramIndex) => (
                                                <div key={paramIndex} className="space-y-2">
                                                    <label className="block text-sm font-medium text-gray-700">
                                                        {param.name}
                                                        {param.required && <span className="text-red-500 ml-1">*</span>}
                                                    </label>
                                                    {param.description && (
                                                        <p className="text-xs text-gray-500">{param.description}</p>
                                                    )}
                                                    {param.type === 'boolean' ? (
                                                        <input
                                                            type="checkbox"
                                                            checked={param.value || false}
                                                            onChange={(e) => updateParameterValue(groupIndex, paramIndex, e.target.checked)}
                                                            className="rounded border-gray-300"
                                                        />
                                                    ) : param.type === 'number' ? (
                                                        <input
                                                            type="number"
                                                            value={param.value || ''}
                                                            onChange={(e) => updateParameterValue(groupIndex, paramIndex, parseFloat(e.target.value) || 0)}
                                                            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                                        />
                                                    ) : (
                                                        <input
                                                            type="text"
                                                            value={param.value || ''}
                                                            onChange={(e) => updateParameterValue(groupIndex, paramIndex, e.target.value)}
                                                            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                                        />
                                                    )}
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ) : (
                        <div className="text-center py-12">
                            <div className="text-gray-400 text-6xl mb-4">⚙️</div>
                            <h3 className="text-lg font-medium text-gray-900 mb-2">No Parameters Set</h3>
                            <p className="text-gray-600 mb-4">
                                Get started by creating a parameter set or importing from a file.
                            </p>
                            <div className="flex gap-2 justify-center">
                                <button
                                    onClick={() => setShowCreateDialog(true)}
                                    className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
                                >
                                    Create Parameter Set
                                </button>
                                <button
                                    onClick={() => setShowImportDialog(true)}
                                    className="px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600 transition-colors"
                                >
                                    Import from File
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Modals */}
            {showCreateDialog && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg p-6 w-full max-w-2xl">
                        <div className="flex justify-between items-start mb-4">
                            <h3 className="text-lg font-medium">Create New Parameter Set</h3>
                            <button
                                onClick={() => setShowCreateDialog(false)}
                                className="text-gray-500 hover:text-gray-700"
                            >
                                ✕
                            </button>
                        </div>
                        <form onSubmit={(e) => {
                            e.preventDefault();
                            const formData = new FormData(e.currentTarget);
                            const newParameterSet: ParameterSet = {
                                name: formData.get('name') as string,
                                description: formData.get('description') as string,
                                groups: []
                            };
                            createParameterSet(newParameterSet);
                        }}>
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">Name</label>
                                    <input
                                        type="text"
                                        name="name"
                                        required
                                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">Description</label>
                                    <textarea
                                        name="description"
                                        rows={3}
                                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                    />
                                </div>
                                <div className="flex justify-end gap-2">
                                    <button
                                        type="button"
                                        onClick={() => setShowCreateDialog(false)}
                                        className="px-4 py-2 text-gray-700 bg-gray-100 rounded hover:bg-gray-200"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        type="submit"
                                        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                                    >
                                        Create
                                    </button>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {showImportDialog && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg p-6 w-full max-w-md">
                        <div className="flex justify-between items-start mb-4">
                            <h3 className="text-lg font-medium">Import Parameters</h3>
                            <button
                                onClick={() => setShowImportDialog(false)}
                                className="text-gray-500 hover:text-gray-700"
                            >
                                ✕
                            </button>
                        </div>
                        <div className="space-y-4">
                            <p className="text-sm text-gray-600">
                                Upload a YAML, JSON, or ENV file to import parameters.
                            </p>
                            <input
                                type="file"
                                accept=".yaml,.yml,.json,.env"
                                onChange={(e) => {
                                    const file = e.target.files?.[0];
                                    if (file) {
                                        importParameters(file);
                                    }
                                }}
                                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                            />
                            <div className="flex justify-end gap-2">
                                <button
                                    onClick={() => setShowImportDialog(false)}
                                    className="px-4 py-2 text-gray-700 bg-gray-100 rounded hover:bg-gray-200"
                                >
                                    Cancel
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {showExportDialog && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg p-6 w-full max-w-md">
                        <div className="flex justify-between items-start mb-4">
                            <h3 className="text-lg font-medium">Export Parameters</h3>
                            <button
                                onClick={() => setShowExportDialog(false)}
                                className="text-gray-500 hover:text-gray-700"
                            >
                                ✕
                            </button>
                        </div>
                        <div className="space-y-4">
                            <p className="text-sm text-gray-600">
                                Choose a format to export your parameters.
                            </p>
                            <div className="grid grid-cols-3 gap-2">
                                <button
                                    onClick={() => {
                                        exportParameters('yaml');
                                        setShowExportDialog(false);
                                    }}
                                    className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                                >
                                    YAML
                                </button>
                                <button
                                    onClick={() => {
                                        exportParameters('json');
                                        setShowExportDialog(false);
                                    }}
                                    className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
                                >
                                    JSON
                                </button>
                                <button
                                    onClick={() => {
                                        exportParameters('env');
                                        setShowExportDialog(false);
                                    }}
                                    className="px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600"
                                >
                                    ENV
                                </button>
                            </div>
                            <div className="flex justify-end gap-2">
                                <button
                                    onClick={() => setShowExportDialog(false)}
                                    className="px-4 py-2 text-gray-700 bg-gray-100 rounded hover:bg-gray-200"
                                >
                                    Cancel
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
} 