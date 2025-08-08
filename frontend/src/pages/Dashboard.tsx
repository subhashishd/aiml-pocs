import React from 'react';
import { useQuery } from 'react-query';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import {
  FiUpload,
  FiFileText,
  FiCheckCircle,
  FiAlertCircle,
  FiClock,
  FiActivity,
  FiTrendingUp,
  FiArrowRight,
} from 'react-icons/fi';

import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { api } from '../services/apiClient';

const DashboardContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
`;

const WelcomeSection = styled.div`
  margin-bottom: 2rem;
`;

const WelcomeTitle = styled.h1`
  color: ${({ theme }) => theme.colors.gray[900]};
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
`;

const WelcomeSubtitle = styled.p`
  color: ${({ theme }) => theme.colors.gray[600]};
  font-size: 1.1rem;
  margin: 0;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
`;

const StatCard = styled(Card)`
  display: flex;
  align-items: center;
  padding: 1.5rem;
`;

const StatIcon = styled.div<{ color: string }>`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background-color: ${({ color }) => color};
  margin-right: 1rem;

  svg {
    color: white;
  }
`;

const StatContent = styled.div`
  flex: 1;
`;

const StatValue = styled.div`
  font-size: 2rem;
  font-weight: 700;
  color: ${({ theme }) => theme.colors.gray[900]};
  line-height: 1;
  margin-bottom: 0.25rem;
`;

const StatLabel = styled.div`
  font-size: 0.875rem;
  color: ${({ theme }) => theme.colors.gray[600]};
`;

const ContentGrid = styled.div`
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;

  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
`;

const RecentTasksSection = styled.div``;

const QuickActionsSection = styled.div``;

const SectionHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
`;

const SectionTitle = styled.h2`
  color: ${({ theme }) => theme.colors.gray[900]};
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
`;

const ViewAllLink = styled(Link)`
  color: ${({ theme }) => theme.colors.primary[600]};
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.25rem;

  &:hover {
    color: ${({ theme }) => theme.colors.primary[700]};
  }
`;

const TaskList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
`;

const TaskItem = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  background-color: ${({ theme }) => theme.colors.white};
  border: 1px solid ${({ theme }) => theme.colors.gray[200]};
  border-radius: 8px;
  transition: all 0.2s ease;

  &:hover {
    border-color: ${({ theme }) => theme.colors.gray[300]};
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }
`;

const TaskInfo = styled.div`
  flex: 1;
`;

const TaskTitle = styled.div`
  font-weight: 500;
  color: ${({ theme }) => theme.colors.gray[900]};
  margin-bottom: 0.25rem;
`;

const TaskMeta = styled.div`
  font-size: 0.875rem;
  color: ${({ theme }) => theme.colors.gray[600]};
`;

const TaskActions = styled.div`
  display: flex;
  align-items: center;
  gap: 0.75rem;
`;

const QuickActionGrid = styled.div`
  display: grid;
  gap: 1rem;
`;

const QuickActionCard = styled(Card)`
  padding: 1.5rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid transparent;

  &:hover {
    border-color: ${({ theme }) => theme.colors.primary[200]};
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
`;

const QuickActionIcon = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: 16px;
  background-color: ${({ theme }) => theme.colors.primary[100]};
  margin: 0 auto 1rem;

  svg {
    color: ${({ theme }) => theme.colors.primary[600]};
  }
`;

const QuickActionTitle = styled.h3`
  color: ${({ theme }) => theme.colors.gray[900]};
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
`;

const QuickActionDescription = styled.p`
  color: ${({ theme }) => theme.colors.gray[600]};
  font-size: 0.875rem;
  margin: 0;
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 2rem;
  color: ${({ theme }) => theme.colors.gray[500]};
