import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import styled from 'styled-components';
import toast from 'react-hot-toast';
import {
  FiUpload,
  FiFile,
  FiX,
  FiCheck,
  FiAlertCircle,
  FiFileText,
} from 'react-icons/fi';

import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { apiEndpoints } from '../services/apiClient';

const UploadContainer = styled.div`
  max-width: 800px;
  margin: 0 auto;
`;

const UploadCard = styled(Card)`
  padding: 2rem;
  margin-bottom: 2rem;
`;

const DropzoneArea = styled.div<{ isDragActive: boolean; hasError: boolean }>`
  border: 2px dashed ${({ isDragActive, hasError, theme }) => 
    hasError ? theme.colors.red[300] : 
    isDragActive ? theme.colors.primary[400] : theme.colors.gray[300]};
  border-radius: 12px;
  padding: 3rem;
  text-align: center;
  background-color: ${({ isDragActive, theme }) => 
    isDragActive ? theme.colors.primary[50] : theme.colors.gray[50]};
  transition: all 0.2s ease;
  cursor: pointer;

  &:hover {
    border-color: ${({ theme }) => theme.colors.primary[400]};
    background-color: ${({ theme }) => theme.colors.primary[50]};
  }
`;

const UploadIcon = styled.div<{ isDragActive: boolean }>`
  display: flex;
  justify-content: center;
  margin-bottom: 1rem;
  
  svg {
    color: ${({ isDragActive, theme }) => 
      isDragActive ? theme.colors.primary[600] : theme.colors.gray[400]};
    transition: color 0.2s ease;
  }
`;

const UploadText = styled.div`
  margin-bottom: 0.5rem;
`;

const UploadTitle = styled.h3`
  color: ${({ theme }) => theme.colors.gray[900]};
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
`;

const UploadSubtitle = styled.p`
  color: ${({ theme }) => theme.colors.gray[600]};
  margin: 0 0 1rem 0;
`;

const FileTypes = styled.div`
  font-size: 0.875rem;
  color: ${({ theme }) => theme.colors.gray[500]};
`;

const FileListContainer = styled.div`
  margin-top: 2rem;
`;

const FileListTitle = styled.h4`
  color: ${({ theme }) => theme.colors.gray[900]};
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
`;

const FileList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
`;

const FileItem = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  background-color: ${({ theme }) => theme.colors.white};
  border: 1px solid ${({ theme }) => theme.colors.gray[200]};
  border-radius: 8px;
`;

const FileInfo = styled.div`
  display: flex;
  align-items: center;
  flex: 1;
`;

const FileIcon = styled.div<{ fileType: string }>`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background-color: ${({ fileType, theme }) => 
    fileType === 'pdf' ? theme.colors.red[100] : theme.colors.green[100]};
  margin-right: 0.75rem;

  svg {
    color: ${({ fileType, theme }) => 
      fileType === 'pdf' ? theme.colors.red[600] : theme.colors.green[600]};
  }
`;

const FileDetails = styled.div`
  flex: 1;
`;

const FileName = styled.div`
  font-weight: 500;
  color: ${({ theme }) => theme.colors.gray[900]};
  margin-bottom: 0.25rem;
`;

const FileSize = styled.div`
  font-size: 0.875rem;
  color: ${({ theme }) => theme.colors.gray[600]};
`;

const FileStatus = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-right: 0.75rem;
`;

const ProgressBar = styled.div`
  width: 100px;
  height: 4px;
  background-color: ${({ theme }) => theme.colors.gray[200]};
  border-radius: 2px;
  overflow: hidden;
`;

const ProgressFill = styled.div<{ progress: number }>`
  height: 100%;
  width: ${({ progress }) => progress}%;
  background-color: ${({ theme }) => theme.colors.primary[600]};
  transition: width 0.3s ease;
`;

const RemoveButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background-color: transparent;
  border-radius: 6px;
  color: ${({ theme }) => theme.colors.gray[400]};
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background-color: ${({ theme }) => theme.colors.red[50]};
    color: ${({ theme }) => theme.colors.red[600]};
  }
`;

const ActionsContainer = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1.5rem;
  border-top: 1px solid ${({ theme }) => theme.colors.gray[200]};
`;

const ErrorMessage = styled.div`
  color: ${({ theme }) => theme.colors.red[600]};
  font-size: 0.875rem;
  margin-top: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

interface FileWithProgress {
  file: File;
  progress: number;
  status: 'pending' | 'uploading' | 'completed' | 'error';
  error?: string;
  taskId?: string;
}

