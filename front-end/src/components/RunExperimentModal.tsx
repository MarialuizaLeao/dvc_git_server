import { useState, useEffect } from 'react';
import { Dialog } from '@headlessui/react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import type { CreateExperimentData } from '../types/api';
import { API_ENDPOINTS } from '../constants/api';

interface ParameterValue {
    name: string;
    value: any;
    type: string;
    description?: string;
    required?: boolean;
    validation?: {
        min?: number;
        max?: number;
        pattern?: string;
    };
}

interface ParameterGroup {
    name: string;
    description?: string;
    parameters: ParameterValue[];
}

interface ParameterSet {
    name: string;
    description?: string;
    groups: ParameterGroup[];
    created_at?: string;
    updated_at?: string;
}

interface RunExperimentModalProps {
    isOpen: boolean;
    onClose: () => void;
    onRun: (params: CreateExperimentData) => void;
    isLoading?: boolean;
    userId: string;
    projectId: string;
}

const RunExperimentModal = ({ isOpen, onClose, onRun, isLoading = false, userId, projectId }: RunExperimentModalProps) => {
    const [formData, setFormData] = useState({
        experiment_name: '',
        message: '',
        set_param: [] as string[],
        force: false,
        queue: false,
        temp: false,
        recursive: false,
        pipeline: false,
        dry: false,
    });

    const [parameterSet, setParameterSet] = useState<ParameterSet | null>(null);
    const [isLoadingParameters, setIsLoadingParameters] = useState(false);
    const [parameterError, setParameterError] = useState<string | null>(null);

    // Load current parameters when modal opens
    useEffect(() => {
        if (isOpen) {
            // Reset form data when modal opens
            setFormData({
                experiment_name: '',
                message: '',
                set_param: [] as string[],
                force: false,
                queue: false,
                temp: false,
                recursive: false,
                pipeline: false,
                dry: false,
            });
            setParameterSet(null);
            setParameterError(null);

            // Load fresh parameters
            loadCurrentParameters();
        }
    }, [isOpen, userId, projectId]);

    const loadCurrentParameters = async () => {
        setIsLoadingParameters(true);
        setParameterError(null);
        try {
            const response = await fetch(API_ENDPOINTS.CURRENT_PARAMETERS(userId, projectId));
            if (response.ok) {
                const data = await response.json();
                if (data.parameter_set) {
                    setParameterSet(data.parameter_set);
                }
            } else {
                const errorData = await response.json();
                setParameterError(errorData.detail || 'Failed to load parameters');
            }
        } catch (err) {
            setParameterError('Failed to load parameters');
        } finally {
            setIsLoadingParameters(false);
        }
    };

    const updateParameterValue = (groupIndex: number, paramIndex: number, value: any) => {
        if (!parameterSet) return;

        const updatedParameterSet = { ...parameterSet };
        updatedParameterSet.groups = [...updatedParameterSet.groups];
        updatedParameterSet.groups[groupIndex] = { ...updatedParameterSet.groups[groupIndex] };
        updatedParameterSet.groups[groupIndex].parameters = [...updatedParameterSet.groups[groupIndex].parameters];
        updatedParameterSet.groups[groupIndex].parameters[paramIndex] = {
            ...updatedParameterSet.groups[groupIndex].parameters[paramIndex],
            value
        };

        setParameterSet(updatedParameterSet);
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();

        // Convert parameter values to set_param format maintaining nested structure
        const setParamValues: Record<string, any> = {};
        if (parameterSet) {
            parameterSet.groups.forEach(group => {
                // Create a nested structure for each group
                const groupParams: Record<string, any> = {};
                let hasGroupParams = false;

                group.parameters.forEach(param => {
                    // Only include parameters that have been explicitly changed from their original values
                    if (param.value !== undefined && param.value !== null && param.value !== '') {
                        groupParams[param.name] = param.value;
                        hasGroupParams = true;
                    }
                });

                // Only add the group if it has parameters
                if (hasGroupParams) {
                    setParamValues[group.name] = groupParams;
                }
            });
        }

        // Filter out empty values
        const params = {
            ...formData,
            set_param: Object.keys(setParamValues).length > 0 ? setParamValues : undefined,
        };

        // Remove empty fields
        Object.keys(params).forEach(key => {
            const value = params[key as keyof typeof params];
            if (
                value === '' ||
                (Array.isArray(value) && (!value || value.length === 0)) ||
                value === undefined
            ) {
                delete params[key as keyof typeof params];
            }
        });

        console.log('Submitting experiment with params:', params);
        onRun(params);
    };

    return (
        <Dialog open={isOpen} onClose={onClose} className="relative z-50">
            <div className="fixed inset-0 bg-black/30" aria-hidden="true" />

            <div className="fixed inset-0 flex items-center justify-center p-4">
                <Dialog.Panel className="mx-auto max-w-4xl w-full bg-white rounded-lg shadow-xl max-h-[90vh] overflow-y-auto">
                    <div className="flex items-center justify-between p-6 border-b">
                        <Dialog.Title className="text-lg font-semibold">
                            Executar Novo Experimento
                        </Dialog.Title>
                        <button
                            onClick={onClose}
                            className="text-gray-400 hover:text-gray-600"
                        >
                            <XMarkIcon className="h-6 w-6" />
                        </button>
                    </div>

                    <form onSubmit={handleSubmit} className="p-6 space-y-6">
                        {/* Basic Settings */}
                        <div className="space-y-4">
                            <h3 className="text-md font-medium text-gray-900">Configurações Básicas</h3>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Nome do Experimento
                                </label>
                                <input
                                    type="text"
                                    value={formData.experiment_name}
                                    onChange={(e) => setFormData(prev => ({ ...prev, experiment_name: e.target.value }))}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                                    placeholder="ex: experimento-001"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Mensagem
                                </label>
                                <textarea
                                    value={formData.message}
                                    onChange={(e) => setFormData(prev => ({ ...prev, message: e.target.value }))}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                                    rows={2}
                                    placeholder="Descrição do experimento..."
                                />
                            </div>
                        </div>

                        {/* Parameters */}
                        <div className="space-y-4">
                            <h3 className="text-md font-medium text-gray-900">Parâmetros</h3>

                            {parameterError && (
                                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                                    {parameterError}
                                </div>
                            )}

                            {isLoadingParameters ? (
                                <div className="flex items-center justify-center py-8">
                                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
                                    <span className="ml-2 text-gray-600">Carregando parâmetros...</span>
                                </div>
                            ) : parameterSet ? (
                                <div className="space-y-4">
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <h4 className="text-lg font-medium text-gray-900">{parameterSet.name}</h4>
                                            {parameterSet.description && (
                                                <p className="text-sm text-gray-600">{parameterSet.description}</p>
                                            )}
                                        </div>
                                    </div>

                                    <div className="space-y-4">
                                        {parameterSet.groups.map((group, groupIndex) => (
                                            <div key={groupIndex} className="border border-gray-200 rounded-lg p-4">
                                                <h5 className="text-md font-medium text-gray-900 mb-3">{group.name}</h5>
                                                {group.description && (
                                                    <p className="text-sm text-gray-600 mb-4">{group.description}</p>
                                                )}
                                                <div className="grid gap-4 md:grid-cols-2">
                                                    {group.parameters.map((param, paramIndex) => (
                                                        <div key={paramIndex} className="space-y-2">
                                                            <label className="block text-sm font-medium text-gray-700">
                                                                {param.name}
                                                                {param.required && <span className="text-red-500 ml-1">*</span>}
                                                            </label>
                                                            {param.description && (
                                                                <p className="text-xs text-gray-500">{param.description}</p>
                                                            )}
                                                            {param.type === 'boolean' ? (
                                                                <input
                                                                    type="checkbox"
                                                                    checked={param.value || false}
                                                                    onChange={(e) => updateParameterValue(groupIndex, paramIndex, e.target.checked)}
                                                                    className="rounded border-gray-300"
                                                                />
                                                            ) : param.type === 'number' ? (
                                                                <input
                                                                    type="number"
                                                                    value={param.value || ''}
                                                                    onChange={(e) => updateParameterValue(groupIndex, paramIndex, parseFloat(e.target.value) || 0)}
                                                                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
                                                                />
                                                            ) : (
                                                                <input
                                                                    type="text"
                                                                    value={param.value || ''}
                                                                    onChange={(e) => updateParameterValue(groupIndex, paramIndex, e.target.value)}
                                                                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
                                                                />
                                                            )}
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            ) : (
                                <div className="text-center py-8">
                                    <div className="text-gray-400 text-4xl mb-4">⚙️</div>
                                    <h4 className="text-lg font-medium text-gray-900 mb-2">Nenhum Parâmetro Configurado</h4>
                                    <p className="text-gray-600">
                                        Configure os parâmetros na página de Gerenciamento de Dados primeiro.
                                    </p>
                                </div>
                            )}
                        </div>

                        {/* Actions */}
                        <div className="flex justify-end gap-3 pt-4 border-t">
                            <button
                                type="button"
                                onClick={onClose}
                                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
                            >
                                Cancelar
                            </button>
                            <button
                                type="submit"
                                disabled={isLoading}
                                className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50"
                            >
                                {isLoading ? 'Executando...' : 'Executar Experimento'}
                            </button>
                        </div>
                    </form>
                </Dialog.Panel>
            </div>
        </Dialog>
    );
};

export default RunExperimentModal;
