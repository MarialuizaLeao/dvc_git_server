import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { CURRENT_USER } from '../constants/user';
import Card from '../components/Card';
import {
    TbBrain,
    TbPlayerPlay,
    TbClock,
    TbX,
    TbChartLine,
    TbChartBar,
    TbActivity,
    TbTimeline,
    TbExternalLink
} from 'react-icons/tb';
import { modelApi, pipelineExecutionApi } from '../services/api';
import { useQuery, useMutation } from '@tanstack/react-query';
import type {
    ModelEvaluation,
    CreateEvaluationRequest,
    PipelineExecution
} from '../types/api';

export default function Models() {
    const { id: projectId } = useParams<{ id: string }>();
    const userId = CURRENT_USER.id;
    const [selectedEvaluation, setSelectedEvaluation] = useState<ModelEvaluation | null>(null);
    const [evaluating, setEvaluating] = useState<string | null>(null);
    const [dvcMetrics, setDvcMetrics] = useState<Record<string, any> | null>(null);

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

    // Fetch pipeline executions to get models produced
    const { data: pipelineExecutions, isLoading: executionsLoading } = useQuery({
        queryKey: ['pipeline-executions', userId, projectId],
        queryFn: () => pipelineExecutionApi.getExecutions(userId, projectId!),
        enabled: !!userId && !!projectId
    });

    // Fetch DVC metrics for pipeline executions and eval directory
    const { data: dvcMetricsData } = useQuery({
        queryKey: ['dvc-metrics', userId, projectId],
        queryFn: async () => {
            if (!userId || !projectId) return null;
            try {
                // Try to get metrics from eval directory first
                const evalResponse = await fetch(`/api/${userId}/${projectId}/metrics_show?output_json=true&targets=eval`);
                if (evalResponse.ok) {
                    const evalMetricsData = await evalResponse.json();
                    console.log('Fetched DVC metrics from eval directory:', evalMetricsData);
                    return evalMetricsData;
                }

                // Fallback to general metrics if eval directory doesn't work
                const response = await fetch(`/api/${userId}/${projectId}/metrics_show?output_json=true`);
                if (response.ok) {
                    const metricsData = await response.json();
                    console.log('Fetched general DVC metrics:', metricsData);
                    return metricsData;
                }
            } catch (error) {
                console.error('Error fetching pipeline metrics:', error);
            }
            return null;
        },
        enabled: !!userId && !!projectId // Always enabled to get eval directory metrics
    });

    // Mutations
    const createEvaluationMutation = useMutation({
        mutationFn: (data: CreateEvaluationRequest) => modelApi.createModelEvaluation(userId, projectId!, data),
        onSuccess: () => {
            evaluationsQuery.refetch();
        }
    });

    const modelPaths = modelPathsData?.model_paths || [];
    const evaluations = evaluationsQuery.data?.model_evaluations || [];
    const executions = pipelineExecutions?.executions || [];

    // Helper function to get evaluation results for a model
    const getModelEvaluationResults = (modelPath: string, execution?: PipelineExecution) => {
        console.log(`Getting evaluation results for model: ${modelPath}`);
        console.log('Execution data:', execution);

        // Special handling for root model.pkl - always try to get metrics from eval directory
        if (modelPath === 'model.pkl') {
            console.log('Processing root model.pkl - checking eval directory metrics');

            // First try to find manual evaluation for this specific model
            const manualEvaluation = evaluations
                .filter(e => e.model_path === modelPath)
                .sort((a, b) => new Date(b.evaluation_date).getTime() - new Date(a.evaluation_date).getTime())[0];

            if (manualEvaluation) {
                console.log('Found manual evaluation for root model:', manualEvaluation);
                return {
                    type: 'manual',
                    evaluation: manualEvaluation,
                    metrics: manualEvaluation.metrics,
                    status: manualEvaluation.status,
                    date: manualEvaluation.evaluation_date,
                    logs: manualEvaluation.evaluation_logs,
                    error: manualEvaluation.error_message
                };
            }

            // If no manual evaluation, try to use DVC metrics (which should include eval directory)
            if (dvcMetricsData) {
                console.log('Using DVC metrics for root model:', dvcMetricsData);
                return {
                    type: 'pipeline',
                    evaluation: null,
                    metrics: dvcMetricsData,
                    status: 'completed',
                    date: new Date().toISOString(),
                    logs: [],
                    error: null
                };
            }

            // If no DVC metrics, create a placeholder with eval directory reference
            console.log('No metrics found for root model - creating placeholder');
            return {
                type: 'manual',
                evaluation: null,
                metrics: {},
                status: 'completed',
                date: new Date().toISOString(),
                logs: ['Looking for metrics in eval directory'],
                error: null
            };
        }

        // Regular handling for other models
        // First try to find manual evaluation
        const manualEvaluation = evaluations
            .filter(e => e.model_path === modelPath)
            .sort((a, b) => new Date(b.evaluation_date).getTime() - new Date(a.evaluation_date).getTime())[0];

        if (manualEvaluation) {
            console.log('Found manual evaluation:', manualEvaluation);
            return {
                type: 'manual',
                evaluation: manualEvaluation,
                metrics: manualEvaluation.metrics,
                status: manualEvaluation.status,
                date: manualEvaluation.evaluation_date,
                logs: manualEvaluation.evaluation_logs,
                error: manualEvaluation.error_message
            };
        }

        // If no manual evaluation and we have pipeline execution, check for pipeline evaluation results
        if (execution) {
            console.log('Checking pipeline execution for evaluation results');
            console.log('Execution metrics:', execution.metrics);
            console.log('Execution output:', execution.execution_output);

            // Check if execution has metrics (from pipeline evaluation stage)
            if (execution.metrics && Object.keys(execution.metrics).length > 0) {
                console.log('Found pipeline metrics:', execution.metrics);
                return {
                    type: 'pipeline',
                    evaluation: null,
                    metrics: execution.metrics,
                    status: execution.status,
                    date: execution.start_time,
                    logs: execution.logs || [],
                    error: execution.error_message
                };
            }

            // If execution completed but no metrics in execution, try to use DVC metrics
            if (execution.status === 'completed' && dvcMetricsData) {
                console.log('Using DVC metrics for pipeline execution:', dvcMetricsData);
                return {
                    type: 'pipeline',
                    evaluation: null,
                    metrics: dvcMetricsData,
                    status: execution.status,
                    date: execution.start_time,
                    logs: execution.logs || [],
                    error: execution.error_message
                };
            }

            // If execution completed but no metrics, still show the execution status
            if (execution.status === 'completed') {
                console.log('Pipeline execution completed but no metrics found');
                return {
                    type: 'pipeline',
                    evaluation: null,
                    metrics: {},
                    status: execution.status,
                    date: execution.start_time,
                    logs: execution.logs || [],
                    error: execution.error_message
                };
            }
        }

        console.log('No evaluation results found');
        return null;
    };

    // Get all latest models (from both pipeline executions and manual configurations)
    const getAllLatestModels = () => {
        const allModels: Array<{
            modelPath: string;
            modelName: string;
            source: 'pipeline' | 'manual';
            execution?: PipelineExecution;
            evaluation?: ModelEvaluation;
            evaluationResults: any;
            executionId?: string;
            status: string;
            startTime: string;
            endTime?: string;
        }> = [];

        // Always include the model.pkl from root
        const rootModelPath = 'model.pkl';
        const rootModelEvaluationResults = getModelEvaluationResults(rootModelPath);
        allModels.push({
            modelPath: rootModelPath,
            modelName: 'model.pkl',
            source: 'manual',
            evaluationResults: rootModelEvaluationResults,
            status: rootModelEvaluationResults?.status || 'unknown',
            startTime: rootModelEvaluationResults?.date || new Date().toISOString(),
            endTime: rootModelEvaluationResults?.date || new Date().toISOString()
        });

        // Add models from pipeline executions (only latest execution)
        if (executions.length > 0) {
            const latestExecution = executions[0]; // Assuming executions are sorted by date descending
            if (latestExecution.models_produced && latestExecution.models_produced.length > 0) {
                latestExecution.models_produced.forEach(modelPath => {
                    // Skip if it's the root model.pkl (already added)
                    if (modelPath === rootModelPath) return;

                    const evaluationResults = getModelEvaluationResults(modelPath, latestExecution);
                    allModels.push({
                        modelPath,
                        modelName: modelPath.split('/').pop() || modelPath,
                        source: 'pipeline',
                        execution: latestExecution,
                        evaluationResults,
                        executionId: latestExecution.execution_id,
                        status: latestExecution.status,
                        startTime: latestExecution.start_time,
                        endTime: latestExecution.end_time
                    });
                });
            }
        }

        // Add models from manual evaluations
        evaluations.forEach(evaluation => {
            // Skip if it's the root model.pkl (already added)
            if (evaluation.model_path === rootModelPath) return;

            // Only add if not already added from pipeline
            const existingModel = allModels.find(m => m.modelPath === evaluation.model_path);
            if (!existingModel) {
                const evaluationResults = getModelEvaluationResults(evaluation.model_path);
                allModels.push({
                    modelPath: evaluation.model_path,
                    modelName: evaluation.model_path.split('/').pop() || evaluation.model_path,
                    source: 'manual',
                    evaluation,
                    evaluationResults,
                    status: evaluation.status,
                    startTime: evaluation.evaluation_date,
                    endTime: evaluation.evaluation_date
                });
            }
        });

        // Sort by start time (most recent first), but keep root model.pkl at the top
        return allModels.sort((a, b) => {
            // Always put root model.pkl first
            if (a.modelPath === rootModelPath) return -1;
            if (b.modelPath === rootModelPath) return 1;
            // Then sort by date
            return new Date(b.startTime).getTime() - new Date(a.startTime).getTime();
        });
    };

    const allLatestModels = getAllLatestModels();

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

    const renderEvaluationPlots = () => {
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

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Modelos</h1>
                    <p className="text-gray-600 mt-1">
                        Gerencie e acompanhe os modelos atuais de aprendizado de máquina
                    </p>
                </div>
            </div>

            {/* Content */}
            <div className="space-y-6">
                {/* Latest Models */}
                <Card title="Modelos Mais Recentes">
                    {pathsLoading || executionsLoading ? (
                        <div className="flex items-center justify-center h-32">
                            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
                        </div>
                    ) : allLatestModels.length > 0 ? (
                        <div className="space-y-6">
                            {allLatestModels.map((modelInfo, index) => {
                                return (
                                    <div key={`${modelInfo.source}-${modelInfo.modelPath}-${index}`} className="border border-gray-200 rounded-lg p-6">
                                        <div className="flex items-center justify-between mb-4">
                                            <div className="flex-1">
                                                <div className="flex items-center space-x-2 mb-2">

                                                    <h3 className="text-xl font-semibold text-gray-900">
                                                        {modelInfo.modelName}
                                                    </h3>
                                                </div>
                                                <p className="text-sm text-gray-600">{modelInfo.modelPath}</p>
                                                <div className="flex items-center space-x-4 mt-2">
                                                    <span className="text-xs text-gray-500">
                                                        Última atualização: {formatDate(modelInfo.startTime)}
                                                    </span>
                                                </div>
                                            </div>
                                            <div className="flex flex-col items-end space-y-3">
                                                <button
                                                    onClick={() => setSelectedEvaluation(modelInfo.evaluation || null)}
                                                    className="text-blue-600 hover:text-blue-800 text-sm font-medium self-end"
                                                    style={{ visibility: modelInfo.evaluation ? 'visible' : 'hidden' }}
                                                >
                                                    Ver Detalhes
                                                </button>
                                                {modelInfo.source === 'manual' && modelInfo.modelPath !== 'model.pkl' && !modelInfo.modelName.toLowerCase().includes('train') && !modelInfo.modelPath.toLowerCase().includes('train') && (
                                                    <button
                                                        onClick={() => handleCreateEvaluation(modelInfo.modelPath)}
                                                        disabled={evaluating === modelInfo.modelPath}
                                                        className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 disabled:opacity-50"
                                                    >
                                                        {evaluating === modelInfo.modelPath ? (
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

                                        {modelInfo.evaluationResults && (
                                            <div className="space-y-4">
                                                <div className="flex items-center justify-between">
                                                    <div className="flex items-center space-x-3">
                                                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(modelInfo.evaluationResults.status)}`}>
                                                            {modelInfo.evaluationResults.status}
                                                        </span>
                                                        <span className="text-sm text-gray-600">
                                                            Última avaliação: {formatDate(modelInfo.evaluationResults.date)}
                                                        </span>
                                                        {modelInfo.modelPath === 'model.pkl' && (
                                                            <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs font-medium rounded-full">
                                                                Root Model
                                                            </span>
                                                        )}
                                                    </div>
                                                </div>

                                                {modelInfo.evaluationResults.metrics && Object.keys(modelInfo.evaluationResults.metrics).length > 0 && (
                                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                                        {Object.entries(modelInfo.evaluationResults.metrics).map(([key, value]) => (
                                                            <div key={key} className="bg-gray-50 p-3 rounded-lg">
                                                                <div className="text-sm text-gray-600 mb-1">{key}</div>
                                                                <div className="text-xl font-semibold text-gray-900">
                                                                    {renderMetricValue(value)}
                                                                </div>
                                                            </div>
                                                        ))}
                                                    </div>
                                                )}

                                                {modelInfo.evaluationResults.error && (
                                                    <div className="bg-red-50 p-3 rounded-lg">
                                                        <h4 className="text-sm font-medium text-red-700 mb-1">Error:</h4>
                                                        <div className="text-sm text-red-600">{modelInfo.evaluationResults.error}</div>
                                                    </div>
                                                )}

                                                {modelInfo.modelPath === 'model.pkl' && modelInfo.evaluationResults.logs && modelInfo.evaluationResults.logs.includes('Looking for metrics in eval directory') && (
                                                    <div className="bg-blue-50 p-3 rounded-lg">
                                                        <h4 className="text-sm font-medium text-blue-700 mb-1">Info:</h4>
                                                        <div className="text-sm text-blue-600">
                                                            This model is configured to show metrics from the 'eval' directory.
                                                            Make sure your evaluation metrics are properly tracked in DVC.
                                                        </div>
                                                    </div>
                                                )}
                                            </div>
                                        )}
                                        {!modelInfo.evaluationResults && (
                                            <div className="text-center py-8 text-gray-500">
                                                <TbActivity className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                                                <p>No evaluation results yet.</p>
                                                <p className="text-sm mt-1">
                                                    {modelInfo.modelPath === 'model.pkl'
                                                        ? 'This root model should show metrics from the eval directory.'
                                                        : modelInfo.source === 'pipeline'
                                                            ? 'Evaluation results will appear here after pipeline execution completes.'
                                                            : 'Run an evaluation to see model performance metrics.'
                                                    }
                                                </p>
                                            </div>
                                        )}
                                    </div>
                                );
                            })}
                        </div>
                    ) : (
                        <div className="text-center py-8 text-gray-500">
                            <TbBrain className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                            <p>No models found.</p>
                            <p className="text-sm mt-1">Execute your pipeline or configure models to see results.</p>
                        </div>
                    )}
                </Card>
            </div>

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
                            {renderEvaluationPlots()}

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