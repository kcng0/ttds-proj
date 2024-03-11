import React, { useState, useEffect } from 'react';
import { fetchSearchTfidf } from './api';
import { Container, Navbar, Nav, InputGroup, FormControl, Button, Card, Badge, Pagination, Form, Row, Col, Spinner } from 'react-bootstrap';
import { BsSearch } from 'react-icons/bs';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';


const SentimentBadge = ({ sentiments }) => {
    const getColorWithIntensity = (baseColor, value) => {
      const intensityFactor = 0.5 + (value * 0.5); 
      return `rgba(${baseColor.r}, ${baseColor.g}, ${baseColor.b}, ${intensityFactor})`;
    };
  
    const getFontColor = (backgroundColor) => {
      const brightness = (backgroundColor.r * 299 + backgroundColor.g * 587 + backgroundColor.b * 114) / 1000;
      return brightness > 125 ? 'black' : 'white';
    };
  
    const totalValue = sentiments.reduce((sum, { value }) => sum + value, 0);
  
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        height: '35px',
        borderRadius: '20px',
        overflow: 'hidden',
        maxWidth: '60%',
        marginLeft: '0',
        alignSelf: 'flex-start',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
      }}>
        {sentiments.map(({ type, value }, index) => {
          if (value === 0) return null;
          const baseColors = {
            positive: { r: 0, g: 128, b: 0 },
            neutral: { r: 128, g: 128, b: 128 },
            negative: { r: 255, g: 0, b: 0 },
          };
          const widthPercent = (value / totalValue) * 100;
          const backgroundColor = getColorWithIntensity(baseColors[type], value);
          const fontColor = getFontColor(backgroundColor);
          
          const tooltipText = `${type.charAt(0).toUpperCase() + type.slice(1)}: ${(value * 100).toFixed(1)}%`;
  
          return (
            <div key={index} style={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              width: `${widthPercent}%`,
              backgroundColor: backgroundColor,
              color: fontColor,
              fontSize: '1rem',
              transition: 'width 0.3s ease',
            }} title={tooltipText}>
              <span style={{ padding: '0 5px' }}>{(value * 100).toFixed(1)}%</span>
            </div>
          );
        })}
      </div>
    );
  };

