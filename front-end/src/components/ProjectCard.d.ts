interface ProjectCardProps {
    userId: string;
    projectId: string;
}

import { ReactElement } from 'react';

declare function ProjectCard(props: ProjectCardProps): ReactElement;

export default ProjectCard;