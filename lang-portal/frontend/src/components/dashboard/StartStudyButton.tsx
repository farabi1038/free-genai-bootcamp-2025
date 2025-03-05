import React from 'react';
import styled from 'styled-components';
import { Link } from 'react-router-dom';
import { theme } from '../../styles/theme';

const ButtonContainer = styled.div`
  background-color: ${theme.colors.snow0};
  border-radius: ${theme.borderRadius};
  padding: ${theme.spacing.xl};
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
`;

const StudyButtonIcon = styled.div`
  font-size: 2.5rem;
  margin-bottom: ${theme.spacing.md};
  color: ${theme.colors.frost3};
`;

const StudyButton = styled(Link)`
  display: inline-block;
  padding: ${theme.spacing.lg} ${theme.spacing.xl};
  background-color: ${theme.colors.frost3};
  color: white;
  font-weight: bold;
  font-size: 1.2rem;
  text-decoration: none;
  border-radius: ${theme.borderRadius};
  transition: all 0.2s;
  
  &:hover {
    background-color: ${theme.colors.frost2};
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  }
  
  &:active {
    transform: translateY(0);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  }
`;

const StudyText = styled.p`
  color: ${theme.colors.textLight};
  margin-bottom: ${theme.spacing.lg};
`;

const StartStudyButton: React.FC = () => {
  return (
    <ButtonContainer>
      <StudyButtonIcon>📝</StudyButtonIcon>
      <StudyText>
        Ready to improve your language skills?
        Choose from flashcards, multiple choice,
        typing practice, and matching games.
      </StudyText>
      <StudyButton to="/study">
        Start Studying
      </StudyButton>
    </ButtonContainer>
  );
};

export default StartStudyButton; 