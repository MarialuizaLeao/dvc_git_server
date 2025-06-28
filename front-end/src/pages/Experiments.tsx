import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useExperiments } from '../hooks/useExperiments';
import { CURRENT_USER } from '../constants/user';
import RunExperimentModal from '../components/RunExperimentModal';
import type { CreateExperimentData } from '../types/api';

const Experiments = () => {
    const { id: projectId } = useParams();
    const [isModalOpen, setIsModalOpen] = useState(false);

    const { experiments, createExperiment } = useExperiments(CURRENT_USER.id, projectId || '');
    const createExperimentMutation = createExperiment;

    const handleCreateExperiment = async (data: CreateExperimentData) => {
        try {
            await createExperimentMutation.mutateAsync(data);
            setIsModalOpen(false);
        } catch (error) {
            console.error('Failed to create experiment:', error);
        }
    };

    // Parse the experiments data from the API response
    const experimentsData = (() => {
        try {
            const output = experiments.data?.output;

            if (!output) return [];

            // If output is a string, try to parse it as JSON
            if (typeof output === 'string') {
                const parsed = JSON.parse(output);
                // DVC exp show --json returns an array of experiment objects
                if (Array.isArray(parsed)) {
                    return parsed;
                }
                return [];
            }

            // If output is already an array
            if (Array.isArray(output)) {
                return output;
            }

            return [];
        } catch (error) {
            console.error('Error parsing experiments data:', error);
            return [];
        }
    })();

    // Transform the experiments data to a more usable format
    const transformedExperiments = experimentsData.flatMap((item: any) => {
        // If this item has experiments, extract them
        if (item.experiments && Array.isArray(item.experiments)) {
            return item.experiments.map((exp: any) => {
                const firstRev = exp.revs && exp.revs[0];
                if (!firstRev) return null;

                // Extract parameters from the experiment's specific revision
                const experimentParams = firstRev.data?.params?.['params.yaml']?.data || {};

                // Extract only the experiment-specific parameters (the ones that were changed)
                const experimentSpecificParams = (() => {
                    const specific: Record<string, any> = {};

                    // Look for parameters that were explicitly set for this experiment
                    // These are typically the ones that differ from the baseline
                    const allParams = experimentParams;

                    // Extract nested parameters first (these are usually the experiment-specific ones)
                    for (const [section, sectionParams] of Object.entries(allParams)) {
                        if (sectionParams && typeof sectionParams === 'object' && !Array.isArray(sectionParams)) {
                            for (const [param, value] of Object.entries(sectionParams)) {
                                specific[`${section}.${param}`] = value;
                            }
                        }
                    }

                    return specific;
                })();

                return {
                    id: firstRev.rev,
                    name: firstRev.name || exp.name,
                    rev: firstRev.rev,
                    timestamp: firstRev.data?.timestamp,
                    params: experimentSpecificParams,
                    metrics: firstRev.data?.metrics?.['eval/metrics.json']?.data || {},
                    deps: firstRev.data?.deps || {},
                    outs: firstRev.data?.outs || {}
                };
            }).filter(Boolean); // Remove null entries
        }

        // If this is a workspace item with data, treat it as a current experiment
        if (item.rev === 'workspace' && item.data) {
            const workspaceParams = item.data.params?.['params.yaml']?.data || {};

            // Flatten the nested parameter structure for better display
            const flattenedWorkspaceParams = (() => {
                const specific: Record<string, any> = {};

                // Extract nested parameters (these are usually the experiment-specific ones)
                for (const [section, sectionParams] of Object.entries(workspaceParams)) {
                    if (sectionParams && typeof sectionParams === 'object' && !Array.isArray(sectionParams)) {
                        for (const [param, value] of Object.entries(sectionParams)) {
                            specific[`${section}.${param}`] = value;
                        }
                    }
                }

                return specific;
            })();

            return [{
                id: 'workspace',
                name: 'Current Workspace',
                rev: 'workspace',
                timestamp: item.data.timestamp,
                params: flattenedWorkspaceParams,
                metrics: item.data.metrics?.['eval/metrics.json']?.data || {},
                deps: item.data.deps || {},
                outs: item.data.outs || {}
            }];
        }

        return [];
    });

    // Ensure transformedExperiments is always an array
    const safeExperimentsData = Array.isArray(transformedExperiments) ? transformedExperiments : [];

    return (
        <div className="h-full flex flex-col">
            <div className="flex justify-between items-center mb-6 flex-shrink-0">
                <h1 className="text-2xl font-semibold">Experimentos</h1>
                <div className="flex gap-3">
                    <button
                        onClick={() => experiments.refetch()}
                        className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                    >
                        🔄 Atualizar
                    </button>
                    <button
                        onClick={() => setIsModalOpen(true)}
                        className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                    >
                        + Novo Experimento
                    </button>
                </div>
            </div>

            <div className="flex-1 overflow-auto">
                {experiments.isLoading ? (
                    <div className="text-center py-12">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4"></div>
                        <p className="text-gray-600">Carregando experimentos...</p>
                    </div>
                ) : experiments.isError ? (
                    <div className="text-center py-12">
                        <div className="text-red-400 text-6xl mb-4">⚠️</div>
                        <h3 className="text-lg font-medium text-gray-900 mb-2">Erro ao Carregar Experimentos</h3>
                        <p className="text-gray-600 mb-6">
                            {(experiments.error as Error)?.message || 'Ocorreu um erro ao carregar os experimentos.'}
                        </p>
                        <button
                            onClick={() => experiments.refetch()}
                            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                        >
                            Tentar Novamente
                        </button>
                    </div>
                ) : safeExperimentsData.length === 0 ? (
                    <div className="text-center py-12">
                        <div className="text-gray-400 text-6xl mb-4">🧪</div>
                        <h3 className="text-lg font-medium text-gray-900 mb-2">Nenhum Experimento Encontrado</h3>
                        <p className="text-gray-600 mb-6">
                            Execute seu primeiro experimento para começar a ver os resultados aqui.
                        </p>
                        <button
                            onClick={() => setIsModalOpen(true)}
                            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                        >
                            + Criar Primeiro Experimento
                        </button>
                    </div>
                ) : (
                    <div className="grid gap-6">
                        {safeExperimentsData.map((experiment: any, index: number) => (
                            <div
                                key={experiment.id || experiment.rev || index}
                                className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm hover:shadow-md transition-shadow"
                            >
                                <div className="flex justify-between items-start mb-4">
                                    <div className="text-purple-700 hover:text-purple-800 text-lg font-medium">
                                        {experiment.name}
                                        {experiment.rev === 'workspace' && (
                                            <span className="ml-2 text-sm text-gray-500">(Atual)</span>
                                        )}
                                    </div>
                                    <div className="space-x-2">
                                        <button className="px-4 py-2 border border-green-300 text-green-700 rounded-lg hover:bg-green-50 transition-colors">
                                            Visualizar
                                        </button>
                                        <button className="px-4 py-2 border border-blue-300 text-blue-700 rounded-lg hover:bg-blue-50 transition-colors">
                                            Comparar
                                        </button>
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 gap-4 mb-4">
                                    <div>
                                        <span className="text-sm text-gray-500">Commit:</span>
                                        <div className="text-sm font-mono text-gray-700 truncate">
                                            {experiment.rev}
                                        </div>
                                    </div>
                                    <div>
                                        <span className="text-sm text-gray-500">Data:</span>
                                        <div className="text-sm text-gray-700">
                                            {experiment.timestamp ? new Date(experiment.timestamp).toLocaleString() : 'N/D'}
                                        </div>
                                    </div>
                                </div>

                                {/* Parameters */}
                                {Object.keys(experiment.params).length > 0 && (
                                    <div className="mb-4">
                                        <h4 className="text-sm font-medium text-gray-700 mb-2">Parâmetros:</h4>
                                        <div className="grid grid-cols-2 gap-2 text-sm">
                                            {Object.entries(experiment.params).map(([key, value]: [string, any]) => (
                                                <div key={key} className="flex justify-between">
                                                    <span className="text-gray-600">{key}:</span>
                                                    <span className="font-mono text-gray-800">{String(value)}</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {/* Metrics */}
                                {Object.keys(experiment.metrics).length > 0 && (
                                    <div>
                                        <h4 className="text-sm font-medium text-gray-700 mb-2">Métricas:</h4>
                                        <div className="grid grid-cols-2 gap-4">
                                            {Object.entries(experiment.metrics).map(([metricName, metricData]: [string, any]) => (
                                                <div key={metricName} className="bg-gray-50 p-3 rounded">
                                                    <div className="text-sm font-medium text-gray-700 mb-1 capitalize">
                                                        {metricName.replace(/_/g, ' ')}
                                                    </div>
                                                    {typeof metricData === 'object' && metricData !== null ? (
                                                        Object.entries(metricData).map(([split, value]: [string, any]) => (
                                                            <div key={split} className="flex justify-between text-sm">
                                                                <span className="text-gray-600 capitalize">{split}:</span>
                                                                <span className="font-mono text-gray-800">
                                                                    {typeof value === 'number' ? value.toFixed(4) : String(value)}
                                                                </span>
                                                            </div>
                                                        ))
                                                    ) : (
                                                        <div className="text-sm font-mono text-gray-800">
                                                            {typeof metricData === 'number' ? metricData.toFixed(4) : String(metricData)}
                                                        </div>
                                                    )}
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                )}
            </div>

            <RunExperimentModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onRun={handleCreateExperiment}
                isLoading={createExperimentMutation.isPending}
                userId={CURRENT_USER.id}
                projectId={projectId || ''}
            />
        </div>
    );
};

export default Experiments; 