import { useParams } from 'react-router-dom';
import { useProjects } from '../hooks/useProjects';
import { CURRENT_USER } from '../constants/user';

export default function Project() {
    const { id } = useParams();
    const { data: project, isLoading, error } = useProjects(CURRENT_USER.id).getProject(id || '');

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-center py-12">
                <h2 className="text-2xl font-semibold text-red-600">Erro ao carregar o projeto</h2>
                <p className="text-gray-700 mt-2">{error instanceof Error ? error.message : 'Ocorreu um erro ao carregar o projeto'}</p>
            </div>
        );
    }

    if (!project) {
        return (
            <div className="text-center py-12">
                <h2 className="text-2xl font-semibold text-gray-700">Projeto não encontrado</h2>
                <p className="text-gray-500 mt-2">O projeto que você procura não existe ou foi excluído.</p>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-white py-10 px-2 md:px-0">
            <div className="max-w-5xl mx-auto space-y-8">
                {/* Header Card */}
                <div className="bg-white border rounded-xl p-8 shadow-sm flex flex-col md:flex-row md:items-center md:justify-between">
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900 mb-1">{project.project_name}</h1>
                        <p className="text-gray-600 mb-1">{project.description || 'Sem descrição'}</p>
                        {project.created_at && (
                            <p className="text-sm text-gray-400">Criado em {new Date(project.created_at).toLocaleDateString()}</p>
                        )}
                    </div>
                    <div className="flex space-x-3 mt-4 md:mt-0">
                        <button className="px-4 py-2 bg-white border border-blue-500 text-blue-500 rounded hover:bg-blue-50">Compartilhar</button>
                        <button className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">Editar Projeto</button>
                    </div>
                </div>

                {/* Top Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {/* Models Card */}
                    <div className="bg-white border rounded-xl p-8 flex flex-col items-center text-center">
                        <h2 className="text-lg font-semibold mb-2">Modelos</h2>
                        <div className="text-3xl font-bold mb-1">{project.models_count || 0}</div>
                        <div className="text-sm text-gray-500 mb-2">Total de modelos</div>
                        <div className="text-xs text-green-600">Melhor acurácia: 98.5%</div>
                        <div className="text-xs text-blue-600">Último: 97.2%</div>
                    </div>
                    {/* Experiments Card */}
                    <div className="bg-white border rounded-xl p-8 flex flex-col items-center text-center">
                        <h2 className="text-lg font-semibold mb-2">Experimentos</h2>
                        <div className="text-3xl font-bold mb-1">{project.experiments_count || 0}</div>
                        <div className="text-sm text-gray-500 mb-2">Total de experimentos</div>
                        <div className="text-xs text-gray-600">Tempo médio de treinamento</div>
                        <div className="text-xs text-blue-600">45 minutos</div>
                    </div>
                    {/* Latest Activity Card */}
                    <div className="bg-white border rounded-xl p-8 flex flex-col">
                        <h2 className="text-lg font-semibold mb-2">Últimas atividades</h2>
                        <ul className="text-sm text-gray-700 space-y-2">
                            <li>Novo experimento iniciado: CNN com aumento de dados<br /><span className="text-xs text-gray-400">15/03/2024, 11:25:00</span></li>
                            <li>Modelo v2 atingiu 98,5% de acurácia<br /><span className="text-xs text-gray-400">15/03/2024, 09:15:00</span></li>
                            <li>Conjunto de dados de treinamento atualizado com novas amostras<br /><span className="text-xs text-gray-400">15/03/2024, 07:45:00</span></li>
                        </ul>
                    </div>
                </div>

                {/* Bottom Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Project Configuration Card */}
                    <div className="bg-white border rounded-xl p-8">
                        <div className="flex justify-between items-center mb-4">
                            <h2 className="text-lg font-semibold">Configuração do projeto</h2>
                            <button className="text-blue-500 hover:underline text-sm">Editar</button>
                        </div>
                        <div className="text-sm text-gray-700 space-y-1">
                            <div><span className="font-medium">Tipo de projeto</span><br />{project.project_type}</div>
                            <div className="mt-2"><span className="font-medium">Framework</span><br />{project.framework}</div>
                            <div className="mt-2"><span className="font-medium">Versão do Python</span><br />{project.python_version}</div>
                            <div className="mt-2"><span className="font-medium">Dependências principais</span></div>
                            <ul className="ml-0 mt-1">
                                {project.dependencies && project.dependencies.map((dep: string, idx: number) => (
                                    <li key={idx} className="font-mono text-xs text-gray-600 bg-gray-50 rounded px-2 py-1 mb-1 w-fit">{dep}</li>
                                ))}
                            </ul>
                        </div>
                    </div>
                    {/* Resources Card */}
                    <div className="bg-white border rounded-xl p-8">
                        <div className="flex justify-between items-center mb-4">
                            <h2 className="text-lg font-semibold">Recursos</h2>
                            <button className="text-blue-500 hover:underline text-sm">Gerenciar</button>
                        </div>
                        <div className="text-sm text-gray-700 space-y-2">
                            <div><span className="font-medium">Armazenamento utilizado</span><br />2.5 GB</div>
                            <div><span className="font-medium">Horas de computação</span><br />10h</div>
                            <div><span className="font-medium">Uso de GPU</span><br />5h<br />NVIDIA T4</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
} 