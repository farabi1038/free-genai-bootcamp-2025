import React from 'react';
import { Link, NavLink as RouterNavLink } from 'react-router-dom';
import styled from 'styled-components';
import { theme } from '../../styles/theme';
import SearchBar from '../search/SearchBar';
import SearchResults from '../search/SearchResults';

const Nav = styled.nav`
  background-color: ${theme.colors.polarNight0};
  color: ${theme.colors.snow0};
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
`;

const NavContainer = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 ${theme.spacing.lg};
  height: 64px;
  max-width: 1200px;
  margin: 0 auto;
`;

const Logo = styled(Link)`
  color: ${theme.colors.snow0};
  font-size: 1.5rem;
  font-weight: bold;
  text-decoration: none;
  
  &:hover {
    color: ${theme.colors.frost3};
  }
`;

const NavLinks = styled.div`
  display: flex;
  align-items: center;
`;

const NavLink = styled(RouterNavLink)`
  color: ${theme.colors.snow0};
  text-decoration: none;
  padding: 0 ${theme.spacing.md};
  height: 64px;
  display: flex;
  align-items: center;
  position: relative;
  
  &:after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 3px;
    background-color: transparent;
    transition: background-color 0.2s;
  }
  
  &:hover {
    color: ${theme.colors.frost0};
  }
  
  &.active {
    color: ${theme.colors.frost2};
    
    &:after {
      background-color: ${theme.colors.frost2};
    }
  }
`;

const SearchContainer = styled.div`
  position: relative;
  margin-left: ${theme.spacing.lg};
`;

const Navbar: React.FC = () => {
  return (
    <Nav>
      <NavContainer>
        <Logo to="/">Language Learning Portal</Logo>
        <NavLinks>
          <NavLink to="/dashboard">Dashboard</NavLink>
          <NavLink to="/study">Study</NavLink>
          <NavLink to="/words">Words</NavLink>
          <NavLink to="/groups">Groups</NavLink>
          <NavLink to="/sessions">Sessions</NavLink>
          <NavLink to="/settings">Settings</NavLink>
          <SearchContainer>
            <SearchBar />
            <SearchResults />
          </SearchContainer>
        </NavLinks>
      </NavContainer>
    </Nav>
  );
};

export default Navbar; 