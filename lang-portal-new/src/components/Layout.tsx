import { ReactNode } from 'react';
import styled from 'styled-components';

const Container = styled.div`
  display: flex;
  min-height: 100vh;
`;

const Sidebar = styled.aside`
  width: 250px;
  background-color: #f5f5f5;
  padding: 20px;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
`;

const MainContent = styled.main`
  flex: 1;
  padding: 20px;
`;

const NavItem = styled.div`
  padding: 12px 8px;
  margin-bottom: 8px;
  cursor: pointer;
  border-radius: 4px;
  
  &:hover {
    background-color: #e0e0e0;
  }
`;

const Logo = styled.div`
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 30px;
  padding: 10px 0;
`;

interface LayoutProps {
  children: ReactNode;
  onNavigate: (page: string) => void;
  currentPage: string;
}

const Layout: React.FC<LayoutProps> = ({ children, onNavigate, currentPage }) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'study', label: 'Study Activities' },
    { id: 'words', label: 'Words' },
    { id: 'groups', label: 'Groups' },
    { id: 'sessions', label: 'Study Sessions' },
    { id: 'settings', label: 'Settings' },
  ];

  return (
    <Container>
      <Sidebar>
        <Logo>Language Portal</Logo>
        {navItems.map((item) => (
          <NavItem
            key={item.id}
            onClick={() => onNavigate(item.id)}
            style={{ 
              backgroundColor: currentPage === item.id ? '#e0e0e0' : 'transparent',
              fontWeight: currentPage === item.id ? 'bold' : 'normal'
            }}
          >
            {item.label}
          </NavItem>
        ))}
      </Sidebar>
      <MainContent>{children}</MainContent>
    </Container>
  );
};

export default Layout; 