const Upload: React.FC = () => {
  const navigate = useNavigate();
  const [files, setFiles] = useState<FileWithProgress[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    setError(null);

    // Handle rejected files
    if (rejectedFiles.length > 0) {
      const errors = rejectedFiles.map(({ file, errors }) => 
        `${file.name}: ${errors.map((e: any) => e.message).join(', ')}`
      );
      setError(errors.join('\n'));
      return;
    }

    // Add accepted files
    const newFiles = acceptedFiles.map(file => ({
      file,
      progress: 0,
      status: 'pending' as const,
    }));

    setFiles(prev => [...prev, ...newFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    maxFiles: 10,
  });

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const clearAll = () => {
    setFiles([]);
    setError(null);
  };

  const uploadFiles = async () => {
    if (files.length === 0) return;

    setIsUploading(true);
    const updatedFiles = [...files];

    for (let i = 0; i < updatedFiles.length; i++) {
      if (updatedFiles[i].status !== 'pending') continue;

      try {
        updatedFiles[i].status = 'uploading';
        setFiles([...updatedFiles]);

        const result = await apiEndpoints.files.upload(
          updatedFiles[i].file,
          (progress: number) => {
            updatedFiles[i].progress = progress;
            setFiles([...updatedFiles]);
          }
        );

        updatedFiles[i].status = 'completed';
        updatedFiles[i].progress = 100;
        updatedFiles[i].taskId = result.taskId;
        setFiles([...updatedFiles]);

        toast.success(`${updatedFiles[i].file.name} uploaded successfully`);
      } catch (error: any) {
        updatedFiles[i].status = 'error';
        updatedFiles[i].error = error.message || 'Upload failed';
        setFiles([...updatedFiles]);

        toast.error(`Failed to upload ${updatedFiles[i].file.name}`);
      }
    }

    setIsUploading(false);

    // Navigate to results if all uploads completed
    const completedCount = updatedFiles.filter(f => f.status === 'completed').length;
    if (completedCount > 0) {
      setTimeout(() => {
        navigate('/results');
      }, 2000);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileType = (filename: string) => {
    const ext = filename.split('.').pop()?.toLowerCase();
    return ext === 'pdf' ? 'pdf' : 'excel';
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <FiCheck color="#10b981" size={16} />;
      case 'error':
        return <FiAlertCircle color="#ef4444" size={16} />;
      case 'uploading':
        return <LoadingSpinner size="small" />;
      default:
        return <FiFile color="#6b7280" size={16} />;
    }
  };

  return (
    <UploadContainer>
      <UploadCard>
        <DropzoneArea
          {...getRootProps()}
          isDragActive={isDragActive}
          hasError={!!error}
        >
          <input {...getInputProps()} />
          <UploadIcon isDragActive={isDragActive}>
            <FiUpload size={48} />
          </UploadIcon>
          <UploadText>
            <UploadTitle>
              {isDragActive ? 'Drop files here' : 'Upload Files'}
            </UploadTitle>
            <UploadSubtitle>
              Drag and drop your files here, or click to browse
            </UploadSubtitle>
            <FileTypes>
              Supported formats: PDF, Excel (.xlsx, .xls) • Max size: 10MB per file
            </FileTypes>
          </UploadText>
        </DropzoneArea>

        {error && (
          <ErrorMessage>
            <FiAlertCircle size={16} />
            {error}
          </ErrorMessage>
        )}
      </UploadCard>

      {files.length > 0 && (
        <Card>
          <FileListContainer>
            <FileListTitle>Files ({files.length})</FileListTitle>
            <FileList>
              {files.map((fileItem, index) => (
                <FileItem key={index}>
                  <FileInfo>
                    <FileIcon fileType={getFileType(fileItem.file.name)}>
                      <FiFileText size={20} />
                    </FileIcon>
                    <FileDetails>
                      <FileName>{fileItem.file.name}</FileName>
                      <FileSize>{formatFileSize(fileItem.file.size)}</FileSize>
                    </FileDetails>
                  </FileInfo>
                  
                  <FileStatus>
                    {fileItem.status === 'uploading' && (
                      <ProgressBar>
                        <ProgressFill progress={fileItem.progress} />
                      </ProgressBar>
                    )}
                    {getStatusIcon(fileItem.status)}
                  </FileStatus>

                  {fileItem.status === 'pending' && (
                    <RemoveButton onClick={() => removeFile(index)}>
                      <FiX size={16} />
                    </RemoveButton>
                  )}
                </FileItem>
              ))}
            </FileList>

            <ActionsContainer>
              <Button variant="ghost" onClick={clearAll} disabled={isUploading}>
                Clear All
              </Button>
              <div style={{ display: 'flex', gap: '0.75rem' }}>
                <Button 
                  variant="outline" 
                  onClick={() => navigate('/')}
                  disabled={isUploading}
                >
                  Cancel
                </Button>
                <Button 
                  onClick={uploadFiles}
                  disabled={isUploading || files.every(f => f.status !== 'pending')}
                  loading={isUploading}
                >
                  Upload Files
                </Button>
              </div>
            </ActionsContainer>
          </FileListContainer>
        </Card>
      )}
    </UploadContainer>
  );
};

export default Upload;
