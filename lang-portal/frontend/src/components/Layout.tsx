import { ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { theme } from '../styles/theme';

const Container = styled.div`
  display: flex;
  min-height: 100vh;
  background-color: ${theme.colors.background};
`;

const Sidebar = styled.aside`
  width: 250px;
  background-color: ${theme.colors.polar4};
  padding: ${theme.spacing.lg};
  box-shadow: ${theme.shadows.md};
  color: ${theme.colors.snow3};
`;

const MainContent = styled.main`
  flex: 1;
  padding: ${theme.spacing.xl};
  overflow-y: auto;
`;

const NavItem = styled(Link)`
  display: block;
  padding: 12px 16px;
  margin-bottom: 8px;
  cursor: pointer;
  border-radius: 6px;
  text-decoration: none;
  color: rgba(255, 255, 255, 0.9);
  transition: all 0.2s;
  
  &:hover {
    background-color: rgba(255, 255, 255, 0.1);
    color: white;
  }
`;

const Logo = styled.div`
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 32px;
  padding: 0 16px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  display: flex;
  align-items: center;
`;

const LogoIcon = styled.div`
  width: 24px;
  height: 24px;
  border-radius: 6px;
  background-color: var(--primary-color);
  margin-right: 12px;
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    width: 16px;
    height: 2px;
    background-color: white;
    top: 8px;
    left: 4px;
  }
  
  &::after {
    content: '';
    position: absolute;
    width: 16px;
    height: 2px;
    background-color: white;
    top: 14px;
    left: 4px;
  }
`;

const ActiveIndicator = styled.div`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--accent-color);
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
`;

interface LayoutProps {
  children: ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();
  const currentPath = location.pathname === '/' ? '/dashboard' : location.pathname;
  
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', path: '/dashboard' },
    { id: 'study', label: 'Study Activities', path: '/study' },
    { id: 'words', label: 'Words', path: '/words' },
    { id: 'groups', label: 'Groups', path: '/groups' },
    { id: 'sessions', label: 'Study Sessions', path: '/sessions' },
    { id: 'settings', label: 'Settings', path: '/settings' },
  ];

  return (
    <Container>
      <Sidebar>
        <Logo>
          <LogoIcon />
          Language Portal
        </Logo>
        {navItems.map((item) => (
          <NavItem
            key={item.id}
            to={item.path}
            style={{ 
              backgroundColor: currentPath === item.path ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
              fontWeight: currentPath === item.path ? 'bold' : 'normal',
              position: 'relative'
            }}
          >
            {item.label}
            {currentPath === item.path && <ActiveIndicator />}
          </NavItem>
        ))}
      </Sidebar>
      <MainContent>{children}</MainContent>
    </Container>
  );
};

export default Layout; 