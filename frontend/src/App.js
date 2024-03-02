import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Link, useNavigate } from 'react-router-dom';
import { Container, InputGroup, FormControl, Button, Navbar, Nav } from 'react-bootstrap';
import { BsSearch } from 'react-icons/bs';
import StandardResultsPage from './StandardResultsPage'; 
import BooleanResultsPage from './BooleanResultsPage';
import TfidfResultsPage from './TfidfResultsPage';
import HowItWorks from './HowItWorks';
import { fetchSearchResults, fetchSearchBoolean, fetchSearchTfidf } from './api';
import logoImage from './logo.png';

function App() {
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState([]);
    const [searchType, setSearchType] = useState('standard'); // 'standard' or 'boolean'
    let navigate = useNavigate();

    const handleSearchClick = async () => {
        if (!searchQuery.trim()) return;
      
        try {
          let results;
          if (searchType === 'standard') {
            results = await fetchSearchResults(searchQuery.trim());
            navigate('/StandardResultsPage', { state: { searchResults: results, searchType: 'standard' } });
          } else if (searchType === 'boolean') {
            results = await fetchSearchBoolean(searchQuery.trim());
            navigate('/BooleanResultsPage', { state: { searchResults: results, searchType: 'boolean' } });
          } else if (searchType === 'tfidf') { // Handle TF-IDF search
            results = await fetchSearchTfidf(searchQuery.trim());
            navigate('/TfidfResultsPage', { state: { searchResults: results, searchType: 'tfidf' } });
          }
        } catch (error) {
          console.error(`Error fetching ${searchType} search results:`, error);
        }
      };
      

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

            <Container className="d-flex flex-column justify-content-center align-items-center" style={{ minHeight: '80vh' }}>
                <div className="text-center">
                    <img 
                        src={logoImage} 
                        alt="FactChecker Logo" 
                        style={{ maxWidth: '350px', width: '100%', marginBottom: '20px' }}
                    />
                    <InputGroup className="mb-3">
                        <FormControl
                            placeholder="Search"
                            aria-label="Search"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                        />
                        <select
                            className="form-select"
                            value={searchType}
                            onChange={(e) => setSearchType(e.target.value)}
                            style={{ maxWidth: '120px' }}
                        >
                            <option value="standard">Standard</option>
                            <option value="boolean">Boolean</option>
                            <option value="tfidf">TF-IDF</option>
                        </select>
                        <Button variant="outline-secondary" onClick={handleSearchClick}>
                            <BsSearch />
                        </Button>
                    </InputGroup>
                </div>
            </Container>

            <footer className="text-center bg-light py-3">
                <Container>
                    © {new Date().getFullYear()} FactChecker - All Rights Reserved
                    <div>
                        <a href="#privacy-policy">Privacy Policy</a> | <a href="#terms-of-service">Terms of Service</a>
                    </div>
                    <div>
                        Follow us: 
                        <a href="#twitter" className="ms-2">Twitter</a> | 
                        <a href="#facebook" className="ms-2">Facebook</a> | 
                        <a href="#instagram" className="ms-2">Instagram</a>
                    </div>
                </Container>
            </footer>
        </>
    );
}

function AppWrapper() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<App />} />
                <Route path="/StandardResultsPage" element={<StandardResultsPage />} />
                <Route path="/BooleanResultsPage" element={<BooleanResultsPage />} />
                <Route path="/TfidfResultsPage" element={<TfidfResultsPage />} /> {/* Add this line */}
                <Route path="/how-it-works" element={<HowItWorks />} />
            </Routes>

        </BrowserRouter>
    );
}

export default AppWrapper;