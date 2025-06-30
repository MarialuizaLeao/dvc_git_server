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
            console.log('Creating experiment with data:', data);
            console.log('Current experiments before creation:', safeExperimentsData);

            const result = await createExperimentMutation.mutateAsync(data);
            console.log('Experiment created successfully:', result);
            setIsModalOpen(false);

            // Force a refetch to ensure we get the latest data
            setTimeout(() => {
                console.log('Refetching experiments after creation...');
                experiments.refetch();
            }, 1000);

            // Additional refetch after a longer delay to ensure DVC has finished
            setTimeout(() => {
                console.log('Second refetch after longer delay...');
                experiments.refetch();
            }, 3000);
        } catch (error) {
            console.error('Failed to create experiment:', error);
            // You might want to show an error message to the user here
        }
    };

    // Parse the experiments data from the API response
    const experimentsData = (() => {
        try {
            const output = experiments.data?.output;

            if (!output) {
                console.log('No output data available');
                return [];
            }

            console.log('Raw experiments output:', output);
            console.log('Output type:', typeof output);

            // If output is a string, try to parse it as JSON
            if (typeof output === 'string') {
                try {
                    const parsed = JSON.parse(output);
                    // DVC exp show --json returns an array of experiment objects
                    if (Array.isArray(parsed)) {
                        console.log('Parsed experiments data:', parsed);
                        return parsed;
                    }
                    console.log('Parsed data is not an array:', parsed);
                    return [];
                } catch (parseError) {
                    console.error('Error parsing JSON string:', parseError);
                    console.error('Raw output that failed to parse:', output);
                    return [];
                }
            }

            // If output is already an array
            if (Array.isArray(output)) {
                console.log('Output is already an array:', output);
                return output;
            }

            console.log('Unexpected output format:', typeof output, output);
            return [];
        } catch (error) {
            console.error('Error parsing experiments data:', error);
            return [];
        }
    })();

    // Transform the experiments data to a more usable format
    const transformedExperiments = experimentsData.flatMap((item: any) => {
        try {
            console.log('Processing experiment item:', item);
            console.log('Item keys:', Object.keys(item));

            // If this item has experiments, extract them
            if (item.experiments && Array.isArray(item.experiments)) {
                console.log('Found experiments array with', item.experiments.length, 'experiments');

                // If no experiments in this item, skip it (unless it's workspace)
                if (item.experiments.length === 0 && item.rev !== 'workspace') {
                    console.log('Skipping item with no experiments:', item.rev);
                    return [];
                }

                return item.experiments.map((exp: any) => {
                    console.log('Processing experiment:', exp);
                    const firstRev = exp.revs && exp.revs[0];
                    if (!firstRev) {
                        console.log('No first revision found for experiment:', exp);
                        return null;
                    }

                    // Extract parameters from the experiment's specific revision
                    const experimentParams = firstRev.data?.params?.['params.yaml']?.data || {};

                    // Extract only the experiment-specific parameters (the ones that were changed)
                    const experimentSpecificParams = (() => {
                        const specific: Record<string, any> = {};

                        // Extract nested parameters first (these are usually the experiment-specific ones)
                        for (const [section, sectionParams] of Object.entries(experimentParams)) {
                            if (sectionParams && typeof sectionParams === 'object' && !Array.isArray(sectionParams)) {
                                for (const [param, value] of Object.entries(sectionParams)) {
                                    specific[`${section}.${param}`] = value;
                                }
                            }
                        }

                        return specific;
                    })();

                    const transformedExp = {
                        id: firstRev.rev,
                        name: firstRev.name || exp.name,
                        rev: firstRev.rev,
                        timestamp: firstRev.data?.timestamp,
                        params: experimentSpecificParams,
                        metrics: firstRev.data?.metrics?.['eval/metrics.json']?.data || {},
                        deps: firstRev.data?.deps || {},
                        outs: firstRev.data?.outs || {}
                    };

                    console.log('Transformed experiment:', transformedExp);
                    return transformedExp;
                }).filter(Boolean); // Remove null entries
            }

            // If this is a workspace item with data, treat it as a current experiment
            if (item.rev === 'workspace' && item.data) {
                console.log('Processing workspace item');
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

                const workspaceExp = {
                    id: 'workspace',
                    name: 'Current Workspace',
                    rev: 'workspace',
                    timestamp: item.data.timestamp,
                    params: flattenedWorkspaceParams,
                    metrics: item.data.metrics?.['eval/metrics.json']?.data || {},
                    deps: item.data.deps || {},
                    outs: item.data.outs || {}
                };

                console.log('Transformed workspace experiment:', workspaceExp);
                return [workspaceExp];
            }

            // If this is a direct experiment item (not nested)
            if (item.rev && item.data) {
                console.log('Processing direct experiment item:', item.rev);
                const experimentParams = item.data.params?.['params.yaml']?.data || {};

                const flattenedParams = (() => {
                    const specific: Record<string, any> = {};
                    for (const [section, sectionParams] of Object.entries(experimentParams)) {
                        if (sectionParams && typeof sectionParams === 'object' && !Array.isArray(sectionParams)) {
                            for (const [param, value] of Object.entries(sectionParams)) {
                                specific[`${section}.${param}`] = value;
                            }
                        }
                    }
                    return specific;
                })();

                const directExp = {
                    id: item.rev,
                    name: item.name || item.rev,
                    rev: item.rev,
                    timestamp: item.data.timestamp,
                    params: flattenedParams,
                    metrics: item.data.metrics?.['eval/metrics.json']?.data || {},
                    deps: item.data.deps || {},
                    outs: item.data.outs || {}
                };

                console.log('Transformed direct experiment:', directExp);
                return [directExp];
            }

            console.log('No matching condition for item:', item);
            return [];
        } catch (error) {
            console.error('Error transforming experiment item:', item, error);
            return [];
        }
    });

    // Ensure transformedExperiments is always an array
    const safeExperimentsData = Array.isArray(transformedExperiments) ? transformedExperiments : [];

    // Only show workspace card if all other cards are just commit/master cards (no real experiments)
    const onlyWorkspace =
        safeExperimentsData.filter(exp => exp.rev !== 'workspace').length === 0;

    const filteredExperimentsData = onlyWorkspace
        ? safeExperimentsData.filter(exp => exp.rev === 'workspace')
        : safeExperimentsData;

    console.log('Final experiments data:', filteredExperimentsData);

    return (
        <div className="h-full flex flex-col">
            <div className="flex justify-between items-center mb-6 flex-shrink-0">
                <h1 className="text-2xl font-semibold">Experimentos</h1>
                <div className="flex gap-3">
                    <button
                        onClick={() => experiments.refetch()}
                        className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                    >
                        Atualizar
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
                ) : filteredExperimentsData.length === 0 ? (
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
                        {filteredExperimentsData.map((experiment: any, index: number) => (
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