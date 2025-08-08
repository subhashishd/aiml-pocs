import React, { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import {
  FiHome,
  FiUpload,
  FiBarChart2,
  FiActivity,
  FiMonitor,
  FiMenu,
  FiX,
} from 'react-icons/fi';

const LayoutContainer = styled.div`
  display: flex;
  height: 100vh;
  background-color: ${({ theme }) => theme.colors.background};
`;

const Sidebar = styled.aside.withConfig({
  shouldForwardProp: (prop) => prop !== 'isOpen',
})<{ isOpen: boolean }>`
  width: ${({ isOpen }) => (isOpen ? '250px' : '70px')};
  background-color: ${({ theme }) => theme.colors.gray[800]};
  border-right: 1px solid ${({ theme }) => theme.colors.gray[700]};
  transition: width 0.3s ease;
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 10;

  @media (max-width: 768px) {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    width: ${({ isOpen }) => (isOpen ? '250px' : '0')};
    transform: ${({ isOpen }) => (isOpen ? 'translateX(0)' : 'translateX(-100%)')};
  }
`;

const SidebarHeader = styled.div.withConfig({
  shouldForwardProp: (prop) => prop !== 'isOpen',
})<{ isOpen: boolean }>`
  padding: 1rem;
  border-bottom: 1px solid ${({ theme }) => theme.colors.gray[700]};
  display: flex;
  align-items: center;
  justify-content: ${({ isOpen }) => (isOpen ? 'space-between' : 'center')};
  min-height: 60px;
`;

const Logo = styled.h1.withConfig({
  shouldForwardProp: (prop) => prop !== 'isOpen',
})<{ isOpen: boolean }>`
  color: ${({ theme }) => theme.colors.primary[400]};
  font-size: 1.25rem;
  font-weight: bold;
  margin: 0;
  opacity: ${({ isOpen }) => (isOpen ? 1 : 0)};
  transition: opacity 0.3s ease;
`;

const MenuButton = styled.button`
  background: none;
  border: none;
  color: ${({ theme }) => theme.colors.gray[400]};
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;

  &:hover {
    background-color: ${({ theme }) => theme.colors.gray[700]};
    color: ${({ theme }) => theme.colors.white};
  }

  @media (min-width: 769px) {
    display: none;
  }
`;

const Navigation = styled.nav`
  flex: 1;
  padding: 1rem 0;
`;

const NavItem = styled(NavLink).withConfig({
  shouldForwardProp: (prop) => prop !== 'isOpen',
})<{ isOpen: boolean }>`
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  color: ${({ theme }) => theme.colors.gray[400]};
  text-decoration: none;
  transition: all 0.2s ease;
  border-left: 3px solid transparent;

  &:hover {
    background-color: ${({ theme }) => theme.colors.gray[700]};
    color: ${({ theme }) => theme.colors.white};
  }

  &.active {
    background-color: ${({ theme }) => theme.colors.primary[900]};
    color: ${({ theme }) => theme.colors.primary[400]};
    border-left-color: ${({ theme }) => theme.colors.primary[400]};
  }

  svg {
    min-width: 20px;
    margin-right: ${({ isOpen }) => (isOpen ? '0.75rem' : '0')};
  }

  span {
    opacity: ${({ isOpen }) => (isOpen ? 1 : 0)};
    transition: opacity 0.3s ease;
    white-space: nowrap;
  }
`;

const MainContent = styled.main.withConfig({
  shouldForwardProp: (prop) => prop !== 'sidebarOpen',
})<{ sidebarOpen: boolean }>`
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;

  @media (max-width: 768px) {
    margin-left: 0;
  }
`;

const TopBar = styled.header`
  background-color: ${({ theme }) => theme.colors.white};
  border-bottom: 1px solid ${({ theme }) => theme.colors.gray[200]};
  padding: 0 1.5rem;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
`;

const MobileMenuButton = styled.button`
  background: none;
  border: none;
  color: ${({ theme }) => theme.colors.gray[600]};
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    background-color: ${({ theme }) => theme.colors.gray[100]};
  }

  @media (min-width: 769px) {
    display: none;
  }
`;

const PageTitle = styled.h2`
  color: ${({ theme }) => theme.colors.gray[900]};
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
`;

const ContentArea = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  background-color: ${({ theme }) => theme.colors.gray[50]};
`;

const Overlay = styled.div.withConfig({
  shouldForwardProp: (prop) => prop !== 'show',
})<{ show: boolean }>`
  display: ${({ show }) => (show ? 'block' : 'none')};
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 5;

  @media (min-width: 769px) {
    display: none;
  }
`;

interface LayoutProps {
  children: React.ReactNode;
}

const navigationItems = [
  { path: '/', label: 'Dashboard', icon: FiHome },
  { path: '/upload', label: 'Upload Files', icon: FiUpload },
  { path: '/results', label: 'Results', icon: FiBarChart2 },
  { path: '/system', label: 'System Status', icon: FiActivity },
  { path: '/monitoring', label: 'Monitoring', icon: FiMonitor },
];

const getPageTitle = (pathname: string): string => {
  const item = navigationItems.find(item => item.path === pathname);
  if (item) return item.label;
  
  if (pathname.startsWith('/results')) return 'Results';
  return 'Dashboard';
};

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const closeSidebar = () => {
    setSidebarOpen(false);
  };

  return (
    <LayoutContainer>
      <Overlay show={sidebarOpen} onClick={closeSidebar} />
      
      <Sidebar isOpen={sidebarOpen}>
        <SidebarHeader isOpen={sidebarOpen}>
          <Logo isOpen={sidebarOpen}>ValidatorAI</Logo>
          <MenuButton onClick={toggleSidebar}>
            {sidebarOpen ? <FiX size={20} /> : <FiMenu size={20} />}
          </MenuButton>
        </SidebarHeader>
        
        <Navigation>
          {navigationItems.map(({ path, label, icon: Icon }) => (
            <NavItem
              key={path}
              to={path}
              isOpen={sidebarOpen}
              onClick={closeSidebar}
            >
              <Icon size={20} />
              <span>{label}</span>
            </NavItem>
          ))}
        </Navigation>
      </Sidebar>

      <MainContent sidebarOpen={sidebarOpen}>
        <TopBar>
          <MobileMenuButton onClick={toggleSidebar}>
            <FiMenu size={20} />
          </MobileMenuButton>
          <PageTitle>{getPageTitle(location.pathname)}</PageTitle>
          <div />
        </TopBar>
        
        <ContentArea>
          {children}
        </ContentArea>
      </MainContent>
    </LayoutContainer>
  );
};

export default Layout;
