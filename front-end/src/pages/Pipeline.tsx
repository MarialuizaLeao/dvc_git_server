import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { usePipelines } from '../hooks/usePipelines';
import { useProjects } from '../hooks/useProjects';
import { CURRENT_USER } from '../constants/user';
import Card from '../components/Card';
import PipelineConfigModal from '../components/PipelineConfigModal';
import type { Pipeline, PipelineExecutionRequest } from '../types/api';

export default function Pipeline() {
    const { id: projectId } = useParams();
    const [isConfigModalOpen, setIsConfigModalOpen] = useState(false);
    const [isExecuting, setIsExecuting] = useState(false);

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
        if (window.confirm('Are you sure you want to recover this pipeline?')) {
            try {
                const result = await recoverPipelineMutation.mutateAsync();
                alert(`Pipeline recovered successfully! ${result.stages_applied} stages applied.`);
            } catch (error) {
                console.error('Failed to recover pipeline:', error);
                alert('Failed to recover pipeline. Please check the console for details.');
            }
        }
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
                <h2 className="text-2xl font-semibold text-red-600">Project Not Found</h2>
                <p className="text-gray-700 mt-2">The project you're looking for doesn't exist.</p>
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto space-y-6">
            {/* Pipeline Header */}
            <div className="bg-white p-6 rounded-lg border border-gray-200">
                <div className="flex justify-between items-start mb-4">
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900">Pipeline Management</h1>
                        <p className="text-gray-500 mt-1">Manage pipeline for {project.project_name}</p>
                    </div>
                    <div className="flex space-x-3">
                        {pipeline ? (
                            <>
                                <button
                                    onClick={handleExecutePipeline}
                                    disabled={isExecuting}
                                    className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors disabled:opacity-50"
                                >
                                    {isExecuting ? 'Executing...' : 'Execute Pipeline'}
                                </button>
                                <button
                                    onClick={() => setIsConfigModalOpen(true)}
                                    className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                                >
                                    Edit Pipeline
                                </button>
                            </>
                        ) : (
                            <button
                                onClick={() => setIsConfigModalOpen(true)}
                                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                            >
                                Create Pipeline
                            </button>
                        )}
                    </div>
                </div>
            </div>

            {/* Pipeline Content */}
            {pipeline ? (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Pipeline Overview */}
                    <div className="lg:col-span-2">
                        <Card title={pipeline.name}>
                            <div className="space-y-4">
                                <div>
                                    <p className="text-gray-600">{pipeline.description || 'No description'}</p>
                                    <div className="flex items-center mt-2">
                                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(pipeline.is_active)}`}>
                                            {pipeline.is_active ? 'Active' : 'Inactive'}
                                        </span>
                                        <span className="ml-2 text-sm text-gray-500">
                                            {pipeline.stages.length} stages
                                        </span>
                                    </div>
                                </div>

                                {/* Last Execution Status */}
                                {pipeline.last_execution && (
                                    <div className="border-t pt-4">
                                        <h4 className="text-sm font-medium text-gray-700 mb-2">Last Execution</h4>
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
                                                    Error: {pipeline.last_execution.error}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                )}

                                {/* Pipeline Stages */}
                                <div>
                                    <h4 className="text-sm font-medium text-gray-700 mb-3">Pipeline Stages</h4>
                                    <div className="space-y-3">
                                        {pipeline.stages.map((stage, index) => (
                                            <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                                                <span className="text-lg mt-1">{getStageIcon(stage.name)}</span>
                                                <div className="flex-1">
                                                    <div className="flex items-center justify-between">
                                                        <h5 className="font-medium text-gray-900">{stage.name}</h5>
                                                        <span className="text-xs text-gray-500">Stage {index + 1}</span>
                                                    </div>
                                                    {stage.description && (
                                                        <p className="text-sm text-gray-600 mt-1">{stage.description}</p>
                                                    )}
                                                    <div className="mt-2 text-xs text-gray-500">
                                                        <div><strong>Command:</strong> {stage.command}</div>
                                                        {stage.deps.length > 0 && (
                                                            <div><strong>Dependencies:</strong> {stage.deps.join(', ')}</div>
                                                        )}
                                                        {stage.outs.length > 0 && (
                                                            <div><strong>Outputs:</strong> {stage.outs.join(', ')}</div>
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
                                        {isExecuting ? 'Executing...' : 'Execute'}
                                    </button>
                                    <button
                                        onClick={handleRecoverPipeline}
                                        className="px-3 py-1 bg-purple-500 text-white text-sm rounded hover:bg-purple-600 transition-colors"
                                    >
                                        Recover
                                    </button>
                                    <button
                                        onClick={() => setIsConfigModalOpen(true)}
                                        className="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600 transition-colors"
                                    >
                                        Edit
                                    </button>
                                    <button
                                        onClick={handleDeletePipeline}
                                        className="px-3 py-1 bg-red-500 text-white text-sm rounded hover:bg-red-600 transition-colors"
                                    >
                                        Delete
                                    </button>
                                </div>

                                {pipeline.created_at && (
                                    <div className="text-xs text-gray-500 pt-2 border-t">
                                        Created: {new Date(pipeline.created_at).toLocaleDateString()}
                                    </div>
                                )}
                            </div>
                        </Card>
                    </div>

                    {/* Pipeline Info */}
                    <div className="lg:col-span-1">
                        <Card title="Pipeline Information">
                            <div className="space-y-4">
                                <div>
                                    <h4 className="text-sm font-medium text-gray-700">Version</h4>
                                    <p className="text-sm text-gray-900">{pipeline.version}</p>
                                </div>
                                <div>
                                    <h4 className="text-sm font-medium text-gray-700">Status</h4>
                                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(pipeline.is_active)}`}>
                                        {pipeline.is_active ? 'Active' : 'Inactive'}
                                    </span>
                                </div>
                                <div>
                                    <h4 className="text-sm font-medium text-gray-700">Stages</h4>
                                    <p className="text-sm text-gray-900">{pipeline.stages.length} stages configured</p>
                                </div>
                                {pipeline.updated_at && (
                                    <div>
                                        <h4 className="text-sm font-medium text-gray-700">Last Updated</h4>
                                        <p className="text-sm text-gray-900">{new Date(pipeline.updated_at).toLocaleDateString()}</p>
                                    </div>
                                )}
                            </div>
                        </Card>
                    </div>
                </div>
            ) : (
                <div className="text-center py-12 bg-gray-50 rounded-lg border border-gray-200">
                    <h3 className="text-lg font-semibold text-gray-700 mb-2">No Pipeline Configured</h3>
                    <p className="text-gray-500 mb-4">Create a pipeline to automate your data processing workflow!</p>
                    <button
                        onClick={() => setIsConfigModalOpen(true)}
                        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
                    >
                        Create Pipeline
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
        </div>
    );
} 