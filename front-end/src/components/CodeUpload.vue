<template>
  <div class="code-upload-container">
    <h2 class="text-2xl font-bold mb-6">Code Upload</h2>
    
    <!-- Tabs -->
    <div class="tabs mb-6">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        @click="activeTab = tab.id"
        :class="['tab-button', { active: activeTab === tab.id }]"
      >
        {{ tab.name }}
      </button>
    </div>

    <!-- Single File Upload -->
    <div v-if="activeTab === 'single'" class="tab-content">
      <form @submit.prevent="uploadSingleFile" class="space-y-4">
        <div>
          <label class="block text-sm font-medium mb-2">User ID:</label>
          <input 
            v-model="singleForm.userId" 
            type="text" 
            required 
            class="w-full p-2 border rounded"
          >
        </div>
        <div>
          <label class="block text-sm font-medium mb-2">Project ID:</label>
          <input 
            v-model="singleForm.projectId" 
            type="text" 
            required 
            class="w-full p-2 border rounded"
          >
        </div>
        <div>
          <label class="block text-sm font-medium mb-2">File Path (e.g., src/main.py):</label>
          <input 
            v-model="singleForm.filePath" 
            type="text" 
            required 
            class="w-full p-2 border rounded"
          >
        </div>
        <div>
          <label class="block text-sm font-medium mb-2">File Type:</label>
          <select v-model="singleForm.fileType" class="w-full p-2 border rounded">
            <option value="python">Python</option>
            <option value="jupyter">Jupyter Notebook</option>
            <option value="config">Configuration</option>
            <option value="documentation">Documentation</option>
            <option value="other">Other</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-2">Description (optional):</label>
          <input 
            v-model="singleForm.description" 
            type="text" 
            class="w-full p-2 border rounded"
          >
        </div>
        <div>
          <label class="block text-sm font-medium mb-2">Select File:</label>
          <input 
            @change="handleSingleFileSelect" 
            type="file" 
            required 
            class="w-full p-2 border rounded"
          >
        </div>
        <button 
          type="submit" 
          :disabled="uploading"
          class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:bg-gray-400"
        >
          {{ uploading ? 'Uploading...' : 'Upload File' }}
        </button>
      </form>
    </div>

    <!-- Multiple Files Upload -->
    <div v-if="activeTab === 'multiple'" class="tab-content">
      <form @submit.prevent="uploadMultipleFiles" class="space-y-4">
        <div>
          <label class="block text-sm font-medium mb-2">User ID:</label>
          <input 
            v-model="multipleForm.userId" 
            type="text" 
            required 
            class="w-full p-2 border rounded"
          >
        </div>
        <div>
          <label class="block text-sm font-medium mb-2">Project ID:</label>
          <input 
            v-model="multipleForm.projectId" 
            type="text" 
            required 
            class="w-full p-2 border rounded"
          >
        </div>
        <div>
          <label class="block text-sm font-medium mb-2">Base Path (e.g., src):</label>
          <input 
            v-model="multipleForm.basePath" 
            type="text" 
            class="w-full p-2 border rounded"
          >
        </div>
        <div>
          <label class="block text-sm font-medium mb-2">Select Files:</label>
          <input 
            @change="handleMultipleFilesSelect" 
            type="file" 
            multiple 
            required 
            class="w-full p-2 border rounded"
          >
        </div>
        <button 
          type="submit" 
          :disabled="uploading"
          class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:bg-gray-400"
        >
          {{ uploading ? 'Uploading...' : 'Upload Files' }}
        </button>
      </form>
    </div>

    <!-- API Upload -->
    <div v-if="activeTab === 'api'" class="tab-content">
      <form @submit.prevent="uploadViaApi" class="space-y-4">
        <div>
          <label class="block text-sm font-medium mb-2">User ID:</label>
          <input 
            v-model="apiForm.userId" 
            type="text" 
            required 
            class="w-full p-2 border rounded"
          >
        </div>
        <div>
          <label class="block text-sm font-medium mb-2">Project ID:</label>
          <input 
            v-model="apiForm.projectId" 
            type="text" 
            required 
            class="w-full p-2 border rounded"
          >
        </div>
        <div>
          <label class="block text-sm font-medium mb-2">File Content:</label>
          <textarea 
            v-model="apiForm.content" 
            placeholder="Paste your code here..."
            class="w-full p-2 border rounded h-32"
          ></textarea>
        </div>
        <div>
          <label class="block text-sm font-medium mb-2">File Name:</label>
          <input 
            v-model="apiForm.fileName" 
            type="text" 
            placeholder="main.py"
            required 
            class="w-full p-2 border rounded"
          >
        </div>
        <div>
          <label class="block text-sm font-medium mb-2">File Path:</label>
          <input 
            v-model="apiForm.filePath" 
            type="text" 
            placeholder="src/main.py"
            required 
            class="w-full p-2 border rounded"
          >
        </div>
        <div>
          <label class="block text-sm font-medium mb-2">File Type:</label>
          <select v-model="apiForm.fileType" class="w-full p-2 border rounded">
            <option value="python">Python</option>
            <option value="jupyter">Jupyter Notebook</option>
            <option value="config">Configuration</option>
            <option value="documentation">Documentation</option>
            <option value="other">Other</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-2">Description (optional):</label>
          <input 
            v-model="apiForm.description" 
            type="text" 
            class="w-full p-2 border rounded"
          >
        </div>
        <button 
          type="submit" 
          :disabled="uploading"
          class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:bg-gray-400"
        >
          {{ uploading ? 'Creating...' : 'Create File' }}
        </button>
      </form>
    </div>

    <!-- View Files -->
    <div v-if="activeTab === 'files'" class="tab-content">
      <form @submit.prevent="loadFiles" class="space-y-4 mb-6">
        <div>
          <label class="block text-sm font-medium mb-2">User ID:</label>
          <input 
            v-model="filesForm.userId" 
            type="text" 
            required 
            class="w-full p-2 border rounded"
          >
        </div>
        <div>
          <label class="block text-sm font-medium mb-2">Project ID:</label>
          <input 
            v-model="filesForm.projectId" 
            type="text" 
            required 
            class="w-full p-2 border rounded"
          >
        </div>
        <button 
          type="submit" 
          :disabled="loading"
          class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:bg-gray-400"
        >
          {{ loading ? 'Loading...' : 'Load Files' }}
        </button>
      </form>

      <div v-if="files.length > 0" class="files-list">
        <div v-for="file in files" :key="file._id" class="file-item border rounded p-4 mb-2">
          <div class="flex justify-between items-start">
            <div class="flex-1">
              <h4 class="font-semibold">{{ file.filename }}</h4>
              <p class="text-sm text-gray-600">Path: {{ file.file_path }}</p>
              <p class="text-sm text-gray-600">Type: {{ file.file_type }} | Size: {{ file.size }} bytes</p>
              <p class="text-sm text-gray-600">Status: {{ file.status }}</p>
            </div>
            <div class="flex gap-2">
              <button 
                @click="viewFileContent(file)"
                class="bg-green-500 text-white px-3 py-1 rounded text-sm hover:bg-green-600"
              >
                View
              </button>
              <button 
                @click="deleteFile(file)"
                class="bg-red-500 text-white px-3 py-1 rounded text-sm hover:bg-red-600"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>
      <div v-else-if="filesLoaded" class="text-gray-500 text-center py-8">
        No files found.
      </div>
    </div>

    <!-- Messages -->
    <div v-if="message" :class="['message', messageType]" class="mt-4 p-4 rounded">
      {{ message }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

const API_BASE = 'http://localhost:8000'

// State
const activeTab = ref('single')
const uploading = ref(false)
const loading = ref(false)
const files = ref([])
const filesLoaded = ref(false)
const message = ref('')
const messageType = ref('success')

// Forms
const singleForm = reactive({
  userId: '',
  projectId: '',
  filePath: '',
  fileType: 'python',
  description: '',
  file: null as File | null
})

const multipleForm = reactive({
  userId: '',
  projectId: '',
  basePath: 'src',
  files: [] as File[]
})

const apiForm = reactive({
  userId: '',
  projectId: '',
  content: '',
  fileName: '',
  filePath: '',
  fileType: 'python',
  description: ''
})

const filesForm = reactive({
  userId: '',
  projectId: ''
})

// Tabs
const tabs = [
  { id: 'single', name: 'Single File Upload' },
  { id: 'multiple', name: 'Multiple Files Upload' },
  { id: 'api', name: 'API Upload' },
  { id: 'files', name: 'View Files' }
]

// Methods
function showMessage(msg: string, type: 'success' | 'error' = 'success') {
  message.value = msg
  messageType.value = type
  setTimeout(() => {
    message.value = ''
  }, 5000)
}

function handleSingleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    singleForm.file = target.files[0]
  }
}

