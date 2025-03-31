import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import {
  Card,
  Typography,
  Button,
  Box,
  Grid,
  LinearProgress,
  Tooltip,
  CircularProgress,
} from '@mui/material';
import { PlusIcon } from '@heroicons/react/24/outline';

// Types
interface FamilyMember {
  id: string;
  name: string;
  relation_type: string;
  health_score: number;
  avatar?: string;
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
  height: 200px;
  
  &:hover {
    transform: translateY(-4px);
  }
`;

const AddMemberCard = styled(MemberCard)`
  border: 1px dashed #ddd;
  background-color: #fafafa;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  
  .plus-icon {
    transition: opacity 0.2s ease-in-out;
  }
  
  .add-member-text {
    opacity: 0;
    position: absolute;
    transition: opacity 0.2s ease-in-out;
    text-align: center;
  }
  
  &:hover {
    border-color: #ccc;
    background-color: white;
    
    .add-member-text {
      opacity: 1;
    }
    
    .plus-icon {
      opacity: 0;
    }
  }
`;

const getHealthScoreColor = (score: number) => {
  if (score >= 80) return '#4CAF50'; // Good
  if (score >= 60) return '#FFC107'; // Warning
  return '#F44336'; // Attention
};

const getDefaultAvatar = (relationType: string): string => {
  const avatars: { [key: string]: string } = {
    'self': '👤',
    'wife': '👩',
    'husband': '👨',
    'child': '👶',
    'son': '👦',
    'daughter': '👧',
    'grandfather': '👴',
    'grandmother': '👵',
    'father': '👨',
    'mother': '👩',
    'dog': '🐶',
    'cat': '🐱',
    'other': '👤',
  };
  return avatars[relationType.toLowerCase()] || '👤';
};

const FamilyDashboard: React.FC = () => {
  const [members, setMembers] = useState<FamilyMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchFamilyMembers = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/v1/family-members', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
          },
        });

        if (!response.ok) {
          throw new Error('Failed to fetch family members');
        }

        const data = await response.json();
        console.log('API Response:', data);
        // Extract the items array from the paginated response
        const familyMembers = data.items || [];
        setMembers(familyMembers);
      } catch (err) {
        setError('Failed to load family members');
        console.error('Error fetching family members:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchFamilyMembers();
  }, []);

  const familyScore = members.length > 0
    ? Math.round(members.reduce((acc, member) => acc + member.health_score, 0) / members.length)
    : 0;

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography color="error">{error}</Typography>
      </Box>
    );
  }

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
              {members.length} family members
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
                {member.avatar || getDefaultAvatar(member.relation_type)}
              </Typography>
              <Typography variant="h6">{member.name}</Typography>
              <Typography variant="body2" color="textSecondary">
                {member.relation_type}
              </Typography>
              
              <Tooltip title={`Health Score: ${member.health_score}/100`}>
                <Box sx={{ width: '100%', mt: 1 }}>
                  <LinearProgress
                    variant="determinate"
                    value={member.health_score}
                    sx={{
                      height: 8,
                      borderRadius: 4,
                      backgroundColor: '#e0e0e0',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: getHealthScoreColor(member.health_score)
                      }
                    }}
                  />
                </Box>
              </Tooltip>
            </MemberCard>
          </Grid>
        ))}
        
        <Grid item xs={12} sm={6} md={3}>
          <AddMemberCard elevation={1}>
            <Box className="plus-icon" sx={{ 
              width: 60, 
              height: 60, 
              borderRadius: '50%', 
              bgcolor: '#f8f8f8', 
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}>
              <PlusIcon width={36} height={36} color="#999" />
            </Box>
            <Box className="add-member-text">
              <Typography variant="h6" sx={{ fontSize: '1.1rem', mb: 0.5 }}>
                Add Family Member
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ fontSize: '0.85rem' }}>
                Track health together
              </Typography>
            </Box>
          </AddMemberCard>
        </Grid>
      </MembersGrid>
    </DashboardContainer>
  );
};

export default FamilyDashboard; 