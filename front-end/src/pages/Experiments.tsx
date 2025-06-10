import { useState } from 'react';
import { Link } from 'react-router-dom';

interface Experiment {
    id: string;
    name: string;
    status: 'running' | 'completed' | 'failed' | 'pending';
    model: string;
    dataset: string;
    created_at: string;
    metrics: {
        accuracy?: number;
        loss?: number;
    };
}

const Experiments = () => {
    const [experiments, setExperiments] = useState<Experiment[]>([
        {
            id: '1',
            name: 'MNIST Training',
            status: 'completed',
            model: 'CNN',
            dataset: 'MNIST',
            created_at: '2024-06-03',
            metrics: {
                accuracy: 0.98,
                loss: 0.045,
            },
        },
        // Add more mock experiments as needed
    ]);

    const getStatusColor = (status: Experiment['status']) => {
        switch (status) {
            case 'running':
                return 'text-blue-600';
            case 'completed':
                return 'text-green-600';
            case 'failed':
                return 'text-red-600';
            default:
                return 'text-gray-600';
        }
    };

    return (
        <div className="h-full flex flex-col">
            <div className="flex justify-between items-center mb-6 flex-shrink-0">
                <h1 className="text-2xl font-semibold">Experimentos</h1>
                <button className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors">
                    + Novo Experimento
                </button>
            </div>

            <div className="flex-1 overflow-auto">
                <div className="grid gap-6">
                    {experiments.map((experiment) => (
                        <div
                            key={experiment.id}
                            className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm hover:shadow-md transition-shadow"
                        >
                            <div className="flex justify-between items-start mb-4">
                                <Link
                                    to={`/experiments/${experiment.id}`}
                                    className="text-purple-700 hover:text-purple-800 text-lg font-medium"
                                >
                                    {experiment.name}
                                </Link>
                                <div className="space-x-2">
                                    {experiment.status === 'running' ? (
                                        <button className="px-4 py-2 border border-red-300 text-red-600 rounded-lg hover:bg-red-50 transition-colors">
                                            Parar
                                        </button>
                                    ) : (
                                        <button className="px-4 py-2 border border-green-300 text-green-600 rounded-lg hover:bg-green-50 transition-colors">
                                            Executar
                                        </button>
                                    )}
                                </div>
                            </div>

                            <div className="grid grid-cols-3 gap-6 mb-4">
                                <div className="bg-gray-50 p-3 rounded-lg">
                                    <p className="text-sm text-gray-600 mb-1">Status</p>
                                    <p className={`${getStatusColor(experiment.status)} font-medium`}>
                                        {experiment.status.charAt(0).toUpperCase() + experiment.status.slice(1)}
                                    </p>
                                </div>
                                <div className="bg-gray-50 p-3 rounded-lg">
                                    <p className="text-sm text-gray-600 mb-1">Modelo</p>
                                    <p className="font-medium">{experiment.model}</p>
                                </div>
                                <div className="bg-gray-50 p-3 rounded-lg">
                                    <p className="text-sm text-gray-600 mb-1">Dataset</p>
                                    <p className="font-medium">{experiment.dataset}</p>
                                </div>
                            </div>

                            {experiment.metrics && (
                                <div className="bg-gray-50 p-4 rounded-lg">
                                    <p className="text-sm text-gray-600 mb-3 font-medium">Métricas</p>
                                    <div className="grid grid-cols-2 gap-6">
                                        {experiment.metrics.accuracy && (
                                            <div>
                                                <p className="text-sm text-gray-600 mb-1">Acurácia</p>
                                                <p className="text-lg font-medium text-purple-700">
                                                    {(experiment.metrics.accuracy * 100).toFixed(2)}%
                                                </p>
                                            </div>
                                        )}
                                        {experiment.metrics.loss && (
                                            <div>
                                                <p className="text-sm text-gray-600 mb-1">Loss</p>
                                                <p className="text-lg font-medium text-purple-700">
                                                    {experiment.metrics.loss.toFixed(4)}
                                                </p>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Experiments; 