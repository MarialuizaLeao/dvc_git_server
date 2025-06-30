import { useState } from 'react';
import type { PipelineExecution } from '../types/api';

interface ExecutionOutputViewerProps {
    execution: PipelineExecution;
    isOpen: boolean;
    onClose: () => void;
}

export default function ExecutionOutputViewer({ execution, isOpen, onClose }: ExecutionOutputViewerProps) {
    const [activeTab, setActiveTab] = useState<'summary' | 'logs' | 'pipeline' | 'raw'>('summary');

    if (!isOpen) return null;

    // Debug log for summary
    if (execution.execution_output?.summary) {
        console.log('Summary:', execution.execution_output.summary);
        console.log('stages_skipped:', execution.execution_output.summary.stages_skipped, typeof execution.execution_output.summary.stages_skipped);
    }

    const getLogTypeColor = (type: string) => {
        switch (type) {
            case 'stage_start':
                return 'text-blue-600 bg-blue-50';
            case 'stage_skipped':
                return 'text-yellow-600 bg-yellow-50';
            case 'error':
                return 'text-red-600 bg-red-50';
            case 'pipeline_status':
                return 'text-green-600 bg-green-50';
            default:
                return 'text-gray-600 bg-gray-50';
        }
    };

    const getLogTypeIcon = (type: string) => {
        switch (type) {
            case 'stage_start':
                return '▶️';
            case 'stage_skipped':
                return '⏭️';
            case 'error':
                return '❌';
            case 'pipeline_status':
                return '✅';
            default:
                return 'ℹ️';
        }
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl h-3/4 flex flex-col">
                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b">
                    <div>
                        <h2 className="text-lg font-semibold text-gray-900">
                            Execution Output - {execution.execution_id}
                        </h2>
                        <p className="text-sm text-gray-500">
                            {new Date(execution.start_time).toLocaleString()}
                        </p>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-gray-600 transition-colors"
                    >
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                {/* Tabs */}
                <div className="flex border-b">
                    <button
                        onClick={() => setActiveTab('summary')}
                        className={`px-4 py-2 text-sm font-medium ${activeTab === 'summary'
                            ? 'text-blue-600 border-b-2 border-blue-600'
                            : 'text-gray-500 hover:text-gray-700'
                            }`}
                    >
                        Summary
                    </button>
                    <button
                        onClick={() => setActiveTab('logs')}
                        className={`px-4 py-2 text-sm font-medium ${activeTab === 'logs'
                            ? 'text-blue-600 border-b-2 border-blue-600'
                            : 'text-gray-500 hover:text-gray-700'
                            }`}
                    >
                        Structured Logs
                    </button>
                    <button
                        onClick={() => setActiveTab('pipeline')}
                        className={`px-4 py-2 text-sm font-medium ${activeTab === 'pipeline'
                            ? 'text-blue-600 border-b-2 border-blue-600'
                            : 'text-gray-500 hover:text-gray-700'
                            }`}
                    >
                        Pipeline Details
                    </button>
                    <button
                        onClick={() => setActiveTab('raw')}
                        className={`px-4 py-2 text-sm font-medium ${activeTab === 'raw'
                            ? 'text-blue-600 border-b-2 border-blue-600'
                            : 'text-gray-500 hover:text-gray-700'
                            }`}
                    >
                        Raw Output
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-auto p-4">
                    {activeTab === 'summary' && (
                        <div className="space-y-4">
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                <div className="bg-blue-50 p-4 rounded-lg">
                                    <div className="text-2xl font-bold text-blue-600">
                                        {execution.execution_output?.summary.stages_executed || 0}
                                    </div>
                                    <div className="text-sm text-blue-700">Stages Executed</div>
                                </div>
                                <div className="bg-yellow-50 p-4 rounded-lg">
                                    <div className="text-2xl font-bold text-yellow-600">
                                        {execution.execution_output?.summary.stages_skipped || 0}
                                    </div>
                                    <div className="text-sm text-yellow-700">Stages Skipped</div>
                                </div>
                                <div className="bg-red-50 p-4 rounded-lg">
                                    <div className="text-2xl font-bold text-red-600">
                                        {execution.execution_output?.summary.stages_failed || 0}
                                    </div>
                                    <div className="text-sm text-red-700">Stages Failed</div>
                                </div>
                                <div className="bg-green-50 p-4 rounded-lg">
                                    <div className="text-2xl font-bold text-green-600">
                                        {execution.execution_output?.pipeline_stats?.models_produced.length || execution.models_produced.length}
                                    </div>
                                    <div className="text-sm text-green-700">Models Produced</div>
                                </div>
                            </div>

                            <div className="bg-gray-50 p-4 rounded-lg">
                                <h3 className="font-medium text-gray-900 mb-2">Execution Details</h3>
                                <div className="grid grid-cols-2 gap-4 text-sm">
                                    <div>
                                        <span className="text-gray-500">Status:</span>
                                        <span className={`ml-2 px-2 py-1 rounded-full text-xs font-medium ${execution.status === 'completed' ? 'bg-green-100 text-green-800' :
                                            execution.status === 'failed' ? 'bg-red-100 text-red-800' :
                                                execution.status === 'running' ? 'bg-blue-100 text-blue-800' :
                                                    'bg-gray-100 text-gray-800'
                                            }`}>
                                            {execution.status}
                                        </span>
                                    </div>
                                    <div>
                                        <span className="text-gray-500">Duration:</span>
                                        <span className="ml-2 font-medium">
                                            {execution.duration ? `${execution.duration.toFixed(2)}s` : 'N/A'}
                                        </span>
                                    </div>
                                    <div>
                                        <span className="text-gray-500">Output Files:</span>
                                        <span className="ml-2 font-medium">{execution.output_files.length}</span>
                                    </div>
                                    <div>
                                        <span className="text-gray-500">Parameters Used:</span>
                                        <span className="ml-2 font-medium">{Object.keys(execution.parameters_used).length}</span>
                                    </div>
                                </div>
                            </div>

                            {execution.models_produced.length > 0 && (
                                <div className="bg-gray-50 p-4 rounded-lg">
                                    <h3 className="font-medium text-gray-900 mb-2">Models Produced</h3>
                                    <div className="space-y-1">
                                        {execution.models_produced.map((modelPath, index) => (
                                            <div key={index} className="text-sm text-gray-600 bg-white p-2 rounded border">
                                                {modelPath.split('/').pop()}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    )}

                    {activeTab === 'logs' && (
                        <div className="space-y-2">
                            {execution.execution_output?.structured_logs.map((log, index) => (
                                <div key={index} className={`p-3 rounded-lg border ${getLogTypeColor(log.type)}`}>
                                    <div className="flex items-start space-x-2">
                                        <span className="text-sm">{getLogTypeIcon(log.type)}</span>
                                        <div className="flex-1">
                                            <div className="text-sm font-medium">{log.message}</div>
                                            <div className="text-xs text-gray-500 mt-1">
                                                {new Date(log.timestamp).toLocaleString()}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                            {(!execution.execution_output?.structured_logs || execution.execution_output.structured_logs.length === 0) && (
                                <div className="text-center py-8 text-gray-500">
                                    No structured logs available
                                </div>
                            )}
                        </div>
                    )}

                    {activeTab === 'pipeline' && (
                        <div className="space-y-4">
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                <div className="bg-blue-50 p-4 rounded-lg">
                                    <div className="text-2xl font-bold text-blue-600">
                                        {execution.execution_output?.summary.stages_executed || 0}
                                    </div>
                                    <div className="text-sm text-blue-700">Stages Executed</div>
                                </div>
                                <div className="bg-yellow-50 p-4 rounded-lg">
                                    <div className="text-2xl font-bold text-yellow-600">
                                        {execution.execution_output?.summary.stages_skipped || 0}
                                    </div>
                                    <div className="text-sm text-yellow-700">Stages Skipped</div>
                                </div>
                                <div className="bg-red-50 p-4 rounded-lg">
                                    <div className="text-2xl font-bold text-red-600">
                                        {execution.execution_output?.summary.stages_failed || 0}
                                    </div>
                                    <div className="text-sm text-red-700">Stages Failed</div>
                                </div>
                                <div className="bg-green-50 p-4 rounded-lg">
                                    <div className="text-2xl font-bold text-green-600">
                                        {execution.execution_output?.pipeline_stats?.models_produced.length || execution.models_produced.length}
                                    </div>
                                    <div className="text-sm text-green-700">Models Produced</div>
                                </div>
                            </div>

                            {execution.execution_output?.pipeline_stats && (
                                <>
                                    {execution.execution_output.pipeline_stats.executed_stages.length > 0 && (
                                        <div className="bg-blue-50 p-4 rounded-lg">
                                            <h3 className="font-medium text-blue-900 mb-2">Executed Stages</h3>
                                            <div className="space-y-1">
                                                {execution.execution_output.pipeline_stats.executed_stages.map((stage, index) => (
                                                    <div key={index} className="text-sm text-blue-700 bg-blue-100 p-2 rounded">
                                                        {stage}
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {execution.execution_output.pipeline_stats.skipped_stages.length > 0 && (
                                        <div className="bg-yellow-50 p-4 rounded-lg">
                                            <h3 className="font-medium text-yellow-900 mb-2">Skipped Stages</h3>
                                            <div className="space-y-1">
                                                {execution.execution_output.pipeline_stats.skipped_stages.map((stage, index) => (
                                                    <div key={index} className="text-sm text-yellow-700 bg-yellow-100 p-2 rounded">
                                                        {stage}
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {execution.execution_output.pipeline_stats.failed_stages.length > 0 && (
                                        <div className="bg-red-50 p-4 rounded-lg">
                                            <h3 className="font-medium text-red-900 mb-2">Failed Stages</h3>
                                            <div className="space-y-1">
                                                {execution.execution_output.pipeline_stats.failed_stages.map((stage, index) => (
                                                    <div key={index} className="text-sm text-red-700 bg-red-100 p-2 rounded">
                                                        {stage}
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {execution.execution_output.pipeline_stats.output_files.length > 0 && (
                                        <div className="bg-gray-50 p-4 rounded-lg">
                                            <h3 className="font-medium text-gray-900 mb-2">Output Files</h3>
                                            <div className="space-y-1">
                                                {execution.execution_output.pipeline_stats.output_files.map((file, index) => (
                                                    <div key={index} className="text-sm text-gray-600 bg-white p-2 rounded border">
                                                        {file}
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {execution.execution_output.pipeline_stats.models_produced.length > 0 && (
                                        <div className="bg-green-50 p-4 rounded-lg">
                                            <h3 className="font-medium text-green-900 mb-2">Models Produced</h3>
                                            <div className="space-y-1">
                                                {execution.execution_output.pipeline_stats.models_produced.map((model, index) => (
                                                    <div key={index} className="text-sm text-green-700 bg-green-100 p-2 rounded">
                                                        {model}
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {Object.keys(execution.execution_output.pipeline_stats.parameters_used).length > 0 && (
                                        <div className="bg-purple-50 p-4 rounded-lg">
                                            <h3 className="font-medium text-purple-900 mb-2">Parameters Used</h3>
                                            <div className="space-y-1">
                                                {Object.entries(execution.execution_output.pipeline_stats.parameters_used).map(([key, value], index) => (
                                                    <div key={index} className="text-sm text-purple-700 bg-purple-100 p-2 rounded">
                                                        <span className="font-medium">{key}:</span> {String(value)}
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </>
                            )}
                        </div>
                    )}

                    {activeTab === 'raw' && (
                        <div className="space-y-4">
                            {execution.execution_output?.stdout && (
                                <div>
                                    <h3 className="font-medium text-gray-900 mb-2">Standard Output</h3>
                                    <pre className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto text-sm">
                                        {execution.execution_output.stdout}
                                    </pre>
                                </div>
                            )}

                            {execution.execution_output?.stderr && (
                                <div>
                                    <h3 className="font-medium text-gray-900 mb-2">Standard Error</h3>
                                    <pre className="bg-gray-900 text-red-400 p-4 rounded-lg overflow-x-auto text-sm">
                                        {execution.execution_output.stderr}
                                    </pre>
                                </div>
                            )}

                            {execution.logs.length > 0 && (
                                <div>
                                    <h3 className="font-medium text-gray-900 mb-2">Raw Logs</h3>
                                    <pre className="bg-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                                        {execution.logs.join('\n')}
                                    </pre>
                                </div>
                            )}

                            {!execution.execution_output?.stdout && !execution.execution_output?.stderr && execution.logs.length === 0 && (
                                <div className="text-center py-8 text-gray-500">
                                    No raw output available
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
} 