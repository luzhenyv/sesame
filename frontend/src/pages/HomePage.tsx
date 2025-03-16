import React from 'react'
import { ArrowRightIcon } from '@heroicons/react/24/outline'
import Slider from 'react-slick'
import styled from 'styled-components'
import Button from '@mui/material/Button'
import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";

export interface BlogPost {
  id: number
  title: string
  author: string
  date: string
  tags: string[]
  readTime: string
  excerpt: string
  image: string
}

export interface HealthAssessment {
  id: number
  name: string
  category: string
  description: string
  time: string
  difficulty: 'Easy' | 'Medium' | 'Advanced'
  icon: string
}

// Styled Components with Responsive Styles
const Container = styled.div`
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f8f9fa;
  color: #333;
  font-family: 'Roboto', sans-serif;
  padding: 0 1rem;
`;

const Header = styled.header`
  background-color: white;
  padding: 1rem 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;

  @media (max-width: 768px) {
    padding: 1rem;
  }
`;

const Logo = styled.h1`
  font-size: 1.5rem;
  color: #1a1a1a;
  margin: 0;

  @media (max-width: 768px) {
    font-size: 1.25rem;
  }
`;

const Nav = styled.nav`
  display: flex;
  gap: 2rem;

  a {
    color: #4a4a4a;
    text-decoration: none;
    font-weight: 500;
    transition: color 0.3s ease;
    
    &:hover {
      color: #007AFF;
    }
  }

  @media (max-width: 768px) {
    width: 100%;
    justify-content: center;
    margin-top: 0.5rem;
    flex-wrap: wrap;
    gap: 1rem;
  }
`;

const MainContent = styled.main`
  flex: 1;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 3rem;
  box-sizing: border-box;

  @media (max-width: 768px) {
    padding: 1rem;
    gap: 2rem;
  }
`;

const CarouselSection = styled.section`
  width: 100%;
  margin: 0 auto;
  box-sizing: border-box;
`;

const Card = styled.div`
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease;

  &:hover {
    transform: translateY(-5px);
  }

  h2 {
    color: #1a1a1a;
    margin-top: 0;
    font-size: 1.25rem;
  }

  p {
    color: #666;
    line-height: 1.6;
  }

  @media (max-width: 768px) {
    padding: 1rem;
  }
`;

const Footer = styled.footer`
  background-color: #1a1a1a;
  color: white;
  padding: 2rem;
  text-align: center;

  @media (max-width: 768px) {
    padding: 1rem;
    font-size: 0.875rem;
  }
`;

const SectionTitle = styled.h2`
  color: #1a1a1a;
  font-size: 1.5rem;
  margin: 2rem 0 1rem;
  grid-column: 1 / -1;

  @media (max-width: 768px) {
    font-size: 1.25rem;
    margin: 1.5rem 0 1rem;
  }
`;

const StyledSlider = styled(Slider)`
  .slick-list {
    margin: 0;
  }

  .slick-slide {
    padding: 0 10px;
    box-sizing: border-box;
  }

  .slick-prev,
  .slick-next {
    z-index: 1;
    width: 40px;
    height: 40px;
    
    &:before {
      font-size: 40px;
      color: #007AFF;
    }
  }

  .slick-prev {
    left: 10px;
  }

  .slick-next {
    right: 10px;
  }

  .slick-dots {
    bottom: -40px;
    
    li button:before {
      font-size: 12px;
      color: #007AFF;
    }
    
    li.slick-active button:before {
      color: #007AFF;
    }
  }

  @media (max-width: 768px) {
    .slick-prev,
    .slick-next {
      width: 30px;
      height: 30px;
      
      &:before {
        font-size: 30px;
      }
    }
  }
`;

const SlideContent = styled.div`
  background: white;
  border-radius: 12px;
  padding: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  margin: 10px;
  height: 100%;
  box-sizing: border-box;

  @media (max-width: 768px) {
    padding: 0.75rem;
    margin: 5px;
  }
`;

const AssessmentGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
  width: 100%;

  @media (max-width: 1200px) {
    grid-template-columns: repeat(2, 1fr);
  }

  @media (max-width: 640px) {
    grid-template-columns: 1fr;
  }
