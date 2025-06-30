import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { usePipelines } from '../hooks/usePipelines';
import { useProjects } from '../hooks/useProjects';
import { CURRENT_USER } from '../constants/user';
import Card from '../components/Card';
import PipelineConfigModal from '../components/PipelineConfigModal';
import ExecutionOutputViewer from '../components/ExecutionOutputViewer';
import { pipelineExecutionApi } from '../services/api';
import { useQuery } from '@tanstack/react-query';
import type { Pipeline, PipelineExecutionRequest, PipelineExecution } from '../types/api';

export default function Pipeline() {
    const { id: projectId } = useParams();
    const [isConfigModalOpen, setIsConfigModalOpen] = useState(false);
    const [isExecuting, setIsExecuting] = useState(false);
    const [activeTab, setActiveTab] = useState<'overview' | 'executions'>('overview');
    const [selectedExecution, setSelectedExecution] = useState<PipelineExecution | null>(null);
    const [isOutputViewerOpen, setIsOutputViewerOpen] = useState(false);

    const { getProject } = useProjects(CURRENT_USER.id);
    const { data: project, isLoading: projectLoading } = getProject(projectId || '');

    const {
        getPipeline,
        createPipeline,
        updatePipeline,
        deletePipeline,
        executePipeline,
        recoverPipeline
    } = usePipelines(CURRENT_USER.id, projectId || '');

    const { data: pipeline, isLoading: pipelineLoading } = getPipeline();

    // Fetch execution history
    const { data: executions, isLoading: executionsLoading, refetch: refetchExecutions } = useQuery({
        queryKey: ['pipeline-executions', CURRENT_USER.id, projectId],
        queryFn: () => pipelineExecutionApi.getExecutions(CURRENT_USER.id, projectId || ''),
        enabled: !!projectId && activeTab === 'executions'
    });

    const createPipelineMutation = createPipeline;
    const updatePipelineMutation = updatePipeline;
    const deletePipelineMutation = deletePipeline;
    const executePipelineMutation = executePipeline;
    const recoverPipelineMutation = recoverPipeline;

    const handleCreatePipeline = async (data: any) => {
        try {
            await createPipelineMutation.mutateAsync(data);
            setIsConfigModalOpen(false);
        } catch (error) {
            console.error('Failed to create pipeline:', error);
        }
    };

    const handleUpdatePipeline = async (data: any) => {
        try {
            await updatePipelineMutation.mutateAsync(data);
            setIsConfigModalOpen(false);
        } catch (error) {
            console.error('Failed to update pipeline:', error);
        }
    };

    const handleDeletePipeline = async () => {
        if (window.confirm('Are you sure you want to delete this pipeline?')) {
            try {
                await deletePipelineMutation.mutateAsync();
            } catch (error) {
                console.error('Failed to delete pipeline:', error);
            }
        }
    };

    const handleExecutePipeline = async () => {
        setIsExecuting(true);
        try {
            const executionData: PipelineExecutionRequest = {
                force: false,
                dry_run: false
            };
            const result = await executePipelineMutation.mutateAsync(executionData);
            alert(`Pipeline execution started! Execution ID: ${result.execution_id}`);
        } catch (error) {
            console.error('Failed to execute pipeline:', error);
            alert('Failed to execute pipeline. Please check the console for details.');
        } finally {
            setIsExecuting(false);
        }
    };

    const handleRecoverPipeline = async () => {
        try {
            await recoverPipelineMutation.mutateAsync();
            alert('Pipeline recovered successfully!');
        } catch (error) {
            console.error('Failed to recover pipeline:', error);
            alert('Failed to recover pipeline. Please check the console for details.');
        }
    };

    const handleViewExecutionOutput = (execution: PipelineExecution) => {
        setSelectedExecution(execution);
        setIsOutputViewerOpen(true);
    };

    const handleCloseOutputViewer = () => {
        setIsOutputViewerOpen(false);
        setSelectedExecution(null);
    };

    const getStatusColor = (isActive: boolean) => {
        return isActive
            ? 'bg-green-100 text-green-800 border-green-200'
            : 'bg-gray-100 text-gray-800 border-gray-200';
    };

    const getStageIcon = (stageName: string) => {
        const name = stageName.toLowerCase();
        if (name.includes('data') || name.includes('load')) return '📥';
        if (name.includes('prep') || name.includes('process') || name.includes('transform')) return '🔄';
        if (name.includes('train') || name.includes('model')) return '⚙️';
        if (name.includes('eval') || name.includes('test')) return '📊';
        if (name.includes('feature')) return '🔧';
        return '📋';
    };

    const getExecutionStatusColor = (status: string) => {
        switch (status) {
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

    const formatDuration = (seconds?: number) => {
        if (!seconds) return 'N/A';
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}m ${remainingSeconds}s`;
    };

    if (projectLoading || pipelineLoading) {
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
            {/* Pipeline Header */}
            <div className="bg-white p-6 rounded-lg border border-gray-200">
                <div className="flex justify-between items-start mb-4">
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900">Gerenciamento de Pipeline</h1>
                        <p className="text-gray-500 mt-1">Gerencie o pipeline para {project.project_name}</p>
                    </div>
                    <div className="flex space-x-3">
                        {pipeline ? (
                            <>
                                <button
                                    onClick={handleExecutePipeline}
                                    disabled={isExecuting}
                                    className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors disabled:opacity-50"
                                >
                                    {isExecuting ? 'Executando...' : 'Executar Pipeline'}
                                </button>
                                <button
                                    onClick={() => setIsConfigModalOpen(true)}
                                    className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                                >
                                    Editar Pipeline
                                </button>
                            </>
                        ) : (
                            <button
                                onClick={() => setIsConfigModalOpen(true)}
                                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                            >
                                Criar Pipeline
                            </button>
                        )}
                    </div>
                </div>

                {/* Tabs */}
                {pipeline && (
                    <div className="border-b border-gray-200">
                        <nav className="-mb-px flex space-x-8">
                            <button
                                onClick={() => setActiveTab('overview')}
                                className={`py-2 px-1 border-b-2 font-medium text-sm ${activeTab === 'overview'
                                    ? 'border-blue-500 text-blue-600'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                    }`}
                            >
                                Visão Geral
                            </button>
                            <button
                                onClick={() => setActiveTab('executions')}
                                className={`py-2 px-1 border-b-2 font-medium text-sm ${activeTab === 'executions'
                                    ? 'border-blue-500 text-blue-600'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                    }`}
                            >
                                Histórico de Execuções
                            </button>
                        </nav>
                    </div>
                )}
            </div>

            {/* Pipeline Content */}
            {pipeline ? (
                <div className="space-y-6">
                    {activeTab === 'overview' && (
                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                            {/* Pipeline Overview */}
                            <div className="lg:col-span-2">
                                <Card title={pipeline.name}>
                                    <div className="space-y-4">
                                        <div>
                                            <p className="text-gray-600">{pipeline.description || 'Sem descrição'}</p>
                                            <div className="flex items-center mt-2">
                                                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(pipeline.is_active)}`}>
                                                    {pipeline.is_active ? 'Ativo' : 'Inativo'}
                                                </span>
                                                <span className="ml-2 text-sm text-gray-500">
                                                    {pipeline.stages.length} estágios
                                                </span>
                                            </div>
                                        </div>

                                        {/* Last Execution Status */}
                                        {pipeline.last_execution && (
                                            <div className="border-t pt-4">
                                                <h4 className="text-sm font-medium text-gray-700 mb-2">Última Execução</h4>
                                                <div className="bg-gray-50 p-3 rounded-lg">
                                                    <div className="flex items-center justify-between">
                                                        <div>
                                                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getExecutionStatusColor(pipeline.last_execution.status)}`}>
                                                                {pipeline.last_execution.status}
                                                            </span>
                                                            <span className="ml-2 text-sm text-gray-500">
                                                                ID: {pipeline.last_execution.execution_id}
                                                            </span>
                                                        </div>
                                                        <span className="text-xs text-gray-500">
                                                            {new Date(pipeline.last_execution.start_time).toLocaleString()}
                                                        </span>
                                                    </div>
                                                    {pipeline.last_execution.error && (
                                                        <div className="mt-2 text-sm text-red-600">
                                                            Erro: {pipeline.last_execution.error}
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        )}

                                        {/* Pipeline Stages */}
                                        <div>
                                            <h4 className="text-sm font-medium text-gray-700 mb-3">Estágios do Pipeline</h4>
                                            <div className="space-y-3">
                                                {pipeline.stages.map((stage, index) => (
                                                    <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                                                        <span className="text-lg mt-1">{getStageIcon(stage.name)}</span>
                                                        <div className="flex-1">
                                                            <div className="flex items-center justify-between">
                                                                <h5 className="font-medium text-gray-900">{stage.name}</h5>
                                                                <span className="text-xs text-gray-500">Estágio {index + 1}</span>
                                                            </div>
                                                            {stage.description && (
                                                                <p className="text-sm text-gray-600 mt-1">{stage.description}</p>
                                                            )}
                                                            <div className="mt-2 text-xs text-gray-500">
                                                                <div><strong>Comando:</strong> {stage.command}</div>
                                                                {stage.deps.length > 0 && (
                                                                    <div><strong>Dependências:</strong> {stage.deps.join(', ')}</div>
                                                                )}
                                                                {stage.outs.length > 0 && (
                                                                    <div><strong>Saídas:</strong> {stage.outs.join(', ')}</div>
                                                                )}
                                                            </div>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>

                                        {/* Actions */}
                                        <div className="flex flex-wrap gap-2 pt-4 border-t">
                                            <button
                                                onClick={handleExecutePipeline}
                                                disabled={isExecuting}
                                                className="px-3 py-1 bg-green-500 text-white text-sm rounded hover:bg-green-600 transition-colors disabled:opacity-50"
                                            >
                                                {isExecuting ? 'Executando...' : 'Executar'}
                                            </button>
                                            <button
                                                onClick={handleRecoverPipeline}
                                                className="px-3 py-1 bg-purple-500 text-white text-sm rounded hover:bg-purple-600 transition-colors"
                                            >
                                                Recuperar
                                            </button>
                                            <button
                                                onClick={() => setIsConfigModalOpen(true)}
                                                className="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600 transition-colors"
                                            >
                                                Editar
                                            </button>
                                            <button
                                                onClick={handleDeletePipeline}
                                                className="px-3 py-1 bg-red-500 text-white text-sm rounded hover:bg-red-600 transition-colors"
                                            >
                                                Excluir
                                            </button>
                                        </div>

                                        {pipeline.created_at && (
                                            <div className="text-xs text-gray-500 pt-2 border-t">
                                                Criado: {new Date(pipeline.created_at).toLocaleDateString()}
                                            </div>
                                        )}
                                    </div>
                                </Card>
                            </div>

                            {/* Pipeline Info */}
                            <div className="lg:col-span-1">
                                <Card title="Informações do Pipeline">
                                    <div className="space-y-4">
                                        <div>
                                            <h4 className="text-sm font-medium text-gray-700">Versão</h4>
                                            <p className="text-sm text-gray-900">{pipeline.version}</p>
                                        </div>
                                        <div>
                                            <h4 className="text-sm font-medium text-gray-700">Status</h4>
                                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(pipeline.is_active)}`}>
                                                {pipeline.is_active ? 'Ativo' : 'Inativo'}
                                            </span>
                                        </div>
                                        <div>
                                            <h4 className="text-sm font-medium text-gray-700">Estágios</h4>
                                            <p className="text-sm text-gray-900">{pipeline.stages.length} estágios configurados</p>
                                        </div>
                                        {pipeline.updated_at && (
                                            <div>
                                                <h4 className="text-sm font-medium text-gray-700">Última Atualização</h4>
                                                <p className="text-sm text-gray-900">{new Date(pipeline.updated_at).toLocaleDateString()}</p>
                                            </div>
                                        )}
                                    </div>
                                </Card>
                            </div>
                        </div>
                    )}

                    {activeTab === 'executions' && (
                        <Card title="Histórico de Execução do Pipeline">
                            <div className="flex justify-between items-center mb-4">
                                <div></div>
                                <button
                                    onClick={() => refetchExecutions()}
                                    className="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600 transition-colors"
                                >
                                    Atualizar
                                </button>
                            </div>
                            {executionsLoading ? (
                                <div className="flex items-center justify-center h-32">
                                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
                                </div>
                            ) : executions && executions.executions.length > 0 ? (
                                <div className="space-y-4">
                                    {executions.executions.map((execution: PipelineExecution) => (
                                        <div key={execution.execution_id} className="border border-gray-200 rounded-lg p-4">
                                            <div className="flex items-center justify-between mb-3">
                                                <div className="flex items-center space-x-3">
                                                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getExecutionStatusColor(execution.status)}`}>
                                                        {execution.status}
                                                    </span>
                                                    <span className="text-sm font-medium text-gray-900">
                                                        Execução {execution.execution_id}
                                                    </span>
                                                </div>
                                                <div className="text-sm text-gray-500">
                                                    {new Date(execution.start_time).toLocaleString()}
                                                </div>
                                            </div>

                                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                                                <div>
                                                    <span className="text-gray-500">Duração:</span>
                                                    <div className="font-medium">{formatDuration(execution.duration)}</div>
                                                </div>
                                                <div>
                                                    <span className="text-gray-500">Modelos Produzidos:</span>
                                                    <div className="font-medium">
                                                        {execution.execution_output?.pipeline_stats?.models_produced.length || execution.models_produced.length}
                                                    </div>
                                                </div>
                                                <div>
                                                    <span className="text-gray-500">Arquivos de Saída:</span>
                                                    <div className="font-medium">
                                                        {execution.execution_output?.pipeline_stats?.output_files.length || execution.output_files.length}
                                                    </div>
                                                </div>
                                                <div>
                                                    <span className="text-gray-500">Parâmetros:</span>
                                                    <div className="font-medium">
                                                        {Object.keys(execution.execution_output?.pipeline_stats?.parameters_used || execution.parameters_used).length}
                                                    </div>
                                                </div>
                                            </div>



                                            {execution.models_produced.length > 0 && (
                                                <div className="mt-3">
                                                    <span className="text-sm font-medium text-gray-700">Modelos Produzidos:</span>
                                                    <div className="mt-1 space-y-1">
                                                        {execution.models_produced.map((modelPath, index) => (
                                                            <div key={index} className="text-sm text-gray-600 bg-gray-50 p-2 rounded">
                                                                {modelPath.split('/').pop()}
                                                            </div>
                                                        ))}
                                                    </div>
                                                </div>
                                            )}

                                            {execution.error_message && (
                                                <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded">
                                                    <span className="text-sm font-medium text-red-700">Erro:</span>
                                                    <div className="text-sm text-red-600 mt-1">{execution.error_message}</div>
                                                </div>
                                            )}

                                            <div className="mt-3 flex justify-end">
                                                <button
                                                    onClick={() => handleViewExecutionOutput(execution)}
                                                    className="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600 transition-colors"
                                                >
                                                    Ver Saída
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="text-center py-8 text-gray-500">
                                    Nenhuma execução de pipeline encontrada.
                                </div>
                            )}
                        </Card>
                    )}
                </div>
            ) : (
                <div className="text-center py-12 bg-gray-50 rounded-lg border border-gray-200">
                    <h3 className="text-lg font-semibold text-gray-700 mb-2">Nenhum Pipeline Configurado</h3>
                    <p className="text-gray-500 mb-4">Crie um pipeline para automatizar seu fluxo de processamento de dados!</p>
                    <button
                        onClick={() => setIsConfigModalOpen(true)}
                        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
                    >
                        Criar Pipeline
                    </button>
                </div>
            )}

            {/* Pipeline Configuration Modal */}
            <PipelineConfigModal
                isOpen={isConfigModalOpen}
                onClose={() => setIsConfigModalOpen(false)}
                onSubmit={pipeline ? handleUpdatePipeline : handleCreatePipeline}
                pipeline={pipeline}
                error={
                    createPipelineMutation.error instanceof Error
                        ? createPipelineMutation.error.message
                        : updatePipelineMutation.error instanceof Error
                            ? updatePipelineMutation.error.message
                            : undefined
                }
                isLoading={createPipelineMutation.isPending || updatePipelineMutation.isPending}
            />

            {/* Execution Output Viewer */}
            {selectedExecution && (
                <ExecutionOutputViewer
                    execution={selectedExecution}
                    isOpen={isOutputViewerOpen}
                    onClose={handleCloseOutputViewer}
                />
            )}
        </div>
    );
} 