import React, { useState } from 'react';
import styled from 'styled-components';
import { FaCalendarAlt, FaCog, FaUserCircle, FaUsers, FaDownload, FaMobileAlt, FaPhoneAlt, FaMoon } from 'react-icons/fa';

// Styled Components
const Container = styled.div`
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f8f9fa;
  color: #333;
  font-family: 'Roboto', sans-serif;
  width: 100%;
  box-sizing: border-box;
`;

const MainContent = styled.main`
  flex: 1;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 2rem;
  box-sizing: border-box;
  
  @media (max-width: 768px) {
    padding: 1rem;
  }
`;

const PageHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  width: 100%;
  box-sizing: border-box;
  
  h1 {
    font-size: 2.5rem;
    font-weight: 600;
    color: #2c3e50;
  }
`;

const SectionContainer = styled.section`
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  padding: 2rem;
  margin-bottom: 2rem;
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
`;

const SectionHeader = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: 1.5rem;
  
  h2 {
    font-size: 1.8rem;
    font-weight: 500;
    margin-left: 0.75rem;
    color: #2c3e50;
  }
  
  svg {
    color: #3498db;
    font-size: 1.8rem;
  }
`;

const TabsContainer = styled.div`
  display: flex;
  border-bottom: 1px solid #e0e0e0;
  margin-bottom: 2rem;
`;

const Tab = styled.button<{ active: boolean }>`
  padding: 0.75rem 1.5rem;
  background: none;
  border: none;
  border-bottom: 3px solid ${props => props.active ? '#3498db' : 'transparent'};
  color: ${props => props.active ? '#3498db' : '#555'};
  font-weight: ${props => props.active ? '600' : '400'};
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
  
  &:hover {
    color: #3498db;
  }
  
  svg {
    font-size: 1.2rem;
  }
`;

// Calendar Components
const CalendarContainer = styled.div`
  margin-top: 1.5rem;
  width: 100%;
  box-sizing: border-box;
`;

const CalendarHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
`;

const CalendarControls = styled.div`
  display: flex;
  gap: 1rem;
  align-items: center;
  
  h3 {
    font-size: 1.4rem;
    font-weight: 500;
    min-width: 180px;
    text-align: center;
  }
  
  button {
    background-color: #f1f1f1;
    border: none;
    border-radius: 50%;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: background-color 0.3s ease;
    
    &:hover {
      background-color: #e0e0e0;
    }
  }
`;

const ViewToggle = styled.div`
  display: flex;
  background-color: #f1f1f1;
  border-radius: 20px;
  overflow: hidden;
`;

const ViewButton = styled.button<{ active: boolean }>`
  padding: 0.5rem 1rem;
  background-color: ${props => props.active ? '#3498db' : 'transparent'};
  color: ${props => props.active ? 'white' : '#555'};
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background-color: ${props => props.active ? '#3498db' : '#e0e0e0'};
  }
`;

const AddEntryButton = styled.button`
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 20px;
  padding: 0.6rem 1.2rem;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: background-color 0.3s ease;
  
  &:hover {
    background-color: #2980b9;
  }
`;

const CalendarGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.5rem;
  width: 100%;
  box-sizing: border-box;
`;

const WeekdayHeader = styled.div`
  text-align: center;
  font-weight: 500;
  color: #666;
  padding: 0.5rem;
`;

const CalendarDay = styled.div<{ isToday?: boolean; hasEvents?: boolean; eventType?: string }>`
  aspect-ratio: 1;
  border-radius: 8px;
  background-color: ${props => props.isToday ? '#e3f2fd' : 'white'};
  border: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
  padding: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  
  &:hover {
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
  }
  
  ${props => props.hasEvents && `
    &::after {
      content: '';
      position: absolute;
      bottom: 5px;
      left: 50%;
      transform: translateX(-50%);
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background-color: ${
        props.eventType === 'checkup' ? '#4caf50' : 
        props.eventType === 'medication' ? '#ff9800' : 
        props.eventType === 'symptom' ? '#f44336' : 
        props.eventType === 'exercise' ? '#9c27b0' : '#3498db'
      };
    }
  `}
`;

const DayNumber = styled.span<{ isCurrentMonth?: boolean }>`
  font-weight: ${props => props.isCurrentMonth ? '400' : '300'};
  color: ${props => props.isCurrentMonth ? '#333' : '#aaa'};
`;

const CalendarLegend = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e0e0e0;
`;

const LegendItem = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const ColorDot = styled.div<{ color: string }>`
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: ${props => props.color};
`;

// Settings Components
const FormGroup = styled.div`
  margin-bottom: 1.5rem;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #555;
`;

const Input = styled.input`
  width: 90%;
  padding: 0.75rem 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  
  &:focus {
    outline: none;
    border-color: #3498db;
    box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
  }
`;

const Select = styled.select`
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  background-color: white;
  
  &:focus {
    outline: none;
    border-color: #3498db;
    box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
  }
`;

const ProfilePictureContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 2rem;
`;

const ProfilePicture = styled.div`
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background-color: #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: center;
  
  svg {
    font-size: 3rem;
    color: #aaa;
  }
`;

