import { useState } from 'react';
import { Link } from 'react-router-dom';

interface Project {
    id: string;
    name: string;
    description: string;
    created_at: string;
    experiments_count: number;
}

const Projects = () => {
    const [project] = useState<Project>({
        id: '1',
        name: 'MNIST',
        description: 'Handwritten digit recognition project',
        created_at: '2024-06-03',
        experiments_count: 5,
    });

    return (
        <div>
            <div className="mb-6">
                <h2 className="text-xl mb-4">{project.name}</h2>
                <p>{project.description}</p>
                <div className="mt-2 text-sm text-gray-600">
                    <p>Criado em: {project.created_at}</p>
                    <p>{project.experiments_count} experimentos</p>
                </div>
            </div>
        </div>
    );
};

export default Projects; 