function TfidfResultsPage() {
    const location = useLocation();
    const navigate = useNavigate();
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState(location.state ? location.state.searchResults : []);
    const [loading, setLoading] = useState(false);
    const [filterYear, setFilterYear] = useState('all');
    const [sentimentFilter, setSentimentFilter] = useState('all');
    const [sourceFilter, setSourceFilter] = useState('all');

    const currentYear = new Date().getFullYear();
    const years = Array.from({ length: currentYear - 2020 + 1 }, (_, i) => String(2020 + i));
    const uniqueSources = [...new Set(searchResults.map(result => result.source))];

    useEffect(() => {
        // Re-fetch on search query change if needed
    }, [searchQuery]);

    const performSearch = async () => {
        setLoading(true);
        try {
            const results = await fetchSearchTfidf(searchQuery);
            setSearchResults(results);
            navigate('/TfidfResultsPage', { state: { searchResults: results } });
        } catch (error) {
            console.error('Error fetching TF-IDF search results:', error);
        }
        setLoading(false);
    };

    const handleSearchInputChange = (e) => {
        setSearchQuery(e.target.value);
    };

    const handleSearch = (e) => {
        if (e.key === 'Enter') {
            e.preventDefault(); 
            performSearch();
        }
    };

    const handleSearchClick = () => {
        performSearch();
    };

    const filteredResults = searchResults.filter(result => {
        const resultYear = new Date(result.date).getFullYear().toString();
        const meetsYearCriteria = filterYear === 'all' || resultYear === filterYear;
        const meetsSourceCriteria = sourceFilter === 'all' || result.source === sourceFilter;

        if (!meetsYearCriteria || !meetsSourceCriteria) return false;

        if (sentimentFilter === 'all') return true;

        return result.sentiment === sentimentFilter;
    });
    
    

    const ColorCodingGuide = () => (
        <div className="d-flex justify-content-end my-2">
            <Badge pill bg="success" className="mx-1">Positive</Badge>
            <Badge pill bg="secondary" className="mx-1">Neutral</Badge>
            <Badge pill bg="danger" className="mx-1">Negative</Badge>
        </div>
    );

    return (
        <>
            <Navbar bg="light" expand="lg">
                <Container>
                    <Navbar.Brand as={Link} to="/">FactChecker</Navbar.Brand>
                    <Navbar.Toggle aria-controls="basic-navbar-nav" />
                    <Navbar.Collapse id="basic-navbar-nav">
                        <Nav className="me-auto">
                            <Nav.Link as={Link} to="/">Home</Nav.Link>
                            <Nav.Link as={Link} to="/how-it-works">How It Works</Nav.Link>
                        </Nav>
                    </Navbar.Collapse>
                </Container>
            </Navbar>

            <Container>
                <Row>
                    <Col md={3}>
                        <h4>Filter Results</h4>
                        <Form>
                            <Form.Group controlId="filterYear">
                                <Form.Label>Year</Form.Label>
                                <Form.Select value={filterYear} onChange={e => setFilterYear(e.target.value)}>
                                    <option value="all">All Years</option>
                                    {years.map(year => (
                                        <option key={year} value={year}>{year}</option>
                                    ))}
                                </Form.Select>
                            </Form.Group>
                            <Form.Group controlId="sentimentFilter">
                                <Form.Label>Sentiment</Form.Label>
                                <Form.Select value={sentimentFilter} onChange={e => setSentimentFilter(e.target.value)}>
                                    <option value="all">All Sentiments</option>
                                    <option value="positive">Positive</option>
                                    <option value="neutral">Neutral</option>
                                    <option value="negative">Negative</option>
                                </Form.Select>
                            </Form.Group>
                            <Form.Group controlId="sourceFilter">
                                <Form.Label>Source</Form.Label>
                                <Form.Select value={sourceFilter} onChange={e => setSourceFilter(e.target.value)}>
                                    <option value="all">All Sources</option>
                                    {uniqueSources.map((source, index) => (
                                        <option key={index} value={source}>{source}</option>
                                    ))}
                                </Form.Select>
                            </Form.Group>
                        </Form>
                    </Col>
                    <Col md={9}>
                        <InputGroup className="mb-3">
                            <FormControl
                                placeholder="Search TF-IDF terms"
                                aria-label="Search"
                                value={searchQuery}
                                onChange={handleSearchInputChange}
                                onKeyPress={handleSearch}
                            />
                            <Button variant="outline-secondary" onClick={handleSearchClick}>
                                <BsSearch />
                            </Button>
                        </InputGroup>
                        
                        <h2>TF-IDF Search Results</h2>
                        <ColorCodingGuide />
                        {loading ? <Spinner animation="border" /> : (
                            filteredResults.length > 0 ? filteredResults.map((result, index) => (
                                <Card key={index} className="mb-3">
                                    <Card.Body>
                                        <Card.Title>{result.title}</Card.Title>
                                        <SentimentBadge sentiments={JSON.parse(result.sentiment).map(item => {
                        const parts = item.split(':');
                        return { type: parts[0].trim(), value: parseFloat(parts[1]) };
                      })} />
                                        <Card.Text>
                                            <strong>Score:</strong> {result.score}<br />
                                            <strong>Summary:</strong> {result.summary}
                                        </Card.Text>
                                        <Button variant="primary" href={result.url}>Read More</Button>
                                    </Card.Body>
                                </Card>
                            )) : <p>No results found for the selected filters.</p>
                        )}
                    </Col>
                </Row>
            </Container>
        </>
    );
}

export default TfidfResultsPage;