const UploadButton = styled.button`
  background-color: #f1f1f1;
  border: none;
  border-radius: 8px;
  padding: 0.6rem 1.2rem;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
  
  &:hover {
    background-color: #e0e0e0;
  }
`;

const SettingsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
`;

const SaveButton = styled.button`
  background-color: #27ae60;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.75rem 1.5rem;
  font-weight: 500;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
  
  &:hover {
    background-color: #219653;
  }
`;

const FamilyMemberCard = styled.div`
  border: 1px solid #e0e0e0;
  border-radius: 10px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
`;

const FamilyMemberInfo = styled.div`
  flex: 1;
  
  h4 {
    font-size: 1.1rem;
    margin-bottom: 0.25rem;
  }
  
  p {
    color: #666;
    margin: 0;
  }
`;

const FamilyMemberActions = styled.div`
  display: flex;
  gap: 0.5rem;
`;

const ActionButton = styled.button`
  background-color: transparent;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background-color: #f1f1f1;
  }
`;

const AdditionalFeaturesGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
  width: 100%;
  box-sizing: border-box;
`;

const FeatureCard = styled.div`
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  }
  
  svg {
    font-size: 2.5rem;
    color: #3498db;
    margin-bottom: 1rem;
  }
  
  h3 {
    font-size: 1.3rem;
    margin-bottom: 0.5rem;
  }
  
  p {
    color: #666;
    font-size: 0.9rem;
  }
`;