function handleMultipleFilesSelect(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files) {
    multipleForm.files = Array.from(target.files)
  }
}

async function uploadSingleFile() {
  if (!singleForm.file) {
    showMessage('Please select a file', 'error')
    return
  }

  uploading.value = true
  const formData = new FormData()
  formData.append('file', singleForm.file)
  formData.append('file_path', singleForm.filePath)
  formData.append('file_type', singleForm.fileType)
  formData.append('description', singleForm.description)

  try {
    const response = await fetch(`${API_BASE}/${singleForm.userId}/${singleForm.projectId}/code/upload`, {
      method: 'POST',
      body: formData
    })

    const result = await response.json()

    if (response.ok) {
      showMessage(`File uploaded successfully! File ID: ${result.file_id}`)
    } else {
      showMessage(`Error: ${result.detail}`, 'error')
    }
  } catch (error) {
    showMessage(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error')
  } finally {
    uploading.value = false
  }
}

async function uploadMultipleFiles() {
  if (multipleForm.files.length === 0) {
    showMessage('Please select files', 'error')
    return
  }

  uploading.value = true
  const formData = new FormData()
  
  for (const file of multipleForm.files) {
    formData.append('files', file)
  }
  formData.append('base_path', multipleForm.basePath)

  try {
    const response = await fetch(`${API_BASE}/${multipleForm.userId}/${multipleForm.projectId}/code/upload/multiple`, {
      method: 'POST',
      body: formData
    })

    const result = await response.json()

    if (response.ok) {
      showMessage(`Upload completed! ${result.successful_uploads} successful, ${result.failed_uploads} failed.`)
    } else {
      showMessage(`Error: ${result.detail}`, 'error')
    }
  } catch (error) {
    showMessage(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error')
  } finally {
    uploading.value = false
  }
}

async function uploadViaApi() {
  uploading.value = true

  const data = {
    filename: apiForm.fileName,
    file_path: apiForm.filePath,
    file_type: apiForm.fileType,
    description: apiForm.description,
    content: apiForm.content
  }

  try {
    const response = await fetch(`${API_BASE}/${apiForm.userId}/${apiForm.projectId}/code/file`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })

    const result = await response.json()

    if (response.ok) {
      showMessage(`File created successfully! File ID: ${result.file_id}`)
    } else {
      showMessage(`Error: ${result.detail}`, 'error')
    }
  } catch (error) {
    showMessage(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error')
  } finally {
    uploading.value = false
  }
}

async function loadFiles() {
  loading.value = true
  filesLoaded.value = false

  try {
    const response = await fetch(`${API_BASE}/${filesForm.userId}/${filesForm.projectId}/code/files`)
    const result = await response.json()

    if (response.ok) {
      files.value = result.code_files
      filesLoaded.value = true
    } else {
      showMessage(`Error: ${result.detail}`, 'error')
    }
  } catch (error) {
    showMessage(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error')
  } finally {
    loading.value = false
  }
}

async function viewFileContent(file: any) {
  try {
    const response = await fetch(`${API_BASE}/${filesForm.userId}/${filesForm.projectId}/code/file/${file._id}/content`)
    const result = await response.json()

    if (response.ok) {
      alert(`File: ${result.filename}\nPath: ${result.file_path}\n\nContent:\n${result.content}`)
    } else {
      showMessage(`Error: ${result.detail}`, 'error')
    }
  } catch (error) {
    showMessage(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error')
  }
}

async function deleteFile(file: any) {
  if (!confirm('Are you sure you want to delete this file?')) {
    return
  }

  try {
    const response = await fetch(`${API_BASE}/${filesForm.userId}/${filesForm.projectId}/code/file/${file._id}`, {
      method: 'DELETE'
    })

    const result = await response.json()

    if (response.ok) {
      showMessage('File deleted successfully!')
      loadFiles() // Reload the files list
    } else {
      showMessage(`Error: ${result.detail}`, 'error')
    }
  } catch (error) {
    showMessage(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error')
  }
}
</script>

<style scoped>
.code-upload-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.tabs {
  display: flex;
  border-bottom: 2px solid #e5e7eb;
}

.tab-button {
  padding: 10px 20px;
  background-color: #f9fafb;
  border: 1px solid #e5e7eb;
  cursor: pointer;
  border-radius: 5px 5px 0 0;
  margin-right: 5px;
}

.tab-button.active {
  background-color: white;
  border-bottom: 1px solid white;
}

.tab-content {
  padding: 20px 0;
}

.message {
  margin-top: 16px;
  padding: 16px;
  border-radius: 4px;
}

.message.success {
  background-color: #d1fae5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.message.error {
  background-color: #fee2e2;
  color: #991b1b;
  border: 1px solid #fca5a5;
}

.files-list {
  max-height: 400px;
  overflow-y: auto;
}

.file-item {
  background-color: #f9fafb;
  transition: background-color 0.2s;
}

.file-item:hover {
  background-color: #f3f4f6;
}
</style> 