`;

const BlogGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  width: 100%;

  @media (max-width: 1200px) {
    grid-template-columns: repeat(2, 1fr);
  }

  @media (max-width: 640px) {
    grid-template-columns: 1fr;
  }
`;

const SectionHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  width: 100%;
`;

const ViewAllButton = styled(Button)`
  && {
    text-transform: none;
    font-weight: 500;
  }
`;

const HomePage: React.FC = () => {
  // Temporary data - replace with API calls
  const companyUpdates = [
    {
      id: 1,
      image: '/assets/images/update1.jpg',
      headline: 'New AI-Powered Health Insights',
      description: 'Get personalized health recommendations using our latest machine learning models',
      date: '2024-03-20'
    },
    {
      id: 2,
      image: '/assets/images/update2.jpg',
      headline: 'Mental Health Awareness Partnership',
      description: 'Collaborating with Mindful.org to provide free anxiety assessment tools',
      date: '2024-03-18'
    },
    {
      id: 3,
      image: '/assets/images/update3.jpg',
      headline: 'Mobile App Update Released',
      description: 'New dark mode and offline tracking capabilities now available',
      date: '2024-03-15'
    },
    {
      id: 4,
      image: '/assets/images/update4.jpg',
      headline: 'Annual Health Report 2024',
      description: 'Discover global health trends in our comprehensive yearly analysis',
      date: '2024-03-12'
    },
    {
      id: 5,
      image: '/assets/images/update5.jpg',
      headline: 'New Diabetes Management Tools',
      description: 'Track blood sugar levels and get predictive insights with our new module',
      date: '2024-03-10'
    }
  ]

  const assessments: HealthAssessment[] = [
    {
      id: 1,
      name: 'Mental Wellness Check',
      category: 'Mental Health',
      description: 'Evaluate your emotional well-being and stress levels',
      time: '10-15 mins',
      difficulty: 'Medium',
      icon: '🧠'
    },
    {
      id: 2,
      name: 'Sleep Quality Analysis',
      category: 'Physical Health',
      description: 'Assess your sleep patterns and get improvement tips',
      time: '5-8 mins',
      difficulty: 'Easy',
      icon: '🌙'
    },
    {
      id: 3,
      name: 'Cognitive Function Test',
      category: 'Mental Health',
      description: 'Measure memory, focus, and problem-solving skills',
      time: '15-20 mins',
      difficulty: 'Advanced',
      icon: '🧩'
    },
    {
      id: 4,
      name: 'Fitness Level Check',
      category: 'Physical Health',
      description: 'Evaluate your cardiovascular endurance and strength',
      time: '10-12 mins',
      difficulty: 'Medium',
      icon: '🏋️♂️'
    },
    {
      id: 5,
      name: 'Social Wellness Quiz',
      category: 'Social Health',
      description: 'Assess your relationship quality and social habits',
      time: '8-10 mins',
      difficulty: 'Easy',
      icon: '👥'
    }
  ]

  const blogPosts: BlogPost[] = [
    {
      id: 1,
      title: '5 Tips for Better Sleep Hygiene',
      author: 'Dr. Sarah Johnson',
      date: '2024-03-10',
      tags: ['Sleep', 'Wellness'],
      readTime: '5 min read',
      excerpt: 'Discover science-backed methods to improve your sleep quality...',
      image: '/assets/images/blog-sleep.jpg'
    }
    // ... more posts
  ]

  const sliderSettings = {
    dots: true,
    infinite: true,
    speed: 500,
    slidesToShow: 1,
    slidesToScroll: 1,
    arrows: true,
    autoplay: true,
    autoplaySpeed: 3000,
    pauseOnHover: true,
    responsive: [
      {
        breakpoint: 1024,
        settings: {
          slidesToShow: 1,
          slidesToScroll: 1,
        }
      },
      {
        breakpoint: 768,
        settings: {
          slidesToShow: 1,
          slidesToScroll: 1,
          arrows: false
        }
      }
    ]
  }

  return (
    <Container>
      <MainContent>
        <CarouselSection>
          <StyledSlider {...sliderSettings}>
            {companyUpdates.map(update => (
              <div key={update.id}>
                <SlideContent>
                  <img 
                    src={update.image} 
                    alt={update.headline} 
                    style={{
                      width: '100%', 
                      height: '300px', 
                      objectFit: 'cover',
                      borderRadius: '8px'
                    }}
                  />
                  <h3 style={{ margin: '1rem 0' }}>{update.headline}</h3>
                  <p style={{ marginBottom: '1rem' }}>{update.description}</p>
                  <div style={{
                    display: 'flex', 
                    justifyContent: 'space-between',
                    alignItems: 'center'
                  }}>
                    <span style={{ color: '#666' }}>
                      {new Date(update.date).toLocaleDateString()}
                    </span>
                    <Button 
                      variant="text" 
                      endIcon={<ArrowRightIcon width={16} />}
                      style={{ minWidth: 'auto' }}
                    >
                      Read More
                    </Button>
                  </div>
                </SlideContent>
              </div>
            ))}
          </StyledSlider>
        </CarouselSection>

        <section>
          <SectionHeader>
            <SectionTitle style={{ margin: 0 }}>Health Assessments</SectionTitle>
            <ViewAllButton
              variant="outlined"
              endIcon={<ArrowRightIcon width={16} />}
              href="/assessments"
            >
              View All Assessments
            </ViewAllButton>
          </SectionHeader>
          <AssessmentGrid>
            {assessments.map(assessment => (
              <Card key={assessment.id}>
                <div style={{display: 'flex', gap: '1rem', alignItems: 'center'}}>
                  <span style={{fontSize: '2rem'}}>{assessment.icon}</span>
                  <div>
                    <h3>{assessment.name}</h3>
                    <small>{assessment.category}</small>
                  </div>
                </div>
                <p>{assessment.description}</p>
                <div style={{display: 'flex', justifyContent: 'space-between'}}>
                  <span>⏱ {assessment.time}</span>
                  <span style={{
                    color: assessment.difficulty === 'Easy' ? '#4CAF50' :
                           assessment.difficulty === 'Medium' ? '#FFC107' : '#F44336'
                  }}>
                    {assessment.difficulty}
                  </span>
                </div>
                <Button 
                  variant="contained" 
                  fullWidth 
                  style={{marginTop: '1rem'}}
                >
                  Start Assessment
                </Button>
              </Card>
            ))}
          </AssessmentGrid>
        </section>

        <section>
          <SectionHeader>
            <SectionTitle style={{ margin: 0 }}>Health Blog</SectionTitle>
            <ViewAllButton
              variant="outlined"
              endIcon={<ArrowRightIcon width={16} />}
              href="/blog"
            >
              View All Articles
            </ViewAllButton>
          </SectionHeader>
          <BlogGrid>
            {blogPosts.map(post => (
              <Card key={post.id}>
                <img 
                  src={post.image} 
                  alt={post.title} 
                  style={{width: '100%', height: '200px', objectFit: 'cover'}}
                />
                <div style={{marginTop: '1rem'}}>
                  <h3>{post.title}</h3>
                  <div style={{display: 'flex', gap: '0.5rem', margin: '0.5rem 0'}}>
                    {post.tags.map(tag => (
                      <span key={tag} style={{
                        background: '#007AFF20',
                        color: '#007AFF',
                        padding: '0.25rem 0.5rem',
                        borderRadius: '4px',
                        fontSize: '0.8rem'
                      }}>
                        {tag}
                      </span>
                    ))}
                  </div>
                  <div style={{display: 'flex', justifyContent: 'space-between'}}>
                    <span>By {post.author}</span>
                    <span>{post.readTime}</span>
                  </div>
                  <p style={{margin: '0.5rem 0'}}>{post.excerpt}</p>
                  <Button  
                    variant="outlined"   
                    fullWidth   
                    endIcon={<ArrowRightIcon width={16} />}  
                  >
                    Read Article  
                  </Button>  
                </div>  
              </Card>  
            ))}
          </BlogGrid>
        </section>
      </MainContent>
    </Container>
  )
}

export default HomePage
