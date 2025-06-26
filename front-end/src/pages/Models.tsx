import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { CURRENT_USER } from '../constants/user';
import Card from '../components/Card';
import {
    TbUpload,
    TbDownload,
    TbEye,
    TbTrash,
    TbFile,
    TbCalendar,
    TbScale,
    TbBrain,
    TbChartLine
} from 'react-icons/tb';
import { modelApi } from '../services/api';
import type { Model, ModelListResponse } from '../types/api';

export default function Models() {
    const { id: projectId } = useParams<{ id: string }>();
    const userId = CURRENT_USER.id;
    const [models, setModels] = useState<Model[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [uploadModalOpen, setUploadModalOpen] = useState(false);
    const [selectedModel, setSelectedModel] = useState<Model | null>(null);
    const [viewModalOpen, setViewModalOpen] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [uploadError, setUploadError] = useState<string | null>(null);
    const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
    const [deleteLoading, setDeleteLoading] = useState<string | null>(null);

    // Fetch models from backend
    useEffect(() => {
        if (!userId || !projectId) return;
        setLoading(true);
        setError(null);
        modelApi.getModels(userId, projectId)
            .then((res: ModelListResponse) => {
                setModels(res.models);
                setLoading(false);
            })
            .catch((err) => {
                setError(err.message || 'Failed to fetch models');
                setLoading(false);
            });
    }, [userId, projectId]);

    const formatFileSize = (bytes: number): string => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    const formatDate = (dateString: string): string => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'active':
                return 'bg-green-100 text-green-800';
            case 'archived':
                return 'bg-gray-100 text-gray-800';
            case 'training':
                return 'bg-blue-100 text-blue-800';
            default:
                return 'bg-gray-100 text-gray-800';
        }
    };

    const handleUploadModel = () => {
        setUploadModalOpen(true);
        setUploadError(null);
        setUploadSuccess(null);
    };

    const handleUploadSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setUploading(true);
        setUploadError(null);
        setUploadSuccess(null);
        const form = e.currentTarget;
        const formData = new FormData(form);
        try {
            await modelApi.uploadModel(userId, projectId!, formData);
            setUploadSuccess('Model uploaded successfully!');
            setUploadModalOpen(false);
            // Refresh models
            setLoading(true);
            const res = await modelApi.getModels(userId, projectId!);
            setModels(res.models);
        } catch (err: any) {
            setUploadError(err.message || 'Failed to upload model');
        } finally {
            setUploading(false);
        }
    };

    const handleViewModel = (model: Model) => {
        setSelectedModel(model);
        setViewModalOpen(true);
    };

    const handleDownloadModel = async (model: Model) => {
        try {
            const res = await modelApi.downloadModel(userId, projectId!, model._id);
            // For now, just open the file path in a new tab (if served statically)
            window.open(`/static/${res.file_path}`, '_blank');
        } catch (err: any) {
            alert(err.message || 'Failed to download model');
        }
    };

    const handleDeleteModel = async (model: Model) => {
        if (!window.confirm(`Are you sure you want to delete ${model.name}?`)) return;
        setDeleteLoading(model._id);
        try {
            await modelApi.deleteModel(userId, projectId!, model._id);
            setModels(models.filter(m => m._id !== model._id));
        } catch (err: any) {
            alert(err.message || 'Failed to delete model');
        } finally {
            setDeleteLoading(null);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
        );
    }
    if (error) {
        return (
            <div className="flex items-center justify-center h-64 text-red-600 font-semibold">
                {error}
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Models</h1>
                    <p className="text-gray-600 mt-1">
                        Manage and track your trained machine learning models
                    </p>
                </div>
                <button
                    onClick={handleUploadModel}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                    <TbUpload className="w-4 h-4 mr-2" />
                    Upload Model
                </button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card title="Total Models">
                    <div className="flex items-center">
                        <div className="flex-shrink-0">
                            <TbBrain className="h-8 w-8 text-blue-600" />
                        </div>
                        <div className="ml-4">
                            <p className="text-sm font-medium text-gray-500">Total Models</p>
                            <p className="text-2xl font-semibold text-gray-900">{models.length}</p>
                        </div>
                    </div>
                </Card>
                <Card title="Active Models">
                    <div className="flex items-center">
                        <div className="flex-shrink-0">
                            <TbScale className="h-8 w-8 text-green-600" />
                        </div>
                        <div className="ml-4">
                            <p className="text-sm font-medium text-gray-500">Active Models</p>
                            <p className="text-2xl font-semibold text-gray-900">
                                {models.filter(m => m.status === 'active').length}
                            </p>
                        </div>
                    </div>
                </Card>
                <Card title="Avg Accuracy">
                    <div className="flex items-center">
                        <div className="flex-shrink-0">
                            <TbChartLine className="h-8 w-8 text-purple-600" />
                        </div>
                        <div className="ml-4">
                            <p className="text-sm font-medium text-gray-500">Avg Accuracy</p>
                            <p className="text-2xl font-semibold text-gray-900">
                                {models.length > 0
                                    ? Math.round(models.reduce((acc, m) => acc + (m.metrics?.accuracy || 0), 0) / models.length * 100)
                                    : 0}%
                            </p>
                        </div>
                    </div>
                </Card>
                <Card title="Total Size">
                    <div className="flex items-center">
                        <div className="flex-shrink-0">
                            <TbFile className="h-8 w-8 text-orange-600" />
                        </div>
                        <div className="ml-4">
                            <p className="text-sm font-medium text-gray-500">Total Size</p>
                            <p className="text-2xl font-semibold text-gray-900">
                                {formatFileSize(models.reduce((acc, m) => acc + m.file_size, 0))}
                            </p>
                        </div>
                    </div>
                </Card>
            </div>

            {/* Models List */}
            <Card title="Trained Models">
                <div className="divide-y divide-gray-200">
                    {models.length === 0 ? (
                        <div className="px-6 py-12 text-center">
                            <TbBrain className="mx-auto h-12 w-12 text-gray-400" />
                            <h3 className="mt-2 text-sm font-medium text-gray-900">No models</h3>
                            <p className="mt-1 text-sm text-gray-500">
                                Get started by uploading your first trained model.
                            </p>
                            <div className="mt-6">
                                <button
                                    onClick={handleUploadModel}
                                    className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                                >
                                    <TbUpload className="w-4 h-4 mr-2" />
                                    Upload Model
                                </button>
                            </div>
                        </div>
                    ) : (
                        models.map((model) => (
                            <div key={model._id} className="px-6 py-4">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center space-x-4">
                                        <div className="flex-shrink-0">
                                            <TbBrain className="h-8 w-8 text-blue-600" />
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-center space-x-2">
                                                <h4 className="text-sm font-medium text-gray-900 truncate">
                                                    {model.name}
                                                </h4>
                                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(model.status)}`}>
                                                    {model.status}
                                                </span>
                                            </div>
                                            <p className="text-sm text-gray-500 truncate">
                                                {model.description || `${model.framework} ${model.model_type} model`}
                                            </p>
                                            <div className="flex items-center space-x-4 mt-1 text-xs text-gray-400">
                                                <span className="flex items-center">
                                                    <TbFile className="w-3 h-3 mr-1" />
                                                    {model.filename}
                                                </span>
                                                <span className="flex items-center">
                                                    <TbCalendar className="w-3 h-3 mr-1" />
                                                    {formatDate(model.created_at)}
                                                </span>
                                                <span>{formatFileSize(model.file_size)}</span>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        {model.metrics?.accuracy && (
                                            <div className="text-right">
                                                <p className="text-sm font-medium text-gray-900">
                                                    {Math.round(model.metrics.accuracy * 100)}%
                                                </p>
                                                <p className="text-xs text-gray-500">Accuracy</p>
                                            </div>
                                        )}
                                        <div className="flex space-x-1">
                                            <button
                                                onClick={() => handleViewModel(model)}
                                                className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md"
                                                title="View details"
                                            >
                                                <TbEye className="w-4 h-4" />
                                            </button>
                                            <button
                                                onClick={() => handleDownloadModel(model)}
                                                className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md"
                                                title="Download model"
                                            >
                                                <TbDownload className="w-4 h-4" />
                                            </button>
                                            <button
                                                onClick={() => handleDeleteModel(model)}
                                                className={`p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-md ${deleteLoading === model._id ? 'opacity-50 pointer-events-none' : ''}`}
                                                title="Delete model"
                                                disabled={deleteLoading === model._id}
                                            >
                                                {deleteLoading === model._id ? (
                                                    <span className="animate-spin w-4 h-4 border-b-2 border-red-600 rounded-full inline-block"></span>
                                                ) : (
                                                    <TbTrash className="w-4 h-4" />
                                                )}
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </Card>

            {/* Upload Modal */}
            {uploadModalOpen && (
                <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
                    <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
                        <form onSubmit={handleUploadSubmit} className="mt-3">
                            <h3 className="text-lg font-medium text-gray-900 mb-4">Upload Model</h3>
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">
                                        Model Name
                                    </label>
                                    <input
                                        name="name"
                                        type="text"
                                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                                        placeholder="Enter model name"
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">
                                        Description
                                    </label>
                                    <textarea
                                        name="description"
                                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                                        rows={3}
                                        placeholder="Enter model description"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">
                                        Model File
                                    </label>
                                    <input
                                        name="file"
                                        type="file"
                                        accept=".pkl,.joblib,.h5,.pb,.onnx"
                                        className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                                        required
                                    />
                                </div>
                                {/* Add more fields as needed for type, framework, version, metrics, parameters */}
                                <div className="flex justify-end space-x-3">
                                    <button
                                        type="button"
                                        onClick={() => setUploadModalOpen(false)}
                                        className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                                        disabled={uploading}
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        type="submit"
                                        className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700"
                                        disabled={uploading}
                                    >
                                        {uploading ? 'Uploading...' : 'Upload'}
                                    </button>
                                </div>
                                {uploadError && <div className="text-red-600 text-sm">{uploadError}</div>}
                                {uploadSuccess && <div className="text-green-600 text-sm">{uploadSuccess}</div>}
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* View Model Modal */}
            {viewModalOpen && selectedModel && (
                <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
                    <div className="relative top-10 mx-auto p-5 border w-3/4 max-w-4xl shadow-lg rounded-md bg-white">
                        <div className="mt-3">
                            <div className="flex justify-between items-center mb-4">
                                <h3 className="text-lg font-medium text-gray-900">{selectedModel.name}</h3>
                                <button
                                    onClick={() => setViewModalOpen(false)}
                                    className="text-gray-400 hover:text-gray-600"
                                >
                                    ×
                                </button>
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div>
                                    <h4 className="text-sm font-medium text-gray-900 mb-3">Model Information</h4>
                                    <dl className="space-y-2">
                                        <div>
                                            <dt className="text-sm font-medium text-gray-500">Filename</dt>
                                            <dd className="text-sm text-gray-900">{selectedModel.filename}</dd>
                                        </div>
                                        <div>
                                            <dt className="text-sm font-medium text-gray-500">Framework</dt>
                                            <dd className="text-sm text-gray-900">{selectedModel.framework}</dd>
                                        </div>
                                        <div>
                                            <dt className="text-sm font-medium text-gray-500">Model Type</dt>
                                            <dd className="text-sm text-gray-900">{selectedModel.model_type}</dd>
                                        </div>
                                        <div>
                                            <dt className="text-sm font-medium text-gray-500">Version</dt>
                                            <dd className="text-sm text-gray-900">{selectedModel.version}</dd>
                                        </div>
                                        <div>
                                            <dt className="text-sm font-medium text-gray-500">File Size</dt>
                                            <dd className="text-sm text-gray-900">{formatFileSize(selectedModel.file_size)}</dd>
                                        </div>
                                        <div>
                                            <dt className="text-sm font-medium text-gray-500">Created</dt>
                                            <dd className="text-sm text-gray-900">{formatDate(selectedModel.created_at)}</dd>
                                        </div>
                                        <div>
                                            <dt className="text-sm font-medium text-gray-500">Description</dt>
                                            <dd className="text-sm text-gray-900">{selectedModel.description || 'No description provided'}</dd>
                                        </div>
                                    </dl>
                                </div>
                                <div>
                                    <h4 className="text-sm font-medium text-gray-900 mb-3">Performance Metrics</h4>
                                    {selectedModel.metrics ? (
                                        <div className="space-y-3">
                                            {Object.entries(selectedModel.metrics).map(([key, value]) => (
                                                <div key={key} className="flex justify-between items-center">
                                                    <span className="text-sm font-medium text-gray-500 capitalize">
                                                        {key.replace('_', ' ')}
                                                    </span>
                                                    <span className="text-sm text-gray-900">
                                                        {typeof value === 'number' && key !== 'loss'
                                                            ? `${Math.round(value * 100)}%`
                                                            : value}
                                                    </span>
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        <p className="text-sm text-gray-500">No metrics available</p>
                                    )}

                                    {selectedModel.parameters && (
                                        <>
                                            <h4 className="text-sm font-medium text-gray-900 mb-3 mt-6">Model Parameters</h4>
                                            <div className="space-y-2">
                                                {Object.entries(selectedModel.parameters).map(([key, value]) => (
                                                    <div key={key} className="flex justify-between items-center">
                                                        <span className="text-sm font-medium text-gray-500 capitalize">
                                                            {key.replace('_', ' ')}
                                                        </span>
                                                        <span className="text-sm text-gray-900">{value}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        </>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
} 