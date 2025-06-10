import { useState } from 'react';
import { useParams } from 'react-router-dom';
import Card from '../components/Card';

// Mock pipeline data - will be replaced with API data later
const mockPipeline = {
    id: '1',
    name: 'MNIST Training Pipeline',
    description: 'Pipeline for training and evaluating MNIST digit classification models',
    status: 'active',
    last_run: '2024-03-15T15:30:00Z',
    steps: [
        {
            id: '1',
            name: 'Data Loading',
            type: 'data_input',
            config: {
                dataset: 'MNIST',
                batch_size: 32,
                shuffle: true
            },
            status: 'completed'
        },
        {
            id: '2',
            name: 'Data Preprocessing',
            type: 'transform',
            config: {
                normalize: true,
                augmentation: ['rotation', 'shift']
            },
            status: 'completed'
        },
        {
            id: '3',
            name: 'Model Training',
            type: 'training',
            config: {
                model: 'CNN',
                epochs: 10,
                learning_rate: 0.001
            },
            status: 'running'
        },
        {
            id: '4',
            name: 'Model Evaluation',
            type: 'evaluation',
            config: {
                metrics: ['accuracy', 'precision', 'recall']
            },
            status: 'pending'
        }
    ]
};

const Pipeline = () => {
    const { id } = useParams();
    const [pipeline] = useState(mockPipeline);
    const [selectedStep, setSelectedStep] = useState<string | null>(null);

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'completed':
                return 'bg-green-100 text-green-800 border-green-200';
            case 'running':
                return 'bg-blue-100 text-blue-800 border-blue-200';
            case 'pending':
                return 'bg-gray-100 text-gray-800 border-gray-200';
            case 'failed':
                return 'bg-red-100 text-red-800 border-red-200';
            default:
                return 'bg-gray-100 text-gray-800 border-gray-200';
        }
    };

    const getStepIcon = (type: string) => {
        switch (type) {
            case 'data_input':
                return '📥';
            case 'transform':
                return '🔄';
            case 'training':
                return '⚙️';
            case 'evaluation':
                return '📊';
            default:
                return '📋';
        }
    };

    return (
        <div className="max-w-7xl mx-auto space-y-6">
            {/* Pipeline Header */}
            <div className="bg-white p-6 rounded-lg border border-gray-200">
                <div className="flex justify-between items-start mb-4">
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900">{pipeline.name}</h1>
                        <p className="text-gray-500 mt-1">{pipeline.description}</p>
                    </div>
                    <div className="flex space-x-3">
                        <button className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors">
                            Run Pipeline
                        </button>
                        <button className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
                            Edit Pipeline
                        </button>
                    </div>
                </div>
                <div className="flex items-center text-sm text-gray-500">
                    <span>Last run: {new Date(pipeline.last_run).toLocaleString()}</span>
                    <span className="mx-2">•</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(pipeline.status)}`}>
                        {pipeline.status.charAt(0).toUpperCase() + pipeline.status.slice(1)}
                    </span>
                </div>
            </div>

            <div className="grid grid-cols-3 gap-6">
                {/* Pipeline Steps */}
                <div className="col-span-2 bg-white rounded-lg border border-gray-200 p-6">
                    <h2 className="text-lg font-semibold mb-4">Pipeline Steps</h2>
                    <div className="space-y-4">
                        {pipeline.steps.map((step, index) => (
                            <div
                                key={step.id}
                                className={`relative flex items-start space-x-4 p-4 rounded-lg border ${selectedStep === step.id ? 'border-blue-500 ring-1 ring-blue-500' : 'border-gray-200'
                                    } cursor-pointer hover:border-blue-500 transition-colors`}
                                onClick={() => setSelectedStep(step.id)}
                            >
                                {/* Connector Line */}
                                {index < pipeline.steps.length - 1 && (
                                    <div className="absolute left-7 top-16 bottom-0 w-0.5 bg-gray-200"></div>
                                )}

                                {/* Step Icon */}
                                <div className="flex-shrink-0 w-6">
                                    <span className="text-xl" role="img" aria-label={step.type}>
                                        {getStepIcon(step.type)}
                                    </span>
                                </div>

                                {/* Step Content */}
                                <div className="flex-1">
                                    <div className="flex justify-between items-start">
                                        <div>
                                            <h3 className="font-medium text-gray-900">{step.name}</h3>
                                            <p className="text-sm text-gray-500">{step.type}</p>
                                        </div>
                                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(step.status)}`}>
                                            {step.status.charAt(0).toUpperCase() + step.status.slice(1)}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Step Details */}
                <div className="col-span-1">
                    {selectedStep ? (
                        <Card title="Step Configuration">
                            {(() => {
                                const step = pipeline.steps.find(s => s.id === selectedStep);
                                if (!step) return null;

                                return (
                                    <div className="space-y-4">
                                        <div>
                                            <h4 className="text-sm font-medium text-gray-500">Step Type</h4>
                                            <p className="mt-1">{step.type}</p>
                                        </div>
                                        <div>
                                            <h4 className="text-sm font-medium text-gray-500">Configuration</h4>
                                            <pre className="mt-2 p-3 bg-gray-50 rounded-lg text-sm overflow-auto">
                                                {JSON.stringify(step.config, null, 2)}
                                            </pre>
                                        </div>
                                        <div className="pt-4">
                                            <button className="w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
                                                Edit Step
                                            </button>
                                        </div>
                                    </div>
                                );
                            })()}
                        </Card>
                    ) : (
                        <div className="text-center py-12 bg-gray-50 rounded-lg border border-gray-200">
                            <p className="text-gray-500">Select a step to view its details</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Pipeline; 