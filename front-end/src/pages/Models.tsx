import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { CURRENT_USER } from '../constants/user';
import Card from '../components/Card';
import {
    TbDownload,
    TbEye,
    TbTrash,
    TbFile,
    TbCalendar,
    TbBrain,
    TbSettings,
    TbPlayerPlay,
    TbClock,
    TbCheck,
    TbX,
    TbChartLine,
    TbChartBar,
    TbActivity
} from 'react-icons/tb';
import { modelApi } from '../services/api';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import type {
    Model,
    ModelListResponse,
    ModelPathConfig,
    CreateModelPathRequest,
    UpdateModelPathRequest,
    ModelEvaluation,
    CreateEvaluationRequest,
    ProjectModelFile,
    ProjectModelFilesResponse
} from '../types/api';

export default function Models() {
    const { id: projectId } = useParams<{ id: string }>();
    const userId = CURRENT_USER.id;
    const [pathModalOpen, setPathModalOpen] = useState(false);
    const [selectedModel, setSelectedModel] = useState<Model | null>(null);
    const [viewModalOpen, setViewModalOpen] = useState(false);
    const [deleteLoading, setDeleteLoading] = useState<string | null>(null);
    const [evaluating, setEvaluating] = useState<string | null>(null);
    const [selectedEvaluation, setSelectedEvaluation] = useState<ModelEvaluation | null>(null);

    const queryClient = useQueryClient();

    // Fetch models
    const { data: modelsData, isLoading: modelsLoading } = useQuery({
        queryKey: ['models', userId, projectId],
        queryFn: () => modelApi.getModels(userId, projectId!),
        enabled: !!userId && !!projectId
    });

    // Fetch model paths
    const { data: modelPathsData, isLoading: pathsLoading } = useQuery({
        queryKey: ['model-paths', userId, projectId],
        queryFn: () => modelApi.getModelPaths(userId, projectId!),
        enabled: !!userId && !!projectId
    });

    // Fetch evaluations
    const evaluationsQuery = useQuery({
        queryKey: ['evaluations', userId, projectId],
        queryFn: () => modelApi.getModelEvaluations(userId, projectId!),
        enabled: !!userId && !!projectId
    });

    // Mutations
    const createEvaluationMutation = useMutation({
        mutationFn: (data: CreateEvaluationRequest) => modelApi.createModelEvaluation(userId, projectId!, data),
        onSuccess: () => {
            evaluationsQuery.refetch();
        }
    });

    const deleteModelMutation = useMutation({
        mutationFn: (modelId: string) => modelApi.deleteModel(userId, projectId!, modelId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['models', userId, projectId] });
        }
    });

    const models = modelsData?.models || [];
    const modelPaths = modelPathsData?.model_paths || [];
    const evaluations = evaluationsQuery.data?.model_evaluations || [];

    const formatFileSize = (bytes: number): string => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    const formatDate = (dateString: string): string => {
        return new Date(dateString).toLocaleDateString('pt-BR', {
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
            case 'completed':
                return 'bg-green-100 text-green-800';
            case 'running':
                return 'bg-blue-100 text-blue-800';
            case 'failed':
                return 'bg-red-100 text-red-800';
            default:
                return 'bg-gray-100 text-gray-800';
        }
    };

    const handleDeleteModelPath = async (pathId: string) => {
        console.log('Caminhos de modelo do pipeline DVC não podem ser excluídos manualmente');
    };

    const handleCreateEvaluation = async (modelPath: string) => {
        setEvaluating(modelPath);
        try {
            await createEvaluationMutation.mutateAsync({
                model_path: modelPath
            });
            // Refetch evaluations
            evaluationsQuery.refetch();
        } catch (error) {
            console.error('Error creating evaluation:', error);
        } finally {
            setEvaluating(null);
        }
    };

    const handleViewModel = (model: Model) => {
        setSelectedModel(model);
        setViewModalOpen(true);
    };

    const handleDownloadModel = async (model: Model) => {
        try {
            const res = await modelApi.downloadModel(userId, projectId!, model.id!);
            window.open(`/static/${res.file_path}`, '_blank');
        } catch (err: any) {
            alert(err.message || 'Falha ao baixar o modelo');
        }
    };

    const handleDeleteModel = async (model: Model) => {
        if (!window.confirm(`Tem certeza que deseja excluir ${model.name}?`)) return;
        setDeleteLoading(model.id!);
        try {
            await deleteModelMutation.mutateAsync(model.id!);
        } catch (err: any) {
            alert(err.message || 'Falha ao excluir o modelo');
        } finally {
            setDeleteLoading(null);
        }
    };

    const renderMetricValue = (value: any) => {
        if (typeof value === 'number') {
            return value.toFixed(4);
        } else if (typeof value === 'object' && value !== null) {
            return (
                <div className="space-y-1">
                    {Object.entries(value).map(([k, v]) => (
                        <div key={k} className="text-xs">
                            <span className="font-medium">{k}:</span> {typeof v === 'number' ? v.toFixed(4) : String(v)}
                        </div>
                    ))}
                </div>
            );
        }
        return String(value);
    };

    const renderEvaluationPlots = (evaluation: ModelEvaluation) => {
        // This would be populated with actual plot data from the backend
        // For now, showing a placeholder
        return (
            <div className="mt-4">
                <h4 className="text-sm font-medium text-gray-700 mb-3">Gráficos de Avaliação</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-gray-50 p-4 rounded-lg border">
                        <div className="flex items-center space-x-2 mb-2">
                            <TbChartLine className="h-4 w-4 text-blue-600" />
                            <span className="text-sm font-medium">Acurácia ao Longo do Tempo</span>
                        </div>
                        <div className="h-32 bg-white rounded border flex items-center justify-center text-gray-500 text-sm">
                            A visualização do gráfico aparecerá aqui
                        </div>
                    </div>
                    <div className="bg-gray-50 p-4 rounded-lg border">
                        <div className="flex items-center space-x-2 mb-2">
                            <TbChartBar className="h-4 w-4 text-green-600" />
                            <span className="text-sm font-medium">Comparação de Métricas</span>
                        </div>
                        <div className="h-32 bg-white rounded border flex items-center justify-center text-gray-500 text-sm">
                            A visualização do gráfico aparecerá aqui
                        </div>
                    </div>
                </div>
            </div>
        );
    };

    if (modelsLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Modelos</h1>
                    <p className="text-gray-600 mt-1">
                        Gerencie e acompanhe seus modelos de aprendizado de máquina treinados
                    </p>
                </div>
            </div>

            {/* Content */}
            <div className="space-y-6">
                {/* Current Model Results */}
                <Card title="Resultados do Modelo Atual">
                    {pathsLoading ? (
                        <div className="flex items-center justify-center h-32">
                            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
                        </div>
                    ) : modelPaths.length > 0 ? (
                        <div className="space-y-6">
                            {modelPaths.map((path) => {
                                const latestEvaluation = evaluations
                                    .filter(e => e.model_path === path.model_path)
                                    .sort((a, b) => new Date(b.evaluation_date).getTime() - new Date(a.evaluation_date).getTime())[0];

                                return (
                                    <div key={path._id} className="border border-gray-200 rounded-lg p-6">
                                        <div className="flex items-center justify-between mb-4">
                                            <div className="flex-1">
                                                <h3 className="text-xl font-semibold text-gray-900">{path.model_name}</h3>
                                                <p className="text-sm text-gray-600 mt-1">{path.model_path}</p>
                                                {path.description && (
                                                    <p className="text-sm text-gray-500 mt-2">{path.description}</p>
                                                )}
                                            </div>
                                            <div className="flex flex-col items-end space-y-3">
                                                <button
                                                    onClick={() => setSelectedEvaluation(latestEvaluation)}
                                                    className="text-blue-600 hover:text-blue-800 text-sm font-medium self-end"
                                                    style={{ visibility: latestEvaluation ? 'visible' : 'hidden' }}
                                                >
                                                    Ver Detalhes
                                                </button>
                                                {!path.model_name.toLowerCase().includes('train') && !path.model_path.toLowerCase().includes('train') && (
                                                    <button
                                                        onClick={() => handleCreateEvaluation(path.model_path)}
                                                        disabled={evaluating === path.model_path}
                                                        className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 disabled:opacity-50"
                                                    >
                                                        {evaluating === path.model_path ? (
                                                            <>
                                                                <TbClock className="h-4 w-4 mr-2" />
                                                                Executando...
                                                            </>
                                                        ) : (
                                                            <>
                                                                <TbPlayerPlay className="h-4 w-4 mr-2" />
                                                                Avaliar
                                                            </>
                                                        )}
                                                    </button>
                                                )}
                                            </div>
                                        </div>

                                        {latestEvaluation ? (
                                            <div className="space-y-4">
                                                <div className="flex items-center justify-between">
                                                    <div className="flex items-center space-x-3">
                                                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(latestEvaluation.status)}`}>
                                                            {latestEvaluation.status}
                                                        </span>
                                                        <span className="text-sm text-gray-600">
                                                            Última avaliação: {formatDate(latestEvaluation.evaluation_date)}
                                                        </span>
                                                    </div>
                                                </div>

                                                {latestEvaluation.metrics && Object.keys(latestEvaluation.metrics).length > 0 && (
                                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                                        {Object.entries(latestEvaluation.metrics).map(([key, value]) => (
                                                            <div key={key} className="bg-gray-50 p-3 rounded-lg">
                                                                <div className="text-sm text-gray-600 mb-1">{key}</div>
                                                                <div className="text-xl font-semibold text-gray-900">
                                                                    {renderMetricValue(value)}
                                                                </div>
                                                            </div>
                                                        ))}
                                                    </div>
                                                )}

                                                {latestEvaluation.error_message && (
                                                    <div className="bg-red-50 p-3 rounded-lg">
                                                        <h4 className="text-sm font-medium text-red-700 mb-1">Error:</h4>
                                                        <div className="text-sm text-red-600">{latestEvaluation.error_message}</div>
                                                    </div>
                                                )}
                                            </div>
                                        ) : (
                                            <div className="text-center py-8 text-gray-500">
                                                <TbActivity className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                                                <p>No evaluation results yet.</p>
                                                <p className="text-sm mt-1">Run an evaluation to see model performance metrics.</p>
                                            </div>
                                        )}
                                    </div>
                                );
                            })}
                        </div>
                    ) : (
                        <div className="text-center py-8 text-gray-500">
                            <TbBrain className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                            <p>No model paths found in DVC pipeline.</p>
                            <p className="text-sm mt-1">Configure your DVC pipeline to include model outputs.</p>
                        </div>
                    )}
                </Card>
            </div>

            {/* Model Path Modal */}
            {pathModalOpen && (
                <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
                    <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
                        <div className="mt-3">
                            <h3 className="text-lg font-medium text-gray-900 mb-4">
                                DVC Pipeline Configuration
                            </h3>
                            <div className="space-y-4">
                                {modelPathsData?.error ? (
                                    <div className="text-red-600 text-sm">
                                        <p><strong>Error:</strong> {modelPathsData.error}</p>
                                        <p className="mt-2">Make sure your project has a valid dvc.yaml file with model outputs defined in the pipeline stages.</p>
                                    </div>
                                ) : modelPathsData?.evaluation_stage ? (
                                    <div className="space-y-3">
                                        <div>
                                            <h4 className="font-medium text-gray-900">Evaluation Stage</h4>
                                            <p className="text-sm text-gray-600">{modelPathsData.evaluation_stage.name}</p>
                                        </div>
                                        {modelPathsData.metrics_path && (
                                            <div>
                                                <h4 className="font-medium text-gray-900">Metrics Path</h4>
                                                <p className="text-sm text-gray-600">{modelPathsData.metrics_path}</p>
                                            </div>
                                        )}
                                        <div>
                                            <h4 className="font-medium text-gray-900">Available Models</h4>
                                            <div className="space-y-2">
                                                {modelPaths.map((path) => (
                                                    <div key={path._id} className="text-sm text-gray-600 p-2 bg-gray-50 rounded">
                                                        <strong>{path.model_name}</strong><br />
                                                        Path: {path.model_path}
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="text-yellow-600 text-sm">
                                        <p>No evaluation stage found in dvc.yaml.</p>
                                        <p className="mt-2">Add an evaluation stage to your DVC pipeline to enable model evaluation.</p>
                                    </div>
                                )}
                            </div>
                            <div className="mt-6 flex justify-end">
                                <button
                                    onClick={() => setPathModalOpen(false)}
                                    className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
                                >
                                    Close
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Evaluation Details Modal */}
            {selectedEvaluation && (
                <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
                    <div className="relative top-10 mx-auto p-6 border w-4/5 max-w-4xl shadow-lg rounded-md bg-white">
                        <div className="flex justify-between items-center mb-4">
                            <h3 className="text-xl font-semibold text-gray-900">
                                Evaluation Details
                            </h3>
                            <button
                                onClick={() => setSelectedEvaluation(null)}
                                className="text-gray-400 hover:text-gray-600"
                            >
                                <TbX className="h-6 w-6" />
                            </button>
                        </div>

                        <div className="space-y-6">
                            {/* Evaluation Header */}
                            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                                <div className="flex items-center space-x-4">
                                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(selectedEvaluation.status)}`}>
                                        {selectedEvaluation.status}
                                    </span>
                                    <div>
                                        <h4 className="font-medium text-gray-900">{selectedEvaluation.model_path}</h4>
                                        <p className="text-sm text-gray-600">{formatDate(selectedEvaluation.evaluation_date)}</p>
                                    </div>
                                </div>
                            </div>

                            {/* Metrics */}
                            {selectedEvaluation.metrics && Object.keys(selectedEvaluation.metrics).length > 0 && (
                                <div>
                                    <h4 className="text-lg font-medium text-gray-900 mb-3">Metrics</h4>
                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                        {Object.entries(selectedEvaluation.metrics).map(([key, value]) => (
                                            <div key={key} className="bg-gray-50 p-4 rounded-lg">
                                                <div className="text-sm text-gray-600 mb-2">{key}</div>
                                                <div className="text-xl font-semibold text-gray-900">
                                                    {renderMetricValue(value)}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Plots */}
                            {renderEvaluationPlots(selectedEvaluation)}

                            {/* Logs */}
                            {selectedEvaluation.evaluation_logs && selectedEvaluation.evaluation_logs.length > 0 && (
                                <div>
                                    <h4 className="text-lg font-medium text-gray-900 mb-3">Evaluation Logs</h4>
                                    <div className="bg-gray-50 p-4 rounded-lg max-h-64 overflow-y-auto">
                                        <div className="space-y-1 text-sm text-gray-700 font-mono">
                                            {selectedEvaluation.evaluation_logs.map((log, index) => (
                                                <div key={index} className="py-1">{log}</div>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* Error */}
                            {selectedEvaluation.error_message && (
                                <div>
                                    <h4 className="text-lg font-medium text-red-700 mb-3">Error</h4>
                                    <div className="bg-red-50 p-4 rounded-lg">
                                        <div className="text-sm text-red-600">{selectedEvaluation.error_message}</div>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
} 