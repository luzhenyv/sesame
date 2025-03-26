import React from 'react';
import styled from 'styled-components';
import {
  Card,
  Typography,
  Button,
  Avatar,
  Box,
  Grid,
  LinearProgress,
  Tooltip
} from '@mui/material';
import { PlusIcon } from '@heroicons/react/24/outline';

// Types
interface FamilyMember {
  id: string;
  name: string;
  role: string;
  avatar: string;
  healthScore: number;
}

interface FamilyDashboardProps {
  familyScore: number;
  memberCount: number;
  members: FamilyMember[];
  onAddMember: () => void;
}

// Styled Components
const DashboardContainer = styled(Card)`
  padding: 1.5rem;
  border-radius: 12px;
  width: 100%;
  box-sizing: border-box;
`;

const HeaderSection = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  
  @media (max-width: 768px) {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
`;

const FamilyScoreSection = styled.div`
  display: flex;
  align-items: center;
  gap: 1.5rem;
  
  @media (max-width: 768px) {
    width: 100%;
  }
`;

const ScoreDisplay = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: #f5f5f5;
  border-radius: 50%;
  width: 100px;
  height: 100px;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  
  @media (max-width: 768px) {
    width: 80px;
    height: 80px;
  }
`;

const MembersGrid = styled(Grid)`
  margin-top: 1.5rem;
`;

const MemberCard = styled(Card)`
  padding: 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  transition: transform 0.2s;
  
  &:hover {
    transform: translateY(-4px);
  }
`;

const AddMemberCard = styled(MemberCard)`
  border: 2px dashed #ccc;
  background-color: #f9f9f9;
  cursor: pointer;
  
  &:hover {
    border-color: #999;
    background-color: #f0f0f0;
  }
`;

const getHealthScoreColor = (score: number) => {
  if (score >= 80) return '#4CAF50'; // Good
  if (score >= 60) return '#FFC107'; // Warning
  return '#F44336'; // Attention
};

// A test return

const FamilyDashboard: React.FC<FamilyDashboardProps> = ({
  familyScore,
  memberCount,
  members,
  onAddMember
}) => {
  return (
    <DashboardContainer 
      elevation={2} 
      sx={{ 
        backgroundColor: `${getHealthScoreColor(familyScore)}10` // Adding 10% opacity to the health score color
      }}
    >
      <HeaderSection>
        <Typography variant="h4" component="h1">
          Family Health Dashboard
        </Typography>
        
        <FamilyScoreSection>
          <div>
            <Typography variant="subtitle1" color="textSecondary">
              Family Health Score
            </Typography>
            <Typography variant="h6">
              {memberCount} family members
            </Typography>
          </div>
          
          <ScoreDisplay>
            <Typography variant="h4" sx={{ color: getHealthScoreColor(familyScore) }}>
              {familyScore}
            </Typography>
            <Typography variant="caption" color="textSecondary">
              /100
            </Typography>
          </ScoreDisplay>
        </FamilyScoreSection>
      </HeaderSection>
      
      <MembersGrid container spacing={3}>
        {members.map(member => (
          <Grid item xs={12} sm={6} md={3} key={member.id}>
            <MemberCard elevation={2}>
              <Typography variant="h1" sx={{ fontSize: '2.5rem' }}>
                {member.avatar}
              </Typography>
              <Typography variant="h6">{member.name}</Typography>
              <Typography variant="body2" color="textSecondary">
                {member.role}
              </Typography>
              
              <Tooltip title={`Health Score: ${member.healthScore}/100`}>
                <Box sx={{ width: '100%', mt: 1 }}>
                  <LinearProgress
                    variant="determinate"
                    value={member.healthScore}
                    sx={{
                      height: 8,
                      borderRadius: 4,
                      backgroundColor: '#e0e0e0',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: getHealthScoreColor(member.healthScore)
                      }
                    }}
                  />
                </Box>
              </Tooltip>
            </MemberCard>
          </Grid>
        ))}
        
        <Grid item xs={12} sm={6} md={3}>
          <AddMemberCard elevation={1} onClick={onAddMember}>
            <Box sx={{ 
              width: 60, 
              height: 60, 
              borderRadius: '50%', 
              bgcolor: '#f0f0f0', 
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <PlusIcon width={30} height={30} color="#666" />
            </Box>
            <Typography variant="h6">Add Family Member</Typography>
            <Typography variant="body2" color="textSecondary">
              Track health together
            </Typography>
          </AddMemberCard>
        </Grid>
      </MembersGrid>
    </DashboardContainer>
  );
};

export default FamilyDashboard; 