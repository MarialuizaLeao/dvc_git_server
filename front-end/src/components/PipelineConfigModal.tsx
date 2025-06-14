import { useState, useEffect } from 'react';
import type { Pipeline, PipelineStage, CreatePipelineRequest, UpdatePipelineRequest } from '../types/api';

interface PipelineConfigModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSubmit: (data: CreatePipelineRequest | UpdatePipelineRequest) => void;
    pipeline?: Pipeline | null;
    error?: string;
    isLoading?: boolean;
}

export default function PipelineConfigModal({
    isOpen,
    onClose,
    onSubmit,
    pipeline,
    error,
    isLoading = false
}: PipelineConfigModalProps) {
    const [formData, setFormData] = useState<CreatePipelineRequest>({
        name: '',
        description: '',
        stages: []
    });

    const [stages, setStages] = useState<PipelineStage[]>([]);

    useEffect(() => {
        if (pipeline) {
            setFormData({
                name: pipeline.name,
                description: pipeline.description || '',
                stages: pipeline.stages
            });
            setStages(pipeline.stages);
        } else {
            setFormData({
                name: '',
                description: '',
                stages: []
            });
            setStages([]);
        }
    }, [pipeline, isOpen]);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSubmit({
            ...formData,
            stages
        });
    };

    const addStage = () => {
        const newStage: PipelineStage = {
            name: '',
            deps: [],
            outs: [],
            command: '',
            description: ''
        };
        setStages([...stages, newStage]);
    };

    const updateStage = (index: number, field: keyof PipelineStage, value: any) => {
        const updatedStages = [...stages];
        updatedStages[index] = { ...updatedStages[index], [field]: value };
        setStages(updatedStages);
    };

    const removeStage = (index: number) => {
        setStages(stages.filter((_, i) => i !== index));
    };

    const addArrayItem = (index: number, field: 'deps' | 'outs' | 'params' | 'metrics' | 'plots') => {
        const updatedStages = [...stages];
        if (!updatedStages[index][field]) {
            updatedStages[index][field] = [];
        }
        updatedStages[index][field] = [...(updatedStages[index][field] || []), ''];
        setStages(updatedStages);
    };

    const updateArrayItem = (stageIndex: number, field: 'deps' | 'outs' | 'params' | 'metrics' | 'plots', itemIndex: number, value: string) => {
        const updatedStages = [...stages];
        const array = [...(updatedStages[stageIndex][field] || [])];
        array[itemIndex] = value;
        updatedStages[stageIndex][field] = array;
        setStages(updatedStages);
    };

    const removeArrayItem = (stageIndex: number, field: 'deps' | 'outs' | 'params' | 'metrics' | 'plots', itemIndex: number) => {
        const updatedStages = [...stages];
        const array = [...(updatedStages[stageIndex][field] || [])];
        array.splice(itemIndex, 1);
        updatedStages[stageIndex][field] = array;
        setStages(updatedStages);
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-2xl font-bold">
                        {pipeline ? 'Edit Pipeline' : 'Create Pipeline'}
                    </h2>
                    <button
                        onClick={onClose}
                        className="text-gray-500 hover:text-gray-700"
                    >
                        ✕
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Pipeline Name *
                        </label>
                        <input
                            type="text"
                            value={formData.name}
                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Description
                        </label>
                        <textarea
                            value={formData.description}
                            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            rows={3}
                        />
                    </div>

                    <div>
                        <div className="flex justify-between items-center mb-4">
                            <h3 className="text-lg font-semibold">Pipeline Stages</h3>
                            <button
                                type="button"
                                onClick={addStage}
                                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
                            >
                                Add Stage
                            </button>
                        </div>

                        <div className="space-y-4">
                            {stages.map((stage, stageIndex) => (
                                <div key={stageIndex} className="border border-gray-200 rounded-lg p-4">
                                    <div className="flex justify-between items-center mb-4">
                                        <h4 className="font-medium">Stage {stageIndex + 1}</h4>
                                        <button
                                            type="button"
                                            onClick={() => removeStage(stageIndex)}
                                            className="text-red-500 hover:text-red-700"
                                        >
                                            Remove
                                        </button>
                                    </div>

                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                                Stage Name *
                                            </label>
                                            <input
                                                type="text"
                                                value={stage.name}
                                                onChange={(e) => updateStage(stageIndex, 'name', e.target.value)}
                                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                                required
                                            />
                                        </div>

                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                                Description
                                            </label>
                                            <input
                                                type="text"
                                                value={stage.description || ''}
                                                onChange={(e) => updateStage(stageIndex, 'description', e.target.value)}
                                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                            />
                                        </div>
                                    </div>

                                    <div className="mt-4">
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            Command *
                                        </label>
                                        <input
                                            type="text"
                                            value={stage.command}
                                            onChange={(e) => updateStage(stageIndex, 'command', e.target.value)}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                            placeholder="python script.py"
                                            required
                                        />
                                    </div>

                                    {/* Dependencies */}
                                    <div className="mt-4">
                                        <div className="flex justify-between items-center mb-2">
                                            <label className="block text-sm font-medium text-gray-700">
                                                Dependencies
                                            </label>
                                            <button
                                                type="button"
                                                onClick={() => addArrayItem(stageIndex, 'deps')}
                                                className="text-sm text-blue-500 hover:text-blue-700"
                                            >
                                                Add
                                            </button>
                                        </div>
                                        {(stage.deps || []).map((dep, depIndex) => (
                                            <div key={depIndex} className="flex gap-2 mb-2">
                                                <input
                                                    type="text"
                                                    value={dep}
                                                    onChange={(e) => updateArrayItem(stageIndex, 'deps', depIndex, e.target.value)}
                                                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                                    placeholder="data/raw"
                                                />
                                                <button
                                                    type="button"
                                                    onClick={() => removeArrayItem(stageIndex, 'deps', depIndex)}
                                                    className="px-3 py-2 text-red-500 hover:text-red-700"
                                                >
                                                    ✕
                                                </button>
                                            </div>
                                        ))}
                                    </div>

                                    {/* Outputs */}
                                    <div className="mt-4">
                                        <div className="flex justify-between items-center mb-2">
                                            <label className="block text-sm font-medium text-gray-700">
                                                Outputs
                                            </label>
                                            <button
                                                type="button"
                                                onClick={() => addArrayItem(stageIndex, 'outs')}
                                                className="text-sm text-blue-500 hover:text-blue-700"
                                            >
                                                Add
                                            </button>
                                        </div>
                                        {(stage.outs || []).map((out, outIndex) => (
                                            <div key={outIndex} className="flex gap-2 mb-2">
                                                <input
                                                    type="text"
                                                    value={out}
                                                    onChange={(e) => updateArrayItem(stageIndex, 'outs', outIndex, e.target.value)}
                                                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                                    placeholder="data/processed"
                                                />
                                                <button
                                                    type="button"
                                                    onClick={() => removeArrayItem(stageIndex, 'outs', outIndex)}
                                                    className="px-3 py-2 text-red-500 hover:text-red-700"
                                                >
                                                    ✕
                                                </button>
                                            </div>
                                        ))}
                                    </div>

                                    {/* Parameters */}
                                    <div className="mt-4">
                                        <div className="flex justify-between items-center mb-2">
                                            <label className="block text-sm font-medium text-gray-700">
                                                Parameters
                                            </label>
                                            <button
                                                type="button"
                                                onClick={() => addArrayItem(stageIndex, 'params')}
                                                className="text-sm text-blue-500 hover:text-blue-700"
                                            >
                                                Add
                                            </button>
                                        </div>
                                        {(stage.params || []).map((param, paramIndex) => (
                                            <div key={paramIndex} className="flex gap-2 mb-2">
                                                <input
                                                    type="text"
                                                    value={param}
                                                    onChange={(e) => updateArrayItem(stageIndex, 'params', paramIndex, e.target.value)}
                                                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                                    placeholder="params.yaml"
                                                />
                                                <button
                                                    type="button"
                                                    onClick={() => removeArrayItem(stageIndex, 'params', paramIndex)}
                                                    className="px-3 py-2 text-red-500 hover:text-red-700"
                                                >
                                                    ✕
                                                </button>
                                            </div>
                                        ))}
                                    </div>

                                    {/* Metrics */}
                                    <div className="mt-4">
                                        <div className="flex justify-between items-center mb-2">
                                            <label className="block text-sm font-medium text-gray-700">
                                                Metrics
                                            </label>
                                            <button
                                                type="button"
                                                onClick={() => addArrayItem(stageIndex, 'metrics')}
                                                className="text-sm text-blue-500 hover:text-blue-700"
                                            >
                                                Add
                                            </button>
                                        </div>
                                        {(stage.metrics || []).map((metric, metricIndex) => (
                                            <div key={metricIndex} className="flex gap-2 mb-2">
                                                <input
                                                    type="text"
                                                    value={metric}
                                                    onChange={(e) => updateArrayItem(stageIndex, 'metrics', metricIndex, e.target.value)}
                                                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                                    placeholder="metrics/accuracy.json"
                                                />
                                                <button
                                                    type="button"
                                                    onClick={() => removeArrayItem(stageIndex, 'metrics', metricIndex)}
                                                    className="px-3 py-2 text-red-500 hover:text-red-700"
                                                >
                                                    ✕
                                                </button>
                                            </div>
                                        ))}
                                    </div>

                                    {/* Plots */}
                                    <div className="mt-4">
                                        <div className="flex justify-between items-center mb-2">
                                            <label className="block text-sm font-medium text-gray-700">
                                                Plots
                                            </label>
                                            <button
                                                type="button"
                                                onClick={() => addArrayItem(stageIndex, 'plots')}
                                                className="text-sm text-blue-500 hover:text-blue-700"
                                            >
                                                Add
                                            </button>
                                        </div>
                                        {(stage.plots || []).map((plot, plotIndex) => (
                                            <div key={plotIndex} className="flex gap-2 mb-2">
                                                <input
                                                    type="text"
                                                    value={plot}
                                                    onChange={(e) => updateArrayItem(stageIndex, 'plots', plotIndex, e.target.value)}
                                                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                                    placeholder="plots/confusion_matrix.png"
                                                />
                                                <button
                                                    type="button"
                                                    onClick={() => removeArrayItem(stageIndex, 'plots', plotIndex)}
                                                    className="px-3 py-2 text-red-500 hover:text-red-700"
                                                >
                                                    ✕
                                                </button>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {error && (
                        <div className="text-red-600 text-sm">{error}</div>
                    )}

                    <div className="flex justify-end space-x-3">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={isLoading || stages.length === 0}
                            className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {isLoading ? 'Saving...' : (pipeline ? 'Update' : 'Create')}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
} 