// Main Component
const ProfilePage: React.FC = () => {
  const [calendarView, setCalendarView] = useState<'month' | 'week'>('month');
  const [activeSettingsTab, setActiveSettingsTab] = useState('profile');
  
  // Mock data for calendar
  const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const currentMonth = 'March 2023';
  
  // Mock calendar days (in real app, this would be dynamically generated)
  const daysInMonth = Array.from({ length: 35 }, (_, i) => ({
    day: i - 2,
    isCurrentMonth: i > 2 && i < 33,
    isToday: i === 15,
    hasEvents: [5, 10, 15, 20, 25].includes(i),
    eventType: i === 5 ? 'checkup' : i === 10 ? 'medication' : i === 15 ? 'symptom' : i === 20 ? 'exercise' : 'other'
  }));

  return (
    <Container>
      <MainContent>
        <PageHeader>
          <h1>My Profile</h1>
        </PageHeader>
        
        {/* Health Calendar Section */}
        <SectionContainer>
          <SectionHeader>
            <FaCalendarAlt />
            <h2>Health Calendar</h2>
          </SectionHeader>
          
          <CalendarContainer>
            <CalendarHeader>
              <CalendarControls>
                <button>{'<'}</button>
                <h3>{currentMonth}</h3>
                <button>{'>'}</button>
              </CalendarControls>
              
              <ViewToggle>
                <ViewButton 
                  active={calendarView === 'month'} 
                  onClick={() => setCalendarView('month')}
                >
                  Month
                </ViewButton>
                <ViewButton 
                  active={calendarView === 'week'} 
                  onClick={() => setCalendarView('week')}
                >
                  Week
                </ViewButton>
              </ViewToggle>
              
              <AddEntryButton>
                <span>+</span> Add New Entry
              </AddEntryButton>
            </CalendarHeader>
            
            <CalendarGrid>
              {weekdays.map(day => (
                <WeekdayHeader key={day}>{day}</WeekdayHeader>
              ))}
              
              {daysInMonth.map((day, index) => (
                <CalendarDay 
                  key={index}
                  isToday={day.isToday}
                  hasEvents={day.hasEvents}
                  eventType={day.eventType}
                >
                  <DayNumber isCurrentMonth={day.isCurrentMonth}>
                    {day.day > 0 ? day.day : ''}
                  </DayNumber>
                </CalendarDay>
              ))}
            </CalendarGrid>
            
            <CalendarLegend>
              <LegendItem>
                <ColorDot color="#4caf50" />
                <span>Check-ups</span>
              </LegendItem>
              <LegendItem>
                <ColorDot color="#ff9800" />
                <span>Medications</span>
              </LegendItem>
              <LegendItem>
                <ColorDot color="#f44336" />
                <span>Symptoms</span>
              </LegendItem>
              <LegendItem>
                <ColorDot color="#9c27b0" />
                <span>Exercise</span>
              </LegendItem>
              <LegendItem>
                <ColorDot color="#3498db" />
                <span>Other</span>
              </LegendItem>
            </CalendarLegend>
          </CalendarContainer>
        </SectionContainer>
        
        {/* Settings Section */}
        <SectionContainer>
          <SectionHeader>
            <FaCog />
            <h2>Settings</h2>
          </SectionHeader>
          
          <TabsContainer>
            <Tab 
              active={activeSettingsTab === 'profile'} 
              onClick={() => setActiveSettingsTab('profile')}
            >
              <FaUserCircle /> User Profile
            </Tab>
            <Tab 
              active={activeSettingsTab === 'family'} 
              onClick={() => setActiveSettingsTab('family')}
            >
              <FaUsers /> Family Members
            </Tab>
            <Tab 
              active={activeSettingsTab === 'general'} 
              onClick={() => setActiveSettingsTab('general')}
            >
              <FaCog /> General Settings
            </Tab>
          </TabsContainer>
          
          {activeSettingsTab === 'profile' && (
            <>
              <ProfilePictureContainer>
                <ProfilePicture>
                  <FaUserCircle />
                </ProfilePicture>
                <UploadButton>Upload New Picture</UploadButton>
              </ProfilePictureContainer>
              
              <SettingsGrid>
                <FormGroup>
                  <Label>Full Name</Label>
                  <Input type="text" placeholder="Enter your full name" />
                </FormGroup>
                
                <FormGroup>
                  <Label>Date of Birth</Label>
                  <Input type="date" placeholder="Select your date of birth" />
                </FormGroup>
                
                <FormGroup>
                  <Label>Gender</Label>
                  <Select>
                    <option value="">Select gender</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </Select>
                </FormGroup>
                
                <FormGroup>
                  <Label>Email</Label>
                  <Input type="email" placeholder="Enter your email" />
                </FormGroup>
                
                <FormGroup>
                  <Label>Phone Number</Label>
                  <Input type="tel" placeholder="Enter your phone number" />
                </FormGroup>
                
                <FormGroup>
                  <Label>Address</Label>
                  <Input type="text" placeholder="Enter your address" />
                </FormGroup>
              </SettingsGrid>
              
              <FormGroup>
                <Label>Health Goals</Label>
                <Input type="text" placeholder="Enter your health goals" />
              </FormGroup>
              
              <SaveButton>Save Changes</SaveButton>
            </>
          )}
          
          {activeSettingsTab === 'family' && (
            <>
              <h3>Family Members</h3>
              
              <FamilyMemberCard>
                <ProfilePicture>
                  <FaUserCircle />
                </ProfilePicture>
                <FamilyMemberInfo>
                  <h4>Jane Doe</h4>
                  <p>Relationship: Spouse</p>
                </FamilyMemberInfo>
                <FamilyMemberActions>
                  <ActionButton>Edit</ActionButton>
                  <ActionButton>Remove</ActionButton>
                </FamilyMemberActions>
              </FamilyMemberCard>
              
              <FamilyMemberCard>
                <ProfilePicture>
                  <FaUserCircle />
                </ProfilePicture>
                <FamilyMemberInfo>
                  <h4>John Jr.</h4>
                  <p>Relationship: Child</p>
                </FamilyMemberInfo>
                <FamilyMemberActions>
                  <ActionButton>Edit</ActionButton>
                  <ActionButton>Remove</ActionButton>
                </FamilyMemberActions>
              </FamilyMemberCard>
              
              <AddEntryButton style={{ marginTop: '1rem' }}>
                <span>+</span> Add Family Member
              </AddEntryButton>
            </>
          )}
          
          {activeSettingsTab === 'general' && (
            <>
              <SettingsGrid>
                <FormGroup>
                  <Label>Language</Label>
                  <Select>
                    <option value="english">English</option>
                    <option value="spanish">Spanish</option>
                    <option value="french">French</option>
                    <option value="german">German</option>
                  </Select>
                </FormGroup>
                
                <FormGroup>
                  <Label>Measurement Units</Label>
                  <Select>
                    <option value="metric">Metric (kg, cm)</option>
                    <option value="imperial">Imperial (lb, ft)</option>
                  </Select>
                </FormGroup>
                
                <FormGroup>
                  <Label>Privacy</Label>
                  <Select>
                    <option value="private">Private - Only Me</option>
                    <option value="family">Family - Me and Family Members</option>
                    <option value="doctor">Doctor - Me, Family and Doctors</option>
                  </Select>
                </FormGroup>
                
                <FormGroup>
                  <Label>Notifications</Label>
                  <Select>
                    <option value="all">All Notifications</option>
                    <option value="important">Important Only</option>
                    <option value="none">None</option>
                  </Select>
                </FormGroup>
              </SettingsGrid>
              
              <SaveButton>Save Changes</SaveButton>
            </>
          )}
        </SectionContainer>
        
        {/* Additional Features Section */}
        <SectionContainer>
          <SectionHeader>
            <FaCog />
            <h2>Additional Features</h2>
          </SectionHeader>
          
          <AdditionalFeaturesGrid>
            <FeatureCard>
              <FaDownload />
              <h3>Health Data Export</h3>
              <p>Download your health logs as CSV or PDF reports</p>
            </FeatureCard>
            
            <FeatureCard>
              <FaMobileAlt />
              <h3>Wearables Integration</h3>
              <p>Sync with fitness trackers and health devices</p>
            </FeatureCard>
            
            <FeatureCard>
              <FaPhoneAlt />
              <h3>Emergency Contacts</h3>
              <p>Store emergency contact details for quick access</p>
            </FeatureCard>
            
            <FeatureCard>
              <FaMoon />
              <h3>Dark Mode Toggle</h3>
              <p>Switch between light and dark themes</p>
            </FeatureCard>
          </AdditionalFeaturesGrid>
        </SectionContainer>
      </MainContent>
    </Container>
  );
};

export default ProfilePage; 