`;

interface DashboardStats {
  totalTasks: number;
  completedTasks: number;
  failedTasks: number;
  pendingTasks: number;
}

interface Task {
  id: string;
  filename: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  created_at: string;
  file_type: 'pdf' | 'excel';
}

const getStatusBadgeProps = (status: string) => {
  switch (status) {
    case 'completed':
      return { variant: 'success' as const, icon: FiCheckCircle };
    case 'failed':
      return { variant: 'error' as const, icon: FiAlertCircle };
    case 'processing':
      return { variant: 'warning' as const, icon: FiClock };
    default:
      return { variant: 'default' as const, icon: FiClock };
  }
};

const Dashboard: React.FC = () => {
  const { data: stats, isLoading: statsLoading } = useQuery<DashboardStats>(
    'dashboard-stats',
    () => api.get('/dashboard/stats'),
    {
      refetchInterval: 30000, // Refresh every 30 seconds
    }
  );

  const { data: recentTasks, isLoading: tasksLoading } = useQuery<Task[]>(
    'recent-tasks',
    () => api.get('/tasks/recent?limit=5'),
    {
      refetchInterval: 30000,
    }
  );

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <DashboardContainer>
      <WelcomeSection>
        <WelcomeTitle>Welcome to ValidatorAI</WelcomeTitle>
        <WelcomeSubtitle>
          Upload and validate your PDF and Excel files with AI-powered intelligence
        </WelcomeSubtitle>
      </WelcomeSection>

      <StatsGrid>
        <StatCard>
          <StatIcon color="#3b82f6">
            <FiFileText size={24} />
          </StatIcon>
          <StatContent>
            <StatValue>{statsLoading ? '--' : stats?.totalTasks || 0}</StatValue>
            <StatLabel>Total Tasks</StatLabel>
          </StatContent>
        </StatCard>

        <StatCard>
          <StatIcon color="#10b981">
            <FiCheckCircle size={24} />
          </StatIcon>
          <StatContent>
            <StatValue>{statsLoading ? '--' : stats?.completedTasks || 0}</StatValue>
            <StatLabel>Completed</StatLabel>
          </StatContent>
        </StatCard>

        <StatCard>
          <StatIcon color="#f59e0b">
            <FiClock size={24} />
          </StatIcon>
          <StatContent>
            <StatValue>{statsLoading ? '--' : stats?.pendingTasks || 0}</StatValue>
            <StatLabel>In Progress</StatLabel>
          </StatContent>
        </StatCard>

        <StatCard>
          <StatIcon color="#ef4444">
            <FiAlertCircle size={24} />
          </StatIcon>
          <StatContent>
            <StatValue>{statsLoading ? '--' : stats?.failedTasks || 0}</StatValue>
            <StatLabel>Failed</StatLabel>
          </StatContent>
        </StatCard>
      </StatsGrid>

      <ContentGrid>
        <RecentTasksSection>
          <Card>
            <SectionHeader>
              <SectionTitle>Recent Tasks</SectionTitle>
              <ViewAllLink to="/results">
                View All <FiArrowRight size={14} />
              </ViewAllLink>
            </SectionHeader>

            {tasksLoading ? (
              <LoadingSpinner />
            ) : recentTasks && recentTasks.length > 0 ? (
              <TaskList>
                {recentTasks.map((task) => {
                  const { variant, icon: StatusIcon } = getStatusBadgeProps(task.status);
                  return (
                    <TaskItem key={task.id}>
                      <TaskInfo>
                        <TaskTitle>{task.filename}</TaskTitle>
                        <TaskMeta>{formatDate(task.created_at)}</TaskMeta>
                      </TaskInfo>
                      <TaskActions>
                        <Badge variant={variant}>
                          <StatusIcon size={14} />
                          {task.status}
                        </Badge>
                        <Button
                          as={Link}
                          to={`/results/${task.id}`}
                          variant="ghost"
                          size="small"
                        >
                          View
                        </Button>
                      </TaskActions>
                    </TaskItem>
                  );
                })}
              </TaskList>
            ) : (
              <EmptyState>
                <FiFileText size={48} style={{ opacity: 0.3, marginBottom: '1rem' }} />
                <p>No tasks yet. Upload your first file to get started!</p>
              </EmptyState>
            )}
          </Card>
        </RecentTasksSection>

        <QuickActionsSection>
          <Card>
            <SectionHeader>
              <SectionTitle>Quick Actions</SectionTitle>
            </SectionHeader>

            <QuickActionGrid>
              <QuickActionCard as={Link} to="/upload">
                <QuickActionIcon>
                  <FiUpload size={32} />
                </QuickActionIcon>
                <QuickActionTitle>Upload Files</QuickActionTitle>
                <QuickActionDescription>
                  Upload PDF or Excel files for validation
                </QuickActionDescription>
              </QuickActionCard>

              <QuickActionCard as={Link} to="/system">
                <QuickActionIcon>
                  <FiActivity size={32} />
                </QuickActionIcon>
                <QuickActionTitle>System Status</QuickActionTitle>
                <QuickActionDescription>
                  Check system health and performance
                </QuickActionDescription>
              </QuickActionCard>

              <QuickActionCard as={Link} to="/monitoring">
                <QuickActionIcon>
                  <FiTrendingUp size={32} />
                </QuickActionIcon>
                <QuickActionTitle>Monitoring</QuickActionTitle>
                <QuickActionDescription>
                  View real-time system metrics
                </QuickActionDescription>
              </QuickActionCard>
            </QuickActionGrid>
          </Card>
        </QuickActionsSection>
      </ContentGrid>
    </DashboardContainer>
  );
};

export default Dashboard;
