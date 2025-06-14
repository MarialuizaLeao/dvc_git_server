import React, { useState } from 'react';

const API_BASE = 'http://localhost:8000';

interface CodeFile {
    _id: string;
    filename: string;
    file_path: string;
    file_type: string;
    size: number;
    status: string;
}

interface Tab {
    id: string;
    name: string;
}

const CodeUpload: React.FC = () => {
    // State
    const [activeTab, setActiveTab] = useState('single');
    const [uploading, setUploading] = useState(false);
    const [loading, setLoading] = useState(false);
    const [files, setFiles] = useState<CodeFile[]>([]);
    const [filesLoaded, setFilesLoaded] = useState(false);
    const [message, setMessage] = useState('');
    const [messageType, setMessageType] = useState<'success' | 'error'>('success');

    // Forms
    const [singleForm, setSingleForm] = useState({
        userId: '',
        projectId: '',
        filePath: '',
        fileType: 'python',
        description: '',
        file: null as File | null
    });

    const [multipleForm, setMultipleForm] = useState({
        userId: '',
        projectId: '',
        basePath: 'src',
        files: [] as File[]
    });

    const [apiForm, setApiForm] = useState({
        userId: '',
        projectId: '',
        content: '',
        fileName: '',
        filePath: '',
        fileType: 'python',
        description: ''
    });

    const [filesForm, setFilesForm] = useState({
        userId: '',
        projectId: ''
    });

    // Tabs
    const tabs: Tab[] = [
        { id: 'single', name: 'Single File Upload' },
        { id: 'multiple', name: 'Multiple Files Upload' },
        { id: 'api', name: 'API Upload' },
        { id: 'files', name: 'View Files' }
    ];

    // Methods
    const showMessage = (msg: string, type: 'success' | 'error' = 'success') => {
        setMessage(msg);
        setMessageType(type);
        setTimeout(() => {
            setMessage('');
        }, 5000);
    };

    const handleSingleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.files && event.target.files[0]) {
            setSingleForm(prev => ({ ...prev, file: event.target.files![0] }));
        }
    };

    const handleMultipleFilesSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.files) {
            setMultipleForm(prev => ({ ...prev, files: Array.from(event.target.files!) }));
        }
    };

    const uploadSingleFile = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!singleForm.file) {
            showMessage('Please select a file', 'error');
            return;
        }

        setUploading(true);
        const formData = new FormData();
        formData.append('file', singleForm.file);
        formData.append('file_path', singleForm.filePath);
        formData.append('file_type', singleForm.fileType);
        formData.append('description', singleForm.description);

        try {
            const response = await fetch(`${API_BASE}/${singleForm.userId}/${singleForm.projectId}/code/upload`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                showMessage(`File uploaded successfully! File ID: ${result.file_id}`);
            } else {
                showMessage(`Error: ${result.detail}`, 'error');
            }
        } catch (error) {
            showMessage(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error');
        } finally {
            setUploading(false);
        }
    };

    const uploadMultipleFiles = async (e: React.FormEvent) => {
        e.preventDefault();
        if (multipleForm.files.length === 0) {
            showMessage('Please select files', 'error');
            return;
        }

        setUploading(true);
        const formData = new FormData();

        for (const file of multipleForm.files) {
            formData.append('files', file);
        }
        formData.append('base_path', multipleForm.basePath);

        try {
            const response = await fetch(`${API_BASE}/${multipleForm.userId}/${multipleForm.projectId}/code/upload/multiple`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                showMessage(`Upload completed! ${result.successful_uploads} successful, ${result.failed_uploads} failed.`);
            } else {
                showMessage(`Error: ${result.detail}`, 'error');
            }
        } catch (error) {
            showMessage(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error');
        } finally {
            setUploading(false);
        }
    };

    const uploadViaApi = async (e: React.FormEvent) => {
        e.preventDefault();
        setUploading(true);

        const data = {
            filename: apiForm.fileName,
            file_path: apiForm.filePath,
            file_type: apiForm.fileType,
            description: apiForm.description,
            content: apiForm.content
        };

        try {
            const response = await fetch(`${API_BASE}/${apiForm.userId}/${apiForm.projectId}/code/file`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                showMessage(`File created successfully! File ID: ${result.file_id}`);
            } else {
                showMessage(`Error: ${result.detail}`, 'error');
            }
        } catch (error) {
            showMessage(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error');
        } finally {
            setUploading(false);
        }
    };

    const loadFiles = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setFilesLoaded(false);

        try {
            const response = await fetch(`${API_BASE}/${filesForm.userId}/${filesForm.projectId}/code/files`);
            const result = await response.json();

            if (response.ok) {
                setFiles(result.code_files);
                setFilesLoaded(true);
            } else {
                showMessage(`Error: ${result.detail}`, 'error');
            }
        } catch (error) {
            showMessage(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error');
        } finally {
            setLoading(false);
        }
    };

    const viewFileContent = async (file: CodeFile) => {
        try {
            const response = await fetch(`${API_BASE}/${filesForm.userId}/${filesForm.projectId}/code/file/${file._id}/content`);
            const result = await response.json();

            if (response.ok) {
                alert(`File: ${result.filename}\nPath: ${result.file_path}\n\nContent:\n${result.content}`);
            } else {
                showMessage(`Error: ${result.detail}`, 'error');
            }
        } catch (error) {
            showMessage(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error');
        }
    };

    const deleteFile = async (file: CodeFile) => {
        if (!confirm('Are you sure you want to delete this file?')) {
            return;
        }

        try {
            const response = await fetch(`${API_BASE}/${filesForm.userId}/${filesForm.projectId}/code/file/${file._id}`, {
                method: 'DELETE'
            });

            const result = await response.json();

            if (response.ok) {
                showMessage('File deleted successfully!');
                // Reload the files list
                const loadEvent = new Event('submit') as any;
                loadFiles(loadEvent);
            } else {
                showMessage(`Error: ${result.detail}`, 'error');
            }
        } catch (error) {
            showMessage(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error');
        }
    };

    return (
        <div className="code-upload-container max-w-4xl mx-auto p-6">
            <h2 className="text-3xl font-bold mb-6">Code Upload</h2>

            {/* Tabs */}
            <div className="tabs mb-6 flex border-b-2 border-gray-200">
                {tabs.map(tab => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`tab-button px-5 py-3 border border-gray-300 cursor-pointer rounded-t-lg mr-1 ${activeTab === tab.id
                                ? 'bg-white border-b-white'
                                : 'bg-gray-100 hover:bg-gray-200'
                            }`}
                    >
                        {tab.name}
                    </button>
                ))}
            </div>

            {/* Single File Upload */}
            {activeTab === 'single' && (
                <div className="tab-content">
                    <form onSubmit={uploadSingleFile} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium mb-2">User ID:</label>
                            <input
                                value={singleForm.userId}
                                onChange={(e) => setSingleForm(prev => ({ ...prev, userId: e.target.value }))}
                                type="text"
                                required
                                className="w-full p-2 border rounded"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-2">Project ID:</label>
                            <input
                                value={singleForm.projectId}
                                onChange={(e) => setSingleForm(prev => ({ ...prev, projectId: e.target.value }))}
                                type="text"
                                required
                                className="w-full p-2 border rounded"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-2">File Path (e.g., src/main.py):</label>
                            <input
                                value={singleForm.filePath}
                                onChange={(e) => setSingleForm(prev => ({ ...prev, filePath: e.target.value }))}
                                type="text"
                                required
                                className="w-full p-2 border rounded"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-2">File Type:</label>
                            <select
                                value={singleForm.fileType}
                                onChange={(e) => setSingleForm(prev => ({ ...prev, fileType: e.target.value }))}
                                className="w-full p-2 border rounded"
                            >
                                <option value="python">Python</option>
                                <option value="jupyter">Jupyter Notebook</option>
                                <option value="config">Configuration</option>
                                <option value="documentation">Documentation</option>
                                <option value="other">Other</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-2">Description (optional):</label>
                            <input
                                value={singleForm.description}
                                onChange={(e) => setSingleForm(prev => ({ ...prev, description: e.target.value }))}
                                type="text"
                                className="w-full p-2 border rounded"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-2">Select File:</label>
                            <input
                                onChange={handleSingleFileSelect}
                                type="file"
                                required
                                className="w-full p-2 border rounded"
                            />
                        </div>
                        <button
                            type="submit"
                            disabled={uploading}
                            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:bg-gray-400"
                        >
                            {uploading ? 'Uploading...' : 'Upload File'}
                        </button>
                    </form>
                </div>
            )}

            {/* Multiple Files Upload */}
            {activeTab === 'multiple' && (
                <div className="tab-content">
                    <form onSubmit={uploadMultipleFiles} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium mb-2">User ID:</label>
                            <input
                                value={multipleForm.userId}
                                onChange={(e) => setMultipleForm(prev => ({ ...prev, userId: e.target.value }))}
                                type="text"
                                required
                                className="w-full p-2 border rounded"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-2">Project ID:</label>
                            <input
                                value={multipleForm.projectId}
                                onChange={(e) => setMultipleForm(prev => ({ ...prev, projectId: e.target.value }))}
                                type="text"
                                required
                                className="w-full p-2 border rounded"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-2">Base Path (e.g., src):</label>
                            <input
                                value={multipleForm.basePath}
                                onChange={(e) => setMultipleForm(prev => ({ ...prev, basePath: e.target.value }))}
                                type="text"
                                className="w-full p-2 border rounded"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-2">Select Files:</label>
                            <input
                                onChange={handleMultipleFilesSelect}
                                type="file"
                                multiple
                                required
                                className="w-full p-2 border rounded"
                            />
                        </div>
                        <button
                            type="submit"
                            disabled={uploading}
                            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:bg-gray-400"
                        >
                            {uploading ? 'Uploading...' : 'Upload Files'}
                        </button>
                    </form>
                </div>
            )}

            {/* API Upload */}
            {activeTab === 'api' && (
                <div className="tab-content">
                    <form onSubmit={uploadViaApi} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium mb-2">User ID:</label>
                            <input
                                value={apiForm.userId}
                                onChange={(e) => setApiForm(prev => ({ ...prev, userId: e.target.value }))}
                                type="text"
                                required
                                className="w-full p-2 border rounded"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-2">Project ID:</label>
                            <input
                                value={apiForm.projectId}
                                onChange={(e) => setApiForm(prev => ({ ...prev, projectId: e.target.value }))}
                                type="text"
                                required
                                className="w-full p-2 border rounded"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-2">File Content:</label>
                            <textarea
                                value={apiForm.content}
                                onChange={(e) => setApiForm(prev => ({ ...prev, content: e.target.value }))}
                                placeholder="Paste your code here..."
                                className="w-full p-2 border rounded h-32"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-2">File Name:</label>
                            <input
                                value={apiForm.fileName}
                                onChange={(e) => setApiForm(prev => ({ ...prev, fileName: e.target.value }))}
                                type="text"
                                placeholder="main.py"
                                required
                                className="w-full p-2 border rounded"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-2">File Path:</label>
                            <input
                                value={apiForm.filePath}
                                onChange={(e) => setApiForm(prev => ({ ...prev, filePath: e.target.value }))}
                                type="text"
                                placeholder="src/main.py"
                                required
                                className="w-full p-2 border rounded"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-2">File Type:</label>
                            <select
                                value={apiForm.fileType}
                                onChange={(e) => setApiForm(prev => ({ ...prev, fileType: e.target.value }))}
                                className="w-full p-2 border rounded"
                            >
                                <option value="python">Python</option>
                                <option value="jupyter">Jupyter Notebook</option>
                                <option value="config">Configuration</option>
                                <option value="documentation">Documentation</option>
                                <option value="other">Other</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-2">Description (optional):</label>
                            <input
                                value={apiForm.description}
                                onChange={(e) => setApiForm(prev => ({ ...prev, description: e.target.value }))}
                                type="text"
                                className="w-full p-2 border rounded"
                            />
                        </div>
                        <button
                            type="submit"
                            disabled={uploading}
                            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:bg-gray-400"
                        >
                            {uploading ? 'Creating...' : 'Create File'}
                        </button>
                    </form>
                </div>
            )}

            {/* View Files */}
            {activeTab === 'files' && (
                <div className="tab-content">
                    <form onSubmit={loadFiles} className="space-y-4 mb-6">
                        <div>
                            <label className="block text-sm font-medium mb-2">User ID:</label>
                            <input
                                value={filesForm.userId}
                                onChange={(e) => setFilesForm(prev => ({ ...prev, userId: e.target.value }))}
                                type="text"
                                required
                                className="w-full p-2 border rounded"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-2">Project ID:</label>
                            <input
                                value={filesForm.projectId}
                                onChange={(e) => setFilesForm(prev => ({ ...prev, projectId: e.target.value }))}
                                type="text"
                                required
                                className="w-full p-2 border rounded"
                            />
                        </div>
                        <button
                            type="submit"
                            disabled={loading}
                            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:bg-gray-400"
                        >
                            {loading ? 'Loading...' : 'Load Files'}
                        </button>
                    </form>

                    {files.length > 0 && (
                        <div className="files-list max-h-96 overflow-y-auto">
                            {files.map(file => (
                                <div key={file._id} className="file-item border rounded p-4 mb-2 bg-gray-50 hover:bg-gray-100 transition-colors">
                                    <div className="flex justify-between items-start">
                                        <div className="flex-1">
                                            <h4 className="font-semibold">{file.filename}</h4>
                                            <p className="text-sm text-gray-600">Path: {file.file_path}</p>
                                            <p className="text-sm text-gray-600">Type: {file.file_type} | Size: {file.size} bytes</p>
                                            <p className="text-sm text-gray-600">Status: {file.status}</p>
                                        </div>
                                        <div className="flex gap-2">
                                            <button
                                                onClick={() => viewFileContent(file)}
                                                className="bg-green-500 text-white px-3 py-1 rounded text-sm hover:bg-green-600"
                                            >
                                                View
                                            </button>
                                            <button
                                                onClick={() => deleteFile(file)}
                                                className="bg-red-500 text-white px-3 py-1 rounded text-sm hover:bg-red-600"
                                            >
                                                Delete
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                    {filesLoaded && files.length === 0 && (
                        <div className="text-gray-500 text-center py-8">
                            No files found.
                        </div>
                    )}
                </div>
            )}

            {/* Messages */}
            {message && (
                <div className={`message mt-4 p-4 rounded ${messageType === 'success'
                        ? 'bg-green-100 text-green-800 border border-green-200'
                        : 'bg-red-100 text-red-800 border border-red-200'
                    }`}>
                    {message}
                </div>
            )}
        </div>
    );
};

export default CodeUpload; 