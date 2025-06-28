import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { dataApi } from '../services/api';
import type {
    CreateDataSourceRequest,
    UpdateDataSourceRequest,
    CreateRemoteRequest
} from '../types/api';

export const useDataManagement = (userId: string, projectId: string) => {
    const queryClient = useQueryClient();

    // Data Sources
    const getDataSources = () => useQuery({
        queryKey: ['data-sources', userId, projectId],
        queryFn: () => dataApi.getDataSources(userId, projectId),
    });

    const getDataSource = (sourceId: string) => useQuery({
        queryKey: ['data-source', userId, projectId, sourceId],
        queryFn: () => dataApi.getDataSource(userId, projectId, sourceId),
        enabled: !!sourceId,
    });

    const createDataSource = useMutation({
        mutationFn: (data: CreateDataSourceRequest) =>
            dataApi.createDataSource(userId, projectId, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['data-sources', userId, projectId] });
        },
    });

    const updateDataSource = useMutation({
        mutationFn: ({ sourceId, data }: { sourceId: string; data: UpdateDataSourceRequest }) =>
            dataApi.updateDataSource(userId, projectId, sourceId, data),
        onSuccess: (_, { sourceId }) => {
            queryClient.invalidateQueries({ queryKey: ['data-sources', userId, projectId] });
            queryClient.invalidateQueries({ queryKey: ['data-source', userId, projectId, sourceId] });
        },
    });

    const deleteDataSource = useMutation({
        mutationFn: (sourceId: string) =>
            dataApi.deleteDataSource(userId, projectId, sourceId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['data-sources', userId, projectId] });
        },
    });

    // Remote Storage
    const getRemoteStorages = () => useQuery({
        queryKey: ['remote-storages', userId, projectId],
        queryFn: () => dataApi.getRemoteStorages(userId, projectId),
    });

    const createRemoteStorage = useMutation({
        mutationFn: (data: CreateRemoteRequest) =>
            dataApi.createRemoteStorage(userId, projectId, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['remote-storages', userId, projectId] });
        },
    });

    const deleteRemoteStorage = useMutation({
        mutationFn: (remoteId: string) =>
            dataApi.deleteRemoteStorage(userId, projectId, remoteId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['remote-storages', userId, projectId] });
        },
    });

    // DVC Operations
    const trackData = useMutation({
        mutationFn: (files: string[]) =>
            dataApi.trackData(userId, projectId, files),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['dvc-status', userId, projectId] });
        },
    });

    const trackFiles = useMutation({
        mutationFn: (files: string[]) =>
            dataApi.trackFiles(userId, projectId, files),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['dvc-status', userId, projectId] });
        },
    });

    const getUrl = useMutation({
        mutationFn: ({ url, dest }: { url: string; dest: string }) =>
            dataApi.getUrl(userId, projectId, url, dest),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['dvc-status', userId, projectId] });
            queryClient.invalidateQueries({ queryKey: ['data-sources', userId, projectId] });
        },
    });

    const setRemote = useMutation({
        mutationFn: ({ remoteUrl, remoteName }: { remoteUrl: string; remoteName?: string }) =>
            dataApi.setRemote(userId, projectId, remoteUrl, remoteName),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['remote-storages', userId, projectId] });
        },
    });

    const pushData = useMutation({
        mutationFn: () =>
            dataApi.pushData(userId, projectId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['dvc-status', userId, projectId] });
        },
    });

    const pullData = useMutation({
        mutationFn: () =>
            dataApi.pullData(userId, projectId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['dvc-status', userId, projectId] });
        },
    });

    const getDvcStatus = () => useQuery({
        queryKey: ['dvc-status', userId, projectId],
        queryFn: () => dataApi.getDvcStatus(userId, projectId),
    });

    return {
        // Data Sources
        getDataSources,
        getDataSource,
        createDataSource,
        updateDataSource,
        deleteDataSource,

        // Remote Storage
        getRemoteStorages,
        createRemoteStorage,
        deleteRemoteStorage,

        // DVC Operations
        trackData,
        trackFiles,
        getUrl,
        setRemote,
        pushData,
        pullData,
        getDvcStatus,
    };
}; 