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
        <div>
            <div className="mb-6">
                <h1 className="text-2xl mb-4">Experimentos</h1>
                <button className="px-2 py-1 border border-gray-300 rounded hover:bg-gray-100">
                    + Novo Experimento
                </button>
            </div>

            <div className="space-y-6">
                {experiments.map((experiment) => (
                    <div key={experiment.id} className="border-t border-gray-200 pt-4">
                        <div className="flex justify-between items-start">
                            <Link to={`/experiments/${experiment.id}`} className="text-purple-700 hover:underline text-lg">
                                {experiment.name}
                            </Link>
                            <div className="space-x-2">
                                {experiment.status === 'running' ? (
                                    <button className="px-2 py-1 border border-red-300 text-red-600 rounded hover:bg-red-50">
                                        Parar
                                    </button>
                                ) : (
                                    <button className="px-2 py-1 border border-green-300 text-green-600 rounded hover:bg-green-50">
                                        Executar
                                    </button>
                                )}
                            </div>
                        </div>

                        <div className="mt-2 grid grid-cols-3 gap-4">
                            <div>
                                <p className="text-sm text-gray-600">Status</p>
                                <p className={getStatusColor(experiment.status)}>
                                    {experiment.status.charAt(0).toUpperCase() + experiment.status.slice(1)}
                                </p>
                            </div>
                            <div>
                                <p className="text-sm text-gray-600">Modelo</p>
                                <p>{experiment.model}</p>
                            </div>
                            <div>
                                <p className="text-sm text-gray-600">Dataset</p>
                                <p>{experiment.dataset}</p>
                            </div>
                        </div>

                        {experiment.metrics && (
                            <div className="mt-4">
                                <p className="text-sm text-gray-600 mb-2">Métricas</p>
                                <div className="grid grid-cols-2 gap-4">
                                    {experiment.metrics.accuracy && (
                                        <div>
                                            <p className="text-sm text-gray-600">Acurácia</p>
                                            <p>{(experiment.metrics.accuracy * 100).toFixed(2)}%</p>
                                        </div>
                                    )}
                                    {experiment.metrics.loss && (
                                        <div>
                                            <p className="text-sm text-gray-600">Loss</p>
                                            <p>{experiment.metrics.loss.toFixed(4)}</p>
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Experiments; 