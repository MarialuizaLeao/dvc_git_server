import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useDataManagement } from '../hooks/useDataManagement';
import { useProjects } from '../hooks/useProjects';
import { CURRENT_USER } from '../constants/user';
import { API_ENDPOINTS } from '../constants/api';
import Card from '../components/Card';
import AddDataSourceModal from '../components/AddDataSourceModal';
import RemoteStorageModal from '../components/RemoteStorageModal';
import ParameterManager from '../components/ParameterManager';
import type { CreateDataSourceRequest, CreateRemoteRequest } from '../types/api';

// Code management types
interface CodeFile {
    _id: string;
    filename: string;
    file_path: string;
    file_type: string;
    description?: string;
    size: number;
    status: string;
    created_at: string;
    updated_at: string;
    git_commit_hash?: string;
}

interface CodeFileContent {
    file_id: string;
    file_path: string;
    filename: string;
    content: string;
}

interface CodeUploadResponse {
    file_id: string;
    message: string;
}

interface CodeFilesResponse {
    code_files: CodeFile[];
    total_count: number;
}

export default function DataManagement() {
    const { id: projectId } = useParams<{ id: string }>();
    const [isDataSourceModalOpen, setIsDataSourceModalOpen] = useState(false);
    const [isRemoteStorageModalOpen, setIsRemoteStorageModalOpen] = useState(false);

    // Code management state
    const [codeFiles, setCodeFiles] = useState<CodeFile[]>([]);
    const [isCodeUploadModalOpen, setIsCodeUploadModalOpen] = useState(false);
    const [isCodeViewModalOpen, setIsCodeViewModalOpen] = useState(false);
    const [selectedCodeFile, setSelectedCodeFile] = useState<CodeFile | null>(null);
    const [codeFileContent, setCodeFileContent] = useState('');
    const [isLoadingCodeFiles, setIsLoadingCodeFiles] = useState(false);
    const [isUploadingCode, setIsUploadingCode] = useState(false);

    const { getProject } = useProjects(CURRENT_USER.id);
    const { data: project, isLoading: projectLoading } = getProject(projectId || '');

    const {
        getDataSources,
        createDataSource,
        deleteDataSource,
        getRemoteStorages,
        createRemoteStorage,
        deleteRemoteStorage,
        getDvcStatus
    } = useDataManagement(CURRENT_USER.id, projectId || '');

    const { data: dataSources, isLoading: dataSourcesLoading } = getDataSources();
    const { data: remoteStorages, isLoading: remotesLoading } = getRemoteStorages();
    const { isLoading: dvcStatusLoading } = getDvcStatus();

    const createDataSourceMutation = createDataSource;
    const deleteDataSourceMutation = deleteDataSource;
    const createRemoteStorageMutation = createRemoteStorage;
    const deleteRemoteStorageMutation = deleteRemoteStorage;

    // Code management functions
    const loadCodeFiles = async (): Promise<void> => {
        if (!projectId) return;

        setIsLoadingCodeFiles(true);
        try {
            const response = await fetch(API_ENDPOINTS.CODE_FILES(CURRENT_USER.id, projectId));
            if (response.ok) {
                const data: CodeFilesResponse = await response.json();
                setCodeFiles(data.code_files || []);
            } else {
                console.error('Failed to load code files');
            }
        } catch (error) {
            console.error('Error loading code files:', error);
        } finally {
            setIsLoadingCodeFiles(false);
        }
    };

    const handleUploadCodeFile = async (formData: FormData): Promise<void> => {
        if (!projectId) return;

        setIsUploadingCode(true);
        try {
            const response = await fetch(API_ENDPOINTS.CODE_UPLOAD(CURRENT_USER.id, projectId), {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const result: CodeUploadResponse = await response.json();
                alert(`Arquivo carregado com sucesso! ID do arquivo: ${result.file_id}`);
                loadCodeFiles(); // Reload the code files list
                setIsCodeUploadModalOpen(false);
            } else {
                const error = await response.json();
                alert(`Upload falhou: ${error.detail}`);
            }
        } catch (error) {
            console.error('Error uploading file:', error);
            alert('Upload falhou. Por favor, tente novamente mais tarde.');
        } finally {
            setIsUploadingCode(false);
        }
    };

    const handleViewCodeFile = async (file: CodeFile): Promise<void> => {
        if (!projectId) return;

        try {
            const response = await fetch(API_ENDPOINTS.CODE_FILE_CONTENT(CURRENT_USER.id, projectId, file._id));
            if (response.ok) {
                const data: CodeFileContent = await response.json();
                setCodeFileContent(data.content);
                setSelectedCodeFile(file);
                setIsCodeViewModalOpen(true);
            } else {
                alert('Failed to load file content');
            }
        } catch (error) {
            console.error('Error loading file content:', error);
            alert('Failed to load file content');
        }
    };

    const handleDeleteCodeFile = async (fileId: string): Promise<void> => {
        if (!projectId || !window.confirm('Are you sure you want to delete this code file?')) return;

        try {
            const response = await fetch(API_ENDPOINTS.CODE_FILE_DELETE(CURRENT_USER.id, projectId, fileId), {
                method: 'DELETE'
            });

            if (response.ok) {
                alert('File deleted successfully!');
                loadCodeFiles(); // Reload the code files list
            } else {
                const error = await response.json();
                alert(`Delete failed: ${error.detail}`);
            }
        } catch (error) {
            console.error('Error deleting file:', error);
            alert('Delete failed. Please try again.');
        }
    };

    const handleCreateDataSource = async (data: CreateDataSourceRequest): Promise<void> => {
        try {
            await createDataSourceMutation.mutateAsync(data);
            setIsDataSourceModalOpen(false);
        } catch (error) {
            console.error('Failed to create data source:', error);
        }
    };

    const handleDeleteDataSource = async (sourceId: string): Promise<void> => {
        if (window.confirm('Are you sure you want to delete this data source?')) {
            try {
                await deleteDataSourceMutation.mutateAsync(sourceId);
            } catch (error) {
                console.error('Failed to delete data source:', error);
            }
        }
    };

    const handleCreateRemoteStorage = async (data: CreateRemoteRequest): Promise<void> => {
        try {
            await createRemoteStorageMutation.mutateAsync(data);
            setIsRemoteStorageModalOpen(false);
        } catch (error) {
            console.error('Failed to create remote storage:', error);
        }
    };

    const handleDeleteRemoteStorage = async (remoteId: string): Promise<void> => {
        if (window.confirm('Are you sure you want to delete this remote storage?')) {
            try {
                await deleteRemoteStorageMutation.mutateAsync(remoteId);
            } catch (error) {
                console.error('Failed to delete remote storage:', error);
            }
        }
    };

    const getStatusColor = (status: string): string => {
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

    const formatFileSize = (bytes: number): string => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    const getFileTypeColor = (fileType: string): string => {
        switch (fileType) {
            case 'python':
                return 'bg-blue-100 text-blue-800';
            case 'jupyter':
                return 'bg-orange-100 text-orange-800';
            case 'config':
                return 'bg-purple-100 text-purple-800';
            case 'documentation':
                return 'bg-green-100 text-green-800';
            default:
                return 'bg-gray-100 text-gray-800';
        }
    };

    // Load code files when component mounts
    useEffect(() => {
        if (projectId) {
            loadCodeFiles();
        }
    }, [projectId]);

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
                <h2 className="text-2xl font-semibold text-red-600">Projeto não encontrado</h2>
                <p className="text-gray-700 mt-2">O projeto que você procura não existe.</p>
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto space-y-6">
            {/* Header */}
            <div className="bg-white p-6 rounded-lg border border-gray-200">
                <div className="flex justify-between items-start mb-4">
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900">Gerenciamento de Dados</h1>
                        <p className="text-gray-500 mt-1">Gerencie conjuntos de dados, armazenamento e código para {project.project_name}</p>
                    </div>
                    <div className="flex space-x-3">
                        <button
                            onClick={() => setIsDataSourceModalOpen(true)}
                            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                        >
                            Adicionar Fonte de Dados
                        </button>
                        <button
                            onClick={() => setIsRemoteStorageModalOpen(true)}
                            className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
                        >
                            Configurar Armazenamento
                        </button>
                        <button
                            onClick={() => setIsCodeUploadModalOpen(true)}
                            className="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors"
                        >
                            Enviar Código
                        </button>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Data Sources */}
                <Card title="Fontes de Dados">
                    <div className="space-y-4">
                        {dataSources && dataSources.length > 0 ? (
                            dataSources.map((source) => (
                                <div key={source._id} className="border border-gray-200 rounded-lg p-4">
                                    <div className="flex justify-between items-start">
                                        <div className="flex-1">
                                            <h4 className="font-medium text-gray-900">{source.name}</h4>
                                            <p className="text-sm text-gray-600 mt-1">{source.description}</p>
                                            <div className="mt-2 text-xs text-gray-500">
                                                <div><strong>Tipo:</strong> {source.type}</div>
                                                <div><strong>Origem:</strong> {source.source}</div>
                                                <div><strong>Destino:</strong> {source.destination}</div>
                                                {source.size && (
                                                    <div><strong>Tamanho:</strong> {formatFileSize(source.size)}</div>
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
                                            Excluir
                                        </button>
                                    </div>
                                </div>
                            ))
                        ) : (
                            <div className="text-center py-8 text-gray-500">
                                <p>Nenhuma fonte de dados configurada</p>
                                <button
                                    onClick={() => setIsDataSourceModalOpen(true)}
                                    className="mt-2 text-blue-500 hover:text-blue-700"
                                >
                                    Adicione sua primeira fonte de dados
                                </button>
                            </div>
                        )}
                    </div>
                </Card>

                {/* Remote Storage */}
                <Card title="Armazenamento Remoto">
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
                                                        Padrão
                                                    </span>
                                                )}
                                            </div>
                                            <p className="text-sm text-gray-600 mt-1">{remote.url}</p>
                                            <div className="mt-2 text-xs text-gray-500">
                                                <div><strong>Tipo:</strong> {remote.type.toUpperCase()}</div>
                                            </div>
                                        </div>
                                        <button
                                            onClick={() => handleDeleteRemoteStorage(remote._id)}
                                            className="text-red-500 hover:text-red-700 ml-2"
                                        >
                                            Excluir
                                        </button>
                                    </div>
                                </div>
                            ))
                        ) : (
                            <div className="text-center py-8 text-gray-500">
                                <p>Nenhum armazenamento remoto configurado</p>
                                <button
                                    onClick={() => setIsRemoteStorageModalOpen(true)}
                                    className="mt-2 text-green-500 hover:text-green-700"
                                >
                                    Configurar armazenamento
                                </button>
                            </div>
                        )}
                    </div>
                </Card>
            </div>

            {/* Code Management */}
            <Card title="Gerenciamento de Código">
                <div className="space-y-4">
                    <div className="flex justify-between items-center">
                        <h3 className="text-lg font-medium text-gray-900">Arquivos de Código do Projeto</h3>
                        <div className="flex space-x-2">
                            <button
                                onClick={loadCodeFiles}
                                disabled={isLoadingCodeFiles}
                                className="px-3 py-1 bg-gray-500 text-white rounded hover:bg-gray-600 transition-colors disabled:opacity-50 text-sm"
                            >
                                {isLoadingCodeFiles ? 'Carregando...' : 'Atualizar'}
                            </button>
                            <button
                                onClick={() => setIsCodeUploadModalOpen(true)}
                                className="px-3 py-1 bg-purple-500 text-white rounded hover:bg-purple-600 transition-colors text-sm"
                            >
                                Enviar Código
                            </button>
                        </div>
                    </div>

                    {isLoadingCodeFiles ? (
                        <div className="flex items-center justify-center py-8">
                            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-purple-500"></div>
                            <span className="ml-2 text-gray-600">Carregando arquivos de código...</span>
                        </div>
                    ) : codeFiles.length > 0 ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {codeFiles.map((file) => (
                                <div key={file._id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                                    <div className="flex justify-between items-start mb-2">
                                        <div className="flex-1">
                                            <h4 className="font-medium text-gray-900 truncate">{file.filename}</h4>
                                            <p className="text-sm text-gray-600 mt-1 truncate">{file.file_path}</p>
                                        </div>
                                        <div className="flex space-x-1">
                                            <button
                                                onClick={() => handleViewCodeFile(file)}
                                                className="text-blue-500 hover:text-blue-700 text-sm"
                                            >
                                                Visualizar
                                            </button>
                                            <button
                                                onClick={() => handleDeleteCodeFile(file._id)}
                                                className="text-red-500 hover:text-red-700 text-sm"
                                            >
                                                Excluir
                                            </button>
                                        </div>
                                    </div>

                                    <div className="flex items-center justify-between text-xs text-gray-500">
                                        <span className={`px-2 py-1 rounded-full ${getFileTypeColor(file.file_type)}`}>
                                            {file.file_type}
                                        </span>
                                        <span>{formatFileSize(file.size)}</span>
                                    </div>

                                    <div className="mt-2">
                                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(file.status)}`}>
                                            {file.status}
                                        </span>
                                    </div>

                                    {file.description && (
                                        <p className="text-xs text-gray-600 mt-2 line-clamp-2">{file.description}</p>
                                    )}

                                    {file.git_commit_hash && (
                                        <p className="text-xs text-gray-400 mt-1 truncate">
                                            Commit: {file.git_commit_hash.substring(0, 8)}
                                        </p>
                                    )}
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-8 text-gray-500">
                            <p>Nenhum arquivo de código enviado ainda</p>
                            <button
                                onClick={() => setIsCodeUploadModalOpen(true)}
                                className="mt-2 text-purple-500 hover:text-purple-700"
                            >
                                Envie seu primeiro arquivo de código
                            </button>
                        </div>
                    )}
                </div>
            </Card>

            {/* Parameter Manager */}
            <ParameterManager userId={CURRENT_USER.id} projectId={projectId || ''} />

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

            {/* Code Upload Modal */}
            {isCodeUploadModalOpen && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg p-6 w-full max-w-md">
                        <h3 className="text-lg font-medium mb-4">Enviar Arquivo de Código</h3>
                        <form onSubmit={(e) => {
                            e.preventDefault();
                            const formData = new FormData(e.currentTarget);
                            handleUploadCodeFile(formData);
                        }}>
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium mb-1">Caminho do Arquivo (ex: src/main.py):</label>
                                    <input
                                        name="file_path"
                                        type="text"
                                        required
                                        className="w-full p-2 border rounded"
                                        placeholder="src/main.py"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-1">Tipo de Arquivo:</label>
                                    <select name="file_type" className="w-full p-2 border rounded">
                                        <option value="python">Python</option>
                                        <option value="jupyter">Jupyter Notebook</option>
                                        <option value="config">Configuração</option>
                                        <option value="documentation">Documentação</option>
                                        <option value="other">Outro</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-1">Descrição (opcional):</label>
                                    <input
                                        name="description"
                                        type="text"
                                        className="w-full p-2 border rounded"
                                        placeholder="Breve descrição do arquivo"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-1">Selecionar Arquivo:</label>
                                    <input
                                        name="file"
                                        type="file"
                                        required
                                        className="w-full p-2 border rounded"
                                    />
                                </div>
                            </div>
                            <div className="flex justify-end space-x-3 mt-6">
                                <button
                                    type="button"
                                    onClick={() => setIsCodeUploadModalOpen(false)}
                                    className="px-4 py-2 text-gray-600 hover:text-gray-800"
                                >
                                    Cancelar
                                </button>
                                <button
                                    type="submit"
                                    disabled={isUploadingCode}
                                    className="px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600 disabled:opacity-50"
                                >
                                    {isUploadingCode ? 'Enviando...' : 'Enviar'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Code View Modal */}
            {isCodeViewModalOpen && selectedCodeFile && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[80vh] overflow-hidden">
                        <div className="flex justify-between items-start mb-4">
                            <div>
                                <h3 className="text-lg font-medium">{selectedCodeFile.filename}</h3>
                                <p className="text-sm text-gray-600">{selectedCodeFile.file_path}</p>
                            </div>
                            <button
                                onClick={() => setIsCodeViewModalOpen(false)}
                                className="text-gray-500 hover:text-gray-700"
                            >
                                ✕
                            </button>
                        </div>
                        <div className="bg-gray-50 p-4 rounded border max-h-96 overflow-auto">
                            <pre className="text-sm text-gray-800 whitespace-pre-wrap">{codeFileContent}</pre>
                        </div>
                        <div className="flex justify-end mt-4">
                            <button
                                onClick={() => setIsCodeViewModalOpen(false)}
                                className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
                            >
                                Fechar
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
} 