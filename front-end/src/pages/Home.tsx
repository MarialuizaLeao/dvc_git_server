import { Link } from 'react-router-dom';

const Home = () => {
    return (
        <div className="max-w-7xl mx-auto">
            <div className="flex flex-col items-center mb-12">
                <img src="/flautim-logo.png" alt="Flautim" className="h-16 mb-8" />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <Link
                    to="/projects"
                    className="p-6 bg-white rounded-lg border border-gray-200 hover:border-blue-500 transition-colors"
                >
                    <h2 className="text-xl font-semibold mb-2">Projetos</h2>
                    <p className="text-gray-600">
                        Visualize e gerencie seus projetos de aprendizado de máquina
                    </p>
                </Link>

                <div className="p-6 bg-white rounded-lg border border-gray-200">
                    <h2 className="text-xl font-semibold mb-2">Atividade Recente</h2>
                    <p className="text-gray-600">
                        Nenhuma atividade recente
                    </p>
                </div>

                <div className="p-6 bg-white rounded-lg border border-gray-200">
                    <h2 className="text-xl font-semibold mb-2">Estatísticas Rápidas</h2>
                    <div className="space-y-2">
                        <p className="text-gray-600">Total de Projetos: 0</p>
                        <p className="text-gray-600">Experimentos Ativos: 0</p>
                        <p className="text-gray-600">Modelos Implantados: 0</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Home; 