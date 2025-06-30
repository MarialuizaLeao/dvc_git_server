import { useState } from 'react';
import type { CreateRemoteRequest } from '../types/api';

interface RemoteStorageModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSubmit: (data: CreateRemoteRequest) => void;
    error?: string;
    isLoading?: boolean;
}

export default function RemoteStorageModal({
    isOpen,
    onClose,
    onSubmit,
    error,
    isLoading = false
}: RemoteStorageModalProps) {
    const [formData, setFormData] = useState<CreateRemoteRequest>({
        name: '',
        url: '',
        type: 's3',
        is_default: false
    });

    const [validationError, setValidationError] = useState<string>('');

    const validateName = (name: string): string => {
        if (!name.trim()) {
            return 'Remote name is required';
        }
        if (name.length > 50) {
            return 'Remote name must be 50 characters or less';
        }
        if (!/^[a-zA-Z0-9_-]+$/.test(name)) {
            return 'Remote name can only contain letters, numbers, hyphens, and underscores';
        }
        return '';
    };

    const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const newName = e.target.value;
        setFormData({ ...formData, name: newName });
        setValidationError(validateName(newName));
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        const nameError = validateName(formData.name);
        if (nameError) {
            setValidationError(nameError);
            return;
        }
        setValidationError('');
        onSubmit(formData);
    };

    const getUrlPlaceholder = () => {
        switch (formData.type) {
            case 's3':
                return 's3://bucket-name/path/';
            case 'gcs':
                return 'gs://bucket-name/path/';
            case 'azure':
                return 'azure://container-name/path/';
            case 'ssh':
                return 'ssh://user@host:/path/';
            case 'local':
                return '/path/to/local/storage/';
            default:
                return '';
        }
    };

    const getTypeDescription = () => {
        switch (formData.type) {
            case 's3':
                return 'Amazon S3 or S3-compatible storage (MinIO, etc.)';
            case 'gcs':
                return 'Google Cloud Storage';
            case 'azure':
                return 'Microsoft Azure Blob Storage';
            case 'ssh':
                return 'SSH/SFTP remote storage';
            case 'local':
                return 'Local file system storage';
            default:
                return '';
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-2xl">
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-2xl font-bold">Configure Remote Storage</h2>
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
                            Remote Name *
                        </label>
                        <input
                            type="text"
                            value={formData.name}
                            onChange={handleNameChange}
                            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${validationError ? 'border-red-500' : 'border-gray-300'
                                }`}
                            placeholder="e.g., my-s3-storage, gcs-backup, etc."
                            required
                        />
                        {validationError && (
                            <p className="text-red-600 text-sm mt-1">{validationError}</p>
                        )}
                        <p className="text-sm text-gray-500 mt-1">
                            Use only letters, numbers, hyphens, and underscores (max 50 characters)
                        </p>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Storage Type *
                        </label>
                        <select
                            value={formData.type}
                            onChange={(e) => setFormData({ ...formData, type: e.target.value as any })}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            required
                        >
                            <option value="s3">Amazon S3 / S3-Compatible</option>
                            <option value="gcs">Google Cloud Storage</option>
                            <option value="azure">Azure Blob Storage</option>
                            <option value="ssh">SSH/SFTP</option>
                            <option value="local">Local Storage</option>
                        </select>
                        <p className="text-sm text-gray-500 mt-1">{getTypeDescription()}</p>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Storage URL *
                        </label>
                        <input
                            type="text"
                            value={formData.url}
                            onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder={getUrlPlaceholder()}
                            required
                        />
                        <p className="text-sm text-gray-500 mt-1">
                            The URL or path to your storage location
                        </p>
                    </div>

                    <div className="flex items-center">
                        <input
                            type="checkbox"
                            id="is_default"
                            checked={formData.is_default}
                            onChange={(e) => setFormData({ ...formData, is_default: e.target.checked })}
                            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <label htmlFor="is_default" className="ml-2 block text-sm text-gray-900">
                            Set as default remote storage
                        </label>
                    </div>

                    <div className="bg-blue-50 p-4 rounded-lg">
                        <h4 className="text-sm font-medium text-blue-900 mb-2">Storage Configuration Tips:</h4>
                        <ul className="text-sm text-blue-800 space-y-1">
                            <li>• <strong>S3:</strong> Use format: <code>s3://bucket-name/path/</code></li>
                            <li>• <strong>GCS:</strong> Use format: <code>gs://bucket-name/path/</code></li>
                            <li>• <strong>Azure:</strong> Use format: <code>azure://container-name/path/</code></li>
                            <li>• <strong>SSH:</strong> Use format: <code>ssh://user@host:/path/</code></li>
                            <li>• <strong>Local:</strong> Use format: <code>/absolute/path/to/storage/</code></li>
                        </ul>
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
                            disabled={isLoading || !!validationError}
                            className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {isLoading ? 'Configuring...' : 'Configure Storage'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
} 