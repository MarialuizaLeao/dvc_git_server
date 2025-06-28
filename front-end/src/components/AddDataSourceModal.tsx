import { useState } from 'react';
import type { CreateDataSourceRequest } from '../types/api';

interface AddDataSourceModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSubmit: (data: CreateDataSourceRequest) => void;
    error?: string;
    isLoading?: boolean;
}

export default function AddDataSourceModal({
    isOpen,
    onClose,
    onSubmit,
    error,
    isLoading = false
}: AddDataSourceModalProps) {
    const [formData, setFormData] = useState<CreateDataSourceRequest>({
        name: '',
        description: '',
        type: 'url',
        source: '',
        destination: ''
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSubmit(formData);
    };

    const getSourcePlaceholder = () => {
        switch (formData.type) {
            case 'url':
                return 'https://example.com/dataset.zip';
            case 'local':
                return '/path/to/local/dataset';
            case 'remote':
                return 's3://bucket/dataset/ or gs://bucket/dataset/';
            default:
                return '';
        }
    };

    const getSourceLabel = () => {
        switch (formData.type) {
            case 'url':
                return 'Data URL';
            case 'local':
                return 'Local Path';
            case 'remote':
                return 'Remote Storage Path';
            default:
                return 'Source';
        }
    };

    const getTypeDescription = () => {
        switch (formData.type) {
            case 'url':
                return 'Download data from a public URL (HTTP/HTTPS)';
            case 'local':
                return 'Use data from a local file or directory';
            case 'remote':
                return 'Use data from cloud storage (S3, GCS, Azure, etc.)';
            default:
                return '';
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-2xl">
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-2xl font-bold">Add Data Source</h2>
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
                            Data Source Name *
                        </label>
                        <input
                            type="text"
                            value={formData.name}
                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="e.g., MNIST Dataset, Customer Data, etc."
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
                            placeholder="Describe what this data source contains..."
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Data Source Type *
                        </label>
                        <select
                            value={formData.type}
                            onChange={(e) => setFormData({ ...formData, type: e.target.value as any })}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            required
                        >
                            <option value="url">URL (Download from web)</option>
                            <option value="local">Local File/Directory</option>
                            <option value="remote">Remote Storage (S3, GCS, etc.)</option>
                        </select>
                        <p className="text-sm text-gray-500 mt-1">{getTypeDescription()}</p>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            {getSourceLabel()} *
                        </label>
                        <input
                            type="text"
                            value={formData.source}
                            onChange={(e) => setFormData({ ...formData, source: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder={getSourcePlaceholder()}
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Destination Path *
                        </label>
                        <input
                            type="text"
                            value={formData.destination}
                            onChange={(e) => setFormData({ ...formData, destination: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="data/dataset or data/raw"
                            required
                        />
                        <p className="text-sm text-gray-500 mt-1">
                            Where to store the data in your project (relative to project root)
                        </p>
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
                            disabled={isLoading}
                            className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {isLoading ? 'Adding...' : 'Add Data Source'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
} 