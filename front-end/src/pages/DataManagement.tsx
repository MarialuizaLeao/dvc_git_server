import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useDataManagement } from '../hooks/useDataManagement';
import { useProjects } from '../hooks/useProjects';
import { CURRENT_USER } from '../constants/user';
import Card from '../components/Card';
import AddDataSourceModal from '../components/AddDataSourceModal';
import RemoteStorageModal from '../components/RemoteStorageModal';
import type { DataSource, RemoteStorage, DvcFile } from '../types/api';

export default function DataManagement() {
    const { id: projectId } = useParams();
    const [isDataSourceModalOpen, setIsDataSourceModalOpen] = useState(false);
    const [isRemoteStorageModalOpen, setIsRemoteStorageModalOpen] = useState(false);
    const [selectedFiles, setSelectedFiles] = useState<string[]>([]);

    const { getProject } = useProjects(CURRENT_USER.id);
    const { data: project, isLoading: projectLoading } = getProject(projectId || '');

    const {
        getDataSources,
        createDataSource,
        deleteDataSource,
        getRemoteStorages,
        createRemoteStorage,
        deleteRemoteStorage,
        trackData,
        trackFiles,
        getUrl,
        setRemote,
        pushData,
        pullData,
        getDvcStatus
    } = useDataManagement(CURRENT_USER.id, projectId || '');

    const { data: dataSources, isLoading: dataSourcesLoading } = getDataSources();
    const { data: remoteStorages, isLoading: remotesLoading } = getRemoteStorages();
    const { data: dvcStatus, isLoading: dvcStatusLoading } = getDvcStatus();

    const createDataSourceMutation = createDataSource;
    const deleteDataSourceMutation = deleteDataSource;
    const createRemoteStorageMutation = createRemoteStorage;
    const deleteRemoteStorageMutation = deleteRemoteStorage;
    const trackDataMutation = trackData;
    const trackFilesMutation = trackFiles;
    const getUrlMutation = getUrl;
    const setRemoteMutation = setRemote;
    const pushDataMutation = pushData;
    const pullDataMutation = pullData;

    const handleCreateDataSource = async (data: any) => {
        try {
            await createDataSourceMutation.mutateAsync(data);
            setIsDataSourceModalOpen(false);
        } catch (error) {
            console.error('Failed to create data source:', error);
        }
    };

    const handleDeleteDataSource = async (sourceId: string) => {
        if (window.confirm('Are you sure you want to delete this data source?')) {
            try {
                await deleteDataSourceMutation.mutateAsync(sourceId);
            } catch (error) {
                console.error('Failed to delete data source:', error);
            }
        }
    };

    const handleCreateRemoteStorage = async (data: any) => {
        try {
            await createRemoteStorageMutation.mutateAsync(data);
            setIsRemoteStorageModalOpen(false);
        } catch (error) {
            console.error('Failed to create remote storage:', error);
        }
    };

    const handleDeleteRemoteStorage = async (remoteId: string) => {
        if (window.confirm('Are you sure you want to delete this remote storage?')) {
            try {
                await deleteRemoteStorageMutation.mutateAsync(remoteId);
            } catch (error) {
                console.error('Failed to delete remote storage:', error);
            }
        }
    };

    const handleTrackData = async () => {
        if (selectedFiles.length === 0) {
            alert('Please select files to track');
            return;
        }
        try {
            await trackDataMutation.mutateAsync(selectedFiles);
            setSelectedFiles([]);
        } catch (error) {
            console.error('Failed to track data:', error);
        }
    };

    const handleTrackFiles = async () => {
        if (selectedFiles.length === 0) {
            alert('Please select files to track');
            return;
        }
        try {
            await trackFilesMutation.mutateAsync(selectedFiles);
            setSelectedFiles([]);
        } catch (error) {
            console.error('Failed to track files:', error);
        }
    };

    const handlePushData = async () => {
        try {
            await pushDataMutation.mutateAsync();
            alert('Data pushed successfully!');
        } catch (error) {
            console.error('Failed to push data:', error);
            alert('Failed to push data. Please check the console for details.');
        }
    };

    const handlePullData = async () => {
        try {
            await pullDataMutation.mutateAsync();
            alert('Data pulled successfully!');
        } catch (error) {
            console.error('Failed to pull data:', error);
            alert('Failed to pull data. Please check the console for details.');
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'completed':
                return 'bg-green-100 text-green-800';
            case 'downloading':
                return 'bg-blue-100 text-blue-800';
            case 'pending':
                return 'bg-yellow-100 text-yellow-800';
            case 'failed':
                return 'bg-red-100 text-red-800';
            default:
                return 'bg-gray-100 text-gray-800';
        }
    };

    const getFileStatusColor = (status: string) => {
        switch (status) {
            case 'tracked':
                return 'bg-green-100 text-green-800';
            case 'untracked':
                return 'bg-yellow-100 text-yellow-800';
            case 'modified':
                return 'bg-blue-100 text-blue-800';
            default:
                return 'bg-gray-100 text-gray-800';
        }
    };

    const formatFileSize = (bytes: number) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    if (projectLoading || dataSourcesLoading || remotesLoading || dvcStatusLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            </div>
        );
    }

    if (!project) {
        return (
            <div className="text-center py-12">
                <h2 className="text-2xl font-semibold text-red-600">Project Not Found</h2>
                <p className="text-gray-700 mt-2">The project you're looking for doesn't exist.</p>
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto space-y-6">
            {/* Header */}
            <div className="bg-white p-6 rounded-lg border border-gray-200">
                <div className="flex justify-between items-start mb-4">
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900">Data Management</h1>
                        <p className="text-gray-500 mt-1">Manage datasets and storage for {project.project_name}</p>
                    </div>
                    <div className="flex space-x-3">
                        <button
                            onClick={() => setIsDataSourceModalOpen(true)}
                            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                        >
                            Add Data Source
                        </button>
                        <button
                            onClick={() => setIsRemoteStorageModalOpen(true)}
                            className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
                        >
                            Configure Storage
                        </button>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Data Sources */}
                <Card title="Data Sources">
                    <div className="space-y-4">
                        {dataSources && dataSources.length > 0 ? (
                            dataSources.map((source) => (
                                <div key={source._id} className="border border-gray-200 rounded-lg p-4">
                                    <div className="flex justify-between items-start">
                                        <div className="flex-1">
                                            <h4 className="font-medium text-gray-900">{source.name}</h4>
                                            <p className="text-sm text-gray-600 mt-1">{source.description}</p>
                                            <div className="mt-2 text-xs text-gray-500">
                                                <div><strong>Type:</strong> {source.type}</div>
                                                <div><strong>Source:</strong> {source.source}</div>
                                                <div><strong>Destination:</strong> {source.destination}</div>
                                                {source.size && (
                                                    <div><strong>Size:</strong> {formatFileSize(source.size)}</div>
                                                )}
                                            </div>
                                            <div className="mt-2">
                                                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(source.status)}`}>
                                                    {source.status}
                                                </span>
                                            </div>
                                        </div>
                                        <button
                                            onClick={() => handleDeleteDataSource(source._id)}
                                            className="text-red-500 hover:text-red-700 ml-2"
                                        >
                                            Delete
                                        </button>
                                    </div>
                                </div>
                            ))
                        ) : (
                            <div className="text-center py-8 text-gray-500">
                                <p>No data sources configured</p>
                                <button
                                    onClick={() => setIsDataSourceModalOpen(true)}
                                    className="mt-2 text-blue-500 hover:text-blue-700"
                                >
                                    Add your first data source
                                </button>
                            </div>
                        )}
                    </div>
                </Card>

                {/* Remote Storage */}
                <Card title="Remote Storage">
                    <div className="space-y-4">
                        {remoteStorages && remoteStorages.length > 0 ? (
                            remoteStorages.map((remote) => (
                                <div key={remote._id} className="border border-gray-200 rounded-lg p-4">
                                    <div className="flex justify-between items-start">
                                        <div className="flex-1">
                                            <div className="flex items-center space-x-2">
                                                <h4 className="font-medium text-gray-900">{remote.name}</h4>
                                                {remote.is_default && (
                                                    <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                                                        Default
                                                    </span>
                                                )}
                                            </div>
                                            <p className="text-sm text-gray-600 mt-1">{remote.url}</p>
                                            <div className="mt-2 text-xs text-gray-500">
                                                <div><strong>Type:</strong> {remote.type.toUpperCase()}</div>
                                            </div>
                                        </div>
                                        <button
                                            onClick={() => handleDeleteRemoteStorage(remote._id)}
                                            className="text-red-500 hover:text-red-700 ml-2"
                                        >
                                            Delete
                                        </button>
                                    </div>
                                </div>
                            ))
                        ) : (
                            <div className="text-center py-8 text-gray-500">
                                <p>No remote storage configured</p>
                                <button
                                    onClick={() => setIsRemoteStorageModalOpen(true)}
                                    className="mt-2 text-green-500 hover:text-green-700"
                                >
                                    Configure storage
                                </button>
                            </div>
                        )}
                    </div>
                </Card>
            </div>

            {/* DVC Status and Operations */}
            <Card title="DVC Status & Operations">
                <div className="space-y-6">
                    {/* DVC Status */}
                    {dvcStatusLoading ? (
                        <div className="flex items-center justify-center py-8">
                            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
                            <span className="ml-2 text-gray-600">Loading DVC status...</span>
                        </div>
                    ) : dvcStatus ? (
                        <div>
                            <h4 className="text-lg font-medium mb-4">File Status</h4>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div className="bg-green-50 p-4 rounded-lg">
                                    <h5 className="font-medium text-green-900">Tracked Files</h5>
                                    <p className="text-2xl font-bold text-green-600">{dvcStatus.tracked.length}</p>
                                    <p className="text-sm text-green-700">
                                        {formatFileSize(dvcStatus.tracked.reduce((sum, file) => sum + file.size, 0))}
                                    </p>
                                </div>
                                <div className="bg-yellow-50 p-4 rounded-lg">
                                    <h5 className="font-medium text-yellow-900">Untracked Files</h5>
                                    <p className="text-2xl font-bold text-yellow-600">{dvcStatus.untracked.length}</p>
                                    <p className="text-sm text-yellow-700">
                                        {formatFileSize(dvcStatus.untracked.reduce((sum, file) => sum + file.size, 0))}
                                    </p>
                                </div>
                                <div className="bg-blue-50 p-4 rounded-lg">
                                    <h5 className="font-medium text-blue-900">Modified Files</h5>
                                    <p className="text-2xl font-bold text-blue-600">{dvcStatus.modified.length}</p>
                                    <p className="text-sm text-blue-700">
                                        {formatFileSize(dvcStatus.modified.reduce((sum, file) => sum + file.size, 0))}
                                    </p>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="text-center py-8 text-gray-500">
                            <p>Unable to load DVC status</p>
                            <p className="text-sm mt-1">DVC may not be initialized or there may be a connection issue</p>
                        </div>
                    )}

                    {/* File Selection */}
                    <div>
                        <h4 className="text-lg font-medium mb-4">Track Files</h4>
                        {dvcStatusLoading ? (
                            <div className="text-gray-500 text-sm">Loading files...</div>
                        ) : dvcStatus && dvcStatus.untracked.length > 0 ? (
                            <div className="space-y-2 max-h-40 overflow-y-auto">
                                {dvcStatus.untracked.map((file: DvcFile) => (
                                    <div key={file.path} className="flex items-center space-x-2">
                                        <input
                                            type="checkbox"
                                            id={file.path}
                                            checked={selectedFiles.includes(file.path)}
                                            onChange={(e) => {
                                                if (e.target.checked) {
                                                    setSelectedFiles([...selectedFiles, file.path]);
                                                } else {
                                                    setSelectedFiles(selectedFiles.filter(f => f !== file.path));
                                                }
                                            }}
                                            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                        />
                                        <label htmlFor={file.path} className="text-sm text-gray-700">
                                            {file.path} ({formatFileSize(file.size)})
                                        </label>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-gray-500 text-sm">
                                {dvcStatus ? "No untracked files found" : "Unable to load file list"}
                            </p>
                        )}
                    </div>

                    {/* Operations */}
                    <div className="flex flex-wrap gap-3">
                        <button
                            onClick={handleTrackData}
                            disabled={selectedFiles.length === 0}
                            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors disabled:opacity-50"
                        >
                            Track Selected Data
                        </button>
                        <button
                            onClick={handleTrackFiles}
                            disabled={selectedFiles.length === 0}
                            className="px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600 transition-colors disabled:opacity-50"
                        >
                            Track Selected Files
                        </button>
                        <button
                            onClick={handlePushData}
                            className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 transition-colors"
                        >
                            Push Data
                        </button>
                        <button
                            onClick={handlePullData}
                            className="px-4 py-2 bg-orange-500 text-white rounded hover:bg-orange-600 transition-colors"
                        >
                            Pull Data
                        </button>
                    </div>
                </div>
            </Card>

            {/* Modals */}
            <AddDataSourceModal
                isOpen={isDataSourceModalOpen}
                onClose={() => setIsDataSourceModalOpen(false)}
                onSubmit={handleCreateDataSource}
                error={
                    createDataSourceMutation.error instanceof Error
                        ? createDataSourceMutation.error.message
                        : undefined
                }
                isLoading={createDataSourceMutation.isPending}
            />

            <RemoteStorageModal
                isOpen={isRemoteStorageModalOpen}
                onClose={() => setIsRemoteStorageModalOpen(false)}
                onSubmit={handleCreateRemoteStorage}
                error={
                    createRemoteStorageMutation.error instanceof Error
                        ? createRemoteStorageMutation.error.message
                        : undefined
                }
                isLoading={createRemoteStorageMutation.isPending}
            />
        </div>
    );
} 